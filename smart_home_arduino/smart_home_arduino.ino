// Include the Adafruit DHT sensor library
#include <Adafruit_Sensor.h>
#include <DHT.h>

// --- Pin Definitions ---
// Define the pin the DHT22 data line is connected to
const int DHT_SENSOR_PIN = 13; // Pin where the DHT22 data pin is connected

// Define the type of DHT sensor
#define DHT_SENSOR_TYPE DHT22   // We are using a DHT22 sensor

// Create an instance of the DHT sensor object
DHT dht(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);
    
// Constants for switch and relay pins
const int switch_hot_pin = 5;         // User feedback: HOT
const int switch_comfortable_pin = 6; // User feedback: COMFORTABLE
const int switch_cold_pin = 7;        // User feedback: COLD

const int relay1_pin = 4;             // Relay 1 (e.g., for heating)
const int relay2_pin = 3;             // Relay 2 (e.g., for cooling)

// --- Variables ---
float currentTemperature = 0.0; // Stores the current temperature (DHT22 provides decimals)
float currentHumidity = 0.0;    // Stores the current humidity (DHT22 provides decimals)
String incomingCommand = "";      // String to store command from Python

// --- Timing Variables ---
unsigned long lastDHTReading = 0;     // Timestamp of last DHT reading
unsigned long lastDataSent = 0;       // Timestamp of last data sent
const unsigned long DHT_INTERVAL = 2000;     // DHT reading interval (2 seconds)
const unsigned long DATA_INTERVAL = 1000;    // Data sending interval (1 second)

// --- Button State Variables with Debouncing ---
int lastSwitchHotState = LOW;         // User feedback: HOT
int lastSwitchComfortableState = LOW; // User feedback: COMFORTABLE
int lastSwitchColdState = LOW;        // User feedback: COLD

int currentSwitchHotState = LOW;
int currentSwitchComfortableState = LOW;
int currentSwitchColdState = LOW;

// Debounce timing
unsigned long lastDebounceTimeHot = 0;
unsigned long lastDebounceTimeComfortable = 0;
unsigned long lastDebounceTimeCold = 0;
const unsigned long debounceDelay = 50;    // 50ms debounce delay

void setup() {
  // Initialize Serial communication
  Serial.begin(9600);
  Serial.println("Arduino Thermostat Control Initialized (DHT22)");

  // Initialize the DHT sensor
  dht.begin();

  // Initialize pin modes
  pinMode(switch_hot_pin, INPUT);
  pinMode(switch_comfortable_pin, INPUT);
  pinMode(switch_cold_pin, INPUT);

  pinMode(relay1_pin, OUTPUT);
  pinMode(relay2_pin, OUTPUT);

  // Set initial relay states (both off)
  digitalWrite(relay1_pin, LOW);
  digitalWrite(relay2_pin, LOW);

  Serial.println("SmartHome AI system ready for user feedback collection");
  
  // Initialize timing
  lastDHTReading = millis();
  lastDataSent = millis();
}

void loop() {
  unsigned long currentTime = millis();
  
  // --- Read Temperature and Humidity from DHT22 (every 2 seconds) ---
  if (currentTime - lastDHTReading >= DHT_INTERVAL) {
    float humidity_reading = dht.readHumidity();
    float temperature_reading = dht.readTemperature();

    // Check if any reads failed.
    if (isnan(humidity_reading) || isnan(temperature_reading)) {
      Serial.println("Failed to read from DHT sensor!");
      // Keep previous valid readings
    } else {
      currentHumidity = humidity_reading;
      currentTemperature = temperature_reading;
    }
    
    lastDHTReading = currentTime;
  }

  // --- Handle User Feedback Buttons with Debouncing ---
  handleButtonPress(switch_hot_pin, currentSwitchHotState, lastSwitchHotState, 
                   lastDebounceTimeHot, "hot", "HOT");
  
  handleButtonPress(switch_comfortable_pin, currentSwitchComfortableState, lastSwitchComfortableState, 
                   lastDebounceTimeComfortable, "comfortable", "COMFORTABLE");
  
  handleButtonPress(switch_cold_pin, currentSwitchColdState, lastSwitchColdState, 
                   lastDebounceTimeCold, "cold", "COLD");

  // --- Send Data to Python over Serial (every 1 second) ---
  if (currentTime - lastDataSent >= DATA_INTERVAL) {
    Serial.print("T:");
    Serial.print(currentTemperature, 1); // Print temperature with 1 decimal place
    Serial.print(",H:");
    Serial.print(currentHumidity, 1);    // Print humidity with 1 decimal place
    Serial.println();
    
    lastDataSent = currentTime;
  }

  // --- Check for Incoming Commands from Python ---
  if (Serial.available() > 0) {
    incomingCommand = Serial.readStringUntil('\n');
    incomingCommand.trim();

    Serial.print("Received command from Python: ");
    Serial.println(incomingCommand);

    if (incomingCommand == "hot") {
      digitalWrite(relay1_pin, LOW);  // Assuming Relay 2 is cooling
      digitalWrite(relay2_pin, HIGH);
      Serial.println("Action: Cooling ON");
    } else if (incomingCommand == "cold") {
      digitalWrite(relay1_pin, HIGH); // Assuming Relay 1 is heating
      digitalWrite(relay2_pin, LOW);
      Serial.println("Action: Heating ON");
    } else if (incomingCommand == "comfortable") {
      digitalWrite(relay1_pin, LOW);
      digitalWrite(relay2_pin, LOW);
      Serial.println("Action: System Idle (Comfortable)");
    }
  }
  
  // Small delay to prevent overwhelming the CPU, but keep it minimal
  delay(10);
}

// Function to handle button press with debouncing
void handleButtonPress(int buttonPin, int &currentState, int &lastState, 
                      unsigned long &lastDebounceTime, String feedbackType, String displayName) {
  int reading = digitalRead(buttonPin);
  unsigned long currentTime = millis();
  
  // If the switch changed, due to noise or pressing:
  if (reading != lastState) {
    // Reset the debouncing timer
    lastDebounceTime = currentTime;
  }

  if ((currentTime - lastDebounceTime) > debounceDelay) {
    // If the button state has changed:
    if (reading != currentState) {
      currentState = reading;

      // Only trigger on button press (LOW to HIGH transition)
      if (currentState == HIGH) {
        // Send user feedback to Python
        Serial.print("USER_FEEDBACK:");
        Serial.print(currentTemperature, 1);
        Serial.print(",");
        Serial.print(currentHumidity, 1);
        Serial.print(",");
        Serial.print(feedbackType);
        Serial.println();
        Serial.print("User feedback: ");
        Serial.println(displayName);
      }
    }
  }

  // Save the reading for next time
  lastState = reading;
}