/**
*    TA-DA ZUKO
* Thermocouple Amplifier - Data Aquisition
* Version 1 codename: ZUKO
* Firmware version: 0.5.1
* by Mark Redd 
*/

#include <OneWire.h>            // TEMPERATURE MEASUREMENT
#include <DallasTemperature.h>  // TEMPERATURE MEASUREMENT
#include <SPI.h>  // SD CARD
#include <SD.h>   // SD CARD
#include <Wire.h>   // RTC 
#include "RTClib.h" // RTC 

#define ONE_WIRE_BUS 2 // data wire is port 2 on the Arduino
#define TEMPERATURE_PRECISION 9 // precision bits
#define SERIAL_BAUDRATE 9600

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
RTC_PCF8523 rtc;    // real time clock instance
DeviceAddress tc0, tc1, tc2, tc3;
float t0, t1, t2, t3; // Temperatures measured
const int chipSelect = 10; // SD CARD 
String dataString;  // data string to output to Serial
File dataFile;      // file pointer to write to SD CARD
char incomingByte = '0'; // '0' means do NOT collect data
DateTime now, start;
long starttime, time_elapsed, tnow;
int time_byte, tindex;
String time_string;
String dtime1[6] = {"","","","","",""};
const int pressurePin = A0; // input pin for p transducer
double pv_torr = 0;   // initialize pressure 
const double      // Calibration fit line
  m = 0.299338,   // torr/sig (slope of calibration fit line)
  b = -64.35767;  // torr (intercept of calibration line)


void setup_temperature_measurement()
{
/**
 * sets up the thermocouple amplifiers for temperature measurement
 * and reports a bunch of information about the setup
 */

// Start up the library
  Serial.println("/Starting Thermocouple Amplifiers...");
  sensors.begin();

  // Index Thermocouples: tc0, tc1, tc2, tc3
  if (!sensors.getAddress(tc0, 0)) Serial.println("/Unable to find address for Device 0"); 
  if (!sensors.getAddress(tc1, 1)) Serial.println("/Unable to find address for Device 1"); 
  if (!sensors.getAddress(tc2, 2)) Serial.println("/Unable to find address for Device 2"); 
  if (!sensors.getAddress(tc3, 3)) Serial.println("/Unable to find address for Device 3");
  

  // set the resolution to 9 bit
  sensors.setResolution(tc0, TEMPERATURE_PRECISION);
  sensors.setResolution(tc1, TEMPERATURE_PRECISION);
  sensors.setResolution(tc2, TEMPERATURE_PRECISION);
  sensors.setResolution(tc3, TEMPERATURE_PRECISION);

  // do not wait for conversion (speeds up thermocouples)
  sensors.setWaitForConversion(false);   
}

void setup_sdcard()
{
/**
 * sets up the SD card reader anc checks if the card
 * is present. The whole program will fail if the 
 * SD card is not present
 */
  Serial.print("/Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("/Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("/card initialized.");
}

void set_write_time(void)
{
  starttime = millis();
  start = rtc.now();
  Serial.print("+ TA-DA start time is: ");
  dataString = String(start.year(), DEC) + String('/')
    + String(start.month(), DEC) + String('/')
    + String(start.day(), DEC) + String(" ")
    + String(start.hour(), DEC) + String(':')
    + String(start.minute(), DEC) + String(':')
    + String(start.second(), DEC);

  Serial.println(dataString);
  Serial.print("/Writing start time to file...");
  
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


void setup_rtc()
{
/**
* Sets up the RTC for running
* The following line sets the RTC to the date & time this sketch was compiled:
*   rtc.adjust(DateTime(__DATE__, __TIME__));
* This line sets the RTC with an explicit date & time, 
* for example to set January 21, 2014 at 3am you would call:
*   rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
*/
  if (! rtc.begin()) {
    Serial.println("/Couldn't find RTC");
    while (1);
  }
  if (! rtc.initialized()) {
    Serial.println("/RTC is NOT running!");
  }
  set_write_time();
}


double sigToTorr(int sig)
{
/*
* Function for to change Signal to P in torr
*/
  double ptorr;
  ptorr = sig * m + b;
  return ptorr;
}

bool temp_read_ready()
{
/**
*  Sets the time and then
*  checks if all the temperatures are ready to be read. If
*  all are ready to be read it returns true.
*  Returns false otherwise
*/
  tnow = millis(); // get the current time
 
  if (
    sensors.isConversionAvailable(tc0) &&
    sensors.isConversionAvailable(tc1) &&
    sensors.isConversionAvailable(tc2) &&
    sensors.isConversionAvailable(tc3) 
  ) return true;
  else return false;
}


void set_RTC_time()
{
/**
* sets the RTC time by reading input from the host 
* computer via serial
* This line sets the RTC with an explicit date & time, 
* for example to set January 21, 2014 at 3am 
* you would call:
* rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
*/
  while (Serial.available() > 0) {
    // parse the incoming date time string
    time_byte = Serial.read();
    time_string += (char)time_byte;
    if (time_byte == ','){
      tindex ++;
      continue;
    }
    dtime1[tindex] += (char)time_byte;
  }
  

  Serial.print("/Syncronizing time...");
  rtc.adjust(DateTime(
    dtime1[0].toInt(), 
    dtime1[1].toInt(), 
    dtime1[2].toInt(), 
    dtime1[3].toInt(), 
    dtime1[4].toInt(), 
    dtime1[5].toInt()));
  Serial.print("Done. \n/Time Set to: ");
  Serial.println(time_string);
  for (int i=0; i<6; i++){
    dtime1[i] = ""; // reset the array
  }
  tindex = 0;
  time_string = "";  // reset time string
  incomingByte = '0'; // or '0': Do not write to datafile
  set_write_time();  // reset clocks
}


void update_datastring()
{
/**
 * Pulls the requested data and combines pressure and temperature
 * data into one datastring
 */
  // Get the temperatures and the vessel gauge pressure
  t0 = sensors.getTempC(tc0);  
  t1 = sensors.getTempC(tc1);
  t2 = sensors.getTempC(tc2);
  t3 = sensors.getTempC(tc3);
  pv_torr = sigToTorr(analogRead(pressurePin));
    // get the elapsed time
  time_elapsed = tnow - starttime; 
  
  // Correct for calibrations here
  
  dataString = "|,";  // Put it all in a string
  dataString += String(time_elapsed) + ",";
  dataString += String(t0)   + ",";
  dataString += String(t1)   + ",";
  dataString += String(t2)   + ",";
  dataString += String(t3)   + ",";
  dataString += String(pv_torr,3);
}


void write_to_datafile()
{
/**
 * Writes datastring to file on the SD card
 * If the dataFile fails to open it throws an error to Serial
 */
  dataFile = SD.open("datalog.csv", FILE_WRITE);
  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(dataString);
    dataFile.close();
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("/Error: datalog.csv open failed");
  }
}


void setup(void)
{
  // start serial port
  Serial.begin(SERIAL_BAUDRATE);
  while (!Serial) {
    ; // wait for serial port to connect
  }

  Serial.println("/\tTA-DA ZUKO");
  Serial.println("/Thermocouple Amplifier - Data Aquisition");

  setup_temperature_measurement();
  setup_sdcard();
  setup_rtc();

  Serial.println("/--- SETUP FINISHED ---");
  sensors.requestTemperatures(); // get the first temp reading
}


void loop(void)
{
/**
* Mainloop of the program
*/
   
  if (temp_read_ready()){ // check that all TC Amps are ready 
    update_datastring(); // put T and P in the datastring variable
    
    // Check for communication over serial
    if(Serial.available() > 0) incomingByte = Serial.read();
    switch (incomingByte) {
      case '1':
        // '1': write data to file on SD card and to serial
        write_to_datafile();
      case '0':
        // '0': only print the data to serial
        Serial.println(dataString);
        break;
      case 't':
        // 't': sync the time
        set_RTC_time(); 
        break;
      default:
        // otherwise throw an error
        Serial.println("|,err,err,err,err,err");
        break;
    }
    sensors.requestTemperatures(); // new temperature request
  }
  else { 
    // if you get a missed temperature try again
    sensors.requestTemperatures();
  }
}

