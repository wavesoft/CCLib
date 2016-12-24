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
from cclib import CCHEXFile, getOptions, openCCDebugger
import sys

# Get serial port either form environment or from arguments
opts = getOptions("Generic CCDebugger Flash Writer Tool", hexIn=True,
	erase="Full chip erase before write", offset=":Offset the addresses in the .hex file by this value")

# Open debugger
try:
	dbg = openCCDebugger(opts['port'], enterDebug=opts['enter'])
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
serial = dbg.getSerial()

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

# Confirm
erasePrompt = "OVERWRITE"
if opts['erase']:
	erasePrompt = "ERASE and REPROGRAM"
print("This is going to %s the chip. Are you sure? <y/N>: " % erasePrompt, end=' ')
ans = sys.stdin.readline()[0:-1]
if (ans != "y") and (ans != "Y"):
	print("Aborted")
	sys.exit(2)


# Flashing messages
print("\nFlashing:")

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
