from google import genai

API = "AIzaSyAyf7u1BQti4OrzcLkNLf3l0H0J1RWBSFg"

client = genai.Client(api_key=API)

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few Words")

print(response.text)
