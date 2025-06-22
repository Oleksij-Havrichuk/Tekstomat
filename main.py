import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Завантаження токенів
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Клавіатура з емодзі
platform_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📸 Instagram", callback_data="platform_instagram"),
        InlineKeyboardButton(text="📘 Facebook", callback_data="platform_facebook"),
        InlineKeyboardButton(text="🛒 Allegro", callback_data="platform_allegro")
    ]
])

# Збереження даних користувача
user_data = {}

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "👋 Вітаю! Я допоможу тобі створити рекламний опис польською мовою для твого товару.\n\n"
        "📝 Просто напиши назву або короткий опис товару, а я згенерую готовий текст для Instagram, Facebook чи Allegro!"
    )

@dp.message(F.text)
async def handle_text(message: Message):
    user_data[message.from_user.id] = {"product": message.text}
    await message.answer("🔹 Обери платформу, для якої створити опис:", reply_markup=platform_keyboard)

@dp.callback_query(F.data.startswith("platform_"))
async def handle_platform(callback_query: types.CallbackQuery):
    await bot.send_chat_action(callback_query.from_user.id, action="typing")
    platform = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    product_name = user_data.get(user_id, {}).get("product")

    if not product_name:
        await callback_query.message.answer("❗️ Спочатку введи назву товару.")
        return

    prompt = f"Створи привабливий рекламний опис для товару '{product_name}' на платформу {platform.capitalize()} польською мовою. Додай емодзі, заклик до дії і стиль, відповідний до цієї платформи."

    try:
        logger.info("📤 Надсилаю запит до OpenAI...")
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти маркетолог, який пише рекламні тексти польською."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        description = response.choices[0].message.content
        logger.info("📥 Відповідь отримано")
        await callback_query.message.answer(
            f"✅ <b>Опис для {platform.capitalize()}:</b>\n\n{description}"
        )
    except Exception as e:
        logger.error("❌ Помилка під час генерації опису", exc_info=True)
        await callback_query.message.answer("⚠️ Сталася помилка під час генерації опису. Спробуй ще раз.")

# Запуск
async def main():
    logger.info("🚀 Запуск бота")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("❌ Глобальна помилка запуску", exc_info=True)
