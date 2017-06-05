#define sclk 13
#define mosi 11
#define cs   10
#define dc   9
#define rst  8  // y

#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library
#include <SPI.h>

Adafruit_ST7735 tft = Adafruit_ST7735(cs, dc, rst);

#if defined(__SAM3X8E__)
    #undef __FlashStringHelper::F(string_literal)
    #define F(string_literal) string_literal
#endif

float timestep = 1.f; // save a measuremnt for every timestep
unsigned long last_time = 0; // start time

int sensorPin = A7;
int count = 0; // to measure overall time and set array indices
int ofy = 140; // y-offset for values and scales
int scale=8; // scaling of pixels/volt
float values[128];

/*
void testdrawtext(String text, uint16_t color, uint16_t tsize) {
  tft.setCursor(0, 0);
  tft.setTextSize(tsize);
  tft.setTextColor(color, ST7735_BLACK); // second color is background, overwrite!
  tft.setTextWrap(true);
  tft.print(text);
}
*/

void setup(){
  tft.initR(INITR_REDTAB);
  tft.fillScreen(ST7735_BLACK);
  // creates the 0/10-lines and clears measurement area
  setup_measurements();
  Serial.begin(115200);
}

float getVoltage(){
  int sensorValue = analogRead(sensorPin);
  return sensorValue * (10.0 / 1023.);
  
}

void setup_measurements(){
  // create the bottom line and text  
  tft.setCursor(0, ofy+3);
  tft.setTextSize(1);
  tft.print("0 V, ");  
  tft.drawLine(0, ofy+1, tft.width()-1, ofy+1, ST7735_WHITE);
  
  // create top-line and text
  tft.setCursor(0, ofy-10*scale-1-10);
  tft.setTextSize(1);
  tft.print("10 V");
  tft.print(", t-step: ");
  tft.print(timestep);
  tft.print(" s");
  tft.drawLine(0, ofy-10*scale-1, tft.width()-1, ofy-10*scale-1, ST7735_WHITE);
}

void printVoltage(float volt, uint16_t color, uint16_t tsize){
  tft.setCursor(0, 0);
  tft.setTextSize(1);
  tft.setTextColor(color, ST7735_BLACK); // second color is background, overwrite!
  tft.setTextWrap(true);
  tft.println("Voltage: ");
  tft.println();
  
  tft.setTextSize(tsize);
  tft.println(volt);
}

void loop(){
  float volt = getVoltage();
  printVoltage(volt, ST7735_WHITE, 3);
  
  if (millis() - last_time >= timestep*1000){
    Serial.println(volt, 4);

    if (count >= tft.width()-1){
      // shift all array elements to the left, replace last value
      for(int k=0; k<127;k++){
        // paint all old pixels black instead of drawing complete lines
        tft.drawPixel(k, ofy-scale*values[k], ST7735_BLACK);
        values[k] = values[k+1];
        tft.drawPixel(k, ofy-scale*values[k], ST7735_GREEN);        
      }
      values[127] = getVoltage();
    }else{
      values[count] = getVoltage();
      tft.drawPixel(count, ofy-scale*values[count], ST7735_GREEN);        
    }
    count = count + 1;
    
    // draw elapsed time
    tft.setCursor(25, ofy+3);
    tft.setTextSize(1);
    tft.print(count*timestep);
    tft.print(" s");

    last_time = millis();    
  }
}
