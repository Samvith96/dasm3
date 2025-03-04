# Copyright 2009 Michael Heyeck
# This file is part of dasm3.py.
#
# dasm3.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# dasm3.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dasm3.py.  If not, see <http://www.gnu.org/licenses/>.



import  struct

class MzHeader:
    _fields = [('c', '%c',          'SigChar0'),
               ('c', '%c',          'SigChar1'),
               ('h', '%d',          'BytesOnLastPage'),
               ('h', '%d (*512)',   'PagesInExe'),
               ('h', '%d',          'RelocationCount'),
               ('h', '%d (*16)',    'ParagraphsInHeader'),
               ('h', '%d (*16)',    'MinAddlParagraphs'),
               ('h', '%d (*16)',    'MaxAddlParagraphs'),
               ('h', '0x%04x',      'InitialRelativeSS'),
               ('h', '0x%04x',      'InitialSP'),
               ('h', '0x%04x',      'Checksum'),
               ('h', '0x%04x',      'InitialIP'),
               ('h', '0x%04x',      'InitialRelativeCS'),
               ('h', '0x%04x',      'RelocationOffset'),
               ('h', '%d',          'OverlayNumber')]

    def __init__ (self, fn):
        self._fn = fn
        fmt = '<' + ''.join ([p[0] for p in self._fields])
        data = struct.unpack_from (fmt, open(self._fn, 'rb').read (struct.calcsize(fmt)))
        for i in range (len (self._fields)): setattr (self, self._fields[i][2], data[i])

    def print_table (self):
        col_len = max (len (p[2]) for p in self._fields)
        print('\n'.join (('%-*s: ' + p[1]) % (col_len, p[2], getattr (self, p[2])) for p in self._fields))

    def check_signature (self):
        # The first two bytes in an MZ header are always 'M' and 'Z'
        return self.SigChar0 + self.SigChar1 == 'MZ'

    def calc_length (self):
        # Find the overall length of the executable, including all headers
        if self.BytesOnLastPage:
            # A non-zero BytesOnLastPage means the final 512-byte page is only partially used
            return (self.PagesInExe - 1) * 0x200 + self.BytesOnLastPage
        else:
            return self.PagesInExe * 0x200

    def calc_code_start (self):
        # Return the file offset of the start of machine code and program data
        return self.ParagraphsInHeader * 16

    def calc_first_instruction_offset (self):
        # Return the file offset of the first instruction executed when the program runs
        return self.calc_code_start () + self.InitialRelativeCS * 16 + self.InitialIP

