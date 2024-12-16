import unittest
from unittest.mock import patch, MagicMock
from backend.pydanticai import VectorData, PlantData, Agent, get_embedding, InferenceResult
import openai

class TestPydanticai(unittest.TestCase):

    def test_vector_data_validation(self):
        with self.assertRaises(ValueError):
            VectorData(data=[])  # Empty data

        VectorData(data=[1.0, 2.0, 3.0])  # Valid data

    def test_plant_data_validation(self):
        with self.assertRaises(ValueError):
             PlantData(plant_name=None, scientific_name="test", description="test", care_instructions="test", soil_type="test", water_requirements="test", sunlight_requirements="test", vector_data=[1,2,3])

        PlantData(plant_name="Test Plant", scientific_name="test", description="test", care_instructions="test", soil_type="test", water_requirements="test", sunlight_requirements="test", vector_data=[1,2,3])

    @patch("backend.pydanticai.openai.Embedding.create")
    def test_get_embedding(self, mock_embedding_create):
        mock_embedding_create.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
        embedding = get_embedding("test text")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

    @patch("backend.pydanticai.openai.Embedding.create")
    def test_get_embedding_api_error(self, mock_embedding_create):
        mock_embedding_create.side_effect = openai.APIError("Test Error")
        embedding = get_embedding("test text")
        self.assertIsNone(embedding)

    @patch("backend.pydanticai.openai.Completion.acreate")
    async def test_agent_run_sync(self, mock_completion_create):
        mock_completion_create.return_value = MagicMock(choices=[MagicMock(text="Test Response")])
        agent = Agent()
        plant_data = [PlantData(plant_name="Test Plant", scientific_name="test", description="test", care_instructions="test", soil_type="test", water_requirements="test", sunlight_requirements="test", vector_data=[1,2,3], similarity=1)]
        inference_result = await agent.run_sync(VectorData(data=[1,2,3]), plant_data, "test query")
        self.assertEqual(inference_result.inference, "Test Response")
        self.assertIsInstance(inference_result, InferenceResult)

    @patch("backend.pydanticai.openai.Completion.acreate")
    async def test_agent_run_sync_no_plant(self, mock_completion_create):
        agent = Agent()
        inference_result = await agent.run_sync(VectorData(data=[1,2,3]), [], "test query")
        self.assertEqual(inference_result.inference, "No similar plants found.")

if __name__ == '__main__':
    unittest.main()