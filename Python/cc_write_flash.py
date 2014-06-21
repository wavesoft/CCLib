#!/usr/bin/python

from cclib import CCDebugger, CCHEXFile
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

# Get serial number
hexFile = CCHEXFile( sys.argv[1] )
hexFile.load()

print "\nSections in %s:\n" % sys.argv[1]
print " Addr.    Size"
print "-------- -------------"
for mb in hexFile.memBlocks:
	# Flash memory block
	print " 0x%04x   %i B " % (mb.addr, mb.size)

# Confirm
print "\nThis is going to program the chip's flash memory. Are you sure? <y/N>: ", 
ans = sys.stdin.readline()[0:-1]
if (ans != "y") and (ans != "Y"):
	print "Aborted"
	sys.exit(2)


# Get BLE info page
print "\nFlashing:"
print " - Backing-up BLE section..."
blePage = dbg.backupBLEInfoPage()

# Send chip erase
#print " - Chip erase..."
#try:
dbg.chipErase()
#except Exception as e:
# 	print "ERROR: %s" % str(e)
# 	try:
# 		print " - Restoring BLE section..."
# 		dbg.restoreBLEInfoPage(blePage)
# 	except Exception as e:
# 		print "ERROR: %s" % str(e)

# 	# Exit
# 	sys.exit(3)

# Flash memory
dbg.pauseDMA(False)
print " - Flashing %i memory blocks..." % len(hexFile.memBlocks)
for mb in hexFile.memBlocks:

	# Flash memory block
	print " -> 0x%04x : %i bytes " % (mb.addr, mb.size),
	try:
		dbg.writeCODE( mb.addr, mb.bytes, showProgress=True )
	except Exception as e:

		print "ERROR: %s" % str(e)

		# Try to restore BLE section
		try:
			print " - Restoring BLE section..."
			dbg.restoreBLEInfoPage(blePage)
		except Exception as e:
			print "ERROR: %s" % str(e)

		# Exit
		sys.exit(3)


# Restore BLE info page
print " - Restoring BLE section..."
dbg.restoreBLEInfoPage(blePage)

# Done
print "\nCompleted"
print ""
