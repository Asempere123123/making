#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "Arduino.h"
#include "Wire.h"
#include "DFRobot_VL53L0X.h"
#include "DFRobot_VEML7700.h"
#include <Adafruit_Sensor.h>

#define STASSID "iPhone de Alex"
#define STAPSK  "holaholahola"

const char* DATA_API_URL = "http://ddns.asempere.net:8000/datos";

DFRobot_VL53L0X sensor_distancia;
DFRobot_VEML7700 sensor_luz;

WiFiClient client;

float leerDistanciaEstable() {
  float suma = 0;
  int lecturasValidas = 0;

  sensor_distancia.start();
  delay(50);

  for (int i = 0; i < 7; i++) {
    float d = sensor_distancia.getDistance();

    if (d > 0.0 && d < 2500.0) {
      suma += d;
      lecturasValidas++;
    }
    delay(40);
  }
  sensor_distancia.stop();

  if (lecturasValidas > 0) {
    return suma / lecturasValidas;
  } else {
    return 8190.0;
  }
}

void setup() {
  Wire.begin();

  sensor_distancia.begin(0x29);
  delay(150);
  sensor_distancia.setMode(sensor_distancia.eSingle, sensor_distancia.eHigh);

  delay(150);
  sensor_luz.begin();
  sensor_luz.setGain(sensor_luz.ALS_GAIN_d4);
  sensor_luz.setIntegrationTime(sensor_luz.ALS_INTEGRATION_100ms);

  Serial.begin(9600);
  delay(100);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(STASSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  float luz;
  sensor_luz.getALSLux(luz);

  float distancia1 = leerDistanciaEstable();

  Serial.print("Luz: ");
  Serial.print(luz);
  Serial.print(" | Distancia calculada: ");
  Serial.println(distancia1);

  Serial.println("");
  Serial.println("Enviando datos al servidor...");

  if (WiFi.status() == WL_CONNECTED) {
    // Send sensor data
    HTTPClient http_data;
    http_data.begin(client, DATA_API_URL);

    http_data.addHeader("Content-Type", "application/json");

    String jsonBody = "{";
    jsonBody += "\"dato1\":" + String(luz, 2) + ",";
    jsonBody += "\"dato2\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato3\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato4\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato5\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato6\":" + String(distancia1);
    jsonBody += "}";

    int httpCode_data = http_data.POST(jsonBody);

    if (httpCode_data > 0) {
      Serial.println("Datos de sensores actualizados. Código HTTP: " + String(httpCode_data));
    } else {
      Serial.println("Error enviando datos: " + http_data.errorToString(httpCode_data));
    }

    http_data.end();
  } else {
    Serial.println("Error: WiFi desconectado");
  }

  delay(400);
}
