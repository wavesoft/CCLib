#!/usr/bin/python
#
# CCLib_proxy Utilities
# Copyright (c) 2014 Ioannis Charalampidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import print_function
from cclib import hexdump, getOptions, openCCDebugger
import sys

# Get serial port either form environment or from arguments
opts = getOptions("Generic CCDebugger CPU Resume Tool")

# Open debugger
try:
	dbg = openCCDebugger(opts['port'], enterDebug=opts['enter'])
except Exception as e:
	print("ERROR: %s" % str(e))
	sys.exit(1)

# Check if we are already outside the debug mode
if (dbg.debugStatus & 0x20) == 0:
	print("CPU Already running")
	sys.exit(0)

# Exit debug mode & resume CPU
print("Exiting DEBUG mode...")
dbg.exit()
if (dbg.debugStatus & 0x20) == 0:
	print("CPU is now running")
else:
	print("ERROR: Could not exit from debug mode")

# Done
print("")
