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

# BLE112/BLE113 use a CC2540 chip
from cclib.chip.cc254x import CC254X

class BlueGigaCCDebugger(CC254X):
	"""
	BlueGiga-Specific extensions to the CCDebugger
	"""

	###############################################
	# BlueGiga-Specific functions
	###############################################

	def mergeBLEInfoPage(self, target, source):
		"""
		Copy the last 64-bytes from source to target
		"""

		# Validate size
		if len(target) != len(source):
			raise IOError("Invalid sizes between target/souce blocks!")

		# Copy upper 64 bytes
		l = len(target)
		target[l-0x40:l] = source[l-0x40:l]

		# Return target
		return target

	def setBLELicense(self, target, license, fromHEX=True):
		"""
		Update the BLE info page and store the given license key
		"""

		# Check if we have to convert the license bytes
		if fromHEX:
			license = fromHex(license)

		# Validate lincense size
		if len(license) != 32:
			raise IOError("Invalid license key size!")

		# Update lincense region
		l = len(target)
		target[l-57:l-25] = license

		# Return target
		return target

	def setBLEAddress(self, target, btAddress, fromHEX=True):
		"""
		Update the BLE info page and store the given license key
		"""

		# Check if we have to convert the bluetooth address bytes
		if fromHEX:
			btAddress = fromHex(btAddress,step=3)

		# Validate lincense size
		if len(btAddress) != 6:
			raise IOError("Invalid bluetooth address size!")

		# Update lincense region
		l = len(target)
		target[l-22:l-16] = btAddress

		# Return target
		return target

	def getBLEInfo(self):
		"""
		Return the translated Bluegiga information struct (last 64 bits)
		"""

		# Get page data
		page = self.readCODE( self.flashSize-0x40, 0x40 )

		# Convert bytes to hex representation
		strLic = "".join( "%02x" % x for x in page[7:39] )
		strBTAddr = "".join( "%02x:" % x for x in page[42:48] )[0:-1]

		# Return translated information
		return {
			"license" : strLic,
			"hwver"   : page[39],
			"btaddr"  : strBTAddr,
			"lockbits": page[48:64]
		}

	def getBLEPStoreSize(self):
		"""
		Return the size (in bytes) of the permanent store
		"""

		# PStore size is stored on 0x1F7EF as page number
		a = self.readCODE(0x1F7EF, 1)

		# Check for invalid values
		if a[0] > int(self.flashSize / self.flashPageSize):
			a[0] = 0

		# Return size in bytes
		return a[0] * self.flashPageSize

	def getBLEPStore(self):
		"""
		Return the permanent store
		"""
		pass

	def setBLEPSStore(self, storePageData):
		"""
		Update the permanent store
		"""
		pass

