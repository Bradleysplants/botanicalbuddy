from crewai.llm import LLM
import google.generativeai as genai

print("Loading backend/utils/GeminiLLM.py")

class GeminiLLM(LLM):
    def __init__(self, api_key=None, **kwargs):
        print("GeminiLLM __init__ called")
        if not api_key:
            raise ValueError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model = 'gemini-pro'
        super().__init__(**kwargs)  # Initialize the base LLM class

    def _complete(self, prompt: str, **kwargs) -> str:
        print(f"GeminiLLM _complete called with prompt: {prompt}")
        response = genai.GenerativeModel(self.model).generate_content(prompt)
        return response.text

    async def _async_complete(self, prompt: str, **kwargs) -> str:
        print(f"GeminiLLM _async_complete called with prompt: {prompt}")
        response = genai.GenerativeModel(self.model).generate_content(prompt)
        return response.text