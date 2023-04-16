from io import BufferedIOBase
import zlib
import logging
from pprint import pprint


log = logging.getLogger(__name__)

INT_MAX = 2147483647


class WrongBlockHeaderException(Exception):
    pass


class FileNotFoundInIndexException(Exception):
    def __init__(self, filename):
        self.message = f'File "{filename}" is not found in container index'
        super().__init__(self.message)


class Block:
    def __init__(self):
        self.document_length: int
        self.length: int
        self.next_block_address: int
        self.data: bytearray

    def read_header(self, header: bytearray):
        self.document_length = bytes_to_address(header[2:10])
        self.length = bytes_to_address(header[11:19])
        self.next_block_address = bytes_to_address(header[20:28])


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
        document_length = 0
        next_block_address = address

        while next_block_address != INT_MAX:
            block = self.read_block(next_block_address)
            next_block_address = block.next_block_address
            document += block.data
            if block.document_length != 0:
                document_length = block.document_length
        return document[:document_length]

    def read_block(self, address: int) -> Block:
        block = Block()

        header = self.read(address, 31)
        if header[0] != 13:
            raise WrongBlockHeaderException
        block.read_header(header)
        block.data = self.read(address + 31, block.length)

        return block

    def read_file(self, filename: str, deflate: bool = True) -> bytearray:
        if filename not in self.index:
            raise FileNotFoundInIndexException(filename)
        file_address = self.index[filename]
        file_data = self.read_document(file_address)
        if deflate:
            file_data = zlib.decompress(file_data, wbits=-zlib.MAX_WBITS)
        return file_data


def bytes_to_address(bytes: bytearray) -> int:
    return int(''.join([chr(byte) for byte in bytes]), base=16)


def bytes_to_filename(bytes: bytearray) -> str:
    filename = ''
    for i in range(0, len(bytes), 2):
        filename += chr(int.from_bytes(bytes[i: i + 2], byteorder='little', signed=False))
    return filename[:-2]


def bytearray_repr(bytes: bytearray) -> str:
    return ' '.join([hex(byte) for byte in bytes])


if __name__ == '__main__':
    with open('test_data/ExtForm.epf', '+rb') as f:
        con = Container(f)
        try:
            d = con.read_file('root')
            pprint(d)
        except FileNotFoundInIndexException as e:
            print(e.message)

        # n, c = con.read_document(n)

        # print(f'{len(b)} | {bytearray_repr(b)}')
