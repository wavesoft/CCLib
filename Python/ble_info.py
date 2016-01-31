#!/usr/bin/python
#
# CCLib_proxy Utilities - BlueGiga Specific
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

from cclib import hexdump, renderDebugStatus, renderDebugConfig
from cclib.extensions.bluegiga import BlueGigaCCDebugger
import sys

# Open debugger
try:
	dbg = BlueGigaCCDebugger("/dev/tty.usbmodem12341")
except Exception as e:
	print "ERROR: %s" % str(e)
	sys.exit(1)

# Get info
print "\nChip information:"
print "      Chip ID : 0x%04x" % dbg.chipID
print "   Flash size : %i Kb" % dbg.chipInfo['flash']
print "    SRAM size : %i Kb" % dbg.chipInfo['sram']
if dbg.chipInfo['usb']:
	print "          USB : Yes"
else:
	print "          USB : No"

# Get device information from the read-only section
print "\nDevice information:"
print " IEEE Address : %s" % dbg.getSerial()
print "           PC : %04x" % dbg.getPC()

# Get bluegiga-specific info
binfo = dbg.getBLEInfo()
print "\nFirmware information:"
print "      License : %s" % binfo['license']
print "   BT Address : %s" % binfo['btaddr']
print " Hardware Ver : %02x" % binfo['hwver']

print "\nDebug status:"
renderDebugStatus(dbg.debugStatus)
print "\nDebug config:"
renderDebugConfig(dbg.debugConfig)

# Done
print ""
