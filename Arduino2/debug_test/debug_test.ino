/*******************************************************************************
 * File          : ARIA_firmware.ino
 * Authors       : Brad Crowther, Mark Redd
 * Last Modified : 182501 (Mar. 13, 2018)
 * Description   :
 *  Code to run the stepper motors and servos on the ARIA (Automated 
 *  Robotic Injector Arm). On receiveing power, the ARIA should lift the 
 *  injector assembly up to the top of the lead screw (about 10 inches up) then
 *  wait for further commands. Two buttons should be connected to the system.
 *  When pressed one should run the sequence for injecting a liquid compound 
 *  sample into the furnace. The other should run the sequence for introducing
 *  a solid sample.
 */
#include <Stepper.h>
#include <Servo.h>

/****** CONSTANTS ********/
const int BAUD_RATE = 9600, // Baud rate set nominally to 9600
          BUTTON1 = 2,      // pin for button 1 that runs the liquid sequence
          BUTTON2 = 3,      // pin for button 2 that runs the solid sequence
          StepsPerRevolution = 200, // Our motors have 200 steps/rotation
// setup pins for each stepper motor and the servo: 
// Lift Motor pins ~ IN1, IN2, IN3, IN4 (pins 4 - 7)
          LiftIN1 = 4, 
          LiftIN2 = 5, 
          LiftIN3 = 6, 
          LiftIN4 = 7,
// Push Motor pins ~ IN1, IN2, IN3, IN4 (pins 8 - 11)
          PushIN1 = 8, 
          PushIN2 = 9, 
          PushIN3 = 10, 
          PushIN4 = 11,         
// Servo Pin
          PinServo = 12,
// Motor Speeds in RPM
          LiftSpeed = 200,  //Set between 0 and 200 RPM                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ,
          PushSpeed = 60,  //Set between 0 and 60 RPM
// Step movements for the stepper motors
          LiftSteps = 3800,
          PushSteps = 475,
// Position constants for the Servo
          PosServo = 130,
// Time constants
          sec = 1000;

/*******************************************************************
 * Wire Connections between Arduino Uno and Plate relative to 1A on Plate
 * Pin 2 - 25A (Button 1)
 * Pin 3 - 26A (Button 2)
 * Pin 4 - 20A (Lift AIN2)
 * Pin 5 - 19A (Lift AIN1)
 * Pin 6 - 17A (Lift BIN1)
 * Pin 7 - 16A (Lift BIN2)
 * Pin 8 - 9A (Push AIN2)
 * Pin 9 - 8A (Push AIN1)
 * Pin 10 - 6A (Push BIN2)
 * Pin 11 - 5A (Push BIN1)
 * Pin 12 - servo
 */
          
Servo DumperServo;
Stepper LiftStepper(StepsPerRevolution, LiftIN1, LiftIN2, LiftIN3, LiftIN4);
Stepper PushStepper(StepsPerRevolution, PushIN1, PushIN2, PushIN3, PushIN4);

void setup(){
  Serial.begin(BAUD_RATE);
  /*pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  LiftStepper.setSpeed(LiftSpeed); //set the speed of the motors here (rpm)
  PushStepper.setSpeed(PushSpeed);
  DumperServo.attach(PinServo);
  DumperServo.write(-PosServo);
  DumperServo.write(PosServo);
  LiftStepper.step(-LiftSteps);
  PORTD = B00000000; // code kills current to stepper motor to keep drivers from overheating.
  PORTB = B00000000;*/
}
 
void loop()
{
/*if(digitalRead(BUTTON1)==HIGH){    //liquid program
    LiftStepper.step(LiftSteps);
    delay(sec);  // Why were all these delays chosen?
    PORTD = B00000000;
    PORTB = B00000000;
    PushStepper.step(-PushSteps);
    delay(15);
    LiftStepper.step(-LiftSteps);
    PushStepper.step(PushSteps);
    PORTD = B00000000;
    PORTB = B00000000; 
  }
if(digitalRead(BUTTON2)==HIGH){
    LiftStepper.step(LiftSteps);
    delay(15);
    PORTD = B00000000;
    PORTB = B00000000;
    DumperServo.write(-PosServo);
    delay((int) 1.5 * sec);
    LiftStepper.step(-LiftSteps);
    DumperServo.write(PosServo);
    PORTD = B00000000;
    PORTB = B00000000;      
  }*/
  if(digitalRead(BUTTON1)==HIGH){
    Serial.println("HIGH");
  }
  else{
    Serial.println("LOW");
  }
}

