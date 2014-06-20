#!/usr/bin/python

from cclib import CCDebugger
import sys

# Wait for filename
if len(sys.argv) < 2:
	print "ERROR: Please specify a source hex filename!"
	sys.exit(1)

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

# Prepare

# Get serial number
print "Loading %s..." % sys.argv[1]
with open(sys.argv[1], "rb") as oFile:
	content = f.readlines()
	for l in content:


# Done
print "\n\nCompleted"
print ""
