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

#ifndef VIRTUALSERIAL_H
#define VIRTUALSERIAL_H

#include <ostream>
#include <istream>
#include <iostream>
#include <string>

class VirtualSerial {
public:

  VirtualSerial(std::istream & ins, std::ostream & outs);

  unsigned char available();
  void begin(int baud);
  void flush();
  char read();
  void write(char data);

private:
  std::istream * ins;
  std::ostream * outs;
  std::string pending;

};

#endif
