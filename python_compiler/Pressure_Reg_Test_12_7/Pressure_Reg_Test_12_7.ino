#include <SPI.h>

#include <Wire.h>

//define pressure regulator pins
//don't need pot pin control

//when defining arduino pins use const int
const int press_reg1 = 3;
const int press_reg2 = 11;
//const int press_reg3 = 5;
const int PotOnOffPin = 10;

int j;
int PotOnOffVal=0;

void setup() {
  // put your setup code here, to run once:
  //Start the serial monitor, to debug
  Serial.begin(9600);
  Serial.println("You've started the serial monitor");

  //define all pressure regulators as outputs
  pinMode(press_reg1, OUTPUT);
  pinMode(press_reg2, OUTPUT);
  //pinMode(press_reg3, OUTPUT);
  
  //write all pressure regulator values to 0
  analogWrite(press_reg1, 0);
  analogWrite(press_reg2, 0);
  //analogWrite(press_reg3, 0);
 
  pinMode(PotOnOffPin, INPUT);
  PotOnOffVal= digitalRead (PotOnOffPin);
  PotOnOffVal= HIGH; //for testing w/o switch
}

void loop() {
  // put your main code here, to run repeatedly:

  //arduino time operates in milliseconds
  long start_time = millis();
  Serial.println(start_time);
  long curr_time; long elapsedtime;
  
  //change to floats if you want to round correctly
  float regval1; 
  float regval2; 
  float regval3;

  //change this to your operating condition (PotOnOffVal == HIGH)
  while( PotOnOffVal == HIGH ){
    curr_time = millis();
    elapsedtime = curr_time - start_time;
    
    //delay is in milliseconds (don't need this here)
    //delay(1000);

    //set up pressure regulator values
    //elapsed time is your runtime
    
    const float C = 2; //Scale Factor 
    const float pi = 3.141593;
    
    //insert actual math
    regval1 = (255/27)*C*(0.3980*cos(2*pi*elapsedtime*0.1-(pi/2))+0.3858*cos(2*pi*elapsedtime*0.18-(pi/2))+0.31*cos(2*pi*elapsedtime*0.24-(pi/2))+.1902*cos(2*pi*elapsedtime*0.3-(pi/2))+0.045*cos(2*pi*elapsedtime*0.54-(pi/2))+1.3291);
    //regval1 = (255/65)*C*(0.3980*cos(2*pi*elapsedtime*0.1)+0.3858*cos(2*pi*elapsedtime*0.18)+0.31*cos(2*pi*elapsedtime*0.24)+.1902*cos(2*pi*elapsedtime*0.3)+0.045*cos(2*pi*elapsedtime*0.54)+1.0622);
    regval2 = (255/27)*C*(0.3980*cos(2*pi*elapsedtime*0.1)+0.3858*cos(2*pi*elapsedtime*0.18)+0.31*cos(2*pi*elapsedtime*0.24)+.1902*cos(2*pi*elapsedtime*0.3)+0.045*cos(2*pi*elapsedtime*0.54)+1.0622);
    //regval3 = (255/25)*C*(0.3980*cos(2*pi*elapsedtime*0.1+(pi/2))+0.3858*cos(2*pi*elapsedtime*0.18+(pi/2))+0.31*cos(2*pi*elapsedtime*0.24+(pi/2))+.1902*cos(2*pi*elapsedtime*0.3+(pi/2))+0.045*cos(2*pi*elapsedtime*0.54+(pi/2))+1.0622);

    
    //write values to pressure regulators (0-255)
    analogWrite(press_reg1, int(regval1));
    analogWrite(press_reg2, int(regval2));
//    analogWrite(press_reg1, 12);
//    analogWrite(press_reg2, 12);
    //analogWrite(press_reg3, int(regval3));

    Serial.println(regval1);
    //delay for appropriate time per pressure regulators (e.g. for a servo 15ms, for some sensors 100+ms)
    //PotOnOffVal= digitalRead (PotOnOffPin);
    delay(1000);

  }
  while (PotOnOffVal == LOW) {
    digitalWrite ( press_reg1, LOW);
    digitalWrite ( press_reg2, LOW);
    //digitalWrite ( press_reg3, LOW);
    PotOnOffVal=digitalRead (PotOnOffPin);
    
  }

}
