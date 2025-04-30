// This code was used on the PCB for SPARROW, this was coded in ArduinoIDE

#include <Wire.h>
#include <HardwareSerial.h>
#include <TinyGPS++.h>

#define NUM_LEVELS 11
HardwareSerial Serial1(USART1);
HardwareSerial SerialGPS(USART3);  // PB10 and PB11 (TX and RX)
TinyGPSPlus gps;
unsigned int iteration = 0;

void setup() {
  // put your setup code here, to run once
  Wire.begin();
  Serial1.begin(115200);  // For Jetson UART forwarding
  SerialGPS.begin(9600);
  while (!Serial1);
  while (!SerialGPS);

  pinMode(PA4, OUTPUT);  // Set PA4 as output
  pinMode(PA5, OUTPUT);  // Set PA5 as output

  // Set thresholds
  writeRegister(0x06, 0x0f, 0xe7);
  writeRegister(0x07, 0x0f, 0x00);
  writeRegister(0x08, 0x00, 0x1a);
  writeRegister(0x09, 0x0f, 0x00);
  writeRegister(0x0a, 0x0f, 0xff);
  writeRegister(0x0b, 0x0f, 0x00);
  writeRegister(0x0c, 0x00, 0xff);
  // writeRegister(0x0d, , );
  writeRegister(0x0e, 0xff, 0xff);
  //writeRegister(0x0f, , );
  writeRegister(0x10, 0xff, 0xff);
  writeRegister(0x11, 0x00, 0xff);
  writeRegister(0x12, 0x00, 0xff);

  // enable bits
  //writeRegister(0x00, , );
  writeRegister(0x01, 0x00, 0x7f);
  //writeRegister(0x03, , );
  writeRegister(0x04, 0x1a, 0xbf);

  writeRegister(0x23, 0x20, 0x00);
  writeRegister(0x24, 0x10, 0x00);

  writeRegister(0x02, 0x0f, 0xe3);

  delay(1000);

  Serial1.println("Finished Writing to Battery Cells");
}

void loop() {

  // blink LEDs
  digitalWrite(PA4, HIGH);  // LED ON
  digitalWrite(PA5, HIGH);  // LED ON
  delay(500);               // wait 500ms
  digitalWrite(PA4, LOW);   // LED OFF
  digitalWrite(PA5, LOW);   // LED OFF
  delay(500);               // wait 500ms
  if (iteration % 5 == 0) {
    readBattery();
  }

  if (SerialGPS.available()) {
    String nmeaSentence = SerialGPS.readStringUntil('\n');  // Read full NMEA sentence
    if (nmeaSentence.length() > 0) {                        // Check if something is received
      Serial1.println(nmeaSentence);
    } else {
      Serial1.println("Waiting for GPS data...");
    }

    for (char c : nmeaSentence) {
      gps.encode(c);
    }

    if (gps.location.isUpdated()) {
      Serial1.print("Latitude ");
      Serial1.print(gps.location.lat(), 6);
      Serial1.print(" Longitude ");
      Serial1.println(gps.location.lng(), 6);
    }
  }

  iteration += 1;
  iteration %= 10;
}

void writeRegister(uint8_t reg, uint8_t msb, uint8_t lsb) {
  Wire.beginTransmission(0x49);
  Wire.write(reg);
  Wire.write(msb);
  Wire.write(lsb);
  Wire.endTransmission();
}

const int voltage_levels[NUM_LEVELS] = {
  4000, 3900, 3800, 3750, 3650, 3580, 3500, 3435, 3350, 3250, 3000
};

const int battery_percentages[NUM_LEVELS] = {
  100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0
};

int voltage_to_percent(int mv) {
  for (int i = 0; i < NUM_LEVELS; i++) {
    if (mv >= voltage_levels[i]) {
      return battery_percentages[i];
    }
  }
  return 0;  // Default to 0% if below the lowest threshold
}

int avg_battery_percent(int battery_mv_array[]) {
  int total = 0;
  int percent = 0;
  for (int i = 0; i < 5; i++) {
    percent = voltage_to_percent(battery_mv_array[i]);
    total += percent;
  }
  return total / 5;
}

void readBattery() {
  int battery_mv[5];
  int battery_shift = 600;  // mV value which the read voltage levels are shifted up by
    for (int i = 0; i < 5; i++) {
    Wire.beginTransmission(0x49);
    Wire.write(0x21 + i);                      // Write to the register address
    byte error = Wire.endTransmission(false);  // Send stop condition
    Wire.requestFrom(0x49, (uint8_t)2);
    if (Wire.available()) {
      byte data1 = Wire.read();
      byte data2 = Wire.read();
      uint16_t data = ((data1 << 8) | data2) & 0x0fff;
      battery_mv[i] = data + battery_shift;
    } else {
      Serial1.println("Error: Incomplete data received\n");
      battery_mv[i] = 0;
    }
  }
  int battery_array_percent = avg_battery_percent(battery_mv);
  char buffer[50];
  sprintf(buffer, "Battery %d", battery_array_percent);
  Serial1.println(buffer);
}
