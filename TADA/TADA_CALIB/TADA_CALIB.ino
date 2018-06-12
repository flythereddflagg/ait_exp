int pressurePin = A8;
int psignal = 0;

void setup() {
  // start serial port
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. 
      //Needed for native USB port only
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  psignal = analogRead(pressurePin);
  Serial.println(psignal);
  // delay(250);
}
