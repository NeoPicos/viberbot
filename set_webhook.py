from settings import TOKEN, WEBHOOK
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

# Конфигурация viber-бота
bot_configuration = BotConfiguration(
    name='neopicosBot',
    avatar='https://viber.com/avatar/jpg',
    auth_token=TOKEN
)
viber = Api(bot_configuration)

# Установка webhook
viber.set_webhook(WEBHOOK)

