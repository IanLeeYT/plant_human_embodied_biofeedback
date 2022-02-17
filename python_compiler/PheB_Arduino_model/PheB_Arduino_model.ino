#include <SPI.h>
#include <Wire.h>

//define pressure regulator pins
//don't need pot pin control

//when defining arduino pins use const int
const int press_reg1 = 3;
const int press_reg2 = 11;
const int press_reg3 = 9;

int prev_regval1 = 0;
int prev_regval2 = 0;
int input_regval;

void setup() {
  Serial.begin(9600);
  Serial.println("Serial Begin");

  //define all pressure regulators as outputs
  pinMode(press_reg1, OUTPUT);
  pinMode(press_reg2, OUTPUT);
  pinMode(press_reg3, OUTPUT);
  
  //write all pressure regulator values to 0
  analogWrite(press_reg1, 0);
  analogWrite(press_reg2, 0);
  analogWrite(press_reg3, 0);
}

void loop() {
  if (Serial.available() > 0){
//    input_regval = Serial.parseInt();
    input_regval = Serial.read();
    if (input_regval > 0){
      Serial.println(input_regval);
      analogWrite(press_reg1, input_regval);
      analogWrite(press_reg2, input_regval);
      prev_regval1 = input_regval;
      prev_regval2 = prev_regval1;
    }
  }
  delay(50);
}