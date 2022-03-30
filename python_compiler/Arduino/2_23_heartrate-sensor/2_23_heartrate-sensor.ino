#include <SPI.h>
#include <Wire.h>

// heart rate variables
unsigned char counter;
unsigned long temp[21];
unsigned long sub;
bool data_effect=true;
unsigned int heart_rate;//the measurement result of heart rate

const int max_heartpluse_duty = 2000;//you can change it follow your system's request.
                        //2000 meams 2 seconds. System return error 
                        //if the duty overtrip 2 second.

const int press_reg1 = 3;
const int press_reg2 = 11;
const int press_reg3 = 9;
const int PotOnOffPin = 10;
float freq_factor = 1;

//change to floats if you want to round correctly
float regval1; 
float regval2; 
float regval3;

//arduino time operates in milliseconds
long start_time = millis();
long curr_time; 
long elapsedtime;
long time_delay = 4;

// parameters for oceanwave equation
const float C = 3; //Scale Factor for 8
const float pi = 3.141593;
const float bias=1.6184; //v=8

//  sigmoid frequency factor
float sig_factor;
    
void setup()
{
    Serial.begin(9600);
    arrayInit();
    attachInterrupt(0, interrupt, RISING);//set interrupt 0,digital port 2
    
    //define all pressure regulators as outputs
    pinMode(press_reg1, OUTPUT);
    pinMode(press_reg2, OUTPUT);
    //pinMode(press_reg3, OUTPUT);
    
    //write all pressure regulator values to 0
    analogWrite(press_reg1, 0);
    analogWrite(press_reg2, 0);
    //analogWrite(press_reg3, 0);
    delay(4000);
}

float sigmoid(int heart_rate) {
  return 0.5 / (1 + exp(8 + -0.1 * heart_rate)) + 0.5;
}

void loop()
{
    

    while( HIGH ){
    curr_time = millis();
    elapsedtime = .001*(curr_time - start_time); 
  

    //set up pressure regulator values
    //elapsed time is your runtime



//    if (heart_rate > 0) {
//      freq_factor = (heart_rate/80.0)*(heart_rate/80.0);
//    } else {
//      freq_factor = 1;
//    }

//     freq_factor = 0.7;
     freq_factor = 1.4;
    
    // oceanwave equation v=8
    regval1 = (255/20)*C*(.382*cos(2*pi*(elapsedtime-time_delay)*.14 * freq_factor)+.758*cos(2*pi*(elapsedtime-time_delay)*.2 * freq_factor)+.269*cos(2*pi*(elapsedtime-time_delay)*.24 * freq_factor)+.332*cos(2*pi*(elapsedtime-time_delay)*.28 * freq_factor)+.064*cos(2*pi*(elapsedtime-time_delay)*.48 * freq_factor)+bias);
    regval2 = (255/20)*C*(.382*cos(2*pi*(elapsedtime)*.14 * freq_factor)+.758*cos(2*pi*(elapsedtime)*.2 * freq_factor)+.269*cos(2*pi*(elapsedtime)*.24 * freq_factor)+.332*cos(2*pi*(elapsedtime)*.28 * freq_factor)+.064*cos(2*pi*(elapsedtime)*.48 * freq_factor)+bias);

    if (heart_rate != 0) {
      sig_factor = sigmoid(heart_rate);
    } else {
      sig_factor = 0.75;
    }
    
    regval1 = sig_factor * regval1;
    regval2 = sig_factor * regval2;
    
    //write values to pressure regulators (0-255)
    analogWrite(press_reg1, int(regval1));
    analogWrite(press_reg2, int(regval2));
    //analogWrite(press_reg3, int(regval3));
    Serial.print("Heart_rate_is:\t");
    Serial.println(heart_rate);
    Serial.println(regval1);
    delay(100);
  }
}

/*Function: calculate the heart rate*/
void sum()
{
 if (data_effect)
    {
      heart_rate=1200000/(temp[20]-temp[0]);//60*20*1000/20_total_time 
      Serial.print("Heart_rate_is:\t");
      Serial.println(heart_rate);
    }
   data_effect=1;//sign bit
}

/*Function: Interrupt service routine.Get the sigal from the external interrupt*/
void interrupt()
{
    temp[counter]=millis();
  //  Serial.println(counter,DEC);
 //   Serial.println(temp[counter]);
    switch(counter)
    {
        case 0:
            sub=temp[counter]-temp[20];
           // Serial.println(sub);
            break;
        default:
            sub=temp[counter]-temp[counter-1];
          //  Serial.println(sub);
            break;
    }
    if(sub>max_heartpluse_duty)//set 2 seconds as max heart pluse duty
    {
        data_effect=0;//sign bit
        counter=0;
      //  Serial.println("Heart rate measure error,test will restart!" );
        arrayInit();
    }
    if (counter==20&&data_effect)
    {
        counter=0;
        sum();
    }
    else if(counter!=20&&data_effect)
    counter++;
    else 
    {
        counter=0;
        data_effect=1;
    }

}
/*Function: Initialization for the array(temp)*/
void arrayInit()
{
    for(unsigned char i=0;i < 20;i ++)
    {
        temp[i]=0;
    }
    temp[20]=millis();
}
