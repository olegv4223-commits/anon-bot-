import asyncio
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8512024930:AAGHa5CMmDW4PkSlvn2Ee6A8wN-cIFB91tQ"

def init_db():
    conn = sqlite3.connect("anon_bot.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def add_user(user_id: int):
    conn = sqlite3.connect("anon_bot.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

class AnonStates(StatesGroup):
    waiting_for_message = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    add_user(message.from_user.id)
    bot_info = await bot.get_me()
    recipient_id = command.args

    if recipient_id and recipient_id.isdigit():
        target_id = int(recipient_id)
        if target_id == message.from_user.id:
            await message.answer("Это ваша ссылка. Отправьте её друзьям, чтобы получать вопросы.")
            return

        await state.update_data(recipient_id=target_id)
        await state.set_state(AnonStates.waiting_for_message)
        await message.answer("Напишите сообщение. Оно будет доставлено анонимно:")
    else:
        my_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        await message.answer(
            f"Привет! Твоя ссылка для получения анонимных сообщений:\n\n{my_link}",
            parse_mode="Markdown"
        )

@dp.message(AnonStates.waiting_for_message)
async def process_anon_message(message: Message, state: FSMContext):
    data = await state.get_data()
    recipient_id = data.get("recipient_id")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Ответить", callback_data=f"reply_{message.from_user.id}")
        ]]
    )

    try:
        if message.text:
            await bot.send_message(
                chat_id=recipient_id,
                text=f"Вам новое анонимное сообщение:\n\n{message.text}",
                reply_markup=kb
            )
        elif message.photo:
            await bot.send_photo(
                chat_id=recipient_id,
                photo=message.photo[-1].file_id,
                caption="Вам анонимное фото",
                reply_markup=kb
            )
        elif message.voice:
            await bot.send_voice(
                chat_id=recipient_id,
                voice=message.voice.file_id,
                caption="Вам анонимное голосовое",
                reply_markup=kb
            )
        await message.answer("Сообщение успешно отправлено!")
    except Exception:
        await message.answer("Не удалось доставить сообщение.")
    finally:
        await state.clear()

async def main():
    init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
