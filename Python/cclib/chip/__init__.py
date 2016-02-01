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

class ChipDriver(CCLibProxy):
	"""
	Base class for implementing chip drivers that subclasses CCLibProxy 
	in order to have a simple API all the way to the serial port.
	"""

	def __init__(self, proxy):
		"""
		Construct a new chip driver
		"""
		# Initialize proxy subclass
		CCLibProxy.__init__(self, parent=proxy)

	@staticmethod
	def test(cls, chipID):
		"""
		Check if this ChipID can be handled by this class
		"""
		raise NotImplementedError("This function is not implemented!")

	def chipName(self):
		"""
		Return chip name
		"""
		raise NotImplementedError("This function is not implemented!")

	def initialize(self):
		"""
		Initialize proxy and/or chip and return True if everything was successful
		"""
		raise NotImplementedError("This function is not implemented!")

	###############################################
	# Interface Functions
	###############################################

	def getSerial(self):
		"""
		Read the serial number from the Chip
		"""
		raise NotImplementedError("This function is not implemented!")

	def getChipInfo(self):
		"""
		Analyze chip info registers
		"""
		raise NotImplementedError("This function is not implemented!")

	def pauseDMA(self, pause):
		"""
		Pause/Unpause DMA in debug mode
		"""
		raise NotImplementedError("This function is not implemented!")

	def readCODE( self, offset, size ):
		"""
		Read and return any-sized buffer from the CODE region
		"""
		raise NotImplementedError("This function is not implemented!")

	def writeCODE(self, offset, data, erase=False, verify=False, showProgress=False):
		"""
		Fully automated function for writing the Flash memory.
		"""
		raise NotImplementedError("This function is not implemented!")

	def readXDATA( self, offset, size ):
		"""
		Read any size of buffer from the XDATA region
		"""
		raise NotImplementedError("This function is not implemented!")

	def writeXDATA( self, offset, bytes ):
		"""
		Write any size of buffer in the XDATA region
		"""
		raise NotImplementedError("This function is not implemented!")
