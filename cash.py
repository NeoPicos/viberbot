from typing import List
from models import Learning


class WordsCash(object):
    def __init__(self, viber_id: str):
        self.viber_id = viber_id
        self.words_list = []

    # Выгрузка слов для изучения
    def cash_learning_words(self):
        learn = Learning()
        self.words_list =  learn.get_study_words(self.viber_id)


class MessageTokenCash(object):
    def __init__(self, viber_id: str):
        self.viber_id = viber_id
        self.last_token = ""
