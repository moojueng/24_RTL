import asyncio
from bleak import BleakClient

# BLE 장치의 MAC 주소
device_mac = 'A0:DD:6C:0F:69:32'

# 특정 characteristic의 UUID
characteristic_uuid = "00002a19-0000-1000-8000-00805f9b34fb"

async def discover_services_and_characteristics(address, uuid):
    async with BleakClient(address) as client:
        try:
            # BLE 서비스 검색
            services = await client.get_services()

            # BLE 서비스와 그에 속한 특성 확인
            for service in services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"Characteristic: {char.uuid} - Handle: {char.handle}")
                    if char.uuid == uuid:
                        return char.handle

            # 특성을 찾지 못한 경우
            print(f"Characteristic with UUID {uuid} not found.")
            return None

        except Exception as e:
            print(f"Error during BLE operation: {e}")
            return None

async def run():
    # 특성 핸들 값 찾기
    characteristic_handle = await discover_services_and_characteristics(device_mac, characteristic_uuid)

    if characteristic_handle is None:
        print("Failed to find characteristic handle. Exiting.")
        return

    # 알림 콜백 함수
    def notification_handler(sender, data):
        value = data.decode('utf-8')
        print(f"value => {value}")
        if value == "CLICK_EVENT":
            # CLICK_EVENT를 받으면 중앙으로 마우스 이동
            print("Mouse moved to center")

    # BleakClient를 사용하여 BLE 알림 시작
    async with BleakClient(device_mac) as client:
        try:
            await client.start_notify(characteristic_handle, notification_handler)
            print("Notification started. Waiting for events...")

            # 알림을 기다리는 동안 무한 루프 유지
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error during notification: {e}")

# 비동기 루프 실행
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
