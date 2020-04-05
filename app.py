import random
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from keyboards import start_keyboard, round_keyboard, remind_keyboard
from settings import TOKEN
from models import User, Learning, Word, Example, Setting
from time import sleep
from flask import render_template
from flask import request
from flask import make_response
from cash import WordsCash
from models import build_db_struct

# Инициализация Flask-приложения
app = Flask(__name__)

# Инициализация Viber-бота
viber = Api(BotConfiguration(
    name='neopicosBot',
    avatar='https://viber.com/avatar/jpg',
    auth_token=TOKEN
))

# Кеш слов для изучения (key: viber_id, value: list of learning words)
word_cash = {}

# Кеш для токенов сообщений
mess_token_cash = {}


# Страница с информацией о боте
@app.route('/')
def index():
    # Отрисовка шаблона
    return render_template("about.html")


# Страница настройки параметров бота
@app.route('/settings', methods=['GET'])
def settings():
    # Отрисовка шаблона
    return render_template("request_page.html")


# Страница успешной установки параметров бота
@app.route('/settings_done', methods=['GET'])
def settings_done():
    # Получение новых параметров бота из формы
    # Количество вопросов в раунде
    total_count = int(request.args.get('total_count'))

    # Время для напоминания
    remind_time = int(request.args.get('remind_time'))

    # Количество отгадываний слов для его заучивания
    limit_words_for_learning = int(request.args.get('limit_words_for_learning'))

    # Установка новых параметров
    setting = Setting()
    setting.set_settings(remind_time, total_count, limit_words_for_learning)

    # Ответ
    result_obj = render_template("settings_done.html")
    response = make_response(result_obj)

    return response


# Обработка приходящих запросов
@app.route('/incoming', methods=['POST'])
def incoming():
    # Входящий запрос
    viber_request = viber.parse_request(request.get_data())

    # Обработка входящего запроса
    processing_request(viber_request)

    # Успешно обработанный запрос
    return Response(status=200)


# Обработка запроса от пользователя
def processing_request(viber_request):
    # Действия для новых пользователей
    if isinstance(viber_request, ViberConversationStartedRequest):
        # Добавление нового пользователя
        user = User()
        user.add(viber_request.user.id)

        user.set_last_message_token(viber_request.user.id, str(viber_request.message_token))

        # Вывод стартового окна
        show_start_area(viber_request)
        return

    # Действия для подписавшихся пользователей
    if isinstance(viber_request, ViberMessageRequest):
        user = User()
        if viber_request.message_token == user.get_last_message_token(viber_request.sender.id):
            return
        else:
           user.set_last_message_token(viber_request.sender.id, viber_request.message_token)

        # Обработка команды 'start': запуск нового раунда
        message = viber_request.message.text
        if message == 'start':
            user = User()
            user.reset_round(viber_request.sender.id)

            # Закешировать слова для изучения
            word_cash[viber_request.sender.id] = WordsCash(viber_request.sender.id)
            word_cash[viber_request.sender.id].cash_learning_words()

            # Вывод второго игрового окна
            show_round_area(viber_request)
            return

        # Напомнить позже
        if message == 'remind_later':
            # Изменить время последнего ответа на текущее
            user = User()
            user.set_time_last_answer(viber_request.sender.id)

            # Отправка сообщения
            setting = Setting()
            textMess = f"Напомню через {str(setting.get_remind_time())} минут(ы)"
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text=textMess)
            ])
            return

        # Продолжение уже начатого раунда, если раунд не закончился
        user = User()
        # Обработка команды 'show_example': вывод примера употребления слова
        if viber_request.message.text == 'show_example':
            send_example_message(viber_request)
        else:
            # Проверка ответа на правильность
            check_answer(viber_request)

            setting = Setting()
            total_count = setting.get_lim_question()
            if user.get_num_question(viber_request.sender.id) < total_count:
                # Продолжение раунда
                show_round_area(viber_request)
                return
            else:
                # Обновить данные из кеша
                word_cash[viber_request.sender.id].cash_learning_words()

                # Завершение рунда
                send_result_message(viber_request)
                user.reset_round(viber_request.sender.id)
                show_start_area(viber_request)
                return


# Вывод стартовой клавитуры и приветствие
def show_start_area(viber_request):
    # Выделение идентификатора пользователя
    if isinstance(viber_request, ViberConversationStartedRequest):
        user_id = viber_request.user.id
    else:
        user_id = viber_request.sender.id

    # Приветственное сообщение
    message = "Этот бот предназначен для заучивания английских слов." \
              " Для начала работы введите start или нажмите на кнопку внизу."

    viber.send_messages(user_id, [
        TextMessage(text=message,
                    keyboard=start_keyboard,
                    tracking_data='tracking_data')
    ])
    return


# Отправка "второго" игрового экрана
def show_round_area(viber_request):
    # Список еще не выученных слов
    study_words = word_cash[viber_request.sender.id].words_list

    # Текущее слово
    current_word = study_words[random.randint(0, len(study_words) - 1)]

    # Расстановка кнопок на клавиатуре
    word = Word()
    translation = word.get_translation(current_word)
    study_words.remove(current_word)
    set_round_keyboard(viber_request, translation, study_words)

    # Отправка сообщения с вопросом
    send_question_message(viber_request, current_word)

    # Сохранение новых параметров раунда
    user = User()
    user.set_round_data(viber_request.sender.id, current_word)


# Отправка сообщения с вопросом
def send_question_message(viber_request, word):
    # Формирование ответного сообщения
    user = User()
    message = str(
        user.get_num_question(viber_request.sender.id) + 1) + ")" + f" Как переводится с английского слово [{word}]?"

    viber.send_messages(viber_request.sender.id, [
        TextMessage(text=message,
                    keyboard=round_keyboard,
                    tracking_data='tracking_data')
    ])


# Динамическая настройка клавиатуры
def set_round_keyboard(viber_request, correct_translation, word_list):
    # Три случайных слова
    wrong_words = random.sample(word_list, 3)

    # Случайная последовательность для нумерации кнопок
    rand_num = random.sample([0, 1, 2, 3], 4)

    user = User()

    # Установка правильного ответа на случайную кнопку
    round_keyboard["Buttons"][rand_num[0]]["Text"] = correct_translation
    round_keyboard["Buttons"][rand_num[0]]["ActionBody"] = str(user.get_num_question(viber_request.sender.id)) + ' ' + correct_translation

    # Расстановка неправильных слов на случайную кнопку
    word = Word()
    wrong_translation = word.get_translation(wrong_words[0])
    round_keyboard["Buttons"][rand_num[1]]["Text"] = wrong_translation
    round_keyboard["Buttons"][rand_num[1]]["ActionBody"] = str(user.get_num_question(viber_request.sender.id)) + ' ' + wrong_translation

    wrong_translation = word.get_translation(wrong_words[1])
    round_keyboard["Buttons"][rand_num[2]]["Text"] = wrong_translation
    round_keyboard["Buttons"][rand_num[2]]["ActionBody"] = str(user.get_num_question(viber_request.sender.id)) + ' ' + wrong_translation

    wrong_translation = word.get_translation(wrong_words[2])
    round_keyboard["Buttons"][rand_num[3]]["Text"] = wrong_translation
    round_keyboard["Buttons"][rand_num[3]]["ActionBody"] = str(user.get_num_question(viber_request.sender.id)) + ' ' + wrong_translation


# Показать пример использования слова
def send_example_message(viber_request):
    # Получить список примеров для текущего слова
    user = User()
    ex = Example()
    current_word = user.get_current_word(viber_request.sender.id)
    example_list = ex.get_examples(current_word)

    # Выбор члучайного примера из списка
    count_examples = len(example_list)
    example = example_list[random.randint(0, count_examples - 1)]

    viber.send_messages(viber_request.sender.id, [
        TextMessage(text=example,
                    keyboard=round_keyboard,
                    tracking_data='tracking_data')
    ])


# Проверка ответа на правильность
def check_answer(viber_request):
    # Получить правильный ответ
    word = Word()
    user = User()
    correct_answer = word.get_translation(user.get_current_word(viber_request.sender.id))

    answer = str(viber_request.message.text).split(' ')
    num_question = int(answer[0]) + 1
    ans = answer[1]
    
    if num_question == user.get_num_question(viber_request.sender.id):
        return
    if answer == correct_answer and num_question == user.get_num_question(viber_request.sender.id):
        # Правильный ответ - зафиксировать в данных раунда
        user = User()
        user.inc_correct_answer(viber_request.sender.id)

        # Зафиксировать правильный ответ в таблице Learning
        learn = Learning()
        learn.mark_correct_answer(viber_request.sender.id, user.get_current_word(viber_request.sender.id))

        # Получить количество правильных ответов на данный вопрос
        num_correct_answer = learn.get_num_correct_answer(viber_request.sender.id,
                                                          user.get_current_word(viber_request.sender.id))
        message = "Ваш ответ: [" + str(correct_answer) + "]. Правильно! Слово отгадано: " + str(
            num_correct_answer) + " раз."
    else:
        message = "Ваш ответ: [" + ans + "]. Неправильно!"

    viber.send_messages(viber_request.sender.id, [
        TextMessage(text=message + str(num_question))
    ])


# Отправка сообщения с результатами
def send_result_message(viber_request):
    # Сообщить количество правильных и неправильных слов
    user = User()
    settings = Setting()
    message = "Конец раунда. Правильных ответов из " + str(settings.get_lim_question()) + ": " + str(
        user.get_round_correct_answer(viber_request.sender.id))

    # Отправка сообщения
    viber.send_messages(viber_request.sender.id, [
        TextMessage(text=message)
    ])


# Сделать напоминание
def remind(viber_id):
    message = 'Привет! Повтори слова, чтобы не забыть их!'

    viber.send_messages(viber_id, [
        TextMessage(text=message,
                    keyboard=remind_keyboard,
                    tracking_data='tracking_data')
    ])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=90)
