#!/usr/bin/python

from cclib import CCDebugger
import sys

# Wait for filename
if len(sys.argv) < 2:
	print "ERROR: Please specify a filename to dump the FLASH memory to!"
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

# Get serial number
print "\nReading %i KBytes to %s..." % (dbg.chipInfo['flash'], sys.argv[1])
with open(sys.argv[1], "wb") as oFile:

	# Read in chunks of 4Kb (for UI-purposes)
	for i in range(0, int(dbg.chipInfo['flash'] / 4)):

		# Read CODE
		chunk = dbg.readCODE( i * 0x1000, 0x1000 )

		# Write chunk to file
		oFile.write("".join(map(chr, chunk)))

		# Log status
		print "%.0f%%..." % ( ( (i+1)*4 * 100) / dbg.chipInfo['flash'] ),
		sys.stdout.flush()


# Done
print "\n\nCompleted"
print ""
