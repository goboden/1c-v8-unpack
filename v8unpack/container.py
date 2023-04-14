from io import BufferedIOBase
import logging
from pprint import pprint


log = logging.getLogger(__name__)

INT_MAX = 2147483647


class Container:

    def __init__(self, file: BufferedIOBase) -> None:
        self.source = file
        self.header = bytearray()
        self.index = {}

        self._read_index()

    def read(self, begin: int, bytes_to_read: int) -> bytearray:
        self.source.seek(begin)
        return self.source.read(bytes_to_read)

    def _read_index(self):
        index_document = self.read_document(16)
        for i in range(0, len(index_document), 12):
            attributes_address = int.from_bytes(index_document[i: i + 4], byteorder='little', signed=False)
            content_address = int.from_bytes(index_document[i + 4: i + 8], byteorder='little', signed=False)
            if attributes_address == 0:
                break
            attributes_data = self.read_document(attributes_address)
            filename = bytes_to_filename(attributes_data[20:])
            self.index[filename] = content_address

    def read_document(self, address: int) -> bytearray:
        document = bytearray()
        next_block_address = address
        while next_block_address != INT_MAX:
            next_block_address, block = self.read_block(next_block_address)
            document += block
        return document

    def read_block(self, address: int) -> bytearray:
        header = self.read(address, 31)
        if header[0] != 13:
            pass
        # print(f'{len(header)} | {bytearray_repr(header)}')

        # doc_len = bytearray_to_address(header[2:10])
        length = bytearray_to_address(header[11:19])
        next = bytearray_to_address(header[20:28])

        data = self.read(address + 31, length)

        return next, data


def bytearray_to_address(b: bytearray) -> int:
    return int(''.join([chr(byte) for byte in b]), base=16)


def bytes_to_filename(b: bytearray) -> str:
    filename = ''
    for i in range(0, len(b), 2):
        sym = b[i: i + 2]
        filename += chr(int.from_bytes(sym, byteorder='little', signed=False))
    return filename


def bytearray_repr(bytes: bytearray) -> str:
    return ' '.join([hex(byte) for byte in bytes])


if __name__ == '__main__':
    with open('test_data/ExtForm.epf', '+rb') as f:
        con = Container(f)
        con._read_index()

        pprint(con.index)

        # n, c = con.read_document(n)
        
        # print(f'{len(b)} | {bytearray_repr(b)}')
