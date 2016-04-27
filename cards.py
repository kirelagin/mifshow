#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Iterable, Sized, Container, Sequence

import utils


class Sector(Sequence):
    def __init__(self, data):
        self._data = data

        trailer = self._data[16*3:64]
        b7, b8 = trailer[7:9]
        c = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        for i in range(4):
            c[3-i][0] = (b7 >> 7-i) & 0x01
        for i in range(4):
            c[3-i][2] = (b8 >> 7-i) & 0x01
        for i in range(4):
            c[3-i][1] = (b8 >> 3-i) & 0x01
        self._permissions_bits = c

        self._keyB_usable = c[3] not in ([0,0,0],[0,1,0],[0,0,1])

    @property
    def pretty(self):
        d = self._data
        lines = map(utils.hexbytes, [d[i:i+16] for i in range(0, len(d), 16)])
        return '\n'.join(map(' '.join, lines))

    @abstractproperty
    def keys(self):
        return None


    def __len__(self):
        return self._data.__len__()

    def __contains__(self):
        return self._data.__contains__()

    def __getitem__(self):
        return self._data.__getitem__()

class MifareClassic1kSector(Sector):
    @property
    def pretty(self):
        c = self._permissions_bits

        lines = []
        for i in range(3):
            block = self._block(i)
            access_str = 'A: '
            access_str += 'r' if c[i] not in ([0,1,1],[1,0,1],[1,1,1],) else '-'
            access_str += 'w' if c[i] in ([0,0,0],) else '-'
            access_str += 'd' if c[i] in ([0,0,0],[1,1,0],[0,0,1],) else '-'
            if self._keyB_usable:
                access_str += ', B: '
                access_str += 'r' if c[i] not in ([1,1,1],) else '-'
                access_str += 'w' if c[i] in ([0,0,0],[1,0,0],[1,1,0],[0,1,1],) else '-'
                access_str += 'd' if c[i] in ([0,0,0],[1,1,0],[0,0,1],) else '-'

            extra = None
            if   (c[i] == [0,0,0]):
                extra = 'transport'
            elif (c[i] in ([0,1,0],[1,0,1])):
                extra = 'RO'
            elif (c[i] == [0,0,1]):
                extra = 'non-rechargeable'
            elif (c[i] == [1,1,1]):
                extra = 'no access'
            if extra:
                access_str += utils.coloured(utils.Colour.CYAN, ' -- ' + extra)
            if c[i] in ([1,1,0], [0,0,1]): # value
                val = utils.mif_value(self._block(i))
                if val is not None:
                    lines.append('{} {:<62}  ({})'.format(utils.coloured(utils.Colour.BLUE, 'VALUE:'), '{} adr={}'.format(*val), access_str))
                else:
                    lines.append('{}  [ {} ]  ({}) {}'.format(' '.join(utils.hexbytes(block)), utils.chrbytes(block), access_str, utils.coloured(utils.Colour.RED, '!VALUE')))
            else:
                lines.append('{}  [ {} ]  ({})'.format(' '.join(utils.hexbytes(block)), utils.chrbytes(block), access_str))

        trailer = utils.hexbytes(self._block(3))
        extra = []
        if c[3] == [0,0,1]:
            extra = ['transport']
        if c[3] not in ([0,0,0],[1,0,0],[0,0,1],[0,1,1]):
            extra.append('keys blocked')
        if c[3] not in ([0,0,1],[0,1,1],[1,0,1]):
            extra.append('access bits blocked')
        if extra:
            extra = '  ( ' + utils.coloured(utils.Colour.CYAN, '-- ' + ', '.join(extra)) + ')'
        else:
            extra = ''
        lines.append(' '*27 + trailer[9] + ' ' + (' '.join(trailer[10:]) if not self._keyB_usable else ' '*17) + ' ' * 22 + extra)

        def col(k):
            if k not in utils.mfoc_default_keys:
                return utils.coloured(utils.Colour.RED, k, highlighted=True)
            else:
                return k
        lines.append('')
        acc_bits = 'Access bits:      ' + ' '.join(trailer[6:9])
        acc_bits += '  (r: A'
        acc_bits += 'B' if c[3] not in ([0,0,0],[0,1,0],[0,0,1]) else '-'
        acc_bits += ', w: '
        acc_bits += 'A' if c[3] == [0,0,1] else '-'
        acc_bits += 'B' if c[3] in ([0,1,1],[1,0,1]) else '-'
        acc_bits += ')'
        lines.append(acc_bits)
        keyA = 'Key A: ' + col(''.join(trailer[:6]))
        keyA += '         (r: --, w: '
        keyA += 'A' if c[3] in ([0,0,0],[0,0,1]) else '-'
        keyA += 'B' if c[3] in ([1,0,0],[0,1,1]) else '-'
        keyA += ')'
        lines.append(keyA)
        if self._keyB_usable:
            keyB = 'Key B: ' + col(''.join(trailer[10:]))
            keyB += '         (r: --, w: -'
            keyB += 'B' if c[3] in ([1,0,0],[0,1,1]) else '-'
            keyB += ')'
            lines.append(keyB)
        return '\n'.join(lines)

    @property
    def keys(self):
        keys = {self._data[16*3:16*3+6],}
        if self._keyB_usable: keys |= {self._data[16*3+10:],}
        return keys

    def _block(self, i):
        return self._data[i*16:i*16+16]


class MifareCard(Sequence):
    def __init__(self, f):
        self._data = f.read()

        offset = 0
        self._sectors = []
        for l, f in self.layout:
            self._sectors.append(f(self._data[offset:offset+l]))
            offset += l


    @abstractproperty
    def layout(self):
        return None

    @property
    def sectors(self):
        return self._sectors


    def __len__(self):
        return self.sectors.__len__()

    def __contains__(self, v):
        return self.sectors.__contains__(v)

    def __getitem__(self, i):
        return self.sectors.__getitem__(v)


class MifareClassic1k(MifareCard):
    @property
    def layout(self):
        f = lambda d: MifareClassic1kSector(d)
        return [(64, f)] * 16
