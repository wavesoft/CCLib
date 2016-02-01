#
# CCLib_proxy Interface Library for High-Level operations
# Copyright (c) 2014-2016 Ioannis Charalampidis
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

from cclib.ccproxy import CCLibProxy
from cclib.cchex import toHex, fromHex
import math
import time
import sys

# Chip drivers the CCDebugger will test for
from cclib.chip.cc2540x import CC254X
CHIP_DRIVERS = [ CC254X ]

def openCCDebugger( port, driver=None ):
	"""
	Factory function that instantiates the appropriate chip and/or extension
	classes according to the information obtained from the serial port
	"""

	# Create a proxy class (this raises IOError on errors)
	proxy = CCLibProxy(port)

	# Locate the appropriate chip driver to instantiate
	if driver is None:

		# Test known drivers
		for d in CHIP_DRIVERS:
			if d.test( proxy.chipID ):
				driver = d
				break

		# Raise an exception if no compatible driver was found
		if not driver:
			raise IOError("No driver found for your chip (chipID=0x%04x)!" % proxy.chipID)

	# Initialize
	inst = driver(proxy=proxy)
	inst.initialize()

	# Log message
	print "INFO: Found %s on %s" % ( inst.chipName(), port )

	# Return driver
	return inst

def renderDebugConfig(cfg):
	"""
	Visualize debug config
	"""
	if (cfg & 0x10) != 0:
		print " [X] SOFT_POWER_MODE"
	else:
		print " [ ] SOFT_POWER_MODE"
	if (cfg & 0x08) != 0:
		print " [X] TIMERS_OFF"
	else:
		print " [ ] TIMERS_OFF"
	if (cfg & 0x04) != 0:
		print " [X] DMA_PAUSE"
	else:
		print " [ ] DMA_PAUSE"
	if (cfg & 0x02) != 0:
		print " [X] TIMER_SUSPEND"
	else:
		print " [ ] TIMER_SUSPEND"

def renderDebugStatus(cfg):
	"""
	Visualize debug status
	"""
	if (cfg & 0x80) != 0:
		print " [X] CHIP_ERASE_BUSY"
	else:
		print " [ ] CHIP_ERASE_BUSY"
	if (cfg & 0x40) != 0:
		print " [X] PCON_IDLE"
	else:
		print " [ ] PCON_IDLE"
	if (cfg & 0x20) != 0:
		print " [X] CPU_HALTED"
	else:
		print " [ ] CPU_HALTED"
	if (cfg & 0x10) != 0:
		print " [X] PM_ACTIVE"
	else:
		print " [ ] PM_ACTIVE"
	if (cfg & 0x08) != 0:
		print " [X] HALT_STATUS"
	else:
		print " [ ] HALT_STATUS"
	if (cfg & 0x04) != 0:
		print " [X] DEBUG_LOCKED"
	else:
		print " [ ] DEBUG_LOCKED"
	if (cfg & 0x02) != 0:
		print " [X] OSCILLATOR_STABLE"
	else:
		print " [ ] OSCILLATOR_STABLE"
	if (cfg & 0x01) != 0:
		print " [X] STACK_OVERFLOW"
	else:
		print " [ ] STACK_OVERFLOW"

