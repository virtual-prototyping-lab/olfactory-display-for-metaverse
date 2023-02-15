#define CHANNEL_COUNT 3

// #define TURNOFF

int channelPins[CHANNEL_COUNT] = {2, 3, 4};
const unsigned long intensityStep = 50; // [ms]
#ifdef TURNOFF
const unsigned long turnOnPeriod = 3000; // [ms]
#endif

int nextIntensity = 10;
int stepIndex = 0;
int channelIntensity[CHANNEL_COUNT];
unsigned long nextStepTime;
#ifdef TURNOFF
unsigned long turnOffTime[CHANNEL_COUNT];
#endif

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < CHANNEL_COUNT; i++) {
    pinMode(channelPins[i], OUTPUT);
    channelIntensity[i] = 0;
#ifdef TURNOFF
    turnOffTime[i] = 0;
#endif
  }

  Serial.print("\nSend a digit between 1 and ");
  Serial.print(CHANNEL_COUNT);
  Serial.print(" (inclusive) to turn this channel on");
#ifdef TURNOFF
  Serial.print(" for ");
  Serial.print((float)turnOnPeriod / 1000.0);
  Serial.print(" seconds.");
#endif
  Serial.println(
      "\nSend 0 to turn of all channels immediately.\n"
      "Send a letter between A and J to set intensity for turned on channels.\n"
      "'A' to emit with 10% duty cycle, 'J' for 100% (the default)\n");

  nextStepTime = millis() + intensityStep;
}

void loop() {
  if (Serial.available()) {
    char command == Serial.read();
    if (command = '0') {
      for (int i = 0; i < CHANNEL_COUNT; i++) {
        channelIntensity[i] = 0;
      }
      Serial.println("Turned off all channels");
    } else if (command >= '0' && command <= '9') {
      int channel = command - '1';
      if (channel < CHANNEL_COUNT) {
        channelIntensity[channel] = nextIntensity;
#ifdef TURNOFF
        turnOffTime[channel] = millis() + turnOnPeriod;
#endif
        Serial.print("Turned on channel ");
        Serial.print(command);
        Serial.print(" with ");
        Serial.print(nextIntensity);
        Serial.println("0% duty cycle");
      } else {
        Serial.print("Only ");
        Serial.print(CHANNEL_COUNT);
        Serial.println(" channels configured");
      }
    } else if ((command >= 'A' && command <= 'J') ||
               (command >= 'a' && command <= 'j')) {
      nextIntensity =
          command <= 'J' ? (command - 'A' + 1) : (command - 'a' + 1);
      Serial.print("Set ");
      Serial.print(nextIntensity);
      Serial.println("0% duty cycle");
    } else if (command != '\n' && command != '\r') {
      Serial.print("Unrecognised command: ");
      Serial.println(command);
    }
  }

#ifdef TURNOFF
  for (int i = 0; i < CHANNEL_COUNT; i++) {
    if (turnOffTime[i] < millis() && channelIntensity[i] > 0) {
      channelIntensity[i] = 0;
      Serial.print("Timed out channel ");
      Serial.print(i + 1);
      Serial.println();
    }
  }
#endif

  if (millis() >= nextStepTime) {
    for (int i = 0; i < CHANNEL_COUNT; i++) {
      if (stepIndex == 0 && channelIntensity[i] > 0) {
        digitalWrite(channelPins[i], HIGH);
      } else if (channelIntensity[i] == stepIndex) {
        digitalWrite(channelPins[i], LOW);
      }
    }

    stepIndex = (stepIndex + 1) % 10;
    nextStepTime += intensityStep;
  }
}