/*
Check RTC time and compare it to computer time
*/

#include <Wire.h>
#include "RTClib.h"

RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
DateTime now;
DateTime start;
long starttime;
long tmel;
long now1;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  //Serial.println("Setting RTC time..."); // uncomment to set to compile time
  //rtc.adjust(DateTime(__DATE__, __TIME__));
  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
    // following line sets the RTC to the date & time this sketch was compiled
    // rtc.adjust(DateTime(__DATE__, __TIME__));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
  // Serial.print("RTC is set...\n");
}

void loop() {
  // put your main code here, to run repeatedly:
  start = rtc.now();
  Serial.print("Current time is:");
  Serial.print(start.year(), DEC);
  Serial.print('/');
  Serial.print(start.month(), DEC);
  Serial.print('/');
  Serial.print(start.day(), DEC);
  Serial.print(" (");
  Serial.print(daysOfTheWeek[start.dayOfTheWeek()]);
  Serial.print(") ");
  Serial.print(start.hour(), DEC);
  Serial.print(':');
  Serial.print(start.minute(), DEC);
  Serial.print(':');
  Serial.print(start.second(), DEC);
  Serial.println();
  delay(1000);
}
