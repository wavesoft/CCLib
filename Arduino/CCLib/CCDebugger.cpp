/**
 * The MIT License (MIT)
 * 
 * Copyright (c) 2014 Ioannis Charalampidis
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

#include <CCDebugger.h>

/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
////                CONSTRUCTOR & CONFIGURATORS                  ////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////

/**
 * Initialize CC Debugger class
 */
CCDebugger::CCDebugger( int pinRST, int pinDC, int pinDD_I, int pinDD_O ) 
{

  // Keep references
  this->pinRST  = pinRST;
  this->pinDC   = pinDC;
  this->pinDD_I = pinDD_I;
  this->pinDD_O = pinDD_O;

  // Reset LEDS
  this->pinReadLED = 0;
  this->pinWriteLED = 0;

  // Prepare CC Pins
  pinMode(pinDC,        OUTPUT);
  pinMode(pinDD_I,      INPUT);
  pinMode(pinDD_O,      OUTPUT);
  pinMode(pinRST,       OUTPUT);
  digitalWrite(pinDC,   LOW);
  digitalWrite(pinDD_I, LOW); // No pull-up
  digitalWrite(pinDD_O, LOW);
  digitalWrite(pinRST,  LOW);

  // Prepare default direction
  setDDDirection(INPUT);

  // We are active by default
  active = true;
  
};

/**
 * Enable/Configure LEDs
 */
void CCDebugger::setLED( int pinReadLED, int pinWriteLED )
{
  // Prepare read LED
  this->pinReadLED  = pinReadLED;
  if (pinReadLED) {
    pinMode(pinWriteLED, OUTPUT);
    digitalWrite(pinWriteLED, LOW);
  }

  // Prepare write LED
  this->pinWriteLED  = pinWriteLED;
  if (pinWriteLED) {
    pinMode(pinWriteLED, OUTPUT);
    digitalWrite(pinWriteLED, LOW);
  }
}

/**
 * Activate/Deactivate debugger
 */
void CCDebugger::setActive( boolean on ) 
{

  // Reset error flag
  errorFlag = 0;

  // Continue only if active
  if (on == this->active) return;
  this->active = on;

  if (on) {

    // Prepare CC Pins
    pinMode(pinDC,        OUTPUT);
    pinMode(pinDD_I,      INPUT);
    pinMode(pinDD_O,      OUTPUT);
    pinMode(pinRST,       OUTPUT);
    digitalWrite(pinDC,   LOW);
    digitalWrite(pinDD_I, LOW); // No pull-up
    digitalWrite(pinDD_O, LOW);
    digitalWrite(pinRST,  LOW);

    // Activate leds
    if (pinReadLED) {
      pinMode(pinReadLED,       OUTPUT);
      digitalWrite(pinReadLED,  LOW);
    }
    if (pinWriteLED) {
      pinMode(pinWriteLED,      OUTPUT);
      digitalWrite(pinWriteLED, LOW);
    }

    // Default direction is INPUT
    setDDDirection(INPUT);

  } else {

    // Put everything in inactive mode
    pinMode(pinDC,        INPUT);
    pinMode(pinDD_I,      INPUT);
    pinMode(pinDD_O,      INPUT);
    pinMode(pinRST,       INPUT);
    digitalWrite(pinDC,   LOW);
    digitalWrite(pinDD_I, LOW);
    digitalWrite(pinDD_O, LOW);
    digitalWrite(pinRST,  LOW);

    // Deactivate leds
    if (pinReadLED) {
      pinMode(pinReadLED,       INPUT);
      digitalWrite(pinReadLED,  LOW);
    }
    if (pinWriteLED) {
      pinMode(pinWriteLED,      INPUT);
      digitalWrite(pinWriteLED, LOW);
    }
    
  }
}

/**
 * Return the error flag
 */
byte CCDebugger::error()
{
  return errorFlag;
}

/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
////                     LOW LEVEL FUNCTIONS                     ////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////

/**
 * Delay a particular number of cycles
 */
void cc_delay( unsigned char d )
{
  volatile unsigned char i = d;
  while( i-- );
}

/**
 * Enter debug mode
 */
byte CCDebugger::enter() 
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (pinWriteLED) digitalWrite(pinWriteLED, HIGH);
  // =============

  // Reset error flag
  errorFlag = 0;

  // Enter debug mode
  digitalWrite(pinRST, LOW);
  cc_delay(200);
  digitalWrite(pinDC, HIGH);
  cc_delay(3);
  digitalWrite(pinDC, LOW);
  cc_delay(3);
  digitalWrite(pinDC, HIGH);
  cc_delay(3);
  digitalWrite(pinDC, LOW);
  cc_delay(200);
  digitalWrite(pinRST, HIGH);
  cc_delay(200);

  // We are now in debug mode
  inDebugMode = 1;

  // =============
  if (pinWriteLED) digitalWrite(pinWriteLED, LOW);

  // Success
  return 0;

};


/**
 * Write a byte to the debugger
 */
byte CCDebugger::write( byte data ) 
{
  if (!active) {
    errorFlag = 1;
    return 0;
  };
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }
  if (pinWriteLED) digitalWrite(pinWriteLED, HIGH);
  // =============

  byte cnt;

  // Make sure DD is on output
  setDDDirection(OUTPUT);

  // Sent bytes
  for (cnt = 8; cnt; cnt--) {

    // First put data bit on bus
    if (data & 0x80)
      digitalWrite(pinDD_O, HIGH);
    else
      digitalWrite(pinDD_O, LOW);

    // Place clock on high (other end reads data)
    digitalWrite(pinDC, HIGH);

    // Shift & Delay
    data <<= 1;
    cc_delay(4);

    // Place clock down
    digitalWrite(pinDC, LOW);
    cc_delay(4);

  }

  // =============
  if (pinWriteLED) digitalWrite(pinWriteLED, LOW);
  return 0;
}

/**
 * Wait until input is ready for reading
 */
byte CCDebugger::switchRead()
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }
  if (pinReadLED) digitalWrite(pinReadLED, HIGH);
  // =============

  byte cnt;
  byte didWait = 0;

  // Switch to input
  setDDDirection(INPUT);

  // Wait at least 83 ns before checking state t(dir_change)
  cc_delay(4);

  // Wait for DD to go LOW (Chip is READY)
  while (digitalRead(pinDD_I) == HIGH) {

    // Do 8 clock cycles
    for (cnt = 8; cnt; cnt--) {
      digitalWrite(pinDC, HIGH);
      cc_delay(4);
      digitalWrite(pinDC, LOW);
      cc_delay(4);
    }

    // Let next function know that we did wait
    didWait = 1;
  }

  // Wait t(sample_wait) 
  if (didWait) cc_delay(4);

  // =============
  if (pinReadLED) digitalWrite(pinReadLED, LOW);
  return 0;
}

/**
 * Switch to output
 */
byte CCDebugger::switchWrite()
{
  setDDDirection(OUTPUT);
  return 0;
}

/**
 * Read an input byte
 */
byte CCDebugger::read()
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (pinReadLED) digitalWrite(pinReadLED, HIGH);
  // =============

  byte cnt;
  byte data = 0;

  // Switch to input
  setDDDirection(INPUT);

  // Send 8 clock pulses if we are HIGH
  for (cnt = 8; cnt; cnt--) {
    digitalWrite(pinDC, HIGH);
    cc_delay(4);

    // Shift and read
    data <<= 1;
    if (digitalRead(pinDD_I) == HIGH)
      data |= 0x01;

    digitalWrite(pinDC, LOW);
    cc_delay(4);
  }

  // =============
  if (pinReadLED) digitalWrite(pinReadLED, LOW);

  return data;
}

/**
 * Switch reset pin
 */
void CCDebugger::setDDDirection( byte direction )
{

  // Switch direction if changed
  if (direction == ddIsOutput) return;
  ddIsOutput = direction;

  // Handle new direction
  if (ddIsOutput) {
    digitalWrite(pinDD_I, LOW); // Disable pull-up
    pinMode(pinDD_O, OUTPUT);   // Enable output
    digitalWrite(pinDD_O, LOW); // Switch to low
  } else {
    digitalWrite(pinDD_I, LOW); // Disable pull-up
    pinMode(pinDD_O, INPUT);    // Disable output
    digitalWrite(pinDD_O, LOW); // Don't use output pull-up
  }

}

/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
////                    HIGH LEVEL FUNCTIONS                     ////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////


/**
 * Exit from debug mode
 */
byte CCDebugger::exit() 
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x48 ); // RESUME
  switchRead();
  bAns = read(); // debug status
  switchWrite(); 

  return 0;
}
/**
 * Get debug configuration
 */
byte CCDebugger::getConfig() {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x20 ); // RD_CONFIG
  switchRead();
  bAns = read(); // Config
  switchWrite(); 

  return bAns;
}

/**
 * Set debug configuration
 */
byte CCDebugger::setConfig( byte config ) {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x18 ); // WR_CONFIG
  write( config );
  switchRead();
  bAns = read(); // Config
  switchWrite();

  return bAns;
}

/**
 * Invoke a debug instruction with 1 opcode
 */
byte CCDebugger::exec( byte oc0 )
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x51 ); // DEBUG_INSTR + 1b
  write( oc0 );
  switchRead();
  bAns = read(); // Accumulator
  switchWrite(); 

  return bAns;
}

/**
 * Invoke a debug instruction with 2 opcodes
 */
byte CCDebugger::exec( byte oc0, byte oc1 )
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x52 ); // DEBUG_INSTR + 2b
  write( oc0 );
  write( oc1 );
  switchRead();
  bAns = read(); // Accumulator
  switchWrite(); 

  return bAns;
}

/**
 * Invoke a debug instruction with 3 opcodes
 */
byte CCDebugger::exec( byte oc0, byte oc1, byte oc2 )
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x53 ); // DEBUG_INSTR + 3b
  write( oc0 );
  write( oc1 );
  write( oc2 );
  switchRead();
  bAns = read(); // Accumulator
  switchWrite(); 

  return bAns;
}

/**
 * Invoke a debug instruction with 1 opcode + 16-bit immediate
 */
byte CCDebugger::execi( byte oc0, unsigned short c0 )
{
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x53 ); // DEBUG_INSTR + 3b
  write( oc0 );
  write( (c0 >> 8) & 0xFF );
  write(  c0 & 0xFF );
  switchRead();
  bAns = read(); // Accumulator
  switchWrite(); 

  return bAns;
}

/**
 * Return chip ID
 */
unsigned short CCDebugger::getChipID() {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  unsigned short bAns;
  byte bRes;

  write( 0x68 ); // GET_CHIP_ID
  switchRead();
  bRes = read(); // High order
  bAns = bRes << 8;
  bRes = read(); // Low order
  bAns |= bRes;
  switchWrite(); 

  return bAns;
}

/**
 * Return PC
 */
unsigned short CCDebugger::getPC() {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  unsigned short bAns;
  byte bRes;

  write( 0x28 ); // GET_PC
  switchRead();
  bRes = read(); // High order
  bAns = bRes << 8;
  bRes = read(); // Low order
  bAns |= bRes;
  switchWrite(); 

  return bAns;
}

/**
 * Return debug status
 */
byte CCDebugger::getStatus() {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x30 ); // READ_STATUS
  switchRead();
  bAns = read(); // debug status
  switchWrite(); 

  return bAns;
}

/**
 * Step instruction
 */
byte CCDebugger::step() {
  if (!active) {
    errorFlag = 1;
    return 0;
  }
  if (!inDebugMode) {
    errorFlag = 2;
    return 0;
  }

  byte bAns;

  write( 0x58 ); // STEP_INSTR
  switchRead();
  bAns = read(); // Accumulator
  switchWrite(); 

  return bAns;
}
