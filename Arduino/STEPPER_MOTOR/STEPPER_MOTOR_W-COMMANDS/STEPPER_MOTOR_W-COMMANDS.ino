#include <Stepper.h>

//These define the keyboard keys that will be used to perform each motion
#define COMMAND_UP 'w'
#define COMMAND_DOWN 's'
#define COMMAND_STOP ' '

//enter the number of total steps you want the stepper motors to take. 200 steps/rotation
int stepsTotal = 200;

//this sets the value for the for loops and sets the amount of steps in each call
int num_of_steps = 1000;
//setup pins for each driver: motor1 ~ IN1, IN2, IN3, IN4; motor2 ~IN1, IN2, IN3, IN4
Stepper myStepper1(stepsTotal, 4, 5, 6, 7);
Stepper myStepper2(stepsTotal, 8, 9, 10, 11);
char lastCall = ' ';

//to move the system up
void upStep(int steps){
  Serial.println("go");
  myStepper1.step(1000);
  myStepper2.step(250);
  myStepper1.step(-1000);
  myStepper2.step(-250);
  delay(10); 
}

//to move the system down
void downStep(int steps){
  Serial.println("down");
  for (int s=0; s<num_of_steps; s++)
  {
  myStepper1.step(-1);
  myStepper2.step(-1);
  }
  delay(10);
}

void allStop(){
  Serial.println("stop");
  //all steppers stop
  PORTD = B00000000;
  PORTB = B00000000;
}
void setup(){
  Serial.begin(9600);
  //set the speed of the motors here (rpm)
  myStepper1.setSpeed(60);
  myStepper2.setSpeed(60);
}

void loop(){
//check to see there is serial communication and if so read the data
if(Serial.available()) {
char data = (char)Serial.read();
//switch to set the char via serial to a command
switch(data){
  case COMMAND_UP:
    upStep(num_of_steps);
    break;
  case COMMAND_DOWN:
    downStep(num_of_steps);
    break;
  case COMMAND_STOP:
    allStop();
    break;
}
lastCall = data;
}
}

  



