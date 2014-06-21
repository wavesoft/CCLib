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

#ifndef CCDEBUGGER_H
#define CCDEBUGGER_H

// For arduino bindings
#include "Arduino.h"

class CCDebugger {
public:

  ////////////////////////////
  // Configuration
  ////////////////////////////

  /**
   * Initialize CC Debugger class
   */
  CCDebugger( int pinRST, int pinDC, int pinDD_I, int pinDD_O );

  /**
   * Set/Enable leds
   */
  void setLED( int pinReadLED, int pinWriteLED );

  /**
   * Activate/deactivate debugger
   */
  void setActive( boolean on );

  /**
   * Return the error flag
   */
  byte error();

  ////////////////////////////
  // High-Level interaction
  ////////////////////////////

  /**
   * Enter debug mode
   */
  byte enter();

  /**
   * Exit from debug mode
   */
  byte exit();

  /**
   * Execute a CPU instructuion
   */
  byte exec( byte oc0 );
  byte exec( byte oc0, byte oc1 );
  byte exec( byte oc0, byte oc1, byte oc2 );
  byte execi( byte oc0, unsigned short c0 );

  /**
   * Return chip ID
   */
  unsigned short getChipID();

  /**
   * Return PC
   */
  unsigned short getPC();

  /**
   * Return debug status
   */
  byte getStatus();

  /**
   * Step a single instruction
   */
  byte step();

  /**
   * Get debug configuration
   */
  byte getConfig();

  /**
   * Set debug configuration
   */
  byte setConfig( byte config );

  /**
   * Massive erasure on the chip
   */
  byte chipErase();

  ////////////////////////////
  // Low-level interaction
  ////////////////////////////

  /**
   * Write to the debugger
   */
  byte write( byte data );

  /**
   * Wait until we are ready to read & Switch to read mode
   */
  byte switchRead();

  /**
   * Switch to write mode
   */
  byte switchWrite();

  /**
   * Read from the debugger
   */
  byte read();


private:

  ////////////////////////////
  // Private/Helper parts
  ////////////////////////////

  /**
   * Switch reset pin
   */
  void setDDDirection( byte direction );

  /**
   * Local properties
   */ 
  int       pinRST;
  int       pinDC;
  int       pinDD_I;
  int       pinDD_O;
  int       pinReadLED;
  int       pinWriteLED;
  byte      errorFlag;
  byte      ddIsOutput;
  byte      inDebugMode;
  boolean   active;

};

#endif

