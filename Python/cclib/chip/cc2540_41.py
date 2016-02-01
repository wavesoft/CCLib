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

class CC2540_41(object):
	"""
	Chip-specific code for CC2540/41 SOC
	"""

	def __init__(self):
		"""
		"""	

	def testChipID(self, chipID):
		"""
		Check if this ChipID can be handled by this class
		"""
		# Validate chip
		if ((self.chipID & 0xff00) != 0x8d00) and ((self.chipID & 0xff00) != 0x4100):
			raise IOError("This class works ONLY with CC2540/2541 TI chips (This is a 0x%04x)!" % self.chipID)
