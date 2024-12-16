import json
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.models import PlantData, QAEntry
from backend.pydanticai import InferenceResult

class PlantInfoViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.plant = PlantData.objects.create(common_name="Test Plant", scientific_name="test", description="test", care_instructions="test", soil_type="test", water_requirements="test", sunlight_requirements="test", vector_data=[1,2,3])
        self.url = reverse('plant_info')

    @patch("backend.views.get_embedding")
    @patch("backend.views.get_similar_qa_entry")
    @patch("backend.views.create_qa_entry")
    @patch("backend.views.agent.run_sync")
    async def test_plant_info_view(self, mock_run_sync, mock_create_qa, mock_get_similar, mock_get_embedding):
        mock_get_similar.return_value = None
        mock_get_embedding.return_value = [1,2,3]
        mock_run_sync.return_value = InferenceResult(inference="Test Response")
        data = {'plant_name': 'Test Plant', 'user_query': 'test query'}
        response = await self.async_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Test Response')

    @patch("backend.views.get_embedding")
    @patch("backend.views.get_similar_qa_entry")
    async def test_plant_info_view_cached(self, mock_get_similar, mock_get_embedding):
        mock_get_embedding.return_value = [1,2,3]
        qa_entry = QAEntry.objects.create(plant=self.plant, question_text="test query", question_vector=[1,2,3], answer_text="cached answer", answer_vector=[1,2,3])
        mock_get_similar.return_value = qa_entry
        data = {'plant_name': 'Test Plant', 'user_query': 'test query'}
        response = await self.async_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'cached answer')
        self.assertTrue(response.data['from_cache'])

    async def test_plant_info_view_no_plant(self):
        data = {'plant_name': 'NonExistentPlant', 'user_query': 'test query'}
        response = await self.async_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_plant_info_view_missing_plant_name(self):
        data = {'user_query': 'test query'}
        response = await self.async_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_plant_info_view_empty_request(self):
        response = await self.async_client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400