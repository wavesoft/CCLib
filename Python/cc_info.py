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

from cclib import hexdump, renderDebugStatus, renderDebugConfig, getOptions, openCCDebugger
import sys

# Get serial port either form environment or from arguments
opts = getOptions("Generic CCDebugger Information Tool")

# Open debugger
try:
	dbg = openCCDebugger(opts['port'])
except Exception as e:
	print "ERROR: %s" % str(e)
	sys.exit(1)

# Get info
print "\nChip information:"
print "      Chip ID : 0x%04x" % dbg.chipID
print "   Flash size : %i Kb" % (dbg.flashSize / 1024)
print "    Page size : %i Kb" % (dbg.flashPageSize / 1024)
print "    SRAM size : %i Kb" % (dbg.sramSize / 1024)
if dbg.chipInfo['usb']:
	print "          USB : Yes"
else:
	print "          USB : No"

# Get device information from the read-only section
print "\nDevice information:"
print " IEEE Address : %s" % dbg.getSerial()
print "           PC : %04x" % dbg.getPC()

print "\nDebug status:"
renderDebugStatus(dbg.debugStatus)
print "\nDebug config:"
renderDebugConfig(dbg.debugConfig)

# Done
print ""
