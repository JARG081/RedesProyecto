/* Seccion de librerias*/
#include <MFRC522v2.h>
#include <MFRC522DriverSPI.h>
#include <MFRC522DriverPinSimple.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
/* Seccion de librerias*/

/* Seccion de asignacion*/
MFRC522DriverPinSimple ss_pin(15);
MFRC522DriverSPI driver{ss_pin}; // Create SPI driver
MFRC522 mfrc522{driver};         // Create MFRC522 instance

const char* ssid = "Galaxy A53 5GB1BC"; // Nombre del wifi al que se conectaran
const char* password = "aaaa3333"; // Clave del wifi al que se conectaran

#define LECTOR_ID "NombreSalaID" //Pueden crear varios RFID de ser necesario
/* Seccion de asignacion*/

/* Seccion de setup general*/
void setup() {
  Serial.begin(115200);
  while (!Serial);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado al WiFi!");
  
  mfrc522.PCD_Init();
  Serial.println("Lector RFID listo!");
}
/* Seccion de setup general*/

/* Seccion de codigo general*/
void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  //Obtener UID de la tarjeta RFID
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  Serial.println("Nueva tarjeta detectada:");
  Serial.println(uid);

  // Proceso de envio al Backend
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, "http://192.168.113.57:5000/registro"); //Aqui debe ir la direccion maquina que hostea el backend
                      // Si estan en la misma red, la local (IPv4)

    http.addHeader("Content-Type", "application/json");

    String payload = "{\"lector_id\":\"" + String(LECTOR_ID) + "\",\"uid\":\"" + uid + "\"}";
    int httpResponseCode = http.POST(payload);

    // Respuesta del servidor opcional
    if (httpResponseCode > 0) {
        Serial.println("Respuesta del servidor: " + String(httpResponseCode));
        String response = http.getString(); 
        Serial.println("Respuesta recibida: " + response);
    } else {
        Serial.println("Error en la solicitud HTTP: " + String(httpResponseCode));
    }

    http.end(); // Finaliza la conexión HTTP
  }

  // Detener la lectura de la tarjeta actual
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  delay(2000); // Retardo para evitar lecturas rapidas
}
/* Seccion de codigo general*/