#!/usr/bin/python

from cclib import CCDebugger, CCHEXFile
import sys

def printHelp():
	"""
	Show help screen
	"""
	print "Usage: cc_write_flash.py <hex file> [[[<license key>] <bt address>] <hw version>]"
	print ""
	print "  <license key> : A 32-byte, hex representation of the license key (64 characters)"
	print "   <bt address> : A bluetooth mac address in XX:XX:XX:XX:XX:XX format"
	print "   <hw version> : A decimal number that defines the hardware version"
	print ""

# Wait for filename
if len(sys.argv) < 2:
	print "ERROR: Please specify a source hex filename!"
	printHelp()
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

# Get bluegiga-specific info
binfo = dbg.getBLEInfo()
serial = dbg.getSerial()

# Check if we have missing license
btaMessage=""
hwvMessage=""
licMessage=""
hasLicense = False
for x in binfo['license']:
	if x != "f":
		hasLicense = True
		break

if not hasLicense or (len(sys.argv)>=3):
	if len(sys.argv) < 3:
		print "ERROR: Your device has no license key"
		print "ERROR: You must specify a license key from the command line!"
		printHelp()
		sys.exit(5)
	else:

		licKey = sys.argv[2]
		if len(licKey) != 64:
			print "ERROR: Invalid license key specified!"
			sys.exit(5)
		else:
			licMessage = "(From command-line)"
			binfo['license'] = licKey

		if len(sys.argv) < 4:
			if not hasLicense:
				binfo['btaddr'] = "".join([ "%s:" % serial[x:x+2] for x in range(0,len(serial),2) ])[0:-1]
				btaMessage = " (Generated using IEEE address)"
		else:
			if len(sys.argv[3]) != 17:
				print "ERROR: Invalid BT Address specified!"
				printHelp()
				sys.exit(5)
			btaMessage = "(From command-line)"
			binfo['btaddr'] = sys.argv[3]

		# Reset Hardware Version
		if len(sys.argv) < 5:
			if not hasLicense:
				binfo['hwver'] = 0x01
		else:
			hwvMessage = "(From command-line)"
			binfo['hwver'] = int(sys.argv[4])

# Print collected license information
print "\nLicense information:"
print " IEEE Address : %s" % serial
print " H/W Version  : %02x" % binfo['hwver'], hwvMessage
print "   BT Address : %s" % binfo['btaddr'], btaMessage
print "      License : %s" % binfo['license'], licMessage
print ""

# Parse the HEX file
hexFile = CCHEXFile( sys.argv[1] )
hexFile.load()

# Display sections & calculate max memory usage
maxMem = 0
print "Sections in %s:\n" % sys.argv[1]
print " Addr.    Size"
print "-------- -------------"
for mb in hexFile.memBlocks:

	# Calculate top position
	memTop = mb.addr + mb.size
	if memTop > maxMem:
		maxMem = memTop

	# Print portion
	print " 0x%04x   %i B " % (mb.addr, mb.size)
print ""

# Check for oversize data
if maxMem > (dbg.chipInfo['flash'] * 1024):
	print "ERROR: Data too bit to fit in chip's memory!"
	sys.exit(4)

# Update BLE information on the file
hexFile.set( dbg.flashSize-57, [ int(binfo['license'][x:x+2],16) for x in range(0,len(binfo['license']),2) ] )
hexFile.set( dbg.flashSize-25, [ binfo['hwver'] ])
hexFile.set( dbg.flashSize-22, [ int(binfo['btaddr'][x:x+2],16) for x in range(0,len(binfo['btaddr']),3) ] )

# Confirm
print "This is going to program the chip's flash memory. Are you sure? <y/N>: ", 
ans = sys.stdin.readline()[0:-1]
if (ans != "y") and (ans != "Y"):
	print "Aborted"
	sys.exit(2)


# Get BLE info page
print "\nFlashing:"

# Check for PStore
pssize = dbg.getBLEPStoreSize()
if pssize > 0:
	print " - Backing-up PS Store (%i Bytes)..." % pssize
	pstoreData = dbg.readCODE( 0x18000, pssize )
	hexFile.set( 0x18000, pstoreData )

# Send chip erase
print " - Chip erase..."
try:
#	dbg.chipErase()
	pass
except Exception as e:
 	print "ERROR: %s" % str(e)
 	sys.exit(3)

# Flash memory
dbg.pauseDMA(False)
print " - Flashing %i memory blocks..." % len(hexFile.memBlocks)
for mb in hexFile.memBlocks:

	# Flash memory block
	print " -> 0x%04x : %i bytes " % (mb.addr, mb.size),
	try:
		dbg.writeCODE( mb.addr, mb.bytes, verify=True, showProgress=True )
	except Exception as e:
		print "ERROR: %s" % str(e)
		sys.exit(3)

# Done
print "\nCompleted"
print ""
