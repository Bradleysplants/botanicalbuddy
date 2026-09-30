import unittest
from unittest.mock import patch

from backend.crew import create_crew_with_dynamic_tasks, Intent
import sys
print(sys.path)

class TestCrewCreation(unittest.TestCase):

    def test_create_crew_with_identify_plant_query(self):
        user_query = "Identify this flower I saw"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Expert Plant Identifier")
        self.assertTrue("identify the plant" in crew.tasks[0].description.lower())

    def test_create_crew_with_plant_care_query(self):
        user_query = "How do I care for my roses?"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Master Horticulturalist")
        self.assertTrue("care instructions" in crew.tasks[0].description.lower())

    def test_create_crew_with_soil_info_query(self):
        user_query = "What kind of soil is best for tomatoes?"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Certified Soil Analysis Expert")
        self.assertTrue("soil-related query" in crew.tasks[0].description.lower())

    def test_create_crew_with_botanical_info_query(self):
        user_query = "Tell me about the origin of sunflowers"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Doctor of Botany")
        self.assertTrue("botanical aspects" in crew.tasks[0].description.lower())

    def test_create_crew_with_general_query(self):
        user_query = "I have a question about my plant"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Tier 1 Customer Support Specialist")
        self.assertTrue("general plant query" in crew.tasks[0].description.lower())

    def test_create_crew_with_empty_query(self):
        user_query = ""
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.tasks[0].agent.role, "Tier 1 Customer Support Specialist")
        self.assertTrue("general plant query" in crew.tasks[0].description.lower())

    def test_crew_agents_are_correct(self):
        user_query = "Tell me something about plants"
        crew = create_crew_with_dynamic_tasks(user_query)
        self.assertIsNotNone(crew)
        expected_agent_roles = {
            "Expert Plant Identifier",
            "Tier 1 Customer Support Specialist",
            "Certified Soil Analysis Expert",
            "Doctor of Botany",
            "Master Horticulturalist",
        }
        actual_agent_roles = {agent.role for agent in crew.agents}
        self.assertEqual(actual_agent_roles, expected_agent_roles)

    # Example of testing with mocking (more advanced)
    @patch("backend.crew.TrefleTool._run")
    def test_trefle_tool_is_called(self, mock_trefle_run):
        mock_trefle_run.return_value = "Mock Trefle Data"
        user_query = "Tell me about the origin of sunflowers"
        crew = create_crew_with_dynamic_tasks(user_query)
        # Assuming the Botanist is the one using the TrefleTool for this query
        if crew.tasks and crew.tasks[0].agent.role == "Doctor of Botany":
            crew.run_tasks("Test Goal")  # You might need to run the crew to trigger the tool
            mock_trefle_run.assert_called()

if __name__ == '__main__':
    unittest.main()