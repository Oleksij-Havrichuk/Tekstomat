import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ Не знайдено ключ OPENAI_API_KEY у .env")

print("✅ Ключ успішно завантажено")