const int ledPin = 12;                                        //defining this to be a constant means it won't change
int ledState = LOW;                                           //int are variables that can change
unsigned long previousMillis = 0;                             //using unsigned long gives more storage for time which is normally longer
const long interval = 1000;
void setup() {
  // put your setup code here, to run once:
  pinMode (ledPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  unsigned long currentMillis = millis();                     //returns time in milliseconds since board started
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
  
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }  
  digitalWrite (ledPin, ledState);
  }

}

