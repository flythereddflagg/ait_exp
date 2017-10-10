/*
    TA-DA ZUKO
 Thermocouple Amplifier - Data Aquisition
 Version 1 codename: ZUKO
 Firmware version: 0.2

 created  8 May 2017
 by Mark Redd

*/


/************** TEMPERATURE MEASUREMENT PREPROCESSOR INFO *********************/
#include <OneWire.h>
#include <DallasTemperature.h>
// Temperature data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
#define TEMPERATURE_PRECISION 9


/************** SD CARD PREPROCESSOR INFO *********************/
#include <SPI.h>
#include <SD.h>


/************** RTC PREPROCESSOR INFO ********************/
#include <Wire.h>
#include "RTClib.h"


/************** TEMPERATURE MEASUREMENT DEFINITIONS *********************/
// Setup a oneWire instance to communicate with any OneWire 
// devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

// arrays to hold device addresses
DeviceAddress Thermometer0, Thermometer1, Thermometer2, Thermometer3;

// Temperatures measured
float t0;
float t1;
float t2;
float t3;


/************** SD CARD DEFINITIONS *********************/
const int chipSelect = 10;
String dataString;
File dataFile;
int incomingByte = 48; // Set to ASCII byte 48 or "0" which means do NOT collect data


/************** RTC DEFINITIONS ********************/
RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
DateTime now;
DateTime start;
long starttime;
long tmel;
long now1;


/************* TEMPERATURE MEASUREMENT FUNCTIONS *************************/
// function to print a device address
void printAddress(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    // zero pad the address if necessary
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

/************* SETUP FUNCTION ***************************/
void setup(void)
{
  // start serial port
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("\tTA-DA ZUKO");
  Serial.println("Thermocouple Amplifier - Data Aquisition");

  /************* SETUP TEMPERATURE MEASUREMENT ***************************/
  // Start up the library
  Serial.println("Starting Thermocouple Amplifiers...");
  sensors.begin();

  // locate devices on the bus
  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // report parasite power requirements
  Serial.print("Parasite power is: "); 
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");


  // Index Thermocouples: Thermometer0, Thermometer1, Thermometer2, Thermometer3
  Serial.println("Indexing Thermocouples");
  if (!sensors.getAddress(Thermometer0, 0)) Serial.println("Unable to find address for Device 0"); 
  if (!sensors.getAddress(Thermometer1, 1)) Serial.println("Unable to find address for Device 1"); 
  if (!sensors.getAddress(Thermometer2, 2)) Serial.println("Unable to find address for Device 2"); 
  if (!sensors.getAddress(Thermometer3, 3)) Serial.println("Unable to find address for Device 3");
  
  // show the addresses we found on the bus Thermometer0, Thermometer1, Thermometer2, Thermometer3
  Serial.print("Device 0 Address: ");
  printAddress(Thermometer0);
  Serial.println();

  Serial.print("Device 1 Address: ");
  printAddress(Thermometer1);
  Serial.println();

  Serial.print("Device 2 Address: ");
  printAddress(Thermometer1);
  Serial.println();

  Serial.print("Device 3 Address: ");
  printAddress(Thermometer3);
  Serial.println();
  
  // set the resolution to 9 bit
  sensors.setResolution(Thermometer0, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer1, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer2, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer3, TEMPERATURE_PRECISION);
  sensors.setWaitForConversion(false); // do not wait for conversion (speeds up thermocouples)

  Serial.print("Device 0 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer0), DEC); 
  Serial.println();

  Serial.print("Device 1 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer1), DEC); 
  Serial.println();
  
  Serial.print("Device 2 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer2), DEC); 
  Serial.println();

  Serial.print("Device 3 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer3), DEC); 
  Serial.println();
  
  
  /************* SETUP SD CARD ***************************/
  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized.");
  
  
  /************* SETUP RTC **************************/
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  rtc.adjust(DateTime(2017,5,9,12,12,12));
  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
    // following line sets the RTC to the date & time this sketch was compiled
    
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
  starttime = millis();
  Serial.print("Start time is: ");
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

  sensors.requestTemperatures(); // get the first temp reading
  now1 = millis(); // get the time of that first reading
  
} /* END SETUP */


void loop(void)
{ 
  if (sensors.isConversionAvailable(Thermometer0) &&\
      sensors.isConversionAvailable(Thermometer1) &&\
      sensors.isConversionAvailable(Thermometer2) &&\
      sensors.isConversionAvailable(Thermometer3)){
    // call sensors.requestTemperatures() to issue a global temperature 
    // request to all devices on the bus
    t0 = sensors.getTempC(Thermometer0);
    t1 = sensors.getTempC(Thermometer1);
    t2 = sensors.getTempC(Thermometer2);
    t3 = sensors.getTempC(Thermometer3);
    
    tmel = now1 - starttime; // elapsed time
  
    dataString = "|,";
    dataString += String(tmel) + ",";
    dataString += String(t0)   + ",";
    dataString += String(t1)   + ",";
    dataString += String(t2)   + ",";
    dataString += String(t3);
  
    if(Serial.available() > 0) incomingByte = Serial.read();
    if(incomingByte == 49) { // look for an ASCII '1'
      dataFile = SD.open("datalog.csv", FILE_WRITE);
    
      // if the file is available, write to it:
      if (dataFile) {
        //Serial.println("Writing to file");
        dataFile.println(dataString);
        dataFile.close();
        // print to the serial port too:
        Serial.println(dataString);
      }
      // if the file isn't open, pop up an error:
      else {
        Serial.println("error opening datalog.csv");
      }
    }
    else if (incomingByte == 48) { // look for an ASCII '0'
      Serial.println(dataString);
    }
    else {                         // otherwise throw an error
      Serial.println("|,err,err,err,err,err");
      }
    
    sensors.requestTemperatures();
    now1 = millis();
    delay(149); // slow down the data collection
    // period of collection is determined roughly by the following relationship
    // on larger time scales this is accurate to +/- 2 ms
    // *** period = delay + 101 ms *** 
    // Max sampling speed is ~ 5.7 Hz
  }
}  
