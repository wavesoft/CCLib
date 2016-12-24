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
from __future__ import print_function
from cclib import CCHEXFile, getOptions, openCCDebugger
from cclib.extensions.bluegiga import BlueGigaCCDebugger
import sys

# Get serial port either form environment or from arguments
opts = getOptions("BlueGiga-Specific CCDebugger Flash Writer Tool", hexIn=True,
	license=":A 32-byte, hex representation of the license key (64 characters)",
	addr=":A bluetooth mac address in XX:XX:XX:XX:XX:XX format",
	ver=":A decimal number that defines the hardware version",
	erase="Full chip erase before write",
	offset=":Offset the addresses in the .hex file by this value")

# Open debugger
try:
	dbg = openCCDebugger(opts['port'], enterDebug=opts['enter'], driver=BlueGigaCCDebugger)
except Exception as e:
	print("ERROR: %s" % str(e))
	sys.exit(1)

# Get offset
offset = 0
if opts['offset']:
	if opts['offset'][0:2] == "0x":
		offset = int(opts['offset'], 16)
	else:
		offset = int(opts['offset'])
	print("NOTE: The memory addresses are offset by %i bytes!" % offset)

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

if not hasLicense:
	if opts['license'] is None:
		print("ERROR: Your device has no license key")
		print("ERROR: You must specify a license key from the command line!")
		sys.exit(5)
	else:

		licKey = opts['license']
		if len(licKey) != 64:
			print("ERROR: Invalid license key specified!")
			sys.exit(5)
		else:
			licMessage = "(From command-line)"
			binfo['license'] = licKey

		if opts['addr'] is None:
			if not hasLicense:
				binfo['btaddr'] = "".join([ "%s:" % serial[x:x+2] for x in range(0,len(serial),2) ])[0:-1]
				btaMessage = " (Generated using IEEE address)"
		else:
			if len(opts['addr']) != 17:
				print("ERROR: Invalid BT Address specified!")
				sys.exit(5)
			btaMessage = "(From command-line)"
			binfo['btaddr'] = opts['addr']

		# Reset Hardware Version
		if opts['ver'] is None:
			if not hasLicense:
				binfo['hwver'] = 0x01
		else:
			hwvMessage = "(From command-line)"
			binfo['hwver'] = int(opts['ver'])

# Print collected license information
print("\nLicense information:")
print(" IEEE Address : %s" % serial)
print(" H/W Version  : %02x" % binfo['hwver'], hwvMessage)
print("   BT Address : %s" % binfo['btaddr'], btaMessage)
print("      License : %s" % binfo['license'], licMessage)
print("")

# Parse the HEX file
hexFile = CCHEXFile( opts['in'] )
hexFile.load()

# Display sections & calculate max memory usage
maxMem = 0
print("Sections in %s:\n" % opts['in'])
print(" Addr.    Size")
print("-------- -------------")
for mb in hexFile.memBlocks:

	# Calculate top position
	memTop = mb.addr + mb.size
	if memTop > maxMem:
		maxMem = memTop

	# Print portion
	print(" 0x%04x   %i B " % (mb.addr + offset, mb.size))
print("")

# Check for oversize data
if maxMem > (dbg.chipInfo['flash'] * 1024):
	print("ERROR: Data too bit to fit in chip's memory!")
	sys.exit(4)

# Update BLE information on the file
hexFile.set( dbg.flashSize-57, [ int(binfo['license'][x:x+2],16) for x in range(0,len(binfo['license']),2) ] )
hexFile.set( dbg.flashSize-25, [ binfo['hwver'] ])
hexFile.set( dbg.flashSize-22, [ int(binfo['btaddr'][x:x+2],16) for x in range(0,len(binfo['btaddr']),3) ] )

# Confirm
erasePrompt = "OVERWRITE"
if opts['erase']:
	erasePrompt = "ERASE and REPROGRAM"
print("This is going to %s the chip. Are you sure? <y/N>: " % erasePrompt, end=' ')
ans = sys.stdin.readline()[0:-1]
if (ans != "y") and (ans != "Y"):
	print("Aborted")
	sys.exit(2)


# Get BLE info page
print("\nFlashing:")

# Check for PStore
pssize = dbg.getBLEPStoreSize()
if pssize > 0:
	print(" - Backing-up PS Store (%i Bytes)..." % pssize)
	pstoreData = dbg.readCODE( 0x18000, pssize )
	hexFile.set( 0x18000, pstoreData )

# Send chip erase
if opts['erase']:
	print(" - Chip erase...")
	try:
		dbg.chipErase()
	except Exception as e:
	 	print("ERROR: %s" % str(e))
	 	sys.exit(3)

# Flash memory
dbg.pauseDMA(False)
print(" - Flashing %i memory blocks..." % len(hexFile.memBlocks))
for mb in hexFile.memBlocks:

	# Flash memory block
	print(" -> 0x%04x : %i bytes " % (mb.addr + offset, mb.size))
	try:
		dbg.writeCODE( mb.addr + offset, mb.bytes, verify=True, showProgress=True )
	except Exception as e:
		print("ERROR: %s" % str(e))
		sys.exit(3)

# Done
print("\nCompleted")
print("")
