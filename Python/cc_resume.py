#!/usr/bin/python

from cclib import CCDebugger, hexdump
import sys

# Open debugger
try:
	dbg = CCDebugger("/dev/tty.usbmodem12341")
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
print ""

# Check if we are already outside the debug mode
if (dbg.debugStatus & 0x20) == 0:
	print "CPU Already running"
	sys.exit(0)

# Exit debug mode & resume CPU
print "Exiting DEBUG mode..."
dbg.exit()
if (dbg.debugStatus & 0x20) == 0:
	print "CPU is now running"
else:
	print "ERROR: Could not exit from debug mode"

# Done
print ""
