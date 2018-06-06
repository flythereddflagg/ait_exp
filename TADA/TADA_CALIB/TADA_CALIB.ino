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
  psignal = 0;
  for (int i = 0; i < 5; i++){
    psignal += analogRead(pressurePin);
  }
  psignal /= 5;
  Serial.println(psignal);
  delay(250);
}
