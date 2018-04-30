 /*******************************************************************************
 * File          : ARIA_firmware.ino
 * Authors       : Brad Crowther, Mark Redd
 * Last Modified : 180304 (April 3, 2018)
 * Description   :
 *  Code to run the stepper motors and servos on the ARIA (Automated 
 *  Robotic Injector Arm). On receiveing power, the ARIA should lift the 
 *  injector assembly up to the top of the lead screw (about 10 inches up) then
 *  wait for further commands. Two buttons should be connected to the system.
 *  When pressed, the LEDs should extinguish. One button should run the sequence 
 *  for injecting a liquid compound sample into the furnace. The other should run the 
 *  sequence for introducing a solid sample. When the LEDs turn back on, it is an 
 *  indication the cycle is complete.
 */
#include <Stepper.h>
#include <Servo.h>

/****** CONSTANTS ********/
const int 
          LEDBUTTON1 = 0,    // pin for LED of button 1
          LEDBUTTON2 = 1,   // pin for LED of button 2
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
          LiftSpeed = 200,  // Set between 0 and 200 RPM
          PushSpeed = 45,  // Set between 0 and 60 RPM
// Step movements for the stepper motors
          LiftSteps = 2780,
          PushSteps = 475,
// Position constants for the Servo
          PosServo = 130,   // set an initial poisiton of the servo
// Time constants
          sec = 1000;    // in milliseconds

/**************Wire Connections from Arduino to plate**************
 * Pin 0 - LED Button (Directly connected to button wires)
 * Pin1 - LED Button (Directly connected to button wires)
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
 * Pin 12 - 28A (Servo)
 */


/**********PORT Functions**********
 * The PORTB/PORTD functions allow the manipulation of pins on 
 * the Arduino uno. Each pin can be set to either High (1) or Low (0).
 * The correlation between functions and pins:
 * 
 *                    PORTD (pins 0-7)
 *  Value      PD7  PD6  PD5  PD4  PD3  PD2  PD1  PD0
 *  Pin         7    6    5    4    3    2    1    0
 *  
 *                    PORTB (pins 8-13)
 *  Value      PB7  PB6  PB5  PB4  PB3  PB2  PB1  PB0
 *  Pin         X    X    13   12   11   10   9    8
 */
 
Servo DumperServo;
Stepper LiftStepper(StepsPerRevolution, LiftIN1, LiftIN2, LiftIN3, LiftIN4);
Stepper PushStepper(StepsPerRevolution, PushIN1, PushIN2, PushIN3, PushIN4);

void setup(){
  pinMode(LEDBUTTON1, OUTPUT);
  pinMode(LEDBUTTON2, OUTPUT);
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  delay(5*sec);                   // delay initial raising to account for human error
  LiftStepper.setSpeed(LiftSpeed); // set the speed of the motors here (rpm)
  PushStepper.setSpeed(PushSpeed);
  DumperServo.attach(PinServo);
  DumperServo.write(-PosServo);
  DumperServo.write(PosServo);
  LiftStepper.step(-LiftSteps);
  PORTD = B00000011; // code sets pins high or low, killing current to stepper motors to prevent overheating. Turns on LED Buttons connected to pins 0,1
  PORTB = B00000000; // enter standby mode
  }
 
void loop()
{
if(digitalRead(BUTTON1) == HIGH){    // liquid program
    digitalWrite(LEDBUTTON1, LOW); // turns off the LED buttons
    digitalWrite(LEDBUTTON2, LOW);
    LiftStepper.step(LiftSteps);
    // problem seems to be here
    delay(sec);
    PORTD = B00000000;             // kills current to LiftStepper, allowing more torque in PushStepper
    PushStepper.step(-PushSteps);
    LiftStepper.step(-LiftSteps);
    PushStepper.step(PushSteps);
    PORTD = B00000011;      // sets pins 0,1 high, turning on the LED buttons, and setting all other pins low
    PORTB = B00000000;      // cycle complete, returns to standby mode
     
  }
if(digitalRead(BUTTON2) == HIGH){
    digitalWrite(LEDBUTTON1, LOW);    // turns off the LED buttons
    digitalWrite(LEDBUTTON2, LOW);
    LiftStepper.step(LiftSteps);
    delay(sec);
    PORTD = B00000000;           // kills current to LiftStepper, allowing more torque in PushStepper
    DumperServo.write(-PosServo);
    delay((int) 1.5 * sec);
    LiftStepper.step(-LiftSteps);
    DumperServo.write(PosServo);
    PORTD = B00000011;    // sets pins 0,1 high, turning on the LED buttons, and setting all other pins low
    PORTB = B00000000;    //cycle complete, returns to standby mode
  }
}

