import logging
import logging.config
from logtail import LogtailHandler

LOGGER = logging.getLogger(__name__)
handler = LogtailHandler(source_token="FaKeNoewAeGNJaxmVLKghFCS")
LOGGER.handlers = []
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(handler)

