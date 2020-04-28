#include <FastLED.h>
#include <stdlib.h>
#define LEDPin 9 //pin of RGB5*5
#define SwitchBtn 5 //pin of a button of switching
#define ConfirmBtn 4 //pin of button of confirming

CRGB leds[25];
CRGB CC[12]; //a color set of chessmen
CRGB CS[4]; //a color set of different states of chessmen
int pos[12]; //positions of 12 chessmen
int s2l[25] = {0,1,2,3,4, 9,8,7,6,5, 10,11,12,13,14, 19,18,17,16,15, 20,21,22,23,24};
//a mapping between s-order and linear order

int state; //state of the chess

void Wait4Start();
void CheckSerial();
void Wait4Opponent();
void Wait4Move();
void Win();
void Lose();
void Update();

void setup() {
  Serial.begin(115200); 
  FastLED.addLeds<NEOPIXEL, LEDPin>(leds, 25);
  FastLED.clear();
  FastLED.show();
  pinMode(SwitchBtn, INPUT);
  pinMode(ConfirmBtn, INPUT);
  
  CC[0] = CRGB(4,0,2);  CC[1] = CRGB(4,0,1);  CC[2] = CRGB(4,0,0);
  CC[3] = CRGB(4,1,0);  CC[4] = CRGB(4,2,0);  CC[5] = CRGB(4,3,0);  
  CC[6] = CRGB(2,0,4);  CC[7] = CRGB(1,0,4);  CC[8] = CRGB(0,0,4);  
  CC[9] = CRGB(0,1,4);  CC[10] = CRGB(0,2,4); CC[11] = CRGB(0,3,4);

  CS[0] = CRGB(0,0,0);  CS[1] = CRGB(3,3,3);  CS[2] = CRGB(0,4,0);  CS[3] = CRGB(1,4,0);

  state = 1;
}

void loop() {
  switch(state){
    case 0: state=1; break;
    case 1: CheckSerial(); break;
    case 2: Wait4Move(); break;
    case 3: Wait4Opponent(); break;
    case 4: Win(); break;
    case 5: Lose(); break;
    default: state=0; break;
  }
  delay(10);
}

void Wait4Start()
{
  int count1 = 0;
  int count2 = 0;
  int interval1 = 5;
  int interval2 = 50;
  int lightState = 0;
  
  while(true){
    //thread 1: check confirm button
    if(count1 < interval1)
      count1++;
    else{
      if(digitalRead(ConfirmBtn)){
        delay(10);
        if(digitalRead(ConfirmBtn)){
          while(digitalRead(ConfirmBtn));
          state = 1;
//          Serial.println("start,");
          return;
        }
      }
      count1 = 0;
    }
    //thread 2: display
    if(count2 < interval2)
      count2++;
    else{
      FastLED.clear();
      lightState = 1 - lightState;
      if(lightState)
        leds[12] = CRGB(0,0,4);
      FastLED.show();
      count2 = 0;
    }
    delay(10);
  }
}

void CheckSerial()
{
  if(Serial.available() > 0){
    int h = 0; //hashcode of the instruction
    char c;
    while(true){
      c = Serial.read();
      if(c == '\n'){
        state = 0;
        break;
      }
      if(c != ',')
        h += c;
      else{
        switch(h){
          case 643: Update(); break;
          case 439: state = 2; break; //move
          case 437: state = 3; Serial.read(); break; //wait
          case 334: state = 4; Serial.read(); break; //win
          case 435: state = 5; Serial.read(); break; //lose
          case 536: state = 0; Serial.read(); break; //abort
          default:  state = 0; Serial.println("abort,"); break;
        }
        break;
      }
    }
  }
}

void Wait4Opponent()
{
  int count1 = 0;
  int count2 = 0;
  int interval1 = 1;
  int interval2 = 50;
  int lightState = 0;
  
  while(true){
    //thread 1: check serial
    if(count1 < interval1)
      count1++;
    else{
      if(Serial.available() > 0){
        state = 1;
        return;
      }
      count1 = 0;
    }
    //thread 2: display
    if(count2 < interval2)
      count2++;
    else{
      FastLED.clear();
      lightState = 1 - lightState;
      if(lightState)
        leds[12] = CRGB(0,4,0);
      FastLED.show();
      count2 = 0;
    }
    delay(10);
  }
}

void Wait4Move()
{
  String s = "";
  char c;
  while((c = Serial.read()) != ',')
    s = s + c;
  int tar = s.toInt(); //target chessman
  int p_des[3]; //positions of destinations
  int n_des; //number of destinations
  
  if(tar < 6){ //red side
    if(pos[tar]%5 == 4){
      n_des = 1;
      p_des[0] = pos[tar] + 5;
    }
    else if(pos[tar] >= 20){
      n_des = 1;
      p_des[0] = pos[tar] + 1;
    }
    else{
      n_des = 3;
      p_des[0] = pos[tar] + 1;
      p_des[1] = pos[tar] + 6;
      p_des[2] = pos[tar] + 5;
    }
  }
  else{ //blue side
    if(pos[tar]%5 == 0){
      n_des = 1;
      p_des[0] = pos[tar] - 5;
    }
    else if(pos[tar] <= 4){
      n_des = 1;
      p_des[0] = pos[tar] - 1;
    }
    else{
      n_des = 3;
      p_des[0] = pos[tar] - 1;
      p_des[1] = pos[tar] - 6;
      p_des[2] = pos[tar] - 5;
    }
  }

  int choi = 0; //choice of destination
  CRGB CO[3]; //orignal colors of destinations
  for(int i=0; i<n_des; i++)
    CO[i] = leds[s2l[p_des[i]]];
    
  leds[s2l[pos[tar]]] = CS[2]; //change the color of target to green
  FastLED.show();
   
  int count1 = 0;
  int count2 = 0;
  int count3 = 0;
  int interval1 = 5;
  int interval2 = 5;
  int interval3 = 50;
  int lightState = 0;
  while(true){
    //thread 1: check confirm button
    if(count1 < interval1)
      count1++;
    else{
      if(digitalRead(ConfirmBtn)){
        delay(10);
        if(digitalRead(ConfirmBtn)){
          while(digitalRead(ConfirmBtn));
          Serial.print("move,");
          Serial.print(tar);  Serial.print(",");
          Serial.print(p_des[choi]);  Serial.println(",");
          for(int i=0; i<n_des; i++)
            leds[s2l[p_des[i]]] = CO[i];
          FastLED.show();
          state = 1;
          return;
        }
      }
      count1 = 0;
    }
    //check switch button
    if(count2 < interval2)
      count2++;
    else{
      if(digitalRead(SwitchBtn)){
        delay(10);
        if(digitalRead(SwitchBtn)){
          while(digitalRead(SwitchBtn));
          choi = (choi + 1) % n_des;
        }
      }
      count2 = 0;
    }

    if(count3 < interval3)
      count3++;
    else{
      lightState = 1 - lightState;
      if(lightState){
        for(int i=0; i<n_des; i++)
          leds[s2l[p_des[i]]] = CS[1];
        leds[s2l[p_des[choi]]] = CS[3];
      }
      else{
        for(int i=0; i<n_des; i++)
          leds[s2l[p_des[i]]] = CO[i];
        leds[s2l[p_des[choi]]] = CS[3];
      }
      FastLED.show();
      count3 = 0;
    }
    delay(10);
  }
}

void Win()
{
  int count1 = 0;
  int count2 = 0;
  int interval1 = 5;
  int interval2 = 50;
  int lightState = 0;
  
  while(true){
    if(count1 < interval1)
      count1++;
    else{
      if(digitalRead(ConfirmBtn)){
        delay(10);
        if(digitalRead(ConfirmBtn)){
          while(digitalRead(ConfirmBtn));
          state = 0;
          return;
        }
      }
      count1 = 0;
    }
    
    if(count2 < interval2)
      count2++;
    else{
      FastLED.clear();
      lightState = 1 - lightState;
      if(lightState)
        leds[12] = CRGB(4,4,4);
      FastLED.show();
      count2 = 0;
    }
    delay(10);
  }
}

void Lose()
{
  int count1 = 0;
  int count2 = 0;
  int interval1 = 5;
  int interval2 = 50;
  int lightState = 0;
  
  while(true){
    if(count1 < interval1)
      count1++;
    else{
      if(digitalRead(ConfirmBtn)){
        delay(10);
        if(digitalRead(ConfirmBtn)){
          while(digitalRead(ConfirmBtn));
          state = 0;
          return;
        }
      }
      count1 = 0;
    }
    
    if(count2 < interval2)
      count2++;
    else{
      FastLED.clear();
      lightState = 1 - lightState;
      if(lightState)
        leds[12] = CRGB(4,0,0);
      FastLED.show();
      count2 = 0;
    }
    delay(10);
  }
}

void Update()
{
  FastLED.clear();
  String s = "";
  char c;
  int i = 0;
  while(i<12){
    c = Serial.read();
    if(c == ','){
      pos[i] = s.toInt();
      if(pos[i] >= 0)
        leds[s2l[pos[i]]] = CC[i];
      i++;
      s = "";
    }
    else
      s = s + c;
  }
  Serial.read();
  FastLED.show();
}
