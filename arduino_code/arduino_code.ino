#define MOTORA_A 10
#define MOTORA_B 9

void setup() {
  pinMode(MOTORA_A, OUTPUT);
  pinMode(MOTORA_B, OUTPUT);
  Serial.begin(9600);
}
int soil_moisture = analogRead(A0);
int light = analogRead(A1);
int data_1,data_2;
void loop() {
  data_1 = soil_moisture;
  data_2 = light;
  Serial.print(data_1);
  Serial.print(",");
  Serial.println(data_2);
  if (data_1<450) {
    digitalWrite(MOTORA_A,HIGH);
    digitalWrite(MOTORA_B,LOW);
    delay(1700);
    digitalWrite(MOTORA_A,LOW);
  }
  delay(1000);
}
