from google import genai

API = "yourapi"

client = genai.Client(api_key=API)

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few Words")

print(response.text)
