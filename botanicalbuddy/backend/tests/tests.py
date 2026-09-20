"""API and unit tests for the backend app.

The database-backed tests need PostgreSQL with the pgvector extension
(see the README: ``docker compose up -d db``). External services (OpenAI,
Ollama, the spaCy model download) are never contacted.
"""
import asyncio
import os
from unittest import mock

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from backend import pydanticai, utils
# NOTE: the models (Conversation.participants, Message.sender) point at
# backend.User, while settings.AUTH_USER_MODEL is still Django's default
# auth.User. Tests use backend.User so they exercise the models as written.
from backend.models import Conversation, PlantData, QAEntry, User


class AuthRequiredTests(TestCase):
    def test_protected_endpoints_reject_anonymous_requests(self):
        client = APIClient()
        for name, kwargs in [
            ('get_plant_data', {'pk': 1}),
            ('get_qa_entry', {'pk': 1}),
            ('chat_list_create', {}),
            ('get_current_user', {}),
        ]:
            with self.subTest(endpoint=name):
                response = client.get(reverse(f'backend:{name}', kwargs=kwargs))
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PlantDataTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.plant = PlantData.objects.create(
            common_name='Rose', scientific_name='Rosa damascena')

    def test_create_plant_data(self):
        response = self.client.post(
            reverse('backend:create_plant_data'),
            {'common_name': 'Sunflower', 'scientific_name': 'Helianthus annuus'},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlantData.objects.count(), 2)

    def test_get_plant_data(self):
        response = self.client.get(
            reverse('backend:get_plant_data', kwargs={'pk': self.plant.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['common_name'], 'Rose')

    def test_get_plant_data_not_found(self):
        response = self.client.get(
            reverse('backend:get_plant_data', kwargs={'pk': 999999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_qa_entry(self):
        entry = QAEntry.objects.create(
            plant=self.plant,
            question_text='How do I care for my rose?',
            answer_text='Roses need full sun.')
        response = self.client.get(
            reverse('backend:get_qa_entry', kwargs={'pk': entry.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question_text'], 'How do I care for my rose?')


class ChatTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        PlantData.objects.create(common_name='Rose')

    def test_create_and_list_chat(self):
        response = self.client.post(
            reverse('backend:chat_list_create'), {'plant_name': 'Rose'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)

        listing = self.client.get(reverse('backend:chat_list_create'))
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data['chats']), 1)

    def test_create_chat_requires_known_plant(self):
        response = self.client.post(
            reverse('backend:chat_list_create'), {'plant_name': 'Nope'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UtilsTests(SimpleTestCase):
    def test_cosine_similarity(self):
        self.assertAlmostEqual(utils.calculate_cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(utils.calculate_cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_get_embedding_returns_vector(self):
        fake_client = mock.Mock()
        fake_client.embeddings.create = mock.AsyncMock(
            return_value=mock.Mock(data=[mock.Mock(embedding=[0.1, 0.2])]))
        with mock.patch.object(utils, 'AsyncOpenAI', return_value=fake_client):
            self.assertEqual(asyncio.run(utils.get_embedding('hi')), [0.1, 0.2])


class AgentTests(SimpleTestCase):
    def test_importing_views_does_not_require_api_keys(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('OPENAI_API_KEY', None)
            import importlib
            from backend import views
            importlib.reload(views)  # must not raise

    def test_create_agent_requires_openai_key(self):
        with mock.patch.dict(os.environ, {'AI_AGENT_TYPE': 'openai'}):
            os.environ.pop('OPENAI_API_KEY', None)
            with self.assertRaises(ValueError):
                pydanticai.create_agent()

    def test_openai_agent_returns_completion_text(self):
        with mock.patch.dict(os.environ, {'AI_AGENT_TYPE': 'openai', 'OPENAI_API_KEY': 'test-key'}):
            agent = pydanticai.create_agent()
        completion = mock.Mock(choices=[mock.Mock(message=mock.Mock(content=' Water weekly. '))])
        agent.client = mock.Mock()
        agent.client.chat.completions.create = mock.AsyncMock(return_value=completion)
        result = asyncio.run(agent.run_inference(
            pydanticai.PlantData(plant_name='Rose'), 'How often should I water?'))
        self.assertEqual(result.answer, 'Water weekly.')
