from datetime import datetime, timedelta, time
from sqlalchemy import create_engine, MetaData, Table, Column, types, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# Декларативный базовый класс
Base = declarative_base()

# Подключение к БД
engine = create_engine('postgres://gfctnifkhemtiv:37f51fd73f1661cf2e439f4be9ba4d5e2bbfbbe36ce527c586badaa2c35be5da@ec2-176-34-97-213.eu-west-1.compute.amazonaws.com:5432/d2i5jskl01pudr', echo=True)

metadata = MetaData()

# Сессия
Session = sessionmaker()
Session.configure(bind=engine)


# Настройки
class Setting(Base):
    __tablename__ = 'setting'

    id = Column(types.Integer, primary_key=True)
    remind_time = Column(types.Integer)
    lim_question = Column(types.Integer)
    num_correct = Column(types.Integer)

    # Добавление новой записи (должна быть всего одна запись)
    @staticmethod
    def create_item():
        session = Session()
        setting_item = Setting(remind_time=3,
                               lim_question=10,
                               num_correct=10)
        session.add(setting_item)
        session.commit()
        session.close()

    # Установка настроек
    def set_settings(self,
                     remind_time,
                     lim_question,
                     num_correct):
        session = Session()
        setting = session.query(Setting).one()
        setting.remind_time = remind_time
        setting.lim_question = lim_question
        setting.num_correct = num_correct
        session.commit()
        session.close()

    # Получить время напоминания
    def get_remind_time(self):
        session = Session()
        remind_time = session.query(Setting.remind_time).one()
        session.close()
        return remind_time[0]

    # Получить количество слов для одного раунда
    def get_lim_question(self):
        session = Session()
        lim_question = session.query(Setting.lim_question).one()
        session.close()
        return lim_question[0]

    # Получить количество правильных ответов, после которых считается, что слово выучено
    def get_num_correct(self):
        session = Session()
        num_correct = session.query(Setting.num_correct).one()
        session.close()
        return num_correct[0]


# Пользователь
class User(Base):
    __tablename__ = 'user'

    id = Column(types.String(), primary_key=True)
    time_last_answer = Column(types.DateTime)
    num_round_question = Column(types.INTEGER)
    num_answer = Column(types.INTEGER)
    current_word = Column(types.String())
    num_round_correct_answer = Column(types.INTEGER)

    # Добавление нового пользователя
    def add(self, viber_id):
        # Создание сессии для работы с БД
        session = Session()
        new_user = User(id=viber_id,
                        time_last_answer=None,
                        num_round_question=0,
                        num_answer=0,
                        current_word='',
                        num_round_correct_answer=0)

        try:
            session.add(new_user)
            session.commit()
            session.close()
        except Exception:
            # Сброс данных прошлого раунда
            user = User()
            user.reset_round(viber_id)
            session.close()
        else:
            session = Session()
            # Добавление слов для изучения новому пользователю
            words = session.query(Word.word).all()
            session.close()
            for word in words:
                learning = Learning()
                learning.add(viber_id, word[0])

    # Сброс данных раунда
    def reset_round(self, viber_id):
        session = Session()
        user = session.query(User).filter_by(id=viber_id).one()
        user.num_round_correct_answer = 0
        user.num_answer = 0
        user.num_round_question = 0
        user.current_word = ''
        session.commit()
        session.close()

    # Установка параметров раунда для текущего пользователя
    def set_round_data(self, viber_id, current_word):
        session = Session()

        # Получение текущего пользователя
        user = session.query(User).filter(User.id == viber_id).one()

        # Установка новых параметров
        user.current_word = current_word
        user.num_round_question += 1
        user.num_answer += 1
        user.time_last_answer = datetime.now()
        session.commit()
        session.close()

    # Получить количество заданных вопросов в текущем раунде
    def get_num_question(self, viber_id):
        session = Session()
        num_question = session.query(User.num_round_question).filter(User.id == viber_id).one()
        session.close()

        return num_question[0]

    # Получить количество ответов
    def get_num_answers(self, viber_id):
        session = Session()
        num_answer = session.query(User.num_answer).filter(User.id == viber_id).one()
        session.close()

        return num_answer[0]

    # Получить текущее слово раунда
    def get_current_word(self, viber_id):
        session = Session()
        word = session.query(User.current_word).filter(User.id == viber_id).one()
        session.close()

        return word[0]

    # Установить правильный ответ
    def inc_correct_answer(self, viber_id):
        session = Session()

        user = session.query(User).filter(User.id == viber_id).one()
        user.num_round_correct_answer += 1
        session.commit()
        session.close()

    def set_time_last_answer(self, viber_id):
        session = Session()

        user = session.query(User).filter(User.id==viber_id).one()
        user.time_last_answer = datetime.now()
        session.commit()
        session.close()

    # Получить количество правильных ответов в раунде
    def get_round_correct_answer(self, viber_id):
        session = Session()

        num_correct = session.query(User.num_round_correct_answer).filter(User.id==viber_id).one()
        session.close()

        return num_correct[0]

    # Получить идентификаторы пользователей для напоминания
    def get_user_id_for_remind(self):
        settings = Setting()
        remind_time = settings.get_remind_time()

        session = Session()

        # Get users list from DB
        users = session.query(User).all()

        # Check User.last_time_answer for remind
        id_list = []
        for user in users:
            delta_time = datetime.now() - user.time_last_answer
            delta_time_minute = delta_time.days * 24 * 60 + delta_time.seconds // 60

            # Save remind user.id
            if delta_time_minute > remind_time:
                id_list.append(user.id)

        session.close()
        return id_list


# Слово
class Word(Base):
    __tablename__ = 'word'

    word = Column(types.String(), primary_key=True)
    translation = Column(types.String())

    # Начальное заполнение данных таблицы word
    @staticmethod
    def init_table():
        study_elements = []
        with open('english_words.json', 'r', encoding='utf-8') as file:
            study_elements = json.load(file)

        session = Session()
        for item in study_elements:
            new_word = Word(word=item['word'], translation=item['translation'])
            session.add(new_word)
            session.commit()
        session.close()

    # Получить перевод слова
    def get_translation(self, word):
        session = Session()
        word = session.query(Word.translation).filter(Word.word == word).one()
        session.close()

        return word[0]


# Пример
class Example(Base):
    __tablename__ = 'example'

    id = Column(types.INTEGER, primary_key=True)
    word = Column(types.String(), ForeignKey('word.word', ondelete='CASCADE'))
    example = Column(types.String())

    # Начальное заполнение данных таблицы example
    @staticmethod
    def init_table():
        study_elements = []
        with open('english_words.json', 'r', encoding='utf-8') as file:
            study_elements = json.load(file)

        session = Session()
        for item in study_elements:
            for example in item['examples']:
                new_example = Example(word=item['word'], example=example)
                session.add(new_example)
                session.commit()
        session.close()

    # Получить примеры употребления слова
    def get_examples(self, word):
        session = Session()
        examples = session.query(Example.example).filter(Example.word == word).all()
        session.close()

        examples_list = []
        for example in examples:
            examples_list.append(str(example[0]))

        return examples_list


# Учеба
class Learning(Base):
    __tablename__ = 'learning'

    id = Column(types.INTEGER, primary_key=True)
    user_id = Column(types.String(), ForeignKey('user.id', ondelete='CASCADE'))
    word = Column(types.String(), ForeignKey('word.word', ondelete='CASCADE'))
    num_correct = Column(types.INTEGER, default=0)
    time_last_answer = Column(types.DateTime)

    # Добавление новой записи
    def add(self, viber_id: str, word: str):
        learning = Learning(user_id=viber_id,
                            word=word,
                            num_correct=0,
                            time_last_answer=None)
        session = Session()
        session.add(learning)
        session.commit()
        session.close()

    # Получить список невыученных слов
    def get_study_words(self, viber_id):
        setting = Setting()
        total_count = setting.get_num_correct()

        session = Session()
        words = session.query(Learning.word).filter(Learning.user_id == viber_id, Learning.num_correct < total_count).all()
        session.close()

        study_words = []
        for word in words:
            study_words.append(str(word[0]))

        return study_words

    # Зафиксировать правильный ответ в таблице
    def mark_correct_answer(self, viber_id, word):
        session = Session()

        learn_elem = session.query(Learning).filter(Learning.user_id==viber_id, Learning.word==word).one()
        learn_elem.num_correct += 1
        session.commit()
        session.close()

    # Получить количество правильных ответов на слово
    def get_num_correct_answer(self, viber_id, word):
        session = Session()

        num = session.query(Learning.num_correct).filter(Learning.user_id == viber_id, Learning.word == word).one()
        session.close()

        return num[0]


# Построить структуру таблиц в БД
def build_db_struct():
    # Построение структуры таблиц
    Base.metadata.create_all(engine)

    # Иницализция таблиц
    Word.init_table()
    Example.init_table()

    # Инициализация настроек бота
    Setting.create_item()

