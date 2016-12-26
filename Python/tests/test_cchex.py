#
# Test for cchex hex files converter
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

from cclib.cchex import CCHEXFile
from unittest import TestCase
from tempfile import NamedTemporaryFile
from binascii import unhexlify


def temp_hexfile(contents):
    hexfile = NamedTemporaryFile(suffix='.hex')
    hexfile.write(contents.encode(encoding='UTF-8'))
    hexfile.seek(0)
    return hexfile


class TestCCHEXFile(TestCase):
    def test_load_creates_correct_single_memblock(self):
        offset = "0100"
        data = "214601360121470136007EFE09D21901"
        checksum = "40"
        with temp_hexfile(":10" + offset + "00" + data + checksum + "\n") as hexfile:
            cchex = CCHEXFile()
            cchex.load(hexfile.name)

            assert len(cchex.memBlocks) == 1
            memBlock = cchex.memBlocks[0]
            assert memBlock.addr == int(offset, 16)
            assert memBlock.bytes == unhexlify(data)

    def test_load_creates_correct_noncontinuous_memblocks(self):
        lines = [
            ":10010000" + "7F" * 16 + "FF\n",
            ":10050000" + "3D" * 16 + "1B\n",
        ]
        with temp_hexfile("".join(lines)) as hexfile:
            cchex = CCHEXFile()
            cchex.load(hexfile.name)

            assert len(cchex.memBlocks) == 2
            assert cchex.memBlocks[0].addr == 0x0100
            assert cchex.memBlocks[0].bytes == b"\x7F" * 16
            assert cchex.memBlocks[1].addr == 0x0500
            assert cchex.memBlocks[1].bytes == b"\x3D" * 16
