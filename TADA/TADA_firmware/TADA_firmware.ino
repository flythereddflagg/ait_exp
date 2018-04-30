/*
    TA-DA ZUKO
 Thermocouple Amplifier - Data Aquisition
 Version 1 codename: ZUKO
 Firmware version: 0.4.3

 last modified on 20 June 2017
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

// Calibration Arrays
// Default values
// double coeffs0[5] = {0.0, 0.0, 0.0, 1.0, 0.0};
// double coeffs1[5] = {0.0, 0.0, 0.0, 1.0, 0.0};
// double coeffs2[5] = {0.0, 0.0, 0.0, 1.0, 0.0};
// double coeffs3[5] = {0.0, 0.0, 0.0, 1.0, 0.0};

double coeffs0[5] = {25.0, 0.0, 0.0, 1.0, 0.0};
double coeffs1[5] = {24.0, 0.0, 0.0, 1.0, 0.0};
double coeffs2[5] = {23.0, 0.0, 0.0, 1.0, 0.0};
double coeffs3[5] = {22.0, 0.0, 0.0, 1.0, 0.0};


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
int time_byte;
String time_string;
int tindex;
String dtime1[6] = {"","","","","",""};


/************** RTC FUNCTIONS *********************/
void set_write_time(void)
{
  starttime = millis();
  start = rtc.now();
  Serial.print("+ TA-DA start time is: ");
  dataString = "";
  dataString += String(start.year(), DEC);
  dataString += String('/');
  dataString += String(start.month(), DEC);
  dataString += String('/');
  dataString += String(start.day(), DEC);
  dataString += String(" ");
  //dataString += String(daysOfTheWeek[start.dayOfTheWeek()]);
  //dataString += String(") ");
  dataString += String(start.hour(), DEC);
  dataString += String(':');
  dataString += String(start.minute(), DEC);
  dataString += String(':');
  dataString += String(start.second(), DEC);
  Serial.println(dataString);

  Serial.print("Writing start time to file...");
  
  
  // Write the current time to differentiate time scales
  dataFile = SD.open("datalog.csv", FILE_WRITE);
    
  // if the file is available, write to it:
  if (dataFile) {
    dataFile.print("start,");
    dataFile.println(dataString);
    dataFile.close();
    Serial.println("DONE.");
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening datalog.csv");
  }
}

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

// Function to correct for calibrations
float t_corr(float val, double cf[5])
{
  float cval;
  float val2 = val*val;
  cval = cf[0]*val2*val2 + cf[1]*val*val2 + cf[2]*val2 +\
    cf[3]*val + cf[4];
  return cval;
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

  // do not wait for conversion (speeds up thermocouples)
  sensors.setWaitForConversion(false); 

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
  
  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
    // following line sets the RTC to the date & time this sketch was compiled
    // rtc.adjust(DateTime(__DATE__, __TIME__));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
  
  set_write_time();
  sensors.requestTemperatures(); // get the first temp reading
  now1 = millis(); // get the time of that first reading
  
} /* END SETUP */

void loop(void)
{ 
  if (sensors.isConversionAvailable(Thermometer0) &&\
      sensors.isConversionAvailable(Thermometer1) &&\
      sensors.isConversionAvailable(Thermometer2) &&\
      sensors.isConversionAvailable(Thermometer3)){ 
      // check that all TC Amps are ready to return a temperature

    
    t0 = sensors.getTempC(Thermometer0);  // Get the temperatures
    t1 = sensors.getTempC(Thermometer1);
    t2 = sensors.getTempC(Thermometer2);
    t3 = sensors.getTempC(Thermometer3);
    
    tmel = now1 - starttime; // get elapsed time

/*
    t0 = t_corr(t0, coeffs0); // Correct for calibrations
    t1 = t_corr(t1, coeffs1);
    t2 = t_corr(t2, coeffs2);
    t3 = t_corr(t3, coeffs3);
*/
  
    dataString = "|,";  // Put it all in a string
    dataString += String(tmel) + ",";
    dataString += String(t0)   + ",";
    dataString += String(t1)   + ",";
    dataString += String(t2)   + ",";
    dataString += String(t3);
  
    if(Serial.available() > 0) incomingByte = Serial.read(); // Check for communication over serial
    if(incomingByte == 49) { // look for an ASCII '1' which means write data to file
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
    else if (incomingByte == 't') { // look for a 't' which means to sync the time
      while (Serial.available() > 0) {
        time_byte = Serial.read();
        time_string += (char)time_byte;
        if (time_byte == ','){
          tindex ++;
          continue;
        }
        dtime1[tindex] += (char)time_byte;
      }
    
      // This line sets the RTC with an explicit date & time, for example to set
      // January 21, 2014 at 3am you would call:
      // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
      Serial.print("Syncronizing time...");
      rtc.adjust(DateTime(
        dtime1[0].toInt(), 
        dtime1[1].toInt(), 
        dtime1[2].toInt(), 
        dtime1[3].toInt(), 
        dtime1[4].toInt(), 
        dtime1[5].toInt()));
      Serial.print("Done. \nTime Set to: ");
      Serial.println(time_string);
      for (int i=0; i<6; i++){
        //Serial.print(dtime1[i]);
        dtime1[i] = ""; // reset the array
      }
      tindex = 0;
      time_string = "";  // reset time string
      incomingByte = 48; // Do not write to datafile
      set_write_time();  // reset clocks
    }
    else {                         // otherwise throw an error
      Serial.println("|,err,err,err,err,err");
      }
    // call sensors.requestTemperatures() to issue a global temperature 
    // request to all devices on the bus
    sensors.requestTemperatures();
    now1 = millis();
    delay(149); // slow down the data collection
    // period of collection is determined roughly by the following relationship
    // on larger time scales this is accurate to +/- 2 ms
    // *** period = delay + 101 ms *** 
    // Max sampling speed is ~ 5.7 Hz
  }
  else { // if you get a missed temperature re-request the temperatures
    sensors.requestTemperatures();
    now1 = millis();
    //Serial.print(sensors.isConversionAvailable(Thermometer0));
    //Serial.print(sensors.isConversionAvailable(Thermometer1));
    //Serial.print(sensors.isConversionAvailable(Thermometer2));
    //Serial.print(sensors.isConversionAvailable(Thermometer3));
    //Serial.println();
    //delay(149);
  }
}  
