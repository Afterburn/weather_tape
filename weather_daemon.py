
import time
import datetime
import multiprocessing

import weather_lib


lib = weather_lib.Weather()
lib.read_weather()


next_check = datetime.datetime.now() + datetime.timedelta(minutes=lib.read_interval)

while True:

    lib.show_conditions()
    time.sleep(1)

     
    now = datetime.datetime.now()
    if now > next_check:
        print('checking')
        lib.read_weather()
        next_check = now + datetime.timedelta(minutes=lib.read_interval)



