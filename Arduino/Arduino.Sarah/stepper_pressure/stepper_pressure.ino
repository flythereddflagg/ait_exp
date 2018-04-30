
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

//Stepper motorin(stepsPerRevolution, 4, 5, 6, 7);
// second function for stepper to inject
// might need to change these pins

// might need to include the following to designate the pins as outputs

/*
pinMode (4, OUTPUT)
pinMode (5, OUTPUT)
...

*/
void setup() {
  motordown.setSpeed(120);
  //motorin.setSpeed(10);
  // set the speed at 10 rpm, this is lower then the example speed because 60 rpm might be to fast for the modern stepper
  
  Serial.begin(9600);
  // initialize the serial port:
  // I don't know if we need this line

  while (!Serial);
  // delays serial interface until the terminal window is open
  Serial.println("Arduino Ready.");
 
}

void loop() {
  if (Serial.available())
  {
  // waiting for a comand from Serial Monitor  
    int steps = Serial.parseInt();
    // converts command to an integer
    
    Serial.println("moving down");
    motordown.step(steps);
    delay(500);
    // moves the first motor to lower down
    
    //Serial.println("injecting")
    //motorin.step(steps)
    //delay(500)
    // moves the second motor in to inject
    
    Serial.println("moving up");
    motordown.step(-steps);
    // moves first motor to lift up
  }
}

