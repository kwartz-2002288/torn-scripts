import pyautogui
import random
import time

# number of clicks

nMax = int(input('Enter the max number of tokens to play and press [return]: '))
nToken = nMax

# centre position of the button
# find out what you want by running pyautogui.position()
void=input('Center the mouse on the zone you want to click and press [return] ')

(x0, y0) = pyautogui.position()
# first click activates the page
pyautogui.click(x=x0, y=y0)
time.sleep(0.2)

dn = 5 # max clicks without moving
deltat = 8.1 # minimal time interval
dt = 1.6 # temporal jitter
dx , dy = 7 , 4 # spatial jitters

while nToken > 0:

    p = int(random.uniform(1,dn)) # clicks number without moving
    moveToX = x0 + random.uniform(-dx, dx)
    moveToY = y0 + random.uniform(-dy, dy)
    
    for i in range(p):
        if nToken > 0:
            pyautogui.click(x=moveToX, y=moveToY)
            t = random.uniform(deltat,deltat+dt)
            if nToken > 1:
                print("Tokens remaining {:03d}/{:03d} [waiting {:.2f}s...]".format(nToken-1, nMax, t))
                time.sleep(t)
            else:
                print("Tokens remaining {:03d}/{:03d}".format(nToken-1, nMax))
                print("Clicks terminated")
        nToken -= 1
