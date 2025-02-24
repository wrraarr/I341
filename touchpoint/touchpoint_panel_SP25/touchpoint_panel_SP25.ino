#include <Wire.h>
#include <Adafruit_MPR121.h>

Adafruit_MPR121 capSensor = Adafruit_MPR121();

void setup() {
  Serial.begin(9600);
  pinMode(2, INPUT_PULLUP);
  
  Wire.begin();
  
  if (!capSensor.begin(0x5A)) {
    Serial.println("MPR121 not found!");
    while (1);
  }
}

void loop() {
  // Read analog sensors
  int sensorA2 = analogRead(A2);
  int sensorA1 = analogRead(A1);
  int sensorA0 = analogRead(A0);
  int enter_button = digitalRead(2);

  // Read capacitive touch sensor
  uint16_t touched = capSensor.touched();
  int shapeID = -1; // Default (no key touched)
  
  for (int i = 0; i < 12; i++) {
    if (touched & (1 << i)) {
      shapeID = i;  // Store first detected key
      break;
    }
  }

  // Send data as CSV
  Serial.print(sensorA2);
  Serial.print(",");
  Serial.print(sensorA1);
  Serial.print(",");
  Serial.print(sensorA0);
  Serial.print(",");
  Serial.print(shapeID);
  Serial.print(",");
  Serial.println(enter_button);
  
  delay(40);
}
