#include <Stepper.h>
#include <LiquidCrystal.h>
#include <EtherCard.h>

#define motorSteps 48 
#define motorPin1 A1
#define motorPin2 A0
#define buzzerPin A2
#define onboardLedPin    6

Stepper myStepper(motorSteps, motorPin1,motorPin2); 
LiquidCrystal lcd(3, 4, 5, 19, 18, 17);

// ethernet bits
Stash stash;
static uint32_t timer;
byte Ethernet::buffer[700];

static byte mymac[] = {  0x74,0x69,0x69,0x2D,0x30,0x28 }; // live
char devicename[] = "feeder1";
char okHeader[] PROGMEM = 
    "HTTP/1.0 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Pragma: no-cache\r\n"
;
static BufferFiller bfill;

long feedCount = 0;
long hits = 0;
int readyCounter = 0;
int readyFlag = 0;

void setup() {
  
  lcd.begin(16, 2);
  Serial.begin(19200);
  Serial.println(" ");
  Serial.println("started");
  updateLcd("Starting up","");
  
  pinMode(buzzerPin,OUTPUT);
  digitalWrite(buzzerPin, LOW);
  
  pinMode(onboardLedPin,OUTPUT);
  digitalWrite(onboardLedPin,LOW);
  
  setupNetwork();
  
  updateLcd("Starting up","Resetting trap");
  myStepper.setSpeed(150);
  myStepper.step(-1000);
  
  updateLcd("Ready","");

}

void loop() {
  
  readyCounter++;
  if (readyCounter == 20000) {
    readyCounter = 0;
    switch (readyFlag)
    {
     case 0:
       updateLcd("Ready","");
       break;
     case 1:
       updateLcd("Ready.","");
       break;
     case 2:
       updateLcd("Ready..","");
       break;
     case 3:
       updateLcd("Ready...","");
       break; 
     case 4:
       updateLcd("Ready....","");
       break;
     case 5:
       updateLcd("Ready.....","");
       readyFlag = -1;
       break;
     }
    readyFlag++;
  }
  int feedReq = 0;
  word len = ether.packetReceive();
  word pos = ether.packetLoop(len);
  if (pos) {
    bfill = ether.tcpOffset();
    char* data = (char *) Ethernet::buffer + pos;
    hits++;
    if (strncmp("GET / ", data, 6) == 0) {
      Serial.println("hit /");
      homePage(bfill);

    } else if (strncmp("GET /feed", data, 6) == 0) {
      Serial.println("hit /feed");
      feedPage(bfill);
      feedReq = 1;
    } else {
      Serial.println("hit other");
      bfill.emit_p(PSTR(
        "HTTP/1.0 401 Unauthorized\r\n"
        "Content-Type: text/html\r\n"
        "\r\n"
        "<h1>401 Unauthorized</h1>"));
    }
    ether.httpServerReply(bfill.position());
  }
  if (feedReq == 1)
  {
    feedCount++;
    Serial.println(feedCount);
    doFeed();
    feedReq = 0;
  }
}

static void homePage(BufferFiller& buf) {
  buf.emit_p(PSTR("$F\r\n"
    "<title>Feeder</title>"
    "<p>$D hits<p>"
    ),okHeader,hits);
} 

static void feedPage(BufferFiller& buf) {

  buf.emit_p(PSTR("$F\r\n"
    "feeding"
    ),okHeader);    

}

void doFeed()
{
    
    updateLcd("Feeding","Sounding buzzer");

    for (int i = 0; i < 6; i++)
    {
      delay(500);
      digitalWrite(buzzerPin, HIGH);
      delay(250);
      digitalWrite(buzzerPin, LOW);
    }
    updateLcd("Feeding","Opening");

    myStepper.step(900);
    
    updateLcd("Feeding","Nudging");
    for (int nudge = 0; nudge < 2; nudge++)
    {
      myStepper.step(-200);
      myStepper.step(200);
    }
    delay(500);
    updateLcd("Feeding","Closing");

    myStepper.step(-900);
    
}

void setupNetwork()
{
  updateLcd("Starting up","Init network");
  if (ether.begin(sizeof Ethernet::buffer, mymac) == 0) 
  {
    Serial.println( "Failed to access Ethernet controller");
    updateLcd("Starting up","ENC28J60 failed");
  }
  // get IP
  if (!ether.dhcpSetup()) {
    Serial.println("DHCP failed");
    updateLcd("Starting up","DHCP failed");
  }
  updateLcd("Starting up","DHCP ok");
  ether.printIp("IP:  ", ether.myip);
  ether.printIp("GW:  ", ether.gwip);  
  ether.printIp("DNS: ", ether.dnsip);  

  delay(500);

}

void updateLcd(String line1, String line2)
{
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print(line1);
    lcd.setCursor(0,1);
    lcd.print(line2); 
}
