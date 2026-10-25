import telebot
from telebot import types

TOKEN = "8512024930:AAGHa5CMmDW4PkSlvn2Ee6A8wN-cIFB91tQ"
bot = telebot.TeleBot(TOKEN)

# Хранилище: кому пользователь сейчас пишет сообщение
user_recipients = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    args = message.text.split()
    bot_info = bot.get_me()

    # Если перешли по ссылке /start <id>
    if len(args) > 1 and args[1].isdigit():
        target_id = int(args[1])
        if target_id == message.chat.id:
            bot.send_message(message.chat.id, "Это ваша собственная ссылка. Отправьте её друзьям, чтобы получать вопросы.")
            return

        user_recipients[message.chat.id] = target_id
        bot.send_message(message.chat.id, "Напишите сообщение. Оно будет доставлено анонимно:")
    else:
        link = f"https://t.me/{bot_info.username}?start={message.chat.id}"
        bot.send_message(
            message.chat.id,
            f"Привет! Твоя ссылка для получения анонимных сообщений:\n\n{link}"
        )

@bot.message_handler(content_types=['text', 'photo', 'voice'])
def handle_message(message):
    sender_id = message.chat.id
    recipient_id = user_recipients.get(sender_id)

    if not recipient_id:
        bot.send_message(sender_id, "Чтобы отправить сообщение, перейдите по персональной ссылке нужного человека.")
        return

    # Кнопка для ответа
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_{sender_id}"))

    try:
        if message.text:
            bot.send_message(recipient_id, f"Вам анонимное сообщение:\n\n{message.text}", reply_markup=markup)
        elif message.photo:
            bot.send_photo(recipient_id, message.photo[-1].file_id, caption="Вам анонимное фото", reply_markup=markup)
        elif message.voice:
            bot.send_voice(recipient_id, message.voice.file_id, caption="Вам анонимное голосовое", reply_markup=markup)

        bot.send_message(sender_id, "Сообщение успешно отправлено анонимно!")
    except Exception:
        bot.send_message(sender_id, "Не удалось доставить сообщение. Возможно, пользователь заблокировал бота.")
    finally:
        user_recipients.pop(sender_id, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply_button(call):
    author_id = int(call.data.split('_')[1])
    user_recipients[call.message.chat.id] = author_id
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Напишите ваш ответ. Он отправится обратно анонимно:")

if __name__ == '__main__':
    print("Бот работает...")
    bot.infinity_polling()


