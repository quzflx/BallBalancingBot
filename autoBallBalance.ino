#include <ESP32Servo.h>
#include <math.h>

// Servo pins
const int servoPin1 = 12;
const int servoPin2 = 14;
const int servoPin3 = 27;

Servo servo1, servo2, servo3;

// PID constants (tune this right here baby)
float Kp = 0.85;
float Ki = 0.05;
float Kd = 8.0;

// PID variables
float error_x = 0, error_y = 0;
float prev_error_x = 0, prev_error_y = 0;
float integral_x = 0, integral_y = 0;

unsigned long lastTime = 0;

// Servo settings
int neutral = 80;
int minAngle = 65;
int maxAngle = 105;

void setup() {
  Serial.begin(115200);

  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);

  servo1.write(neutral);
  servo2.write(neutral);
  servo3.write(neutral);

  lastTime = millis();
}

void loop() {

  // --- DROP OLD DATA ---
  while (Serial.available() > 64) {
    Serial.read();
  }

  // --- READ THE INCOMING DATA ---
  String input = "";

  while (Serial.available()) {
    input = Serial.readStringUntil('\n');
  }

  // --- PARSE ---
  if (input.length() > 0) {
    int spaceIndex = input.indexOf(' ');

    if (spaceIndex > 0) {
      error_x = input.substring(0, spaceIndex).toFloat();
      error_y = input.substring(spaceIndex + 1).toFloat();
    }
    /*
    Serial.print("Parsed: ");
    Serial.print(error_x);
    Serial.print(" ");
    Serial.println(error_y);
    */
  }

  // --- TIME ---
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  lastTime = now;

  if (dt <= 0) return;

  // --- DEADZONE ---
  if (abs(error_x) < 0.03) error_x = 0;
  if (abs(error_y) < 0.03) error_y = 0;

  // --- PID X ---
  integral_x += error_x * dt;
  integral_x = constrain(integral_x, -5, 5);

  float derivative_x = (error_x - prev_error_x) / dt;
  float pitch = Kp * error_x + Ki * integral_x + Kd * derivative_x;

  prev_error_x = error_x;

  // --- PID Y ---
  integral_y += error_y * dt;
  integral_y = constrain(integral_y, -5, 5);

  float derivative_y = (error_y - prev_error_y) / dt;
  float roll = Kp * error_y + Ki * integral_y + Kd * derivative_y;

  prev_error_y = error_y;

  // --- INVERSE KINEMATICS ---
  float pos1 = -pitch;
  float pos2 = (pitch - (roll * sqrt(3))) / 2;
  float pos3 = (pitch + (roll * sqrt(3))) / 2;

  // --- SERVO OUTPUT ---
  int angle1 = constrain(neutral + pos1, minAngle, maxAngle);
  int angle2 = constrain(neutral + pos2, minAngle, maxAngle);
  int angle3 = constrain(neutral + pos3, minAngle, maxAngle);

  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  delay(2);
}
