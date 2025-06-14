import time
import telebot
from g4f.client import Client
from telebot import types
import threading

TOKEN = ''
CHANNEL_ID = '@RandomNews22'

bot = telebot.TeleBot(TOKEN)
client = Client()

# Флаг для контроля работы автопостинга
auto_posting_active = False
post_interval = 60
last_post_time = 0


def generate_random_post():
    prompt = (
        """Сгенерируй один уникальный, необычный и максимально рандомный факт на любую тему: наука, природа, история, культура, космос или вымысел. Факт должен быть:
    - Неочевидным
    - Интересным и удивляющим
    - Кратким (1–3 предложения)
    - Может содержать научную загадку, исторический курьёз, странный закон природы или футуристическую теорию

    Примеры:
    🔹 В 1958 году NASA отправило в космос золотую мышь.
    🔹 У осьминога три сердца и синяя кровь.
    🔹 Некоторые виды медуз могут "стареть в обратном порядке".

    Придумай свой!
"""
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка генерации: {e}"


def post_to_channel():
    if not CHANNEL_ID:
        return
    post = generate_random_post()
    try:
        bot.send_message(CHANNEL_ID, post)
    except Exception as e:
        print(f"Не удалось опубликовать пост: {e}")


def auto_post_loop():
    global auto_posting_active
    while auto_posting_active:
        post_to_channel()
        time.sleep(post_interval)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен. Используйте /run для автопубликации.")


@bot.message_handler(commands=['channel'])
def send_post_now(message):
    post = generate_random_post()
    bot.send_message(message.chat.id, post)
    if CHANNEL_ID:
        bot.send_message(CHANNEL_ID, post)


@bot.message_handler(commands=['run'])
def run(message):
    global auto_posting_active
    if auto_posting_active:
        bot.reply_to(message, "Автопубликация уже запущена.")
        return

    auto_posting_active = True
    bot.reply_to(message, "Автопубликация начата.")
    thread = threading.Thread(target=auto_post_loop)
    thread.start()


# Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)
