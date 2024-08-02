#include <Wire.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <BleMouse.h>

uint8_t data[6];
int16_t gyroX, gyroY, gyroZ;

int Sensitivity = 600;
int delayi = 20;

BleMouse bleMouse;

uint32_t timer;
uint8_t i2cData[14];

const uint8_t IMUAddress = 0x68;
const uint16_t I2C_TIMEOUT = 1000;

const int relayPin = 14; // 릴레이 스위치가 연결된 핀 번호 (D14 핀)
const int ledPin = 2;    // ESP32 내장 LED 핀 번호

const float xThreshold = 20.0; // 진동 감지 임계값 (-20 ~ +20)
const float zThreshold = 20.0; // Z축 진동 감지 임계값

bool calibrating = false;
bool bleConnected = false;

uint8_t i2cWrite(uint8_t registerAddress, uint8_t* data, uint8_t length, bool sendStop) {
  Wire.beginTransmission(IMUAddress);
  Wire.write(registerAddress);
  Wire.write(data, length);
  return Wire.endTransmission(sendStop); // 성공 시 0 반환
}

uint8_t i2cWrite2(uint8_t registerAddress, uint8_t data, bool sendStop) {
  return i2cWrite(registerAddress, &data, 1, sendStop); // 성공 시 0 반환
}

uint8_t i2cRead(uint8_t registerAddress, uint8_t* data, uint8_t nbytes) {
  uint32_t timeOutTimer;
  Wire.beginTransmission(IMUAddress);
  Wire.write(registerAddress);
  if (Wire.endTransmission(false))
    return 1;
  Wire.requestFrom(IMUAddress, nbytes, (uint8_t)true);
  for (uint8_t i = 0; i < nbytes; i++) {
    if (Wire.available())
      data[i] = Wire.read();
    else {
      timeOutTimer = micros();
      while (((micros() - timeOutTimer) < I2C_TIMEOUT) && !Wire.available());
      if (Wire.available())
        data[i] = Wire.read();
      else
        return 2;
    }
  }
  return 0;
}

void setup() {
  Wire.begin();
  pinMode(relayPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);

  i2cData[0] = 7;
  i2cData[1] = 0x00;
  i2cData[3] = 0x00;

  while (i2cWrite(0x19, i2cData, 4, false));
  while (i2cWrite2(0x6B, 0x01, true));
  while (i2cRead(0x75, i2cData, 1));
  delay(100);
  while (i2cRead(0x3B, i2cData, 6));

  timer = micros();
  Serial.begin(115200);
  bleMouse.begin();
  delay(100);
}

void loop() {
  static bool lastRelayState = HIGH;

  bool relayState = digitalRead(relayPin);
  if (relayState == LOW && lastRelayState == HIGH) {
    // 스위치가 눌린 경우 내부 LED 켜기
    digitalWrite(ledPin, HIGH);

    // 파이썬 스크립트 실행
    // Serial.println("RUN_PYTHON_SCRIPT");

    // // 화면 중앙 좌표 계산
    // int centerX = screenWidth / 2;
    // int centerY = screenHeight / 2;

    // // 마우스 커서를 화면 중앙으로 이동
    // bleMouse.move(centerX, centerY);

    // Serial.println("Relay switch clicked. Mouse cursor moved to center.");

    // 잠시 기다렸다가 내부 LED 끄기
    delay(2000);
    digitalWrite(ledPin, LOW);
  }
  lastRelayState = relayState;

  // BLE 연결 상태 확인
  if (!bleMouse.isConnected()) {
    bleConnected = false;
    Serial.println("BLE connection lost. Reconnecting...");
    bleMouse.begin(); // BLE 재시도
  } else {
    bleConnected = true;
  }

  if (bleConnected) {
    while (i2cRead(0x3B, i2cData, 14));

    gyroX = ((i2cData[8] << 8) | i2cData[9]);
    gyroY = ((i2cData[10] << 8) | i2cData[11]);
    gyroZ = ((i2cData[12] << 8) | i2cData[13]);

    gyroX = gyroX / Sensitivity * (-1); // x축의 좌우 방향을 반대로 변경
    gyroY = gyroY / Sensitivity; // y축의 상하 방향은 그대로 유지
    gyroZ = gyroZ / Sensitivity; // z축의 가속도를 정규화

    // X축 진동 감지
    if (gyroX < -xThreshold || gyroX > xThreshold) {
      // 진동 감지 시 마우스 클릭 이벤트 발생
      bleMouse.click(MOUSE_LEFT);
    }

    // Z축 진동 감지
    if (gyroZ < -zThreshold || gyroZ > zThreshold) {
      // Z축 진동 감지 시 마우스 클릭 이벤트 발생
      bleMouse.click(MOUSE_LEFT);
    }

    // Serial.print(gyroX);
    // Serial.print("   ");
    // Serial.print(gyroY);
    // Serial.print("   ");
    // Serial.print(gyroZ);
    // Serial.print("\r\n");
    bleMouse.move(gyroY, gyroX); // X축은 좌우, Y축은 상하로 설정하여 마우스 이동
    delay(delayi);
  }
}
