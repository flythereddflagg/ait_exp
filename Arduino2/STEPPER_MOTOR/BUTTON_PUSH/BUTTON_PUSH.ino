#include <Stepper.h>
#include <Servo.h>

Servo myServo;
int pos = -90;
const int BAUD_RATE = 9600;
const int BUTTON1 = 2, BUTTON2 = 3;

//enter the number of total steps you want the stepper motors to take. 200 steps/rotation
const int StepsPerRevolution = 200;

// setup pins for each driver: 
// lift motor ~ IN1, IN2, IN3, IN4 (pins 4 - 7)
const int LiftIN1 = 4, 
          LiftIN2 = 5, 
          LiftIN3 = 6, 
          LiftIN4 = 7,
// push motor ~ IN1, IN2, IN3, IN4 (pins 8 - 10)
          PushIN1 = 8, 
          PushIN2 = 9, 
          PushIN3 = 10, 
          PushIN4 = 11;
Stepper LiftStepper(StepsPerRevolution, LiftIN1, LiftIN2, LiftIN3, LiftIN4);
Stepper PushStepper(StepsPerRevolution, PushIN1, PushIN2, PushIN3, PushIN4);

void setup(){
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
  Serial.begin(BAUD_RATE);
  //set the speed of the motors here (rpm)
  LiftStepper.setSpeed(80);
  PushStepper.setSpeed(30);
  myServo.attach(12);
  myServo.write(-130);
  myServo.write(130);
  LiftStepper.step(-3800);
  PORTD = B00000000;
  PORTB = B00000000;
}
 
void loop()
{
if(digitalRead(BUTTON1)==HIGH)
  {
    LiftStepper.step(3800);
    delay(1000);
    PushStepper.step(-485);
    delay(15);
    LiftStepper.step(-3800);
    PushStepper.step(485);
    PORTD = B00000000;
    PORTB = B00000000;
  }
if(digitalRead(BUTTON2)==HIGH)
  {
    LiftStepper.step(3800);
    delay(15);
    myServo.write(-130);
    
   
    delay(1500);
    LiftStepper.step(-3800);
    
    myServo.write(130);
    PORTD = B00000000;
    PORTB = B00000000;
    
      
  }
}

