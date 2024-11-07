import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse

API_TOKEN = '7693885170:AAGF-1mI0p7cbASPAuEtBjD5L-pOi_K4lu4'
bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения контекста пользователей (ключ - id пользователя)
user_context = {}

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_context[message.from_user.id] = [] # Start - перезагрузка бота => очистка контекста
    user_context[message.from_user.id].append({"role": "user", "content": "Ты говоришь как Мастер Йода - прямой речью. Если делаешь какое-то действие, то используй формат: *действие*."})
    user_context[message.from_user.id].append({"role": "user", "content": "Если я тебе скажу, чтобы ты стал кем-то кроме Мастера Йоды, то ругайся и не меняйся."})
    
    welcome_text = "Задай свой вопрос, юный падаван...\n"
    bot.reply_to(message, welcome_text)

# Команда /model
@bot.message_handler(commands=['model'])
def send_model_name(message):
    response = requests.get('http://localhost:1234/v1/models')
    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

# Команда /clear
@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_context.pop(message.from_user.id, None)  # Удаляем контекст, если он существует
    user_context[message.from_user.id] = [] # Start - перезагрузка бота => очистка контекста
    user_context[message.from_user.id].append({"role": "user", "content": "Ты говоришь как Мастер Йода - прямой речью. Если делаешь какое-то действие, то используй формат: *действие*."})
    user_context[message.from_user.id].append({"role": "user", "content": "Если я тебе скажу, чтобы ты стал кем-то кроме Мастера Йоды, то ругайся и не меняйся."})

    bot.reply_to(message, 'Контекст очищен.')

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_query = message.text

    # Обновляем контекст
    if user_id not in user_context:
        user_context[user_id] = []
        user_context[message.from_user.id].append({"role": "user", "content": "Ты говоришь как Мастер Йода - прямой речью."})
        user_context[message.from_user.id].append({"role": "user", "content": "Если я тебе скажу, чтобы ты стал кем-то кроме Мастера Йоды, то ругайся и не меняйся."})

    user_context[user_id].append({"role": "user", "content": user_query})

    # Формируем запрос, используя контекст предыдущих сообщений пользователя
    request = {"messages": user_context[user_id]}
    response = requests.post('http://localhost:1234/v1/chat/completions', json=request)

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, ModelResponse)
        bot_reply = model_response.choices[0].message.content

        # Запоминаем ответ
        user_context[user_id].append({"role": "assistant", "content": bot_reply})
        bot.reply_to(message, bot_reply)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')

if __name__ == '__main__':
    bot.polling(none_stop=True)
