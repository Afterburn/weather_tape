import requests 
import json
import time
import random
import copy
import mmap

import blinkytape


class Weather():
    def __init__(self,  dev_port='/dev/blinkytape'):
        self.api_url = 'http://api.wunderground.com/api/%s/conditions/q/%s/%s.json'
        self.strip   = blinkytape.BlinkyTape(dev_port)
        self.settings = None
        self.temp = 30
        self.is_precip = False
        self.is_thunderstorm = False
        self.color = (0,0,0)
        self.color_map = {
                -20: (255, 0, 255),
                -10: (158, 0, 255),
                 0: (0, 0, 255),
                 10: (0, 126, 255),
                 20: (0, 204, 255),
                 30: (5, 247, 247),
                 40: (127, 255, 0),
                 50: (247, 247, 5),
                 60: (255, 204, 0),
                 70: (255, 153, 0),
                 80: (255, 79, 0),
                 90: (204, 0, 0),
                 100: (169, 3, 3),
                 110: (186, 50, 50)}

        #self.rain_color = (30,50,60)
        self.rain_color = (10,30,40)
        self.snow_color = (255,255,255)
        self.precip_buffer = []

        with open('/etc/weather_tape/config.json') as cfg:
            self.settings = json.load(cfg)['settings']

        
        self.read_interval = self.settings['read-interval']

    def demo_temp_colors(self):
        for key in sorted(self.color_map.keys()):
            color = self.color_map[key]
            print('demo: displaying %s degress' % (key))
            self.strip.display_color(color[0], color[1], color[2])
            time.sleep(2)

    def random_pixel(self):
        return random.randrange(0,60)


    def lightning(self):
        buff = self.strip.get_buffer()

        c = random.randrange(0,4)

        if c != 0:
            return 

        for x in range(2):
            if random.choice([True,False]):
                self.strip.display_color(255,255,255)
                time.sleep(.25)
                self.strip.write_buffer(buff)
        
  
    def show_conditions(self):
        
        if self.is_precip:
            self.precip()

        elif len(self.precip_buffer):
            self.remove_precip()

        if self.is_thunderstorm:
            self.lightning()


    def remove_precip(self):
        if len(self.precip_buffer):
            rp_off = random.choice(self.precip_buffer)
            self.strip.set_pixel(rp_off, self.color[0], self.color[1], self.color[2])
            self.precip_buffer.remove(rp_off)
            self.strip.write_buffer()


    def add_precip(self, sleep_range=5, amount=5):
        rp = self.random_pixel()

        if rp not in self.precip_buffer:
            self.precip_buffer.append(rp)

        #self.strip.set_pixel(self.random_pixel(), self.rain_color[0], self.rain_color[1], self.rain_color[2])

        for position in self.precip_buffer:
            if self.temp <= 32:
                self.strip.set_pixel(position, self.snow_color[0], self.snow_color[1], self.snow_color[2])
                
            else:
                self.strip.set_pixel(position, self.rain_color[0], self.rain_color[1], self.rain_color[2])
            
        self.strip.write_buffer()

        # Looks more realistic if you wait a second, then turn turn a pixel back to normal. 
        
        if len(self.precip_buffer) >= amount:
            self.remove_precip()
       
        time.sleep(random.randrange(0, sleep_range))


    def temp_to_color(self, temp):
        for key in sorted(self.color_map.keys()):
            if temp < key:
                return self.color_map[key]

        return (0,0,0)
    
    
    def set_background(self, dim=False):
        color = self.temp_to_color(self.temp)

        if color == self.color:
            # Don't need to keep setting the same color
            return 

        print('Setting color to: %s - %s' % (self.temp, color))

        if self.settings['dim'] == True and self.is_precip == True:
            print('dimming')
            self.color = (color[0]/5, color[1]/5, color[2]/5)

        else:
            self.color = color

        self.strip.display_color(self.color[0], self.color[1], self.color[2], use_buff=True)
        
    def read_weather(self):
        try:
            page = requests.get(self.api_url % (self.settings['api_key'], self.settings['state'], self.settings['zipcode']))
            data = json.loads(page.text)

        except:
            self.strip.display_color(255, 0, 0)
            time.sleep(1)
            self.strip.display_color(255/3, 0, 0)
            time.sleep(1)
            return


        co              = data['current_observation']
        temp            = int(co['temp_f'])
        t_storm    = " ".join(co['weather'].split()).lower()

        self.is_precip = bool(float(co['precip_1hr_in']))
        self.is_thunderstorm = bool('thunderstorm' in t_storm)
  
        if temp != self.temp:
            self.temp = temp
            self.set_background()

