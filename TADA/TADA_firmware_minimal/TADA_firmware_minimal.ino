/**
*    TA-DA ZUKO
* Thermocouple Amplifier - Data Aquisition 
* Version 1 codename: ZUKO
* Firmware version: 0.5.3 (Minimal Edition)
* by Mark Redd 
*/

/************** TEMPERATURE MEASUREMENT PREPROCESSOR INFO *********************/
#include <OneWire.h>
#include <DallasTemperature.h>
// Temperature data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
#define TEMPERATURE_PRECISION 9


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

long starttime, now1;
String dataString;

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
 //Serial.print("VERSION "); // print the version
 //Serial.println(DALLASTEMPLIBVERSION);
  // Start up the library
  Serial.println("/Starting Thermocouple Amplifiers...");
  sensors.begin();

  // locate devices on the bus
  Serial.print("/Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // report parasite power requirements
  Serial.print("/Parasite power is: "); 
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

  // Index Thermocouples: Thermometer0, Thermometer1, Thermometer2, Thermometer3
  Serial.println("/Indexing Thermocouples");
  if (!sensors.getAddress(Thermometer0, 0)) Serial.println("/Unable to find address for Device 0"); 
  if (!sensors.getAddress(Thermometer1, 1)) Serial.println("/Unable to find address for Device 1"); 
  if (!sensors.getAddress(Thermometer2, 2)) Serial.println("/Unable to find address for Device 2"); 
  if (!sensors.getAddress(Thermometer3, 3)) Serial.println("/Unable to find address for Device 3");
  
  // show the addresses we found on the bus Thermometer0, Thermometer1, Thermometer2, Thermometer3
  Serial.print("/Device 0 Address: ");
  printAddress(Thermometer0);
  Serial.println();

  Serial.print("/Device 1 Address: ");
  printAddress(Thermometer1);
  Serial.println();

  Serial.print("/Device 2 Address: ");
  printAddress(Thermometer1);
  Serial.println();

  Serial.print("/Device 3 Address: ");
  printAddress(Thermometer3);
  Serial.println();
  
  // set the resolution to 9 bit
  sensors.setResolution(Thermometer0, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer1, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer2, TEMPERATURE_PRECISION);
  sensors.setResolution(Thermometer3, TEMPERATURE_PRECISION);

  // do not wait for conversion (speeds up thermocouples)
  sensors.setWaitForConversion(false); 

  Serial.print("/Device 0 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer0), DEC); 
  Serial.println();

  Serial.print("/Device 1 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer1), DEC); 
  Serial.println();
  
  Serial.print("/Device 2 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer2), DEC); 
  Serial.println();

  Serial.print("/Device 3 Resolution: ");
  Serial.print(sensors.getResolution(Thermometer3), DEC); 
  Serial.println();
}



bool temp_read_ready()
{
/**
 *  checks if all the temperatures are ready to be read. If
 *  all are ready to be read it returns true.
 *  Returns false otherwise
 */
  /*Serial.print(sensors.isConversionAvailable(Thermometer0));
  Serial.print(sensors.isConversionAvailable(Thermometer1));
  Serial.print(sensors.isConversionAvailable(Thermometer2));
  Serial.print(sensors.isConversionAvailable(Thermometer3));
  Serial.println("");/**/

  if (sensors.isConversionAvailable(Thermometer0) &&\
      sensors.isConversionAvailable(Thermometer1) &&\
      sensors.isConversionAvailable(Thermometer2) &&\
      sensors.isConversionAvailable(Thermometer3)) return true;
  else return false;
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
  
  // get the elapsed time
  long tmel = now1 - starttime; 
  
  // Correct for calibrations here
  
  dataString = "|,";  // Put it all in a string
  dataString += String(tmel) + ",";
  dataString += String(t0)   + ",";
  dataString += String(t1)   + ",";
  dataString += String(t2)   + ",";
  dataString += String(t3);
}




void setup(void)
{
  // start serial port
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect
  }

  Serial.println("/\tTA-DA ZUKO");
  Serial.println("/Thermocouple Amplifier - Data Aquisition");

  setup_temperature_measurement();

  sensors.requestTemperatures(); // get the first temp reading
  now1 = millis(); // get the time of that first reading
  Serial.println("/--- SETUP FINISHED ---");
}


void loop(void)
{
/**
 * The following relationship:
 *    sample period = delay time - 101 (ms)
 * will determine the maximum sample rate. For instance the default delay_time is 149 (ms) 
 * which translates to about 4 Hz or a sample every 0.25 seconds.
 */
   
  if (temp_read_ready()){ // check that all TC Amps are ready to return a temperature
    //if (millis() - now1 < delay_time) return; // slow down data collection
    // check if the WaitForConversion flag is set to true the reset it to false if it is.    
    update_datastring(); // put the temperature and pressure data into the datastring variable
    Serial.println(dataString);
    sensors.requestTemperatures(); // request temperature from all devices
    now1 = millis(); // get the current time
    
  }
  else { 
    // if you get a missed temperature,
    // set the WaitForConversion flag to true and 
    // re-request the temperatures
    sensors.requestTemperatures();
    now1 = millis();
  }
}
