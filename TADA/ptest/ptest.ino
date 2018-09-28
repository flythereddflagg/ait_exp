const int pressurePin = A0;

void setup() {
  // put your setup code here, to run once:
  // start serial port
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect
  }

}

void loop() {
  // put your main code here, to run repeatedly:
  int psig = analogRead(pressurePin);
  Serial.println(psig);
}
