// stepper_stage_control.ino
//
// Code to control the stepper motor in a Fuyu motorized linear stage via serial commands

#include <AccelStepper.h>
#include <Adafruit_MotorShield.h>

// global variables
bool keepMoving = false;
const byte instructionLength = 16;
char instruction[instructionLength];

Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *myAFStepper = AFMS.getStepper(200, 1);

// Use AccelStepper library with functions
void forwardstep1() {
  myAFStepper->onestep(FORWARD, DOUBLE);
}

void backwardstep1() {
  myAFStepper->onestep(BACKWARD, DOUBLE);
}

AccelStepper Astepper1(forwardstep1, backwardstep1);  // use functions to step


void setup() {
  // put your setup code here, to run once:

  bool motorShieldFound;

  Serial.begin(9600);

  // initialize motor shield
  AFMS.begin();

  // set AccelStepper parameters
  Astepper1.setMaxSpeed(100.0);  // steps per second
  // Fuyu stage has 200 steps/rev and 2 mm pitch, so this 1 mm/second
  Astepper1.setAcceleration(25.0);  // steps per second^2

  //Serial.println("Setup complete");
}

void loop() {
  // put your main code here, to run repeatedly:
  // listen for command on serial port

  if (Serial.available() > 0) {
    // read the serial port and respond appropriately
    readSerialInstruction();
  }
}

void readSerialInstruction() {
  // Serial instruction description:
  //   All commands end with newline \n
  //   Move forward: F#######\n (number of steps relative to current position as string)
  //   Move backwards: R######\n (number of steps back relative to current position as string)
  //   Emergency stop: S\n
  //   Get position: P\n

  char receivedChar;
  byte ndx = 0;
  char endMarker = '\n';
  long relSteps;

  //Serial.println("Instruction received");
  while (receivedChar != endMarker) {
    if (Serial.available() > 0) {
      receivedChar = Serial.read();
      if (receivedChar != endMarker) {
        instruction[ndx] = receivedChar;
      }

      else {
        instruction[ndx] = '\0'; // string termination character
      }
      //Serial.println(ndx);
      //Serial.println(receivedChar);
      ndx++;
    }
  }

  switch (instruction[0]) {
    case 'S':
      //Serial.println("Emergency stop");
      onEmergencyStop();
      break;
    case 'P':
      onReportPosition();
      break;
    case 'F':
      relSteps = strtol(&instruction[1], NULL, 0); // convert after initial character
      onMove(relSteps);
      break;
    case 'R':
      relSteps = strtol(&instruction[1], NULL, 0);
      onMove(-1*relSteps);
      break;
  }
}


void onMove(long deltaSteps) {
  // Set target position (relative to current)
  Astepper1.move(deltaSteps);

  keepMoving = true;
  bool accelStepperRunning = true;

  while (keepMoving == true && accelStepperRunning == true) {
    // motion loop

    // check to see if there was an emergency stop command
    if (Serial.available() > 0) {
      readSerialInstruction();
    }

    accelStepperRunning = Astepper1.run(); // returns false once target position reached
  }

  keepMoving = false;
  // report current position
  onReportPosition();
}


void onEmergencyStop() {
  keepMoving = false;
}


void onReportPosition() {
  Serial.println(Astepper1.currentPosition());
}