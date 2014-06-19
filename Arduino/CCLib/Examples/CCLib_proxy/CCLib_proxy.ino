/*
 
 This example demonstrates the use of the CCDebugger class from CCLib.
 
 It provides a low-level passthrough proxy for driving the entire CC.Debugger 
 process from the computer.
 
 This version works with 2-wire DD configuration which is used for providing
 the required voltage division from 5V to 3.3V:
 
 For the DD Pin:
 
 <CC_DD_O> --[ 100k ]-- <CC_DD_I> --[ 200k ]-- <GND>
                            |
                           {DD}
 
 For the DC Pin:
 
 <CC_DC> --[ 100k ]-- {DC} --[ 200k ]-- <GND>
 
 For the RST Pin:
 
 <CC_DC> --[ 100k ]-- {RST} --[ 200k ]-- <GND>
 
 */
 
// Include the CCDebugger
#include <CCDebugger.h>

// Pinout configuration (Configured for Teensy 2.0++)
int LED      = 6;
int CC_RST   = 5;
int CC_DD_I  = 45;
int CC_DD_O  = 38;
int CC_DC    = 17;

// Command constants
#define   CMD_ENTER    byte(0x01)
#define   CMD_EXIT     byte(0x02)
#define   CMD_CHIP_ID  byte(0x03)
#define   CMD_STATUS   byte(0x04)
#define   CMD_PC       byte(0x05)
#define   CMD_STEP     byte(0x06)
#define   CMD_EXEC_1   byte(0x07)
#define   CMD_EXEC_2   byte(0x08)
#define   CMD_EXEC_3   byte(0x09)
#define   CMD_PING     byte(0xF0)
#define   ANS_OK       byte(0x01)
#define   ANS_ERROR    byte(0x02)

// Initialize properties
CCDebugger * dbg;
byte inByte;
byte c1, c2, c3;
char cAns;
unsigned short s1;

/**
 * Initialize debugger
 */
void setup() {
  
  // Create debugger
  dbg = new CCDebugger( CC_RST, CC_DC, CC_DD_I, CC_DD_O );
  dbg->setLED( LED, LED );
  
  // Initialize serial port
  Serial.begin(115200);
  
  // Wait for chip to initialize
  delay(100);
  
  // Enter debug mode
  dbg->enter();

}

/**
 * Check if debugger is in error state and if yes,
 * reply with an error code.
 */
boolean handleError( ) {
  if (dbg->error()) {
    Serial.write(ANS_ERROR);
    Serial.write(dbg->error());
    Serial.flush();
    return true;
  }
  return false;
}

/**
 * Main program loop
 */
void loop() {
  
  // Wait for incoming data frame
  if (Serial.available() < 4)
    return;
  
  // Read input frame
  inByte = Serial.read();
      c1 = Serial.read();
      c2 = Serial.read();
      c3 = Serial.read();  
  
  // Handle commands
  if (inByte == CMD_PING) {
    Serial.write(ANS_OK);
    
  } else if (inByte == CMD_ENTER) {
    cAns = dbg->enter();
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.flush();

  } else if (inByte == CMD_EXIT) {
    cAns = dbg->exit();
    if (handleError()) return;
    Serial.write(ANS_OK);
    
  } else if (inByte == CMD_CHIP_ID) {
    s1 = dbg->getChipID();
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write( (s1 >> 8) & 0xFF );
    Serial.write( s1 & 0xFF );
    
  } else if (inByte == CMD_PC) {
    s1 = dbg->getChipID();
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write( (s1 >> 8) & 0xFF );
    Serial.write( s1 & 0xFF );
    
  } else if (inByte == CMD_STATUS) {
    c1 = dbg->getChipID();
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write( c1 );

  } else if (inByte == CMD_STEP) {
    cAns = dbg->step();
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write(cAns);

  } else if (inByte == CMD_EXEC_1) {
    
    cAns = dbg->exec( c1 );
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write(cAns);

  } else if (inByte == CMD_EXEC_2) {
    
    cAns = dbg->exec( c1, c2 );
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write(cAns);

  } else if (inByte == CMD_EXEC_3) {    
    cAns = dbg->exec( c1, c2, c3 );
    if (handleError()) return;
    Serial.write(ANS_OK);
    Serial.write(cAns);
    
  } else {
    Serial.write(ANS_ERROR);
    Serial.write(0xFF);    
    
  }
  
  // Wait for data to be written
  Serial.flush();

}

