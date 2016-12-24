#
# CC2540/41 Chip-Specific code for CCLib
#
# Copyright (c) 2014-2016 Ioannis Charalampidis
# Copyright (c) 2016 Sjoerd Langkemper
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
from cclib.chip import ChipDriver
import sys
import time

# From the SWRU191F user guide, section 3.6, CHIPID register
chipIDs = {
    0xA5: 'CC2530',
    0xB5: 'CC2531',
    0x95: 'CC2533',
    0x8D: 'CC2540',
    0x41: 'CC2541',
}


def getChipName(chipID):
	"""
	Determine the name of the chip from the first byte of the chipID.
	Raises a KeyError if the chip is not supported by this driver.
	"""
	shortID = (chipID & 0xff00) >> 8
	return chipIDs[shortID]


class CC254X(ChipDriver):
	"""
	Chip-specific code for CC253X and CC2540/41 SOC
	"""

	@staticmethod
	def test(chipID):
		"""
		Check if this ChipID can be handled by this class
		"""
		try:
			getChipName(chipID)
			return True
		except KeyError:
			return False

	def chipName(self):
		"""
		Return Chip Name
		"""
		return getChipName(self.chipID)

	def initialize(self):
		"""
		Initialize chip driver
		"""

		# Make sure the CC.Debugger instruction set that arduino should use is the default.
		# The current table is compatible with most of CC24xx chips
		if self.instructionTableVersion != 1:
			self.updateInstructionTable(1, [
					0x40, # I_HALT
					0x48, # I_RESUME
					0x20, # I_RD_CONFIG
					0x18, # I_WR_CONFIG
					0x51, # I_DEBUG_INSTR_1
					0x52, # I_DEBUG_INSTR_2
					0x53, # I_DEBUG_INSTR_3
					0x68, # I_GET_CHIP_ID
					0x28, # I_GET_PC
					0x30, # I_READ_STATUS
					0x58, # I_STEP_INSTR
					0x10, # I_CHIP_ERASE
				])

		# Get chip info
		self.chipInfo = self.getChipInfo()

		# Populate variables
		self.flashSize = self.chipInfo['flash'] * 1024
		self.flashPageSize = 0x800
		self.sramSize = self.chipInfo['sram'] * 1024
		self.bulkBlockSize = 0x800


	###############################################
	# Data reading
	###############################################

	def readXDATA( self, offset, size ):
		"""
		Read any size of buffer from the XDATA region
		"""

		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Prepare ans array
		ans = bytearray()

		# Read bytes
		for i in range(0, size):
			a = self.instr ( 0xE0 )			# MOVX A,@DPTR
			ans.append(a)
			a = self.instr ( 0xA3 )			# INC DPTR

		# Return ans
		return ans

	def writeXDATA( self, offset, bytes ):
		"""
		Write any size of buffer in the XDATA region
		"""

		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Read bytes
		for b in bytes:
			a = self.instr ( 0x74, b )		# MOV A,#data
			a = self.instr ( 0xF0 )			# MOVX @DPTR,A
			a = self.instr ( 0xA3 )			# INC DPTR

		# Return bytes written
		return len(bytes)

	def readCODE( self, offset, size ):
		"""
		Read any size of buffer from the XDATA+0x8000 (code-mapped) region
		"""

		# Pick the code bank this code chunk belongs to
		fBank = int(offset / 0x8000 )
		self.selectXDATABank( fBank )

		# Recalibrate offset
		offset -= fBank * 0x8000

		# Read XDATA-mapped CODE region
		return self.readXDATA( 0x8000 + offset, size )


	def getRegister( self, reg ):
		"""
		Return the value of the given register
		"""
		return self.instr( 0xE5, reg )		# MOV A,direct

	def setRegister( self, reg, v ):
		"""
		Update the value of the
		"""
		return self.instr( 0x75, reg, v )	# MOV direct,#data

	def selectXDATABank(self, bank):
		"""
		Select XDATA bank from the Memory Arbiter Control register
		"""
		a = self.getRegister( 0xC7 )
		a = (a & 0xF8) | (bank & 0x07)
		return self.setRegister( 0xC7, a )

	def selectFlashBank(self, bank):
		"""
		Select a bank for
		"""
		return self.setRegister( 0x9F, bank & 0x07 )


	###############################################
	# Chip information
	###############################################

	def getSerial(self):
		"""
		Read the IEEE address from the 0x780E register
		"""

		# Serial number is 6 bytes, stored on 0x780E
		bytes = self.readXDATA( 0x780E, 6 )

		# Build serial number string
		serial = ""
		for i in range(5,-1,-1):
			serial += "%02x" % bytes[i]

		# Return serial
		return serial

	def getChipInfo(self):
		"""
		Analyze chip info registers
		"""

		# Get chip info registers
		chipInfo = self.readXDATA(0x6276, 2)

		# Extract the useful info
		return {
			'flash' : pow(2, 4 + ((chipInfo[0] & 0x70) >> 4)), # in Kb
			'usb'	: (chipInfo[0] & 0x08) != 0, # in Kb
			'sram'	: (chipInfo[1] & 0x07) + 1
		}

	def getInfoPage(self):
		"""
		Return the read-only information page (2kb)
		"""

		# Read XDATA
		data = self.readXDATA( 0x7800, self.flashPageSize )

		# Get license key
		return data

	def getLastCODEPage(self):
		"""
		Return the entire last flash page
		"""

		# Return the last page-size bytes
		return self.readCODE( self.flashSize - self.flashPageSize, self.flashPageSize )

	def writeLastCODEPage(self, pageData):
		"""
		Write the entire last flash code page
		"""

		# Validate page data
		if len(pageData) > self.flashPageSize:
			raise IOError("Data bigger than flash page size!")

		# Write flash code page
		return self.writeCODE( self.flashSize - self.flashPageSize, pageData, erase=True )


	###############################################
	# DMA functions
	###############################################

	def pauseDMA(self, pause):
		"""
		Pause/Unpause DMA in debug mode
		"""
		# Get current debug config
		a = self.readConfig()
		# Update
		if pause:
			a |= 0x4
		else:
			a &= ~0x4
		# Commit
		self.writeConfig(a)

	def configDMAChannel(self, index, srcAddr, dstAddr, trigger, vlen=0, tlen=1,
		word=False, transferMode=0, srcInc=0, dstInc=0, interrupt=False, m8=True,
		priority=0, memBase=0x1000):
		"""
		Create a DMA buffer and place it in memory
		"""

		# Calculate numeric flags
		nword = 0
		if word:
			nword = 1
		nirq = 0
		if interrupt:
			nirq = 1
		nm8 = 1
		if m8:
			nm8 = 0

		# Prepare DMA configuration bytes
		config = [
			(srcAddr >> 8) & 0xFF,		# 0: SRCADDR[15:8]
			(srcAddr & 0xFF),			# 1: SRCADDR[7:0]
			(dstAddr >> 8) & 0xFF,		# 2: DESTADDR[15:8]
			(dstAddr & 0xFF),			# 3: DESTADDR[7:0]
			(vlen & 0x07) << 5 |		# 4: VLEN[2:0]
			((tlen >> 8) & 0x1F),		# 4: LEN[12:8]
			(tlen & 0xFF),				# 5: LEN[7:0]
			(nword << 7) |				# 6: WORDSIZE
			(transferMode << 5) |		# 6: TMODE[1:0]
			(trigger & 0x1F),			# 6: TRIG[4:0]
			((srcInc & 0x03) << 6) |	# 7: SRCINC[1:0]
			((dstInc & 0x03) << 4) |	# 7: DESTINC[1:0]
			(nirq << 3) |				# 7: IRQMASK
			(nm8 << 2) |				# 7: M8
			(priority & 0x03)			# 7: PRIORITY[1:0]
		]

		# Pick an offset in memory to store the configuration
		memAddr = memBase + index*8
		self.writeXDATA( memAddr, config )

		# Split address in high/low
		cHigh = (memAddr >> 8) & 0xFF
		cLow = (memAddr & 0xFF)

		# Update DMA registers
		if index == 0:
			self.instr( 0x75, 0xD4, cLow  ) # MOV direct,#data @ DMA0CFGL
			self.instr( 0x75, 0xD5, cHigh ) # MOV direct,#data @ DMA0CFGH

		else:

			# For DMA1+ they reside one after the other, starting
			# on the base address of the first in DMA1CFGH:DMA1CFGL
			memAddr = memBase + 8
			cHigh = (memAddr >> 8) & 0xFF
			cLow = (memAddr & 0xFF)

			self.instr( 0x75, 0xD2, cLow  ) # MOV direct,#data @ DMA1CFGL
			self.instr( 0x75, 0xD3, cHigh ) # MOV direct,#data @ DMA1CFGH

	def getDMAConfig(self, index, memBase=0x1000):
		"""
		Read DMA configuration
		"""
		# Pick an offset in memory to store the configuration
		memAddr = memBase + index*8
		return self.readXDATA(memAddr, 8)

	def setDMASrcAddr(self, index, srcAddr, memBase=0x1000):
		"""
		Set the DMA source address
		"""

		# Pick an offset in memory to store the configuration
		memAddr = memBase + index*8
		self.writeXDATA( memAddr, [
			(srcAddr >> 8) & 0xFF,		# 0: SRCADDR[15:8]
			(srcAddr & 0xFF),			# 1: SRCADDR[7:0]
		])

	def setDMADstAddr(self, index, dstAddr, memBase=0x1000):
		"""
		Set the DMA source address
		"""

		# Pick an offset in memory to store the configuration
		memAddr = memBase + index*8
		self.writeXDATA( memAddr+2, [
			(dstAddr >> 8) & 0xFF,		# 2: DESTADDR[15:8]
			(dstAddr & 0xFF),			# 3: DESTADDR[7:0]
		])

	def armDMAChannel(self, index):
		"""
		Arm a DMA channel (index in 0-4)
		"""

		# Get DMAARM state
		a = self.getRegister(0xD6) # MOV A,direct @ DMAARM

		# Set given flag
		a |= pow(2, index)

		# Update DMAARM state
		self.setRegister(0xD6, a) # MOV direct,#data @ DMAARM

		time.sleep(0.01)

	def disarmDMAChannel(self, index):
		"""
		Disarm a DMA channel (index in 0-4)
		"""

		# Get DMAARM state
		a = self.getRegister( 0xD6 )

		# Unset given flag
		flag = pow(2, index)
		a &= ~flag

		# Update DMAARM state
		self.setRegister( 0xD6, a )

	def isDMAArmed(self, index):
		"""
		Check if DMA IRQ flag is set (index in 0-4)
		"""

		# Get DMAARM state
		a = self.getRegister( 0xD1 )

		# Lookup IRQ bit
		bit = pow(2, index)

		# Check if IRQ bit is set
		return ((a & bit) != 0)

	def isDMAIRQ(self, index):
		"""
		Check if DMA IRQ flag is set (index in 0-4)
		"""

		# Get DMAIRQ state
		a = self.getRegister( 0xD1 )

		# Lookup IRQ bit
		bit = pow(2, index)

		# Check if IRQ bit is set
		return ((a & bit) != 0)

	def clearDMAIRQ(self, index):
		"""
		Clear DMA IRQ flag (index in 0-4)
		"""

		# Get DMAIRQ state
		a = self.getRegister( 0xD1 )

		# Unset given flag
		flag = pow(2, index)
		a &= ~flag

		# Update DMAIRQ state
		self.setRegister( 0xD1, a )

	###############################################
	# Flash functions
	###############################################

	def setFlashWordOffset(self, address):
		"""
		Set the flash address offset in FADDRH:FADDRL
		"""

		# Split address in high/low order bytes
		cHigh = (address >> 8) & 0xFF
		cLow = (address & 0xFF)

		# Place in FADDRH:FADDRL
		self.writeXDATA( 0x6271, [cLow, cHigh])

	def isFlashFull(self):
		"""
		Check if the FULL bit is set in the flash register
		"""

		# Read flash status register
		a = self.readXDATA(0x6270, 1)
		return (a[0] & 0x40 != 0)

	def isFlashBusy(self):
		"""
		Check if the BUSY bit is set in the flash register
		"""

		# Read flash status register
		a = self.readXDATA(0x6270, 1)
		return (a[0] & 0x80 != 0)

	def isFlashAbort(self):
		"""
		Check if the ABORT bit is set in the flash register
		"""

		# Read flash status register
		a = self.readXDATA(0x6270, 1)
		return (a[0] & 0x20 != 0)

	def clearFlashStatus(self):
		"""
		Clear the flash status register
		"""

		# Read & mask-out status register bits
		a = self.readXDATA(0x6270, 1)
		a[0] &= 0x1F
		return self.writeXDATA(0x6270, a)

	def setFlashWrite(self):
		"""
		Set the WRITE bit in the flash control register
		"""

		# Set flash WRITE bit
		a = self.readXDATA(0x6270, 1)
		a[0] |= 0x02
		return self.writeXDATA(0x6270, a)

	def setFlashErase(self):
		"""
		Set the ERASE bit in the flash control register
		"""

		# Set flash ERASE bit
		a = self.readXDATA(0x6270, 1)
		a[0] |= 0x01
		return self.writeXDATA(0x6270, a)

	def writeCODE(self, offset, data, erase=False, verify=False, showProgress=False):
		"""
		Fully automated function for writing the Flash memory.

		WARNING: This requires DMA operations to be unpaused ( use: self.pauseDMA(False) )
		"""

		# Prepare DMA-0 for DEBUG -> RAM (using DBG_BW trigger)
		self.configDMAChannel( 0, 0x6260, 0x0000, 0x1F, tlen=self.bulkBlockSize, srcInc=0, dstInc=1, priority=1, interrupt=True )
		# Prepare DMA-1 for RAM -> FLASH (using the FLASH trigger)
		self.configDMAChannel( 1, 0x0000, 0x6273, 0x12, tlen=self.bulkBlockSize, srcInc=1, dstInc=0, priority=2, interrupt=True )

		# Reset flags
		self.clearFlashStatus()
		self.clearDMAIRQ(0)
		self.clearDMAIRQ(1)
		self.disarmDMAChannel(0)
		self.disarmDMAChannel(1)

		# Split in 2048-byte chunks
		iOfs = 0
		while (iOfs < len(data)):

			# Check if we should show progress
			if showProgress:
				print("\r    Progress %0.0f%%... " % (iOfs*100/len(data)), end=' ')
				sys.stdout.flush()

			# Get next page
			iLen = min( len(data) - iOfs, self.bulkBlockSize )

			# Update DMA configuration if we have less than bulk-block size data
			if (iLen < self.bulkBlockSize):
				self.configDMAChannel( 0, 0x6260, 0x0000, 0x1F, tlen=iLen, srcInc=0, dstInc=1, priority=1, interrupt=True )
				self.configDMAChannel( 1, 0x0000, 0x6273, 0x12, tlen=iLen, srcInc=1, dstInc=0, priority=2, interrupt=True )

			# Upload to RAM through DMA-0
			self.armDMAChannel(0)
			self.brustWrite( data[iOfs:iOfs+iLen] )

			# Wait until DMA-0 raises interrupt
			while not self.isDMAIRQ(0):
				time.sleep(0.010)

			# Clear DMA IRQ flag
			self.clearDMAIRQ(0)

			# Calculate the page where this data belong to
			fAddr = offset + iOfs
			fPage = int( fAddr / self.flashPageSize )

			# Calculate FLASH address High/Low bytes
			# for writing (addressable as 32-bit words)
			fWordOffset = int(fAddr / 4)
			cHigh = (fWordOffset >> 8) & 0xFF
			cLow = fWordOffset & 0xFF
			self.writeXDATA( 0x6271, [cLow, cHigh] )

			# Debug
			#print "[@%04x: p=%i, ofs=%04x, %02x:%02x]" % (fAddr, fPage, fWordOffset, cHigh, cLow),
			#sys.stdout.flush()

			# Check if we should erase page first
			if erase:
				# Select the page to erase using FADDRH[7:1]
				#
				# NOTE: Specific to (CC2530, CC2531, CC2540, and CC2541),
				#       the CC2533 uses FADDRH[6:0]
				#
				cHigh = (fPage << 1)
				cLow = 0
				self.writeXDATA( 0x6271, [cLow, cHigh] )
				# Set the erase bit
				self.setFlashErase()
				# Wait until flash is not busy any more
				while self.isFlashBusy():
					time.sleep(0.010)

			# Upload to FLASH through DMA-1
			self.armDMAChannel(1)
			self.setFlashWrite()

			# Wait until DMA-1 raises interrupt
			while not self.isDMAIRQ(1):
				# Also check for errors
				if self.isFlashAbort():
					self.disarmDMAChannel(1)
					raise IOError("Flash page 0x%02x is locked!" % fPage)
				time.sleep(0.010)

			# Clear DMA IRQ flag
			self.clearDMAIRQ(1)

			# Check if we should verify
			if verify:
				verifyBytes = self.readCODE(fAddr, iLen)
				if verifyBytes != data[iOfs:iOfs+iLen]:
					raise IOError("Flash verification error on offset 0x%04x" % fAddr)
			iOfs += iLen

		if showProgress:
			print("\r    Progress 100%... OK")
