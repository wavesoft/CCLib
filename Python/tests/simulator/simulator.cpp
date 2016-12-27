/**
 *
 * CC-Debugger Protocol Library Simulator Utilities
 * Copyright (c) 2014-2016 Ioannis Charalampidis
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

#import <iostream>
#include "emulated/Arduino.h"
#include "VirtualSerial.h"
#include "Platform.h"
using namespace std;

VirtualSerial Serial(cin, cout);

// Load the arduino sketch
#include "../../../Arduino/CCLib/Examples/CCLib_proxy/CCLib_proxy.ino"

// Main loop
int main(int argc, char ** argv) {
  setup();

  while (1) {
    loop();
    sleepcp(25);
  }
}
