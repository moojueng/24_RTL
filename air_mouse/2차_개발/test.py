from pynput.mouse import Controller
import time

mouse = Controller()

def move_mouse(x, y):
    current_pos = mouse.position
    new_pos = (current_pos[0] + x, current_pos[1] + y)
    mouse.position = new_pos

def main():
    while True:
        move_mouse(10, 0)  # x 방향으로 10픽셀 이동
        time.sleep(0.1)
        move_mouse(-10, 0)  # x 방향으로 -10픽셀 이동
        time.sleep(0.1)

if __name__ == "__main__":
    main()

