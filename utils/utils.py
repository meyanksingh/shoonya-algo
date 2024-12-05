import time
from datetime import datetime
import logging

def wait_until(target_time: str, text: str = '')->None:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    while current_time < target_time:
        time_left = (datetime.strptime(target_time, "%H:%M") - datetime.strptime(current_time, "%H:%M")).total_seconds() / 60
        logging.info(f'Waiting for {time_left:.2f} minutes until {target_time} {text}')
        time.sleep(25)
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        