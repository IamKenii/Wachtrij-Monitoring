LCD_PRINT = 0x01
LCD_CLEAR = 0x02
LCD_SET_CURSOR = 0x03


class LCD():

    def __init__(self, arduino):
        self.arduino = arduino

    def set_cursor(self, x, y):
        self.arduino.send_sysex(LCD_SET_CURSOR, [x, y])

    def clear(self):
        self.arduino.send_sysex(LCD_CLEAR, [])

    def print(self, message):
        self.arduino.send_sysex(LCD_PRINT, [ord(char) for char in message])
