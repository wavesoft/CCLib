#!/usr/bin/python

from cclib import CCDebugger
import sys

# Open debugger
try:
	dbg = CCDebugger("/dev/tty.usbmodem12341")
except Exception as e:
	print "ERROR: %s" % str(e)
	sys.exit(0)

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

# Get bluegiga-specific info
binfo = dbg.getBLEInfo()
print "\nFirmware information:"
print "      License : %s" % binfo['license']
print "   BT Address : %s" % binfo['btaddr']
print " Hardware Ver : %02x" % binfo['hwver']

# Done
print ""
