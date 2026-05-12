#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <Servo.h>
#include "DFRobot_VL53L0X.h"

#define STASSID "iPhone de Alex"
#define STAPSK  "holaholahola"

const char* apiURL = "http://ddns.asempere.net:8000/estado";
const char* DATA_API_URL = "http://ddns.asempere.net:8000/datos";

DFRobot_VL53L0X sensor_distancia;
Servo servo;
WiFiClient client;

void setup() {
  Wire.begin();

  sensor_distancia.begin(0x29);
  delay(150);
  sensor_distancia.setMode(sensor_distancia.eSingle,sensor_distancia.eLow);

  servo.attach(D8, 350, 2250);

  Serial.begin(9600);
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
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(client, apiURL);
    int httpCode = http.GET();

    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();

        StaticJsonDocument<200> doc;
        DeserializationError error = deserializeJson(doc, payload);

        if (!error) {
          int estado = doc["estado_a"];

          int angulo = 90;
          if (estado == 0) angulo = 0;   // Izquierda
          if (estado == 1) angulo = 90;  // Adelante
          if (estado == 2) angulo = 180; // Derecha

          servo.write(angulo);
          Serial.println("Estado recibido: " + String(estado) + " -> Moviendo a " + String(angulo) + " grados");
        } else {
          Serial.println("Error parseando el JSON");
        }
      }
    } else {
      Serial.println("Error en la conexión HTTP");
    }
    http.end();
  }

  // SENSOR:
  delay(150);
  sensor_distancia.start();
  delay(300);
  float distancia1 = sensor_distancia.getDistance();
  delay(150);
  sensor_distancia.stop();

  Serial.println(distancia1);

  Serial.println("");
  Serial.println("Enviando datos al servidor...");

  if (WiFi.status() == WL_CONNECTED) {
    // Send sensor data
    HTTPClient http_data;
    http_data.begin(client, DATA_API_URL);

    http_data.addHeader("Content-Type", "application/json");

    String jsonBody = "{";
    jsonBody += "\"dato1\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato2\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato3\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato4\":" + String(0.0, 2) + ",";
    jsonBody += "\"dato5\":" + String(distancia1) + ",";
    jsonBody += "\"dato6\":" + String(0.0, 2);
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

  delay(500);
}
