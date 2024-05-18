#include <M5Core2.h>

// Variables to store timer values
int minutes = 0;
int seconds = 0;

bool timerRunning = false;
unsigned long previousMillis = 0;
const long interval = 1000; // Timer interval in milliseconds

void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(10);
  displayTime();
}

void loop() {
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
        M5.Axp.SetVibration(true);  
        delay(1000);
        M5.Axp.SetVibration(false);  
      }
      if (seconds < 0) {
        seconds = 59;
        minutes--;
        if (minutes < 0) {
          // Timer finished
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
