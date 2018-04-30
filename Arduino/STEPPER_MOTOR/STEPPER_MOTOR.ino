#include <Stepper.h>
  
const int Steps = 200;
Stepper myStepper1(Steps, 4, 5, 6, 7);
Stepper myStepper2(Steps, 8, 9, 10, 11);

void setup() 
{
  // set the speed at 60 rpm:
  myStepper1.setSpeed(60);
  myStepper2.setSpeed(60);
  // initialize the serial port:
  Serial.begin(9600);
}


void loop() {
  // step one revolution  in one direction:
  Serial.println("clockwise");
  
  for(int s=0; s<Steps; s++)
  {
  Serial.println(s);  
  myStepper1.step(1);
  myStepper2.step(1);
  }
  delay(500);
}



