import pyautogui
import threading
import time
import sys
import serial

# 시리얼 포트 설정
ser = serial.Serial('COM8', 115200)  # COM8 포트는 실제 ESP32가 연결된 포트로 변경 필요

# 스위치 상태를 추적하기 위한 플래그
switch_pressed = True

# 좌표 알아보는 함수
def print_mouse_position():
    try:
        while True:
            x, y = pyautogui.position()  # 현재 마우스 좌표를 가져옴
            print(f"Current mouse position: ({x}, {y})", end="\r\n")
            time.sleep(0.1)  # 0.1초마다 좌표를 업데이트
    except KeyboardInterrupt:
        print("\nPressing Ctrl+C...")
        press_ctrl_c()
        time.sleep(1)  # 1초 대기
        print("Ctrl+C pressed.")

# Ctrl+C를 자동으로 누르는 함수
def press_ctrl_c():
    pyautogui.hotkey('ctrl', 'c')  # Ctrl+C를 누름

# 스위치가 눌렸을 때 실행될 함수
def switch_pressed_action():
    global switch_pressed
    switch_pressed = False
    print("Switch pressed. Moving mouse to (1024, 445)...")
    pyautogui.moveTo(960, 540)
    switch_pressed = True  # 화면 중앙 이동 후 플래그를 초기화

# 메인 프로그램
if __name__ == "__main__":
    # 시작 시 마우스 좌표를 출력하는 스레드 시작
    mouse_position_thread = threading.Thread(target=print_mouse_position)
    mouse_position_thread.daemon = True  # 데몬 스레드로 설정
    mouse_position_thread.start()

    # 메인 스레드가 종료될 때까지 대기
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print("input => " + line + "\n")
                if "RUN_PYTHON_SCRIPT" in line:
                # if line == "RUN_PYTHON_SCRIPT\n":
                    switch_pressed_action()
            time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit()
