/**
*    TA-DA ZUKO
* Thermocouple Amplifier - Data Aquisition
* Version 1 codename: ZUKO
* Firmware version: 0.5.1
* by Mark Redd
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
const int delay_time = 149; // how much to slow the data collection

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


void setup_temperature_measurement()
{
/**
 * sets up the thermocouple amplifiers for temperature measurement
 * and reports a bunch of information about the setup
 */
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
}


/************** SD CARD DEFINITIONS *********************/
const int chipSelect = 10;
String dataString;
File dataFile;
int incomingByte = 48; // Set to ASCII byte 48 or "0" which means do NOT collect data

void setup_sdcard()
{
/**
 * sets up the SD card reader anc checks if the card
 * is present. The whole program will fail if the 
 * SD card is not present
 */
  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized.");
}

/************** RTC DEFINITIONS ********************/
RTC_PCF8523 rtc;
char daysOfTheWeek[7][12] = {
  "Sunday", 
  "Monday", 
  "Tuesday", 
  "Wednesday", 
  "Thursday", 
  "Friday", 
  "Saturday"};
DateTime now;
DateTime start;
long starttime;
long tmel;
long now1;
int time_byte;
String time_string;
int tindex;
String dtime1[6] = {"","","","","",""};

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


void setup_rtc()
{
/**
 * Sets up the RTC for running
 */
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  
  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
    /*
     * The following line sets the RTC to the date & time this sketch was compiled:
     *   rtc.adjust(DateTime(__DATE__, __TIME__));
     * This line sets the RTC with an explicit date & time, 
     * for example to set January 21, 2014 at 3am you would call:
     *   rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
    */
  }
  set_write_time();
}

/************* PRESSURE MEASUREMENT DEFINITIONS *******************/
const int 
  pressurePin = A8, // input pin for pressure transducer
  solenoidPin = 7;  // pin to open solenoid
int safetySig = 0;    // signal from pressure transducer for solenoid open
double pv_torr = 0;   // initialize value from pressure vessel

//Calibration fit line
const double 
  m = 0.299338,      // torr/sig (slope of calibration fit line)
  b = -64.35767;     // torr (intercept of calibration line)

//Function for torr
double sigToTorr(int sig)
{
  double ptorr;
  ptorr = sig * m + b;
  return ptorr;
}

bool temp_read_ready()
{
/**
 *  checks if all the temperatures are ready to be read. If
 *  all are ready to be read it returns true.
 *  Returns false otherwise
 */
  if (sensors.isConversionAvailable(Thermometer0) &&\
      sensors.isConversionAvailable(Thermometer1) &&\
      sensors.isConversionAvailable(Thermometer2) &&\
      sensors.isConversionAvailable(Thermometer3)) return true;
  else return false;
}


void set_RTC_time()
{
/**
 * sets the RTC time by reading input from the host 
 * computer via serial
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


void update_datastring()
{
/**
 * Pulls the requested data and combines pressure and temperature
 * data into one datastring
 */
  // Get the temperatures and the vessel gauge pressure
  t0 = sensors.getTempC(Thermometer0);  
  t1 = sensors.getTempC(Thermometer1);
  t2 = sensors.getTempC(Thermometer2);
  t3 = sensors.getTempC(Thermometer3);
  pv_torr = sigToTorr(analogRead(pressurePin));
  
  // get the elapsed time
  tmel = now1 - starttime; 
  
  // Correct for calibrations here
  
  dataString = "|,";  // Put it all in a string
  dataString += String(tmel) + ",";
  dataString += String(t0)   + ",";
  dataString += String(t1)   + ",";
  dataString += String(t2)   + ",";
  dataString += String(t3)   + ",";
  dataString += String(pv_torr,3);
}


void write_to_datafile()
{
/**
 * Writes datastring to file on the SD card and prints to serial
 */
  dataFile = SD.open("datalog.csv", FILE_WRITE);
  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(dataString);
    dataFile.close();
    Serial.println(dataString); // print to the serial port too:
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening datalog.csv");
  }
}


void setup(void)
{
  // start serial port
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect
  }

  Serial.println("\tTA-DA ZUKO");
  Serial.println("Thermocouple Amplifier - Data Aquisition");

  setup_temperature_measurement();
  setup_sdcard();
  setup_rtc();
  
  sensors.requestTemperatures(); // get the first temp reading
  now1 = millis(); // get the time of that first reading
  
  Serial.println("--- SETUP FINISHED ---");
}


void loop(void)
{
/**
 * period of collection is determined roughly by the following relationship
 * on larger time scales this is accurate to +/- 2 ms
 * *** period = delay + 101 ms *** 
 * Max sampling speed is ~ 5.7 Hz
 */
  if (temp_read_ready()){ // check that all TC Amps are ready to return a temperature
    
    update_datastring(); // put the temperature and pressure data into the datastring variable
    
    if(Serial.available() > 0) incomingByte = Serial.read(); // Check for communication over serial
    switch (incomingByte) {
      case '0':
        // ASCII '0' is the default state and just prints the data to serial
        Serial.println(dataString);
        break;
      case '1':
        // an ASCII '1' means write data to file on SD card and to serial
        write_to_datafile(); 
        break;
      case 't':
        // a 't' means to sync the time
        set_RTC_time(); 
        break;
      default:
        // otherwise throw an error
        Serial.println("|,err,err,err,err,err");
    }
    
    sensors.requestTemperatures(); // request temperature from all devices
    now1 = millis(); // get the current time
    delay(delay_time); // slow down the data collection
    
  }
  else { // if you get a missed temperature re-request the temperatures
    sensors.requestTemperatures();
    now1 = millis();
  }
}  
