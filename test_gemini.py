
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")
else:
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Explain Python functions in 3 simple sentences."
        )

        print("Gemini connected successfully!")
        print(response.text)

    except Exception as e:
        print("Gemini request failed.")
        print("Error:", e)
