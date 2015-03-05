import serial

class BlinkyTape(object):
    def __init__(self, port, led_count=60):
        self.port = port
        self.led_count = led_count
        self.position  = 0
        self.buff      = None
        self.serial    = serial.Serial(port, 115200)
        self.control   = chr(0) + chr(0) + chr(255)

        self.init_buffer() 

    def validate_colors(self, r, g, b):
        ''' Makes sure the colors are within range'''
        if r >= 255:
            r = 254

        if r < 0:
            r = 0

        if g >= 255:
            g = 254

        if g < 0:
            g = 0

        if b >= 255:
            b = 254

        if b < 0:
            b = 0
        
        return chr(r) + chr(g) + chr(b)


    def init_buffer(self):
        '''Create the internal buffer'''
        new_buff = []
        for x in range(self.led_count):
            new_buff.append(self.validate_colors(0,0,0))
        
        self.buff = new_buff


    def write_buffer(self, buff=False):
        '''Write either the current buffer, or one given to us.'''
        if buff:
            to_write = "".join(str(x) for x in buff)

        else:
            to_write = "".join(str(x) for x in self.buff)

        self.serial.write(to_write + self.control)
        self.serial.flush()
        self.serial.flushInput()


    def set_pixel(self, position, r, g, b, warn=False):
        if position >= 0 and position < self.led_count:
            self.buff[position] = self.validate_colors(r,g,b)

        elif warn:
            raise RuntimeError("Attempting to set pixel outside range!")


    def get_buffer(self):
        return self.buff


    def set_buffer(self, buff):
        self.buff = buff


    def display_color(self, r, g, b, use_buff=False):
        '''Displays the color, using either the internal buffer or given buffer'''
        if use_buff:
            for i in range(self.led_count):
                self.buff[i] = self.validate_colors(r,g,b)

            self.write_buffer()

        else:
            buff = [0] * self.led_count 
            
            for i in range(self.led_count):
                buff[i] = self.validate_colors(r,g,b)
           
            self.write_buffer(buff=buff)


    def reset_to_bootloader(self):
        '''Initiates a reset on BlinkyTape.'''
        self.serial.setBaudrate(1200)
        self.close()


    def close(self):
        self.serial.close()
