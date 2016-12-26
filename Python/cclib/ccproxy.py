#
# CCLib_proxy Interface Library for High-Level operations
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
import sys
import time
import glob
import serial
import serial.tools.list_ports

# Command constants
CMD_ENTER     = 0x01
CMD_EXIT      = 0x02
CMD_CHIP_ID   = 0x03
CMD_STATUS    = 0x04
CMD_PC        = 0x05
CMD_STEP      = 0x06
CMD_EXEC_1    = 0x07
CMD_EXEC_2    = 0x08
CMD_EXEC_3    = 0x09
CMD_BRUSTWR   = 0x0A
CMD_RD_CFG    = 0x0B
CMD_WR_CFG    = 0x0C
CMD_CHPERASE  = 0x0D
CMD_RESUME    = 0x0E
CMD_HALT      = 0x0F
CMD_PING      = 0xF0
CMD_INSTR_VER = 0xF1
CMD_INSTR_UPD = 0xF2

# Response constants
ANS_OK       = 0x01
ANS_ERROR    = 0x02
ANS_READY    = 0x03

class CCLibProxy:
	"""
	CCLib_proxy interface class that provides the high-level API for communicating
	with the arduino board.

	Because the CCLib_proxy was used for experimentation with the CCDebugger protocol,
	all the higher-level logic is implemented in this class. In order to cope with the
	performance issues, a binary serial protocol was used.
	"""

	def __init__(self, port=None, parent=None, enterDebug=False):
		"""
		Initialize the CCLibProxy class
		"""

		# If we are subclassing, just adopt properties
		if not parent is None:

			# Subclass all properties
			self.ser = parent.ser
			self.port = parent.port
			self.chipID = parent.chipID
			self.debugStatus = parent.debugStatus
			self.debugConfig = parent.debugConfig
			self.instructionTableVersion = parent.instructionTableVersion

		else:

			# If we don't have a port specified perform autodetect
			if port is None or port == 'auto':
				self.detectPort()

			else:
				# Open port
				try:
					self.ser = serial.Serial(port)
					self.port = port
				except:
					raise IOError("Could not open port %s" % port)

				# Ping
				try:
					self.ping()
				except IOError:
					raise IOError("Could not find CCLib_proxy device on port %s" % self.ser.name)

			# Check if we should enter debug mode
			if enterDebug:
				self.enter()

			# Get instruction table version
			self.instructionTableVersion = self.getInstructionTableVersion()

			# Get chip info & ID
			self.chipID = self.getChipID()
			self.debugStatus = self.getStatus()
			self.debugConfig = self.readConfig()

	def detectPort(self):
		"""
		Iterate over system COM ports in order to locate a port that the proxy
		responds upon.
		"""
		print("NOTE: Performing auto-detection (use -p to specify port manually)")

		# Prioritize known ports, since on linux and osx scanning
		# weird ports will cost more
		ports = []
		priority_names =  ['acm', 'usb', 'ttys']
		all_ports = list(serial.tools.list_ports.comports())
		for name in priority_names:
			for i in range(0, len(all_ports)):
				if name.lower() in all_ports[i][0]:
					ports.append(all_ports[i])
					all_ports.pop(i)
		ports += all_ports

		# Try to ping each one
		for port in ports:
			try:
				print("INFO: Checking %s" % port[0])
				self.ser = serial.Serial(port[0])

				# If ping fails, we will get an exception
				self.sendFrame(CMD_PING)
				self.port = port[0]
				return

			except:
				try:
					self.ser.close()
				except:
					pass
				self.ser = None

		# No port defined? Raise an exception
		raise IOError("Could not detect a CCLib_proxy connected on any serial port")

	###############################################
	# Low-level functions
	###############################################

	def readFrame(self, raiseException=True):
		"""
		Read and translate the 3-byte response frame from arduino
		"""

		# Read response frame
		b = self.ser.read()
		if len(b) == 0:
			raise IOError("Could not read from the serial port!")
		status = ord(b)
		b = self.ser.read()
		if len(b) == 0:
			raise IOError("Could not read from the serial port!")
		bH = ord(b)
		b = self.ser.read()
		if len(b) == 0:
			raise IOError("Could not read from the serial port!")
		bL = ord(b)

		# Handle error responses
		if status == ANS_ERROR:
			if raiseException:
				if bL == 0x01:
					raise IOError("CCDebugger is not properly initialized. Check your arduino sketch!")
				elif bL == 0x02:
					raise IOError("The chip is not in debug mode! Use the '-E' option (--help for more)")
				elif bL == 0x03:
					raise IOError("The chip is not responding. Check your connection and/or wiring!")
				else:
					raise IOError("CCDebugger responded with an error (0x%02x)" % bL)
			else:
				return -bL

		# Check for responses other than OK
		elif status != ANS_OK:

			# Ready is a special case
			if status == ANS_READY:
				return ANS_READY
			else:
				raise IOError("CCDebugger responded with an unknown status (0x%02x)" % status)

		# Otherwise we are good
		return (bH << 8) | bL

	def sendFrame(self, cmd, c1=0, c2=0 ,c3=0, raiseException=True ):
		"""
		Send the specified frame to the output queue
		"""

		# Send the 4-byte command frame
		self.ser.write( chr(cmd)+chr(c1)+chr(c2)+chr(c3) )
		self.ser.flush()

		# Read frame
		return self.readFrame(raiseException)

	###############################################
	# Debug-level functions
	###############################################

	def ping(self):
		"""
		Send a PING frame
		"""

		# This will raise an exception on error
		self.sendFrame(CMD_PING)
		return True

	def enter(self):
		"""
		Enter in debug mode
		"""
		return self.sendFrame(CMD_ENTER)

	def exit(self):
		"""
		Exit from debug mode by resuming the CPU
		"""
		status = self.sendFrame(CMD_EXIT)

		# Update debug status
		self.debugStatus = status
		return status

	def readConfig(self):
		"""
		Read debug configuration
		"""
		return self.sendFrame(CMD_RD_CFG)

	def writeConfig(self, config):
		"""
		Read debug configuration
		"""
		ans = self.sendFrame(CMD_WR_CFG, config)

		# Update local variables
		self.debugConfig = config
		self.debugStatus = ans
		return ans

	def step(self):
		"""
		Step a single instruction
		"""
		return self.sendFrame(CMD_STEP)

	def resume(self):
		"""
		resume program exec
		"""
		return self.sendFrame(CMD_RESUME)

	def halt(self):
		"""
		halt program exec
		"""
		return self.sendFrame(CMD_HALT)

	def getChipID(self):
		"""
		Return the ChipID as read from the chip
		"""
		return self.sendFrame(CMD_CHIP_ID)

	def getStatus(self):
		"""
		Return the debug status
		"""
		ans = self.sendFrame(CMD_STATUS)

		# Update local variables
		self.debugStatus = ans
		return ans

	def getPC(self):
		"""
		Return the program counter position
		"""
		return self.sendFrame(CMD_PC)

	def instr(self, c1, c2=None, c3=None):
		"""
		Execute a debug instruction
		"""

		# Call the appropriate instruction according
		# to the number of bytes
		if (c2 == None):
			return self.sendFrame(CMD_EXEC_1, c1)
		elif (c3 == None):
			return self.sendFrame(CMD_EXEC_2, c1, c2)
		else:
			return self.sendFrame(CMD_EXEC_3, c1, c2, c3)

	def instri(self, c1, i1):
		"""
		Execute a debug instruction with 16-bit constant
		"""

		# Split short in high/low order bytes
		cHigh = (i1 >> 8) & 0xFF
		cLow = (i1 & 0xFF)

		# Send instruction
		return self.sendFrame(CMD_EXEC_3, c1, cHigh, cLow)

	def brustWrite(self, data):
		"""
		Perform a brust-write operation which allows us to write
		up to 2Kb in the DBGDATA register.
		"""

		# Validate length
		length = len(data)
		if length > 2048:
			return False

		# Split length in high/low order bytes
		cHigh = (length >> 8) & 0xFF
		cLow = (length & 0xFF)

		# Prepare for BRUST frame transmission
		ans = self.sendFrame(CMD_BRUSTWR, cHigh, cLow)
		if ans != ANS_READY:
			raise IOError("Unable to prepare for brust-write! (Unknown response 0x%02x)" % ans)

		# Start sending data
		self.ser.write(data)
		self.ser.flush()

		# Handle response & update debug status
		self.debugStatus = self.readFrame()
		return self.debugStatus

	def chipErase(self):
		"""
		Perform a chip erase
		"""

		# Re-enter debug mode
		self.enter()

		# Send chip erase command & update debug status
		self.debugStatus = self.sendFrame(CMD_CHPERASE)

		# Wait until CHIP_ERASE_BUSY goes down
		s = self.getStatus()
		while (( s & 0x80 ) != 0):
			time.sleep(0.01)
			s = self.getStatus()

		# We are good
		self.debugStatus = s
		return self.debugStatus

	def getInstructionTableVersion(self):
		"""
		Get CC.Debugger instruction table version
		"""
		return self.sendFrame(CMD_INSTR_VER)

	def updateInstructionTable(self, version, instr):
		"""
		Update CC.Debugger instruction table
		"""

		# Check limits
		if len(instr) > 15:
			raise IOError("Invalid size of the instruction table! It must be smaller than 16")

		# Insert version
		table = [version] + list(instr)

		# Append zeroes if table is smaller than 16
		if len(table) < 16:
			table += [0] * (16 - len(table))

		# Express our interest to update the instruction table
		ans = self.sendFrame(CMD_INSTR_UPD)
		if ans != ANS_READY:
			raise IOError("Unable to prepare for instruction table update! (Unknown response 0x%02x)" % ans)

		# Start sending data
		for b in table:
			self.ser.write(chr(b & 0xFF))
		self.ser.flush()

		# Get confirmation
		newVersion = self.readFrame()
		if newVersion != version:
			raise IOError("Unable to update the instruction table! (Unknown response 0x%02x)" % ans)

		# Return new version
		self.instructionTableVersion = newVersion
		return newVersion
