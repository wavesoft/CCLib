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

class CCHEXFile:
	"""
	Utility class for reading/writing Intel HEX files
	"""

	def __init__(self, filename):
		"""
		Initialize the HEX file parser/reader
		"""
		self.filename = filename

	def _checksum(self, bytes):
		"""
		Calculate the checksum byte of the line
		"""

	def _loadHex(self):
		"""
		Load source file in HEX format
		"""

		# Open source file
		i = 0
		with open(self.filename, "w") as f:

			# Scan lines
			for line in f.readlines():
				i += 1

				# Validate format
				if not line[0:1] == ":":
					raise IOError("Source file is not in HEX format!")

				# Convert input line to bytes
				lineBytes = []
				for j in range(0,len(line)-1,2):
					lineBytes.append( int(line[j+1:2], 16) )

