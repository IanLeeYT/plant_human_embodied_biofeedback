 // Function: This program can be used to measure heart rate, the lowest pulse in the program be set to 30.
    //         Use an external interrupt to measure it.
    // Hardware: Grove - Ear-clip Heart Rate Sensor, Grove - Base Shield, Grove - LED
    // Arduino IDE: Arduino-1.0
    // Author: FrankieChu       
    // Date: Jan 22, 2013
    // Version: v1.0
    // by www.seeedstudio.com
    #define LED 4//indicator, Grove - LED is connected with D4 of Arduino
    boolean led_state = LOW;//state of LED, each time an external interrupt 
                                    //will change the state of LED
    unsigned char counter;
    unsigned long temp[21];
    unsigned long sub;
    bool data_effect=true;
    unsigned int heart_rate;//the measurement result of heart rate
 
    const int max_heartpluse_duty = 2000;//you can change it follow your system's request.
                            //2000 meams 2 seconds. System return error 
                            //if the duty overtrip 2 second.
    #include <SPI.h>

    #include <Wire.h>

    //define pressure regulator pins
    //don't need pot pin control

    //when defining arduino pins use const int
    const int press_reg1 = 3;
    const int press_reg2 = 11;
    const int press_reg3 = 9;
    const int PotOnOffPin = 10;

    int j;
    int PotOnOffVal=0;

    void setup()
    {
        pinMode(LED, OUTPUT);
        Serial.begin(9600);
        Serial.println("Please ready your chest belt.");
        delay(5000);
        arrayInit();
        Serial.println("Heart rate test begin.");
        attachInterrupt(0, interrupt, RISING);//set interrupt 0,digital port 2
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
        PotOnOffVal= HIGH;
    }
    
    void loop()
    {
        digitalWrite(LED, led_state);//Update the state of the indicator
        Serial.print("Heart_rate_is:\t");
        Serial.println(heart_rate);
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
          elapsedtime = .001*(curr_time - start_time); 
        
          
          //delay is in milliseconds (don't need this here)
          
          //set up pressure regulator values
          //elapsed time is your runtime
      
          
          const float C = 3; //Scale Factor for 8
          const float pi = 3.141593;
          const float bias=1.6184; //v=8
          
          //insert actual math
          
          //v=8
          regval1 = (255/65)*C*(.382*cos(2*pi*(elapsedtime-2)*.14)+.758*cos(2*pi*(elapsedtime-2)*.2)+.269*cos(2*pi*(elapsedtime-2)*.24)+.332*cos(2*pi*(elapsedtime-2)*.28)+.064*cos(2*pi*(elapsedtime-2)*.48)+bias);
          regval2 = (255/65)*C*(.382*cos(2*pi*(elapsedtime)*.14)+.758*cos(2*pi*(elapsedtime)*.2)+.269*cos(2*pi*(elapsedtime)*.24)+.332*cos(2*pi*(elapsedtime)*.28)+.064*cos(2*pi*(elapsedtime)*.48)+bias);

          if(heart_rate<=60){
            regval1 = 0.5*regval1;
            regval2 = 0.5*regval2;
          }
          else if(heart_rate<=80){
            regval1 = 0.7*regval1;
            regval2 = 0.7*regval2;
          }
          else if(heart_rate<=100){
            regval1 = 0.7*regval1;
            regval2 = 0.7*regval2;
          }
          
          //write values to pressure regulators (0-255)
          analogWrite(press_reg1, int(regval1));
          analogWrite(press_reg2, int(regval2));
          //analogWrite(press_reg3, int(regval3));
      
          Serial.println(regval1);
          //Serial.println(regval2);
          //Serial.println(regval3);
          //delay for appropriate time per pressure regulators (e.g. for a servo 15ms, for some sensors 100+ms)
          //PotOnOffVal= digitalRead (PotOnOffPin);
          delay(1000);
      
        }
        while (PotOnOffVal == LOW) {
          digitalWrite ( press_reg1, LOW);
          digitalWrite ( press_reg2, LOW);
          digitalWrite ( press_reg3, LOW);
          PotOnOffVal=digitalRead (PotOnOffPin);
          
        }
    }
    /*Function: calculate the heart rate*/
    void sum()
    {
     if(data_effect)
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
        Serial.println(counter,DEC);
        Serial.println(temp[counter]);
        switch(counter)
        {
            case 0:
                sub=temp[counter]-temp[20];
                Serial.println(sub);
                break;
            default:
                sub=temp[counter]-temp[counter-1];
                Serial.println(sub);
                break;
        }
        if(sub>max_heartpluse_duty)//set 2 seconds as max heart pluse duty
        {
            data_effect=0;//sign bit
            counter=0;
            Serial.println("Heart rate measure error,test will restart!" );
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
