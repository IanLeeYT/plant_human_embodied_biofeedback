#include <SPI.h>
#include <Wire.h>

//define pressure regulator pins

const int press_reg1 = 3;
const int press_reg2 = 11;

int input_regval;

void setup() {
  Serial.begin(9600);
  Serial.println("Serial Begin");

  //define all pressure regulators as outputs
  pinMode(press_reg1, OUTPUT);
  pinMode(press_reg2, OUTPUT);
  
  //write all pressure regulator values to 0
  analogWrite(press_reg1, 0);
  analogWrite(press_reg2, 0);
}

void loop() {
  if (Serial.available() > 0){
    input_regval = Serial.read();
    if (input_regval > 0){
      Serial.println(input_regval);
      analogWrite(press_reg1, input_regval);
      analogWrite(press_reg2, input_regval);
    }
  }
  delay(50);
}
