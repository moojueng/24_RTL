import pygame
import smbus2
import time

# MPU-6050 I2C 주소 및 레지스터 정의
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

sensitivity = 1100

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.mouse.set_visible(False)

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

def read_word_2c(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value -= 0x10000
    return value

def get_sensor_data():
    accel_x = read_word_2c(ACCEL_XOUT_H)
    accel_y = read_word_2c(ACCEL_YOUT_H)
    accel_z = read_word_2c(ACCEL_ZOUT_H)
    gyro_x = read_word_2c(GYRO_XOUT_H)
    gyro_y = read_word_2c(GYRO_YOUT_H)
    gyro_z = read_word_2c(GYRO_ZOUT_H)
    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

def main():
    running = True
    x, y = pygame.mouse.get_pos()  # 현재 마우스 위치 가져오기

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 센서 데이터 읽기
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = get_sensor_data()

        # 데이터 출력
        print(f"Accel X: {accel_x}, Accel Y: {accel_y}, Accel Z: {accel_z}")
        print(f"Gyro X: {gyro_x}, Gyro Y: {gyro_y}, Gyro Z: {gyro_z}")

        # 민감도에 따른 조정
        gyro_y /= sensitivity
        gyro_z /= sensitivity

        # 마우스 이동 거리 계산
        mouse_x = int(gyro_z)
        mouse_y = int(-gyro_y)

        # 현재 마우스 위치 업데이트
        x += mouse_x
        y += mouse_y

        # 화면 경계를 벗어나지 않도록 조정
        x = max(0, min(x, screen.get_width() - 1))
        y = max(0, min(y, screen.get_height() - 1))

        # 마우스 위치 설정
        pygame.mouse.set_pos((x, y))

        # 일정 시간 대기
        time.sleep(0.02)

    pygame.quit()

if __name__ == "__main__":
    main()

