from apscheduler.schedulers.blocking import BlockingScheduler
from reminder import check_user_time
import requests
from settings import URL

sched = BlockingScheduler()

# Напоминание
@sched.scheduled_job('interval', minutes=1)
def do_reminder():
    check_user_time()
    request.get(URL)

    
sched.start()
