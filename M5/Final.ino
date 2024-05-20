#include <M5Core2.h>
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "infrastructure";
const char* password = "ykyT3GJqnq52";
const char* mqtt_server = "csse4011-iot.zones.eait.uq.edu.au";
const char* button_topic = "JupiterBlueButton";

// Variables to store timer values
int minutes = 0;
int seconds = 0;

bool timerRunning = false;
unsigned long previousMillis = 0;
const long interval = 1000; // Timer interval in milliseconds

void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);
  setupWifi();
  client.setServer(mqtt_server, 1883);
  M5.Lcd.setTextSize(10);
  displayTime();
  // Setup MQTT server below
  
}

void loop() {
  // Check for MQTT Client Connection
  if (!client.connected()) {
      reConnect();
  }
  client.loop();
    
  // Check for button presses
  handleButtons();

  // If the timer is running, update timer
  if (timerRunning) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
      // Update seconds and minutes
      seconds--;
      // Vibrate for final 30 seconds
      if (minutes < 1 and seconds == 30) {
        client.publish(button_topic, "30 Seconds");
        M5.Axp.SetVibration(true);  
        delay(1000);
        M5.Axp.SetVibration(false);  
      }
      if (seconds < 0) {
        seconds = 59;
        minutes--;
        if (minutes < 0) {
          // Timer finished
          client.publish(button_topic, "Stop");
          M5.Axp.SetVibration(true); 
          delay(2000);
          M5.Axp.SetVibration(false);  
          seconds = 0;
          minutes = 0;
          timerRunning = false;
        }
      }
      displayTime();
      previousMillis = currentMillis;
    }
  }
}

void displayTime() {
  M5.Lcd.setCursor(50, 100);
  M5.Lcd.printf("%02d:%02d", minutes, seconds);
}

void handleButtons() {
  M5.update();

  // Increment in seconds when user taps button A
  if (M5.BtnA.wasReleased()) {
    seconds++;
    if (seconds > 59) {
      seconds = 0;
      minutes++;
    }
    displayTime();
  }

  // Increment in minutes when user holds button A
  if (M5.BtnA.pressedFor(1000, 200)) {
    minutes++;
    displayTime();
    delay(500);
  }

  // Decrement in seconds when user taps button B
  if (M5.BtnB.wasReleased()) {
    seconds--;
    if (seconds < 0) {
      seconds = 59;
      minutes--;
      if (minutes < 0) {
          // Cap minimum to be 00:00
          seconds = 0;
          minutes = 0;
      }
    }
    displayTime();
  }

  // Decrement in minutes when user holds button B
  if (M5.BtnB.pressedFor(1000, 200)) {
    minutes--;
    if (minutes < 0) {
        // Cap minimum to be 00:00
        seconds = 0;
        minutes = 0;
    }
    displayTime();
    delay(500);
  }

  if (M5.BtnC.wasReleased() || M5.BtnC.pressedFor(1000, 200)) {
    client.publish(button_topic, "Start");
    M5.Axp.SetVibration(true);  
    delay(1000);
    M5.Axp.SetVibration(false);  
    // Start/Stop timer
    timerRunning = !timerRunning;
    if (timerRunning) {
      previousMillis = millis();
    }
  }
}

// Initiate Wifi Connection
void setupWifi() {
    delay(10);
    M5.Lcd.printf("Connecting to %s", ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        M5.Lcd.print(".");
    }
    M5.Lcd.printf("\nSuccess\n");
}

// Establish MQTT connection when required
void reConnect() {
    while (!client.connected()) {
//        M5.Lcd.print("Attempting MQTT connection...");
        String clientId = "M5Stack-";
        clientId += String(random(0xffff), HEX);
        if (client.connect(clientId.c_str())) {
//            M5.Lcd.printf("\nSuccess\n");
             client.publish(button_topic, "set timer");
        }
//        } else {
//            M5.Lcd.print("failed, rc=");
//            M5.Lcd.print(client.state());
//            M5.Lcd.println("try again in 5 seconds");
//            delay(5000);
//        }
    }
}
