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
opts = getOptions("BlueGiga-Specific CCDebugger Flash Reader Tool", hexOut=True)

# Open debugger
try:
	dbg = openCCDebugger(opts['port'], enterDebug=opts['enter'], driver=BlueGigaCCDebugger)
except Exception as e:
	print("ERROR: %s" % str(e))
	sys.exit(1)

# Get serial number
print("\nReading %i KBytes to %s..." % (dbg.chipInfo['flash'], opts['out']))
hexFile = CCHEXFile(opts['out'])

# Read in chunks of 4Kb (for UI-update purposes)
for i in range(0, int(dbg.chipInfo['flash'] / 4)):

	# Read CODE
	chunk = dbg.readCODE( i * 0x1000, 0x1000 )

	# Write chunk to file
	hexFile.stack(chunk)

	# Log status
	print("\r    Progress %.0f%%..." % ( ( (i+1)*4 * 100) / dbg.chipInfo['flash'] ), end=' ')
	sys.stdout.flush()

# Log completion
print("\r    Progress 100%... OK")

# Save file
hexFile.save()

# Done
print("\n\nCompleted")
print("")
