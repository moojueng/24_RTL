#include <BleMouse.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID "0000180f-0000-1000-8000-00805f9b34fb"
#define CHARACTERISTIC_UUID "00002a19-0000-1000-8000-00805f9b34fb"

BLECharacteristic *pCharacteristic;
bool deviceConnected = false;

const int switchPin = 14; // D14 / GPIO14
bool switchState = false;
bool lastSwitchState = false;

class MyServerCallbacks : public BLEServerCallbacks {
public:
void onConnect(BLEServer* pServer) {
deviceConnected = true;
}


void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
}
};

void setup() {
Serial.begin(115200);


pinMode(switchPin, INPUT_PULLUP);  // D14를 내부 풀업 저항 사용하는 입력으로 설정

BLEDevice::init("ESP32Mouse");
BLEServer *pServer = BLEDevice::createServer();
pServer->setCallbacks(new MyServerCallbacks());

BLEService *pService = pServer->createService(BLEUUID(SERVICE_UUID));
pCharacteristic = pService->createCharacteristic(
                      BLEUUID(CHARACTERISTIC_UUID),
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                  );

pCharacteristic->addDescriptor(new BLE2902());

pService->start();

BLEAdvertising *pAdvertising = pServer->getAdvertising();
pAdvertising->start();

Serial.print("Bluetooth MAC Address: ");
Serial.println(BLEDevice::getAddress().toString().c_str());
}

void loop() {
// 스위치 상태 읽기
switchState = digitalRead(switchPin);


// 스위치가 눌린 경우 처리
if (switchState == LOW && lastSwitchState == HIGH) {
    // 특성 값 업데이트
    pCharacteristic->setValue("CLICK_EVENT");

    // 연결된 장치에 알림 전송
    if (deviceConnected) {
        pCharacteristic->notify();
    }
}

// 마지막 스위치 상태 업데이트
lastSwitchState = switchState;

delay(20);  // 지연 시간 추가 (디바운싱 효과)
}