class WrongOSMLFormatEcxeption(Exception):
    def __init__(self, char):
        self.message = f'Wrong OSML format. First char: "{char}"'
        super().__init__(self.message)


class _Parser:
    def __init__(self, osml_string: str):
        self.osml_string = osml_string
        self.position = 0

    def parse(self) -> list:
        char = self._current_char()
        if char == '{':
            self._next()
            return self._parse_folder()
        else:
            raise WrongOSMLFormatEcxeption(char)

    def _parse_folder(self) -> list:
        folder = []
        while self.position < len(self.osml_string):
            char = self._current_char()
            if char in ['\n', '\r', ',']:
                self._next()
                continue

            if char == '"':
                self._next()
                value = self._parse_string()
                folder.append(value)
                continue

            if char == '{':
                self._next()
                value = self._parse_folder()
                folder.append(value)
                self._next()
                continue

            if char == '}':
                self._next()
                return folder

            value = self._parse_value()
            folder.append(value)

        return folder

    def _parse_string(self) -> str:
        value = ''
        while self.position < len(self.osml_string):
            char = self._current_char()
            if char == '"' and self._current_char(1) == '"':
                value += '"'
                self._next(2)
                continue
            elif char == '"':
                self._next()
                return value

            value += char
            self._next()

    def _parse_value(self) -> str:
        value = ''
        while self.position < len(self.osml_string):
            char = self._current_char()
            if char in [',', '}']:
                if char == ',':
                    self._next()
                # -> int?
                return value

            value += char
            self._next()

    def _current_char(self, offset=0):
        return self.osml_string[self.position + offset]

    def _next(self, offset=1):
        self.position += offset


def decode(osml_string: str) -> list:
    parser = _Parser(osml_string)
    return parser.parse()


if __name__ == '__main__':
    from pprint import pprint

    # with open('test_data/index.osml', 'r', encoding='utf-8') as osml_file:
    with open('test_data/index_module.osml', 'r', encoding='utf-8') as osml_file:
        osml_decoded = decode(osml_file.read())
        pprint(osml_decoded)
