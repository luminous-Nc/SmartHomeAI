// Include the Adafruit DHT sensor library
#include <Adafruit_Sensor.h>
#include <DHT.h>

// --- Pin Definitions for Testing ---
// Switches (using pins from your original code for consistency)
const int SWITCH_1_PIN = 5; // Was switch_hot_pin, will test Fan
const int SWITCH_2_PIN = 6; // Was switch_comfortable_pin, will test LED
const int SWITCH_3_PIN = 7; // Was switch_cold_pin, will test DHT

// Outputs
const int FAN_RELAY_PIN = 4; // Was relay1_pin
const int LED_PIN = 8;       // Dedicated pin for LED testing

// DHT Sensor
const int DHT_SENSOR_PIN = 13;    // Pin where the DHT22 data pin is connected
#define DHT_SENSOR_TYPE DHT22 // We are using a DHT22 sensor

// Create an instance of the DHT sensor object
DHT dht(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

// --- State Variables for Testing ---
// Fan and LED states
bool fanOn = false;
bool ledOn = false;

// Button Debouncing Variables
// For Switch 1
int lastSwitch1State = LOW;
int currentSwitch1State = LOW;
unsigned long lastDebounceTime1 = 0;

// For Switch 2
int lastSwitch2State = LOW;
int currentSwitch2State = LOW;
unsigned long lastDebounceTime2 = 0;

// For Switch 3
int lastSwitch3State = LOW;
int currentSwitch3State = LOW;
unsigned long lastDebounceTime3 = 0;

const unsigned long debounceDelay = 50; // 50ms debounce delay

void setup() {
  // Initialize Serial communication
  Serial.begin(9600);
  Serial.println("--- Installation Test Started ---");
  Serial.println("Connect components and follow instructions.");
  Serial.println();

  // Initialize the DHT sensor
  dht.begin();

  // Initialize pin modes
  // Switches
  pinMode(SWITCH_1_PIN, INPUT);
  pinMode(SWITCH_2_PIN, INPUT);
  pinMode(SWITCH_3_PIN, INPUT);

  // Outputs
  pinMode(FAN_RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  // Set initial output states (both off)
  digitalWrite(FAN_RELAY_PIN, LOW); // Fan OFF
  digitalWrite(LED_PIN, LOW);       // LED OFF

  Serial.println("Step 1: Switch Test");
  Serial.println(" - Connect Switch 1 (Pin " + String(SWITCH_1_PIN) + ")");
  Serial.println(" - Connect Switch 2 (Pin " + String(SWITCH_2_PIN) + ")");
  Serial.println(" - Connect Switch 3 (Pin " + String(SWITCH_3_PIN) + ")");
  Serial.println(" - Press each switch. You should see a confirmation message.");
  Serial.println("-------------------------------------");
}

void loop() {
  handleSwitch1();
  handleSwitch2();
  handleSwitch3();

  // Small delay to make the loop more manageable
  delay(10);
}

// --- Handler Functions for Each Switch ---

void handleSwitch1() {
  int reading = digitalRead(SWITCH_1_PIN);
  unsigned long currentTime = millis();

  if (reading != lastSwitch1State) {
    lastDebounceTime1 = currentTime;
  }

  if ((currentTime - lastDebounceTime1) > debounceDelay) {
    if (reading != currentSwitch1State) {
      currentSwitch1State = reading;
      if (currentSwitch1State == HIGH) {
        Serial.println("Switch 1 pressed.");

        // Stage 2: Fan Relay Test
        // Check if FAN_RELAY_PIN is a valid output pin before trying to control it
        if (FAN_RELAY_PIN >= 0) { // Simple check, ensure it's not a negative placeholder
            fanOn = !fanOn; // Toggle fan state
            digitalWrite(FAN_RELAY_PIN, fanOn ? HIGH : LOW);
            if (fanOn) {
            Serial.println(" -> Fan Relay: ON");
            } else {
            Serial.println(" -> Fan Relay: OFF");
            }
            Serial.println("   (Ensure Fan Relay is connected to Pin " + String(FAN_RELAY_PIN) + ")");
        } else {
            Serial.println(" -> Fan Relay Pin not configured for test.");
        }
      }
    }
  }
  lastSwitch1State = reading;
}

void handleSwitch2() {
  int reading = digitalRead(SWITCH_2_PIN);
  unsigned long currentTime = millis();

  if (reading != lastSwitch2State) {
    lastDebounceTime2 = currentTime;
  }

  if ((currentTime - lastDebounceTime2) > debounceDelay) {
    if (reading != currentSwitch2State) {
      currentSwitch2State = reading;
      if (currentSwitch2State == HIGH) {
        Serial.println("Switch 2 pressed.");
        
        // Stage 2: LED Test
        if (LED_PIN >= 0) {
            ledOn = !ledOn; // Toggle LED state
            digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
            if (ledOn) {
            Serial.println(" -> LED: ON");
            } else {
            Serial.println(" -> LED: OFF");
            }
            Serial.println("   (Ensure LED is connected to Pin " + String(LED_PIN) + ")");
        } else {
            Serial.println(" -> LED Pin not configured for test.");
        }
      }
    }
  }
  lastSwitch2State = reading;
}

void handleSwitch3() {
  int reading = digitalRead(SWITCH_3_PIN);
  unsigned long currentTime = millis();

  if (reading != lastSwitch3State) {
    lastDebounceTime3 = currentTime;
  }

  if ((currentTime - lastDebounceTime3) > debounceDelay) {
    if (reading != currentSwitch3State) {
      currentSwitch3State = reading;
      if (currentSwitch3State == HIGH) {
        Serial.println("Switch 3 pressed.");

        // Stage 3: DHT Sensor Test
        Serial.println(" -> Reading DHT Sensor (Pin " + String(DHT_SENSOR_PIN) + ")");
        float humidity = dht.readHumidity();
        float temperature = dht.readTemperature(); // Reads in Celsius by default

        if (isnan(humidity) || isnan(temperature)) {
          Serial.println("    Failed to read from DHT sensor!");
          Serial.println("    Ensure DHT sensor is connected correctly.");
        } else {
          Serial.print("    Temperature: ");
          Serial.print(temperature);
          Serial.println(" *C");
          Serial.print("    Humidity: ");
          Serial.print(humidity);
          Serial.println(" %");
        }
      }
    }
  }
  lastSwitch3State = reading;
}