import asyncio
from bleak import BleakClient
import pyautogui

# BLE 장치의 MAC 주소
device_mac = 'A0:DD:6C:0F:69:32'

# 특정 characteristic의 UUID
characteristic_uuid = "00002a19-0000-1000-8000-00805f9b34fb"

# 알림을 처리하는 콜백 함수
def notification_handler(sender, data):
    value = data.decode('utf-8')
    print(f"value => {value}")
    if value == "CLICK_EVENT":
        # CLICK_EVENT를 받으면 중앙으로 마우스 이동
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        pyautogui.moveTo(center_x, center_y, duration=1.0)
        print("Mouse moved to center")

async def run():
    async with BleakClient(device_mac) as client:
        # BLE 알림 시작
        await client.start_notify(characteristic_uuid, notification_handler)
        print("Notification started. Waiting for events...")

        # 알림을 기다리는 동안 무한 루프 유지
        while True:
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
