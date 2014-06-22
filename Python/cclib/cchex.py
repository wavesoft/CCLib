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

def toHex(data):
	"""
	Utility function to convert a buffer to hexadecimal
	"""
	return "".join( "%02x" % x for x in data )

def fromHex(data,offset=0,step=2):
	"""
	Utility function to convert a hexadecimal string to buffer
	"""
	return bytearray([ int(data[x:x+2],16) for x in range(offset,len(data),step) ])

def hexdump(src, length=8):
	"""
	Utility function to perform hex-dumps
	"""
	result = []
	digits = 4 if isinstance(src, unicode) else 2
	for i in xrange(0, len(src), length):
		s = src[i:i+length]
		hexa = b' '.join(["%0*X" % (digits, x)  for x in s])
		text = b''.join([chr(x) if 0x20 <= x < 0x7F else b'.'  for x in s])
		result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
	return b'\n'.join(result)

class CCMemBlock:
	"""
	Memory blocks
	"""

	def __init__(self, addr=None):
		"""
		Initialize memory block
		"""
		self.addr = addr
		self.size = 0
		self.bytes = bytearray()

	def contains(self, addr, size):
		"""
		Check if memory block contains the given address
		"""

		# Check bundaries
		return (addr >= self.addr) and ((addr+size) <= (self.addr+self.size))

	def isContinuous(self, addr):
		"""
		Check if it's continuous
		"""
		if self.addr == None:
			self.addr = addr
			self.size = 0
			return True
		else:
			return ((self.addr + self.size) == addr)

	def set(self, offset, bytes):
		"""
		Update bock bytes
		"""
		#print "Replacing @ %04x (%i):" % (offset, len(bytes))
		#print "<-", "".join(["%02x" % x for x in self.bytes[offset:offset+len(bytes)]])
		self.bytes[offset:offset+len(bytes)] = bytes
		#print "->", "".join(["%02x" % x for x in self.bytes[offset:offset+len(bytes)]])

	def stack(self, bytes):
		"""
		Stack bytes to the memory block
		"""
		self.size += len(bytes)
		self.bytes += bytes

	def __repr__(self):
		return "<MemBlock @ 0x%04x (%i Bytes)>" % (self.addr, self.size)

class CCHEXFile:
	"""
	Utility class for reading/writing Intel HEX files
	"""

	def __init__(self, filename):
		"""
		Initialize the HEX file parser/reader
		"""
		self.filename = filename
		self.memBlocks = []

	def load(self):
		"""
		Load file
		"""
		self._loadHex()

	def set(self, addr, bytes):
		"""
		Update a memory region 
		"""

		# Try to find a block that contains
		# the target region
		for b in self.memBlocks:
			if b.contains(addr, len(bytes)):
				b.set(addr - b.addr, bytes)
				return

		# If none found, create new block
		targetBlock = CCMemBlock(addr)
		targetBlock.stack(bytes)

	def _checksum(self, bytes):
		"""
		Calculate the checksum byte of the line
		"""
		# Sum
		val = sum(bytes) & 0xFF
		# Two's coplement
		val = 0xFF - val + 1
		# Return
		return val & 0xFF

	def _saveHex(self):
		"""
		Save destination file in HEX format
		"""

		# Open target file
		with open(self.filename, "w") as f:

			def _write(bytes):

				# Prepend size of data field
				dlen = len(bytes) - 3
				bytes = [dlen] + bytes

				# Append checksum
				bytes += [self._checksum(bytes)]

				# Write to file
				f.write(":%s\n" % toHex(bytes))

			# Handle memory blocks
			for mb in self.memBlocks:

				# Define offset address
				b = [ 0x00, 0x00, 0x04, (mb.addr >> 8) & 0xFF, mb.addr & 0xFF ]

	def _loadHex(self):
		"""
		Load source file in HEX format
		"""

		# Prepare memory block
		mb = CCMemBlock()
		self.memBlocks = []

		# Open source file
		i = 0
		with open(self.filename, "r") as f:

			# Base address
			baseAddress = 0x00

			# Scan lines
			for line in f.readlines():
				i += 1

				# Trim ending newline
				line = line[0:-1]

				# Validate format
				if not line[0:1] == ":":
					raise IOError("Line %i: Source file is not in HEX format!" % i)

				# Convert input line to bytes
				bytes = [ int(line[x:x+2],16) for x in range(1,len(line),2) ]
				csum = bytes.pop()

				# Validate checksum
				c1 = self._checksum(bytes)
				if self._checksum(bytes) != csum:
					raise IOError("Line %i: Checksum error" % i)

				# Get sub-fields
				bCount = bytes.pop(0)
				aHi = bytes.pop(0)
				aLo = bytes.pop(0)
				bAddr = (aHi << 8) | aLo
				bType = bytes.pop(0)

				# Check for end-of-file
				if bType == 0x01:
					break

				# Check for address shift records
				elif bType == 0x02:
					baseAddress = ((bytes[0] << 8) | bytes[1]) << 4
				elif bType == 0x04:
					baseAddress = ((bytes[0] << 8) | bytes[1]) << 16

				# Check for data
				elif bType == 0x00:

					# Apply base address shift
					bAddr |= baseAddress

					# Check if we are continuing
					if mb.isContinuous(bAddr):
						mb.stack(bytearray(bytes))
					else:
						self.memBlocks.append(mb)
						mb = CCMemBlock(bAddr)

					#print "0x%06x : " % bAddr, "".join( "%02x " % x for x in bytes )

				# Everything else raise error
				else:
					raise IOError("Line %i: Unknown record type %02x" % (i, bType))

			# Stack rest
			self.memBlocks.append(mb)
