#pragma once

#include <M5Cardputer.h>
#include <WiFi.h>
#include <SD.h>
#include <ArduinoJson.h>
#include <NimBLEDevice.h>
#include <esp_wifi.h>
#include <vector>

struct NetworkInfo {
  String ssid;
  String bssid;
  int rssi = 0;
  int channel = 0;
  String encryption;
  String password;
  bool pmf = false;
};

extern std::vector<NetworkInfo> gNetworks;
extern NetworkInfo gSelected;
extern uint8_t gDeauth[26];

void cpSetup();
void cpLoop();
void cpDrawMenu();
void cpScanWifi();
void cpDeauth();
void cpHandshake();
void cpCrack();
void cpBleMenu();
void cpPortal();
void cpExportJson();
void cpOtaHint();
