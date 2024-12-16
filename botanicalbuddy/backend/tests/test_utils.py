import unittest
from backend.utils import calculate_cosine_similarity

class TestUtils(unittest.TestCase):

    def test_calculate_cosine_similarity(self):
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)

        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 1.0)

        vec1 = [1, 1, 0]
        vec2 = [0, 1, 1]
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.5)

        vec1 = []
        vec2 = [1,2,3]
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)

        vec1 = [1,2,3]
        vec2 = []
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)