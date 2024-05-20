#include <M5Core2.h>
#include <WiFi.h>
#include <PubSubClient.h>

//
//#define TRIG_PIN G33
//#define ECHO_PIN G32

// Define UART parameters
#define RX_PIN 16
#define TX_PIN 17
#define BAUD_RATE 115200

WiFiClient espClient;
PubSubClient client(espClient);

const char* ssid = "infrastructure";
const char* password = "BjFBkWCwqYuH";
const char* mqtt_server = "csse4011-iot.zones.eait.uq.edu.au";
const char* button_topic = "JupiterBlueButton";
const char* gesture_topic = "JupiterBlueGestureShow"; // add topic in 2nd file !!!


unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

void setupWifi();
void callback(char* topic, byte* payload, unsigned int length);
void reConnect();
void drawArrowDown();
void drawArrowUp();
void drawArrowLeft();
void drawArrowRight();

void setup() {
  M5.begin();
//    pinMode(TRIG_PIN, OUTPUT);
//    pinMode(ECHO_PIN, INPUT);
  setupWifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  char* msg = "Hello";
  client.publish(button_topic, msg);

  // Initialize UART communication on Serial2
  Serial2.begin(BAUD_RATE, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {
    if (!client.connected()) {
        reConnect();
    }
    client.loop();
    
    // delay(2000);
    // drawArrowUp();
    // delay(2000);
    // drawArrowLeft();
    // delay(2000);
    // drawArrowDown();
    // delay(2000);
    // drawArrowRight();
    // delay(2000);

//    M5.Lcd.printf("\nSent\n");

    // delay(1000);
}

void drawArrowDown() {
    M5.Lcd.clear();
    M5.Lcd.setBrightness(200);
    M5.Lcd.fillScreen(0xffff);
    M5.Lcd.setRotation(1);
    //straight down line
    for (int i = 160; i < 164; i++) {
      M5.Lcd.drawLine(i , 32, i, 200, 0xe8e4);
    }
    for (int x = 98; x < 103; x++) {
      M5.Lcd.drawLine(x , 125, x + 62, 200, 0xe8e4);
    }
    for (int x = 222; x < 227; x++) {
      M5.Lcd.drawLine(x , 125, x - 62, 200, 0xe8e4);
    }
}

void drawArrowUp() {
    M5.Lcd.clear();
    M5.Lcd.setBrightness(200);
    M5.Lcd.fillScreen(0xffff);
    M5.Lcd.setRotation(3);
    //straight down line
    for (int i = 160; i < 164; i++) {
      M5.Lcd.drawLine(i , 32, i, 200, 0xe8e4);
    }
    for (int x = 98; x < 103; x++) {
      M5.Lcd.drawLine(x , 125, x + 62, 200, 0xe8e4);
    }
    for (int x = 222; x < 227; x++) {
      M5.Lcd.drawLine(x , 125, x - 62, 200, 0xe8e4);
    }
}

void drawArrowLeft() {
    M5.Lcd.clear();
    M5.Lcd.setBrightness(200);
    M5.Lcd.fillScreen(0xffff);
    M5.Lcd.setRotation(1);
    for (int i = 115; i < 119; i++) {
      M5.Lcd.drawLine(90 , i, 258, i, 0xe8e4);
    }
    for (int y = 53; y < 58; y++) {
      M5.Lcd.drawLine(165 , y, 90, y + 62, 0xe8e4);
    }
    for (int y = 177; y < 183; y++) {
      M5.Lcd.drawLine(165 , y, 90, y - 62, 0xe8e4);
    }
}

void drawArrowRight() {
    M5.Lcd.clear();
    M5.Lcd.setBrightness(200);
    M5.Lcd.fillScreen(0xffff);
    M5.Lcd.setRotation(3);
    for (int i = 115; i < 119; i++) {
      M5.Lcd.drawLine(90 , i, 258, i, 0xe8e4);
    }
    for (int y = 53; y < 58; y++) {
      M5.Lcd.drawLine(165 , y, 90, y + 62, 0xe8e4);
    }
    for (int y = 177; y < 183; y++) {
      M5.Lcd.drawLine(165 , y, 90, y - 62, 0xe8e4);
    }
}

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

void callback(char* topic, byte* payload, unsigned int length) {
    char msg[10];
    memset(msg, 0, 10);
    // M5.Lcd.print("Message arrived ["); 
    // M5.Lcd.print(topic);
    // M5.Lcd.print("] ");
    for (int i = 0; i < length; i++) {
//        M5.Lcd.print((char)payload[i]);
        msg[i] = (char)payload[i];
    }
    if (!strcmp(topic, gesture_topic)) {
      if (memcmp(msg, "UP", 2) == 0) {
        drawArrowUp();
        char* msg = "UpDone";
        client.publish(button_topic, msg);
      } else if (memcmp(msg, "DOWN", 4) == 0) {
        drawArrowDown();
        char* msg = "DownDone";
        client.publish(button_topic, msg);
      } else if (memcmp(msg, "LEFT", 4) == 0) {
        drawArrowLeft();
        char* msg = "LeftDone";
        client.publish(button_topic, msg);
      } else if (memcmp(msg, "RIGHT", 5) == 0) {
        drawArrowRight();
        char* msg = "RightDone";
        client.publish(button_topic, msg);
      } 
      //m5.Lcd.print(msg);
      // strcmp() -> with "hi"
  //    if (msg == "hi") {
  //      M5.Lcd.printf("\nLets Go!\n");
  //    }
      M5.Lcd.println();
    } else if (!strcmp(topic, button_topic)) {
      const char *message = "A";
  
      // Send data through UART
      Serial2.println(message);
    }
}

void reConnect() {
    while (!client.connected()) {
        M5.Lcd.print("Attempting MQTT connection...");
        String clientId = "M5Stack-";
        clientId += String(random(0xffff), HEX);
        if (client.connect(clientId.c_str())) {
            M5.Lcd.printf("\nSuccess\n");
            // client.publish(button_topic, "hello world");
            client.subscribe(gesture_topic);
            client.subscribe(button_topic);
        } else {
            M5.Lcd.print("failed, rc=");
            M5.Lcd.print(client.state());
            M5.Lcd.println("try again in 5 seconds");
            delay(5000);
        }
    }
}
