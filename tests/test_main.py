import logging


log = logging.getLogger(__name__)


def test_read_container():
    with open('test_data/ExtForm.epf', '+rb') as f:
        log.info(f)
        assert 0
