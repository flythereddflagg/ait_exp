//hello world!
//for Arduino
int a = 3;
int b = 4;
int h;
#include "math.h"

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("Let's calculate a hypoteneuse");
  Serial.print ("a = ");
  Serial.println (a);
  Serial.print ("b = ");
  Serial.println (b);
  Serial.print ("h = ");
  h = sqrt (a*a+b*b);
  Serial.println(h);
}

void loop() {
  // put your main code here, to run repeatedly:
}
