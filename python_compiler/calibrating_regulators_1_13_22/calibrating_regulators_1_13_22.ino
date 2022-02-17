#include <SPI.h>

#include <Wire.h>

//define pressure regulator pins
//don't need pot pin control

//when defining arduino pins use const int
const int press_reg1 = 3;
const int press_reg2 = 11;
const int press_reg3 = 9;
const int PotOnOffPin = 10;

int heart_rate = 100; //change heart rate here

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
  pinMode(press_reg3, OUTPUT);
  
  //write all pressure regulator values to 0
  analogWrite(press_reg1, 0);
  analogWrite(press_reg2, 0);
  analogWrite(press_reg3, 0);
 
  pinMode(PotOnOffPin, INPUT);
  PotOnOffVal= digitalRead (PotOnOffPin);
  PotOnOffVal= HIGH; //for testing w/o switch
}

void loop() {
  // put your main code here, to run repeatedly:

  //arduino time operates in milliseconds
  long start_time = millis();
  Serial.println(start_time);
  long curr_time; float elapsedtime;
  
  //change to floats if you want to round correctly
  float regval1; 
  float regval2; 
  float regval3;

  //change this to your operating condition (PotOnOffVal == HIGH)
  while( PotOnOffVal == HIGH ){
    curr_time = millis();
    elapsedtime = .001*(curr_time - start_time); 
    Serial.println(elapsedtime);

 
   
    
    const float C = 3; //Scale Factor for 8
    const float pi = 3.141593;
    const float bias=1.6184; //v=8
    
    //insert actual math
    
    //v=8
    regval1 = (255/25)*C*(.382*cos(2*pi*(elapsedtime-2)*.14)+.758*cos(2*pi*(elapsedtime-2)*.2)+.269*cos(2*pi*(elapsedtime-2)*.24)+.332*cos(2*pi*(elapsedtime-2)*.28)+.064*cos(2*pi*(elapsedtime-2)*.48)+bias);
    regval2 = (255/25)*C*(.382*cos(2*pi*(elapsedtime)*.14)+.758*cos(2*pi*(elapsedtime)*.2)+.269*cos(2*pi*(elapsedtime)*.24)+.332*cos(2*pi*(elapsedtime)*.28)+.064*cos(2*pi*(elapsedtime)*.48)+bias);
    if(heart_rate<=60){
      regval1 = 0.6*regval1;
      regval2 = 0.6*regval2;
      }
    else if(heart_rate<=80){
      regval1 = 0.7*regval1;
      regval2 = 0.7*regval2;
    }
    else if(heart_rate<=100){
      regval1 = 0.8*regval1;
      regval2 = 0.8*regval2;
    }
    
    //write values to pressure regulators (0-255)
    analogWrite(press_reg1, int(regval1));
    analogWrite(press_reg2, int(regval2));
    //analogWrite(press_reg3, int(regval3));

    Serial.println(regval1);
    //Serial.println(regval2);
    //Serial.println(regval3);
    //delay for appropriate time per pressure regulators (e.g. for a servo 15ms, for some sensors 100+ms)
   // PotOnOffVal= digitalRead (PotOnOffPin);
    delay(100);
    
  }

}
