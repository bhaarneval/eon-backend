# import the logging library
import logging
import inspect


# Get an instance of a logger


class Logging:
    """
    This class handles logging
    """

    def __init__(self):
        self.debug_logger = logging.getLogger("debug_logger")
        self.info_logger = logging.getLogger("info_logger")
        self.error_logger = logging.getLogger("error_logger")
        self.warning_logger = logging.getLogger("warning_logger")

    def log_error(self, msg, details=False):
        """
        This method logs error msg
        :param details:
        :param msg:
        :return:
        """
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        if details:
            self.error_logger.error(
                ":: FILE : %s || FUNCTION: %s || DETAILS :: %s \n",
                calframe[1][1],
                calframe[1][3],
                msg,
            )
        else:
            self.error_logger.error("DETAILS :: %s \n", msg, stack_info=True)

    def log_info(self, msg, details=True):
        """
        This method logs info msg
        :param details:
        :param msg:
        :return:
        """
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        if details:
            self.info_logger.info(
                ":: FILE : %s || FUNCTION: %s || DETAILS :: %s \n",
                calframe[1][1],
                calframe[1][3],
                msg,
            )
        else:
            self.info_logger.warning("DETAILS :: %s \n", msg, stack_info=True)

    def log_warning(self, msg, details=True):
        """
        This method logs info msg
        :param details:
        :param msg:
        :return:
        """
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        if details:
            self.warning_logger.warning(
                ":: FILE : %s || FUNCTION: %s || DETAILS :: %s \n",
                calframe[1][1],
                calframe[1][3],
                msg,
            )
        else:
            self.warning_logger.warning("DETAILS :: %s \n", msg)
