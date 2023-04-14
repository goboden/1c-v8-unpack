import v8unpack.container as container

import logging


log = logging.getLogger(__name__)


def test_read_container():
    with open('test_data/ExtForm.epf', '+rb') as f:
        container.read_fragment(f, 0, 10)
        assert 1
