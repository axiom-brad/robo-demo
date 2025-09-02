// TemuBot

#include <Stepper.h>

const int steps_per_rev = 2048;  // Steps per revoution for 28BYJ-48 stepper motor
const int stepper_rpm = 10;      // Typical speed is 10-15 RPM under normal 5V conditions

// Initialize the stepper objects with pin numbers
Stepper motor1(steps_per_rev, 5, 3, 4, 2);
Stepper motor2(steps_per_rev, 9, 7, 8, 6);
Stepper motor3(steps_per_rev, 13, 11, 12, 10);

// Store the current angle of each motor
float angle1 = 0.0;
float angle2 = 0.0;
float angle3 = 0.0;

String command;

void setup() {
  // Initialize the stepper motors
  motor1.setSpeed(stepper_rpm);
  motor2.setSpeed(stepper_rpm);
  motor3.setSpeed(stepper_rpm);

  // Initialize the serial port:
  Serial.begin(9600);
  Serial.setTimeout(10);  // ms
  Serial.println("TemuBot Ready");
}

void move(float relative_move, int id, Stepper *motor, float *angle) {
  *angle += relative_move;
  motor->step(relative_move / 360.0 * steps_per_rev);
  Serial.print("motor ");
  Serial.print(id);
  Serial.print(" moved to angle ");
  Serial.println(*angle);

}

void loop() {
  if (Serial.available()) {
    command = Serial.readString();
    command.trim();

    if (command.equals("ping")) {
      Serial.println("OK");
    } else if (command.equals("get angle 1")) {
      Serial.print("motor angle 1 is ");
      Serial.println(angle1);
    } else if (command.equals("get angle 2")) {
      Serial.print("motor angle 2 is ");
      Serial.println(angle2);
    } else if (command.equals("get angle 3")) {
      Serial.print("motor angle 3 is ");
      Serial.println(angle3);
    } else if (command.equals("reset angle 1")) {
      angle1 = 0.0;
      Serial.print("motor angle 1 is ");
      Serial.println(angle1);
    } else if (command.equals("reset angle 2")) {
      angle2 = 0.0;
      Serial.print("motor angle 2 is ");
      Serial.println(angle2);
    } else if (command.equals("reset angle 3")) {
      angle3 = 0.0;
      Serial.print("motor angle 3 is ");
      Serial.println(angle3);
    } else if (command.startsWith("move motor 1 relative ")) {
      // Relative move in degrees, e.g. move motor 1 relative 90.0
      float relative_move = command.substring(22).toFloat();
      move(relative_move, 1, &motor1, &angle1);
    } else if (command.startsWith("move motor 2 relative ")) {
      // Relative move in degrees, e.g. move motor 2 relative 90.0
      float relative_move = command.substring(22).toFloat();
      move(relative_move, 2, &motor2, &angle2);
    } else if (command.startsWith("move motor 3 relative ")) {
      // Relative move in degrees, e.g. move motor 3 relative 90.0
      float relative_move = command.substring(22).toFloat();
      move(relative_move, 3, &motor3, &angle3);
    } else if (command.startsWith("move motor 1 absolute ")) {
      // Absolute move in degrees, e.g. move motor 1 absolute 90.0
      float absolute_move = command.substring(22).toFloat();
      float relative_move = absolute_move - angle1;
      move(relative_move, 1, &motor1, &angle1);
    } else if (command.startsWith("move motor 2 absolute ")) {
      // Absolute move in degrees, e.g. move motor 2 absolute 90.0
      float absolute_move = command.substring(22).toFloat();
      float relative_move = absolute_move - angle2;
      move(relative_move, 2, &motor2, &angle2);
    } else if (command.startsWith("move motor 3 absolute ")) {
      // Absolute move in degrees, e.g. move motor 3 absolute 90.0
      float absolute_move = command.substring(22).toFloat();
      float relative_move = absolute_move - angle3;
      move(relative_move, 3, &motor3, &angle3);
    } else {
      Serial.println("ERROR");
    }
  }

  delay(500);  // ms
}
