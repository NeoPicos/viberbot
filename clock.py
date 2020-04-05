from apscheduler.schedulers.blocking import BlockingScheduler
from reminder import check_user_time
import requests
from settings import URL

sched_remind = BlockingScheduler()
sched_request = BlockingSheduler()

# Напоминание
@sched_remind.scheduled_job('interval', minutes=1)
def do_reminder():
    check_user_time()

    
# Фиктивный запрос
@sched_request.scheduled_job('interval', minutes=1)
def do_request_to_server():
    requests.get(URL)
    
    
sched_remind.start()
sched_request.start()
