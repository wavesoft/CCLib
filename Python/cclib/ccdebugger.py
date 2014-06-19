#
# The MIT License (MIT)
# 
# Copyright (c) 2014 Ioannis Charalampidis
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import serial
import struct

# Command constants
CMD_ENTER    = 0x01
CMD_EXIT     = 0x02
CMD_CHIP_ID  = 0x03
CMD_STATUS   = 0x04
CMD_PC       = 0x05
CMD_STEP     = 0x06
CMD_EXEC_1   = 0x07
CMD_EXEC_2   = 0x08
CMD_EXEC_3   = 0x09
CMD_PING     = 0xF0

# Response constants
ANS_OK       = 0x01
ANS_ERROR    = 0x02

class CCDebugger:
	"""
	The core CCDebugger class which provides both low-level and high-level functions
	for interacting with a TI component.
	"""

	def __init__(self, port):
		"""
		Initialize serial port
		"""

		# Open port
		try:
			self.ser = serial.Serial(port, timeout=1)
		except:
			print "Could not open port %s" % port
			return

		# Ping
		if self.ping():
			print "Using CCDebugger on port %s" % self.ser.name 
		else:
			print "Could not find CCDebugger on port %s" % self.ser.name

		# Get chip info & ID
		self.chipID = self.getChipID()
		self.chipInfo = self.getChipInfo()

	def sendFrame(self, cmd, c1=0,c2=0,c3=0 ):
		"""
		Send the specified frame to the output queue
		"""
		self.ser.write( chr(cmd)+chr(c1)+chr(c2)+chr(c3) )
		self.ser.flush()
		status = ord(self.ser.read())
		if status != ANS_OK:
			status = ord(self.ser.read())
			raise IOError("CCDebugger responded with an error (0x%02x)" % status)

		return True


	def ping(self):
		"""
		Send a PING frame
		"""
		return self.sendFrame(CMD_PING)


	def enter(self):
		"""
		Enter in debug mode
		"""
		return self.sendFrame(CMD_ENTER)

	def exit(self):
		"""
		Exit from debug mode by resuming the CPU
		"""
		return self.sendFrame(CMD_EXIT)

	def step(self):
		"""
		Step a single instruction
		"""
		if not self.sendFrame(CMD_STEP):
			return 0

		# Read accumulator
		b1 = ord(self.ser.read())
		return b1

	def getChipID(self):
		"""
		Return the ChipID as read from the chip
		"""
		
		# Execute command CMD_CHIP_ID
		if not self.sendFrame(CMD_CHIP_ID):
			return False
		
		# Read Chip ID
		b1 = ord(self.ser.read())
		b2 = ord(self.ser.read())
		return (b1 <<  8) | b2

	def getPC(self):
		"""
		Return the PC position as read from the chip
		"""
		
		# Execute command CMD_CHIP_ID
		if not self.sendFrame(CMD_PC):
			return False
		
		# Read Chip ID
		b1 = ord(self.ser.read())
		b2 = ord(self.ser.read())
		return (b1 <<  8) | b2

	def instr(self, c1, c2=None, c3=None):
		"""
		Execute a debug instruction
		"""

		# Check how many bytes are we passing
		if (c2 == None):
			if not self.sendFrame(CMD_EXEC_1, c1):
				return False
		elif (c3 == None):
			if not self.sendFrame(CMD_EXEC_2, c1, c2):
				return False
		else:
			if not self.sendFrame(CMD_EXEC_3, c1, c2, c3):
				return False

		# Read accumulator
		b1 = ord(self.ser.read())
		return b1

	def instri(self, c1, i1):
		"""
		Execute a debug instruction with 16-bit constant
		"""

		# Split short in high/low order bytes
		cHigh = (i1 >> 8) & 0xFF
		cLow = (i1 & 0xFF)

		# Send instruction
		if not self.sendFrame(CMD_EXEC_3, c1, cHigh, cLow):
			return False

		# Read accumulator
		b1 = ord(self.ser.read())
		return b1


	def readCODE( self, offset, size ):

		# Pick the code bank this code chunk belongs to


		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Prepare ans array
		ans = []

		# Read bytes
		for i in range(0, size):
			a = self.instr ( 0xE4 )			# CLR A
			a = self.instr ( 0x93 )			# MOVC A,@A+DPTR
			ans.append(a)
			a = self.instr ( 0xA3 )			# INC DPTR

		# Return ans
		return ans

	def readXDATA( self, offset, size ):

		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Prepare ans array
		ans = []

		# Read bytes
		for i in range(0, size):
			a = self.instr ( 0xE0 )			# MOVX A,@DPTR
			ans.append(a)
			a = self.instr ( 0xA3 )			# INC DPTR

		# Return ans
		return ans

	def writeRAM( self, offset, bytes ):

		# Setup DPTR
		a = self.instri( 0x90, offset )		# MOV DPTR,#data16

		# Read bytes
		for b in bytes:
			a = self.instr ( 0x74, b )		# MOV A,#data
			a = self.instr ( 0xF0 )			# MOVX @DPTR,A
			a = self.instr ( 0xA3 )			# INC DPTR

		# Return bytes written
		return len(bytes)

	def getRegister( self, reg ):
		return self.instr( 0xE5, reg )		# MOV A,direct

	def setRegister( self, reg, v ):
		return self.instr( 0x75, reg, v )	# MOV direct,#data

	def selectXDATABank(self, bank):
		return self.setRegister( 0xC7, bank & 0x07 )

	def selectFlashBank(self, bank):
		return self.setRegister( 0x9F, bank & 0x07 )

	def getSerial(self):

		# Serial number is 6 bytes, stored on 0x780E
		bytes = self.readXDATA( 0x780E, 6 )

		# Build serial number string
		serial = ""
		for i in range(5,0,-1):
			serial += "%02x" % bytes[i]

		# Return serial
		return serial

	def getInfoPage(self):

		# Read XDATA
		data = self.readXDATA( 0x7800, 57 )

		# Get license key

	def getChipInfo(self):

		# Get chip info registers
		chipInfo = self.readXDATA(0x6276, 2)

		# Extract the useful info
		return {
			'flash' : pow(2, 4 + ((chipInfo[0] & 0x70) >> 4)),
			'usb'	: (chipInfo[0] & 0x08) != 0,
			'sram'	: (chipInfo[1] & 0x07) + 1
		}
