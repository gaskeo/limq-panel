import pyautogui as pg
import time
from Xlib import display

# coordinates
# 280 250
# 210 265
# 270 315
debug = 0
while debug:
    c = display.Display().screen().root.query_pointer()._data
    x = c["root_x"]
    y = c["root_y"]

    print(x, y)
    time.sleep(0.1)
time.sleep(6)
pg.moveTo(800, 600)
time.sleep(1)
pg.moveTo(280, 250, 2.2)
time.sleep(1)
pg.click()
time.sleep(0.5)
pg.moveTo(210, 265, 1)
time.sleep(0.5)
pg.click()
pg.write('New channel', 0.3)
pg.moveTo(270, 315, 1)
pg.click()



