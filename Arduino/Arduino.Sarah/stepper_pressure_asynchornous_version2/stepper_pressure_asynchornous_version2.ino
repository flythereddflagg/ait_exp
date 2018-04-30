
/*
  Stepper Motor Control - serial monitor, two arduinos

*/

#include <Stepper.h>

const int stepsPerRevolution = 200;
// number of revolutions for our stepper motor
// might need to change this if hardware uses half step defaults

Stepper motordown(stepsPerRevolution, 8, 9, 10, 11);
// initialize the stepper library on pins 8 through 11:
// a help said to change the sequence to (blah, 8, 10, 9, 11)

Stepper motorin(stepsPerRevolution, 4, 5, 6, 7);
// second function for stepper to inject
// might need to change these pins

int motorprogress;
int a;
int b;
int c;
int d;
int e;

void setup() {
  Serial.begin(9600);
  motordown.setSpeed(120);
  motorin.setSpeed(120);
  // set the speed at 120 rpm
  
  
  motorprogress = 0;
  // When program gets input to start collecting data initialize motorprogress, motorprogress is a counter variable. It just keeps track of where
       // we are in the injection
  // this variables a-e are for changing how many rotations
  a = 2;
  b = 10;
  c = 15;
  d = 20;
  e = 25;
}
void loop() {
  // suppose we know how many steps to go down and inject, then we don't need a serial import, we just need to do it in small segements in between
  // temp data collection until it has injected and risen
  Serial.print("motor progress");
  Serial.println(motorprogress);
  if (motorprogress < a)
  {
    motorprogress = motorprogress + 1;
    delay (500);
    if (motorprogress = a)
    {
      Serial.println("beginning to lower needle");
    }
  }
  // This portion will delay the injection for a short while so that a real temp can be calculated

    
  if (motorprogress > a-1 && motorprogress < b )
  {
    motordown.step(200);
    delay (500);
    motorprogress = motorprogress + 1;
    if (motorprogress = b)
    {
      Serial.println("needle lowered");
    }
  }
  // This portion lowers the motor in segments until the needle is fully lowered

 
  if (motorprogress > b-1 && motorprogress < c)
  {
    motorin.step(200);
    delay (500);
    motorprogress = motorprogress + 1;
    if (motorprogress = c)
    {
      Serial.println("sample injected");
    }
  }
  // This portion injects the sample in segments until the plunger is fully depressed
  
  if (motorprogress > c-1 && motorprogress < d)
  {
    motorin.step(200);
    delay (500);
    motorprogress = motorprogress + 1;
    if (motorprogress = d)
    {
      Serial.println("needle raised");
    }
  }
  // This portion raises the needle out of the furnace
 
  if (motorprogress > d-1 && motorprogress < e)
  {
    motorin.step(-200);
    delay (500);
    motorprogress = motorprogress + 1;
    if (motorprogress = e)
    {
      Serial.println("injector released");
    }
  }
  // This portion releases the injector

  
  if (motorprogress > e-1)
  {
    motorprogress = motorprogress + 1;
    //delay (149);
  }
  // This portion returns to a normal delay in between the measurements
}
