void setup() {
  Serial.begin(115200); // use the same baud-rate as the python side
}
String str;
void loop() {
  while(Serial.available()>0){
    char c = Serial.read();
    if(c=='\n'){
      if(str == "\r"){
          str = "";
      }
      else{
        Serial.println("arduino received: " + str); // write a string
        //Serial.flush();
        str = "";
        //delay(1000);
      }
    }
    else{
      str = str + c;
    }
  }
  while(Serial.available()==0){}
  //Serial.flush();
}
