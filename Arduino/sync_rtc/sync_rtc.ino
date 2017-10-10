/*
*Syncronizes RTC with computer time
*Created by D. Sjunnesson 1scale1.com d.sjunnesson (at) 1scale1.com
*
*Created with combined information from 
*http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1180908809
*http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1191209057
*
*Big credit to  mattt (please contact me for a more correct name...) 
*from the Arduino forum which has written the main part of the library 
*which I have modified
*
*
*Modifed for use with the PCF8523 by Mark Redd on 5/15/17
*
*To Use:
*  - Change the last line of the setup function to read some time in the 
*     future to which you wish to syncronize (usually about a minute 
*     into the future
*  - Open your compter's clock and upload the sketch
*  - Open the serial monitor and type in some character but DO NOT SEND IT
*  - The moment your computer time matches the time in your setup function
*      press ENTER.
*  - The RTC will now return a syncronized time that should match your 
*      computer's time
*/

#include <Wire.h>
#include "RTClib.h"

RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = {
  "Sunday", 
  "Monday", 
  "Tuesday", 
  "Wednesday", 
  "Thursday", 
  "Friday", 
  "Saturday"
  };
DateTime start;

void setup()
{
  Serial.begin(9600);
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  
  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
  }
  
  Serial.println ("Hit a key to start");     // signal initalization done
  while(Serial.available() == 0){}
  // Hit upload about 10 seconds before selected time
  // This line sets the RTC with an explicit date & time, for example to set
  // January 21, 2014 at 3pm you would call:
  // rtc.adjust(DateTime(2014, 1, 21, 15, 0, 0)); 
  rtc.adjust(DateTime(2017, 6, 13, 10, 13, 0)); // Adjust this line!
  Serial.println("RTC Syncronized Successfully");
}

void loop()
{
  start = rtc.now();
  Serial.print("Current time is: ");
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


