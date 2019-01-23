from pynput.keyboard import Key, Controller

keyboard = Controller()
def call_shortcut(val):
    if(val == 1):
        pause()
    elif(val == 2):
        move_forward()
    elif(val == 3):
        mov_backward()
    elif(val == 4):
        move_to_start()

def pause():
    keyboard.press(Key.space)
    keyboard.release(Key.space)

def move_to_start():
    keyboard.press('0')
    keyboard.release('0')

def move_forward():
    keyboard.press(Key.right)
    keyboard.release(Key.right)

def mov_backward():
    keyboard.press(Key.left)
    keyboard.release(Key.left)