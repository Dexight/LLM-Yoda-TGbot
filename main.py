import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
API_TOKEN = '7693885170:AAGF-1mI0p7cbASPAuEtBjD5L-pOi_K4lu4'
bot = telebot.TeleBot(API_TOKEN)

# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Задай вопрос, юный падаван.\n"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    # Отправляем запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_query = message.text
    request = {
        "messages": [
          {
            "role": "user",
            "content": message.text
          },
    ]
  }
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response :ModelResponse = jsons.loads(response.text, ModelResponse)
        bot.reply_to(message, model_response.choices[0].message.content)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)