int led = D7;
int errorPin = D5;
int healthPin = D4;
int currentStateError = LOW;
int currentStateHealth = LOW;

void setup() {
    pinMode(led, OUTPUT);
    pinMode(errorPin, INPUT_PULLDOWN);
    pinMode(healthPin, INPUT_PULLDOWN);
}

void loop() {
    if (digitalRead(errorPin) != currentStateError)
    {
        if (digitalRead(errorPin) == HIGH)
        {
            Particle.publish("error", "error");
        } else {
            Particle.publish("clearerror", "clear");
        }
        currentStateError = digitalRead(errorPin);
    }
    if (digitalRead(healthPin) != currentStateHealth)
    {
        if (digitalRead(healthPin) == HIGH)
        {
            Particle.publish("healtherror", "error");
        } else {
            Particle.publish("clearhealtherror", "clear");
        }
        currentStateHealth = digitalRead(healthPin);
    }
    if (digitalRead(healthPin) == HIGH or digitalRead(errorPin) == HIGH)
    {
        digitalWrite(led, HIGH);
    }
    else
    {
        digitalWrite(led, LOW);
    }
}