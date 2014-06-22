/**
 *
 * CC-Debugger Protocol Library for Arduino
 * Copyright (c) 2014 Ioannis Charalampidis
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *  
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

