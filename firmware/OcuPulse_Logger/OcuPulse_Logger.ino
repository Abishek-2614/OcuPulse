/*
  OcuPulse ESP32 sensor event logger
  - VL53L1X ToF: Pololu VL53L1X Arduino library
  - MAX30102: SparkFun MAX3010x Sensor Library
  - Optional OLED: Adafruit SSD1306 + Adafruit GFX

  Emits separate timestamped events, not synchronized sample pairs:
    event,timestamp_us,value,valid
    TOF,<micros>,<distance_mm>,<0_or_1>
    PPG,<micros>,<raw_IR_count>,<0_or_1>

  This is experimental data-acquisition firmware. It does not estimate IOP.
  Compile and bench-test against the exact installed library/board versions.
*/
#include <Wire.h>
#include <VL53L1X.h>
#include "MAX30105.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

static const int I2C_SDA = 21;
static const int I2C_SCL = 22;
static const uint32_t SERIAL_BAUD = 115200;
static const uint32_t TOF_PERIOD_MS = 20;
static const uint32_t TOF_BUDGET_US = 20000;
static const uint32_t OLED_REFRESH_MS = 1000;

VL53L1X tof;
MAX30105 ppg;
Adafruit_SSD1306 display(128, 64, &Wire, -1);

bool tofOk = false;
bool ppgOk = false;
bool oledOk = false;
uint16_t lastDistanceMm = 0;
uint32_t lastIr = 0;
uint32_t lastOledMs = 0;
uint32_t tofEvents = 0;
uint32_t ppgEvents = 0;

void emitEvent(const char *eventName, uint32_t timestampUs, uint32_t value, bool valid) {
  Serial.print(eventName);
  Serial.print(',');
  Serial.print(timestampUs);
  Serial.print(',');
  Serial.print(value);
  Serial.print(',');
  Serial.println(valid ? 1 : 0);
}

void refreshDisplay() {
  if (!oledOk) return;
  const uint32_t now = millis();
  if (now - lastOledMs < OLED_REFRESH_MS) return;
  lastOledMs = now;

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("OcuPulse - Research"));
  display.print(F("ToF: "));
  display.println(tofOk ? F("OK") : F("ERROR"));
  display.print(F("PPG: "));
  display.println(ppgOk ? F("OK") : F("ERROR"));
  display.print(F("Distance: "));
  if (tofOk && lastDistanceMm > 0) {
    display.print(lastDistanceMm);
    display.println(F(" mm"));
  } else {
    display.println(F("--"));
  }
  display.print(F("IR count: "));
  display.println(ppgOk ? lastIr : 0);
  display.println(F("No clinical IOP output"));
  display.display();
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(250);
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);

  Serial.println(F("# OcuPulse experimental sensor logger"));
  Serial.println(F("# Separate ToF and PPG events; timestamps must be aligned offline"));

  tof.setTimeout(500);
  tof.setBus(&Wire);
  tofOk = tof.init();
  if (tofOk) {
    tof.setDistanceMode(VL53L1X::Short);
    const bool budgetOk = tof.setMeasurementTimingBudget(TOF_BUDGET_US);
    if (!budgetOk) {
      Serial.println(F("# Warning: ToF timing budget configuration was rejected"));
    }
    tof.startContinuous(TOF_PERIOD_MS);
  } else {
    Serial.println(F("# ERROR: VL53L1X initialization failed"));
  }

  ppgOk = ppg.begin(Wire, I2C_SPEED_FAST);
  if (ppgOk) {
    // IR + red mode, averaging 1, nominal sensor sample rate 100 Hz.
    // Effective cadence must be verified from timestamps on the actual board.
    ppg.setup(0x1F, 1, 2, 100, 411, 4096);
  } else {
    Serial.println(F("# ERROR: MAX30102 initialization failed"));
  }

  oledOk = display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  if (!oledOk) Serial.println(F("# OLED not found; continuing without display"));

  Serial.println(F("# Firmware ready; comments start with #"));
  Serial.println(F("event,timestamp_us,value,valid"));
}

void loop() {
  if (ppgOk) {
    ppg.check();
    while (ppg.available()) {
      const uint32_t ir = ppg.getFIFOIR();
      const uint32_t stamp = micros();
      lastIr = ir;
      const bool valid = (ir > 0);
      emitEvent("PPG", stamp, ir, valid);
      ppgEvents++;
      ppg.nextSample();
    }
  }

  if (tofOk && tof.dataReady()) {
    const uint16_t distanceMm = tof.read(false);
    const uint32_t stamp = micros();
    lastDistanceMm = distanceMm;
    const bool timedOut = tof.timeoutOccurred();
    const bool valid = (!timedOut && distanceMm > 0 && distanceMm < 4000);
    emitEvent("TOF", stamp, distanceMm, valid);
    tofEvents++;
  }

  refreshDisplay();
}
