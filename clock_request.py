
from apscheduler.schedulers.blocking import BlockingScheduler
from reminder import check_user_time
import requests
from settings import URL

sched = BlockingScheduler()

# Фиктивный запрос
@sched.scheduled_job('interval', minutes=1)
def do_request_to_server():
    requests.get(URL)


sched.start()
