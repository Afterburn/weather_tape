
import time
import multiprocessing

import weather_lib


lib = weather_lib.Weather()

while True:
    try:
        lib.read_weather()
    except Exception as e:
        print(e)
        lib.demo_temp_colors()

    #lib.set_background(dim=True)
    lib.show_conditions()
    time.sleep(1)



