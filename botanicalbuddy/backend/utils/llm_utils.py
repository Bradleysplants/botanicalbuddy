# backend/llm_utils.py
import google.generativeai as genai
import os

class GeminiLLM:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-pro")

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the Gemini model.

        Args:
            prompt: The text prompt to send to the Gemini model.

        Returns:
            The generated text response from the model.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "An error occurred while generating the response."