import logging
import logging.config


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


for log_name, log_obj in logging.Logger.manager.loggerDict.items():
     if log_name != __name__:
          log_obj.disabled = True