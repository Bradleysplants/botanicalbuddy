# backend/tests/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

from backend.models import PlantData, QAEntry
from backend.utils import get_embedding


class PlantDataTests(TestCase):
    async def setUp(self):
        self.client = APIClient()
        self.user = await sync_to_async(User.objects.create_user)(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.plant_data = await sync_to_async(PlantData.objects.create)(
            common_name="Rose",
            scientific_name="Rosa damascena",
            # ... other fields ...
        )

    async def test_create_plant_data(self):
        """
        Test creating a new PlantData object.
        """
        await self.setUp()
        data = {
            "common_name": "Sunflower",
            "scientific_name": "Helianthus annuus",
            # ... other fields ...
        }
        response = await sync_to_async(self.client.post)(
            reverse('backend:create_plant_data'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(await sync_to_async(PlantData.objects.count)(), 2)

    async def test_get_plant_data(self):
        """
        Test retrieving a PlantData object.
        """
        await self.setUp()
        response = await sync_to_async(self.client.get)(
            reverse('backend:get_plant_data',
                    kwargs={'pk': self.plant_data.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['common_name'], "Rose")


class QAEntryTests(TestCase):
    async def setUp(self):
        self.client = APIClient()
        self.user = await sync_to_async(User.objects.create_user)(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.plant_data = await sync_to_async(PlantData.objects.create)(
            common_name="Rose",
            scientific_name="Rosa damascena",
            # ... other fields ...
        )
        self.qa_entry = await sync_to_async(QAEntry.objects.create)(
            plant=self.plant_data,
            question_text="How do I care for my rose?",
            question_vector=await get_embedding("How do I care for my rose?"),
            answer_text="Roses need...",
        )

    async def test_create_qa_entry(self):
        """
        Test creating a new QAEntry object.
        """
        await self.setUp()
        data = {
            "plant": self.plant_data.pk,
            "question_text": "When should I prune my rose?",
            "answer_text": "Prune your rose...",
        }
        response = await sync_to_async(self.client.post)(
            reverse('backend:create_qa_entry'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(await sync_to_async(QAEntry.objects.count)(), 2)

    async def test_get_qa_entry(self):
        """
        Test retrieving a QAEntry object.
        """
        await self.setUp()
        response = await sync_to_async(self.client.get)(
            reverse('backend:get_qa_entry', kwargs={'pk': self.qa_entry.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['question_text'],
                         "How do I care for my rose?")


class APITests(TestCase):
    async def setUp(self):
        self.client = APIClient()
        self.user = await sync_to_async(User.objects.create_user)(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.plant_data = await sync_to_async(PlantData.objects.create)(
            common_name="Rose",
            scientific_name="Rosa damascena",
            common_diseases=["black spot", "powdery mildew"],
            common_pests=["aphids", "spider mites"],
            # ... other fields ...
        )

    async def test_upload_image(self):
        """
        Test uploading an image.
        """
        await self.setUp()
        with open(
                '/home/bradleys/Pictures/Screenshots/Screenshot from 2024-08-28 21-09-47.png',
                'rb') as image_file:
            response = await sync_to_async(self.client.post)(
                reverse('backend:upload_image'),
                {'image': image_file,
                 'plant_id': self.plant_data.pk},
                format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prediction', response.data)

    async def test_ask_botanical_question(self):
        """
        Test asking a question about a plant.
        """
        await self.setUp()

        data = {
            'query': "How do I care for my rose?",
            'plant_name': "Rose"
        }
        response = await sync_to_async(self.client.post)(
            reverse('backend:ask_botanical_question'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)

        # Test a diagnostic question with mock prediction results
        data = {
            'query': "My rose has black spots on its leaves.",
            'plant_name': "Rose",
            'prediction': {
                'disease_probability': 0.9,
                'disease_label': "black spot",
                'pest_probability': 0.1,
                'pest_label': "aphids"
            }
        }
        response = await sync_to_async(self.client.post)(
            reverse('backend:ask_botanical_question'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)
        self.assertIn('common_diseases', response.data)
        self.assertIn('common_pests', response.data)