long randNumber;
String output;

void setup() {
  Serial.begin(9600);

  // if analog input pin 0 is unconnected, random analog
  // noise will cause the call to randomSeed() to generate
  // different seed numbers each time the sketch runs.
  // randomSeed() will then shuffle the random function.
  randomSeed(analogRead(0));
  Serial.println("/Initalized!");
}

void loop() {
  // print a random number from 0 to 299
  randNumber = random(300);
  output = "|,"+String(millis())+"," + String(random(300))+"," + String(random(300))+","\
    + String(random(300))+"," + String(random(300))+"," + String(random(300));
  Serial.println(output);


  delay(230);
}
