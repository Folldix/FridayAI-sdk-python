import logging


logger = logging.getLogger("tests")


def pytest_runtest_setup(item):
    logger.info("START %s", item.nodeid)


def pytest_runtest_teardown(item):
    logger.info("END   %s", item.nodeid)
