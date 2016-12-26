#
# Test for cchex hex files converter
# Copyright (c) 2016 Sjoerd Langkemper
# Copyright (c) 2016 Ioannis Charalampidis
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
import os
import atexit
from tempfile import NamedTemporaryFile

def temp_hexfile(contents):
  """
  Windows cannot share a file created with `NamedTemporaryFile`, therefore
  we are choosing the less secure, yet more portable way of using that
  featuer only to give us a unique temporary file name that will be deleted
  upon exit
  """
  hexfile = NamedTemporaryFile(suffix='.hex', delete=False)
  hexfile.write(contents.encode(encoding='UTF-8'))
  hexfile.close()

  atexit.register(os.unlink, hexfile.name)

  return hexfile.name
