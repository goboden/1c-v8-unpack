from typing import BinaryIO
import zlib
import logging

import osml


log = logging.getLogger(__name__)

INT_MAX = 2147483647


class WrongBlockHeaderException(Exception):
    def __init__(self, first_byte) -> None:
        self.message = f'Wrong first header byte {str(first_byte)}'
        super().__init__(self.message)


class FileNotFoundInIndexException(Exception):
    def __init__(self, filename):
        self.message = f'File "{filename}" is not found in container index'
        super().__init__(self.message)


class Block:
    def __init__(self) -> None:
        self.document_length: int = 0
        self.length: int = 0
        self.next_block_address: int = 0
        self.data: bytes = bytes()

    @staticmethod
    def _address(bytes_in: bytes) -> int:
        return int(''.join([chr(byte) for byte in bytes_in]), base=16)

    def read_header(self, header: bytes):
        self.document_length = self._address(header[2:10])
        self.length = self._address(header[11:19])
        self.next_block_address = self._address(header[20:28])


class Container:
    def __init__(self, file: BinaryIO):
        self.source = file
        self.header = bytes()
        self.index: dict[str, int] = {}
        self.metadata_id: str = ''
        self.metadata: list = []

        self._read_index()
        # self._read_metadata()

    def read(self, begin: int, bytes_to_read: int) -> bytes:
        self.source.seek(begin)
        return self.source.read(bytes_to_read)

    def _read_index(self):
        index_document = self.read_document(16)
        for i in range(0, len(index_document), 12):
            attributes_address = int.from_bytes(index_document[i: i + 4], byteorder='little')
            content_address = int.from_bytes(index_document[i + 4: i + 8], byteorder='little')
            if attributes_address == 0:
                break
            attributes_data = self.read_document(attributes_address)
            filename = bytes_to_filename(attributes_data[20:])
            self.index[filename] = content_address

    def _read_metadata(self):
        root_file = self.read_file('root')
        root = osml.decode(root_file.decode(encoding='utf-8-sig'))
        metadata_filename = root[1]
        metadata_file = self.read_file(metadata_filename)

        self.metadata = osml.decode(metadata_file.decode(encoding='utf-8-sig'))
        self.metadata_id = self.metadata[3][0]

    def read_document(self, address: int) -> bytes:
        document = bytes()
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
            raise WrongBlockHeaderException(header[0])
        block.read_header(header)
        block.data = self.read(address + 31, block.length)

        return block

    def read_file(self, filename: str, deflate: bool = True) -> bytes:
        if filename not in self.index:
            raise FileNotFoundInIndexException(filename)
        file_address = self.index[filename]
        file_data = self.read_document(file_address)
        if deflate:
            file_data = zlib.decompress(file_data, wbits=-zlib.MAX_WBITS)
        return file_data


def bytes_to_address(bytes_in: bytes) -> int:
    return int(''.join([chr(byte) for byte in bytes_in]), base=16)


def bytes_to_filename(bytes_in: bytes) -> str:
    filename = ''
    for i in range(0, len(bytes_in), 2):
        filename += chr(int.from_bytes(bytes_in[i: i + 2], byteorder='little'))
    return filename[:-2]


def bytearray_repr(bytes_in: bytes) -> str:
    return ' '.join([hex(byte) for byte in bytes_in])


def file_is_container(file_data: bytes) -> bool:
    return int.from_bytes(file_data[:4], byteorder='little') == INT_MAX


if __name__ == '__main__':
    with open('test_data/ExtForm.epf', '+rb') as f:
        try:
            from pprint import pprint

            con = Container(f)
            # pprint(con.index)
            # pprint(con.metadata)
            # pprint(con.metadata[1])

            # pprint(con.metadata[3][1])
            # pprint(con.metadata[3][1][1][3][1][1][2])
            # pprint(con.metadata)
            # pprint(con.metadata_id)
            # pprint(metadata.METADATA[con.metadata_id]['forms'])

            # d = con.read_file('dc0ab8e3-733d-4741-8ef6-682a5c43fafc.0')
            # print(file_is_container(d))
            # d = con.read_file('f894cf26-3fd1-4688-bf8c-098944f6b435.0')
            # print(file_is_container(d))
            # # print(d.decode())
            # osml_decoded = osml.decode(d.decode(encoding='utf-8-sig'))
            # pprint(osml_decoded)

            # # container
            # d = con.read_file('dc0ab8e3-733d-4741-8ef6-682a5c43fafc.0')
            # c2 = Container(BytesIO(d))
            # print(c2.index)
            # d2 = c2.read_file('module', False)
            # print(d2.decode())
            # # osml_decoded = osml.decode(d2.decode())
            # # print(osml_decoded)

            # d = con.read_file('f894cf26-3fd1-4688-bf8c-098944f6b435.0')
            # print(d.decode())

            # d = con.read_file('7f880901-628f-4c26-b8b6-351c578879ab')
            # print(d.decode())

            # res = osml.decode(d.decode())
            # pprint(res)

        except FileNotFoundInIndexException as e:
            print(e.message)

        # n, c = con.read_document(n)

        # print(f'{len(b)} | {bytearray_repr(b)}')
