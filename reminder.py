from models import User
from app import remind


# Проверить данные о времени
def check_user_time():
    # Получить user id для напомининя
    user = User()
    id_list = user.get_user_id_for_remind()
    
    if len(id_list) == 0:
        return
    
    # Отправить пользователям сообщение-напоминание
    for id in id_list:
        remind(str(id))
    
    id_list.clear()



