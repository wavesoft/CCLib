#
# CS2510 Chip-Specific code for CCLib
#
# Copyright (c) 2015 Simon Schulz - github.com/fishpepper
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
from __future__ import print_function
from cclib.chip import ChipDriver
import sys
import time

class CC2510(ChipDriver):
	"""
	Chip-specific code for CC2510 SOC
	"""

	@staticmethod
	def test(chipID):
		"""
		Check if this ChipID can be handled by this class
		"""
		return ((chipID & 0xFF00) == 0x8100)

	def chipName(self):
		"""
		Return Chip Name
		"""
		return "CC251x"

	def initialize(self):
		"""
		Initialize chip driver
		"""

		# Update the CC.Debugger instruction set that arduino should use with
		# the chip, because CC251xx chips use a different one
		if self.instructionTableVersion != 2:
			self.updateInstructionTable(2, [
					0x44, # I_HALT
					0x4C, # I_RESUME
					0x24, # I_RD_CONFIG
					0x1D, # I_WR_CONFIG
					0x55, # I_DEBUG_INSTR_1
					0x56, # I_DEBUG_INSTR_2
					0x57, # I_DEBUG_INSTR_3
					0x68, # I_GET_CHIP_ID
					0x28, # I_GET_PC
					0x34, # I_READ_STATUS
					0x5C, # I_STEP_INSTR
					0x14, # I_CHIP_ERASE
				])

		# Custom chip info for cc2510
		self.chipInfo = {
			'flash' : 16,
			'usb'   : 0,
			'sram'  : 2
		}

		# Populate variables
		self.flashSize = self.chipInfo['flash'] * 1024
		#all cc251x have 0x400 as flash page size
		self.flashPageSize = 0x400
		self.sramSize = self.chipInfo['sram'] * 1024
		self.bulkBlockSize = 0x400 # < This should be the same as the flash page size
		self.flashWordSize = 2 #cc251x have 2 bytes per word

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

		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Prepare ans array
		ans = bytearray()

		# Read bytes
		for i in range(0, size):
			a = self.instr ( 0xE4 )			# MOVX A,@DPTR
			a = self.instr ( 0x93 )			# MOVX A,@DPTR
			ans.append(a)
			a = self.instr ( 0xA3 )			# INC DPTR


		#
		return ans


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
		#a = self.getRegister( 0xC7 )
		#a = (a & 0xF8) | (bank & 0x07)
		#return self.setRegister( 0xC7, a )
		return self.instr(0x75, 0xC7, bank*16 + 1);


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
	# cc251x
	###############################################

	def readFlashPage(self, address):
		if (not self.debug_active):
			print("ERROR: not in debug mode! did you forget a enter() call?\n")
			sys.exit(2)
		return self.readCODE(address & 0x7FFFF, self.flashPageSize)

	def writeFlashPage(self, address, inputArray, erase_page=True):
		if len(inputArray) != self.flashPageSize:
			raise IOError("input data size != flash page size!")

		if (not self.debug_active):
			print("ERROR: not in debug mode! did you forget a enter() call?\n")
			sys.exit(2)

		#calc words per flash page
		words_per_flash_page = self.flashPageSize / self.flashWordSize

		#print "words_per_flash_page = %d" % (words_per_flash_page)
		#print "flashWordSize = %d" % (self.flashWordSize)
		if (erase_page):
			print("[page erased]", end=' ')

		routine8_1 = [
			#see http://www.ti.com/lit/ug/swra124/swra124.pdf page 11
			0x75, 0xAD, ((address >> 8) / self.flashWordSize) & 0x7E, 	#MOV FADDRH, #imm;
			0x75, 0xAC, 0x00						#MOV FADDRL, #00;
		]
		routine8_erase = [
			0x75, 0xAE, 0x01,						#MOV FLC, #01H; // ERASE
			#; Wait for flash erase to complete
			0xE5, 0xAE,							#eraseWaitLoop:  MOV A, FLC;
			0x20, 0xE7, 0xFB						#JB ACC_BUSY, eraseWaitLoop;
		]
		routine8_2 = [
			#; Initialize the data pointer
			0x90, 0xF0, 0x00,						#MOV DPTR, #0F000H;
			#; Outer loops
			0x7F, (((words_per_flash_page)>>8)&0xFF),			#MOV R7, #imm;
			0x7E, ((words_per_flash_page)&0xFF),				#MOV R6, #imm;
			0x75, 0xAE, 0x02,						#MOV FLC, #02H; // WRITE
			#; Inner loops
			0x7D, self.flashWordSize,					#writeLoop:          MOV R5, #imm;
			0xE0,								#writeWordLoop:          MOVX A, @DPTR;
			0xA3,								#INC DPTR;
			0xF5, 0xAF,							#MOV FWDATA, A;
			0xDD, 0xFA,							#DJNZ R5, writeWordLoop;
			#; Wait for completion
			0xE5, 0xAE,							#writeWaitLoop:      MOV A, FLC;
			0x20, 0xE6, 0xFB,						#JB ACC_SWBSY, writeWaitLoop;
			0xDE, 0xF1,							#DJNZ R6, writeLoop;
			0xDF, 0xEF,							#DJNZ R7, writeLoop;
			#set green led for debugging info (DO NOT USE THIS!)
			#LED_GREEN_DIR |= (1<<LED_GREEN_PIN);
			#0x43, 0xFF, 0x18,	#      [24]  935         orl     _P2DIR,#0x10
			#LED_GREEN_PORT = (1<<LED_GREEN_PIN);
			#0x75, 0xA0, 0x18,	#      [24]  937         mov     _P2,#0x10
			#; Done with writing, fake a breakpoint in order to HALT the cpu
			0xA5								#DB 0xA5;
		]

		#build routine
		routine = routine8_1
		if (erase_page):
			routine += routine8_erase
		routine += routine8_2

		#add led code to flash code (for debugging)
		#aroutine = led_routine + routine
		#routine = routine + led_routine

		#for x in routine:
		#	print "%02X" % (x),

		#halt CPU
		self.halt()

		#send data to xdata memory:
		if (self.show_debug_info): print("copying data to xdata")
		self.writeXDATA(0xF000, inputArray)

		#send program to xdata mem
		if (self.show_debug_info): print("copying flash routine to xdata")
		self.writeXDATA(0xF000 + self.flashPageSize, routine)

		if (self.show_debug_info): print("executing code")
		#execute MOV MEMCTR, (bank * 16) + 1;
		self.instr(0x75, 0xC7, 0x51)

		#set PC to start of program
		self.setPC(0xF000 + self.flashPageSize)

		#start program exec, will continue after routine exec due to breakpoint
		self.resume()


		if (self.show_debug_info): print("page write running", end=' ')

		#set some timeout (2 seconds)
		timeout = 200
		while (timeout > 0):
			#show progress
			if (self.show_debug_info):
				print(".", end=' ')
				sys.stdout.flush()
			#check status (bit 0x20 = cpu halted)
			if ((self.getStatus() & 0x20 ) != 0):
				if (self.show_debug_info): print("done")
				break
			#timeout increment
			timeout -= 1
			#delay (10ms)
			time.sleep(0.01)


		if (timeout <=0):
			raise IOError("flash write timed out!")

		self.halt()

		if (self.show_debug_info): print("done")


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
		flashRetries = 0

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
				for i in range(0, iLen):
					if verifyBytes[i] != data[iOfs+i]:
						if flashRetries < 3:
							print("\n[Flash Error at @0x%04x, will retry]" % (fAddr+i))
							flashRetries += 1
							continue
						else:
							raise IOError("Flash verification error on offset 0x%04x" % (fAddr+i))
			flashRetries = 0

			# Forward to next page
			iOfs += iLen

		if showProgress:
			print("\r    Progress 100%... OK")
