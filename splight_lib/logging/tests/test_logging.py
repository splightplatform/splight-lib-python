import logging
import os

import pytest

from splight_lib.logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    getLogger,
)
from splight_lib.logging._internal import get_splight_logger
from splight_lib.logging.component import get_component_logger
from splight_lib.logging.logging import SplightLogger, standard_output_handler


@pytest.fixture(scope="session")
def logger():
    """This is just a common logger with stdout handler."""
    # setup logger
    name, level = "test", DEBUG
    logger = SplightLogger(name=name)
    logger.setLevel(level)
    logger.addHandler(standard_output_handler(log_level=logger.level))

    yield logger

    # clean logger
    logger.setLevel(INFO)


@pytest.fixture(autouse=True)
def setup_caplog(caplog, logger):
    logger.addHandler(caplog.handler)


def _get_log_tags(caplog, msg):
    for record in caplog.records:
        if msg in record.message:
            return record.tags
    return None


@pytest.mark.parametrize(
    "logger", [SplightLogger("test"), getLogger(), get_splight_logger()]
)
def test_default_log_level_INFO(logger):
    assert logger.level == INFO


@pytest.mark.parametrize(
    "fun", ["debug", "info", "warning", "error", "critical", "exception"]
)
def test_filename_in_formatter(caplog, logger, fun):
    log = getattr(logger, fun)
    log("Testing filename")
    assert (
        "test:test_logging.py" in caplog.text
        or "test:logging.py" in caplog.text
    )


def test_exception_filename_in_formatter(caplog, logger):
    msg = "Testing filename forcing exception"
    try:
        raise Exception(msg)
    except Exception as e:
        logger.exception(e)
    assert (
        "test:test_logging.py" in caplog.text
        or "test:logging.py" in caplog.text
    )


@pytest.mark.parametrize(
    "fun", ["debug", "info", "warning", "error", "critical"]
)
def test_log_message_and_tags_are_present(caplog, logger, fun):
    msg = f"Testing {fun} level log"
    tags = {"level": fun}
    log = getattr(logger, fun)
    log(msg, tags=tags)
    assert msg in caplog.text
    assert tags == _get_log_tags(caplog, msg)


def test_exception_log_message_tags_and_trace(caplog, logger):
    msg = "Forcing exception just to test"
    tags = {"level": "exception"}
    try:
        raise Exception(msg)
    except Exception as e:
        logger.exception(e, tags=tags)
    assert msg in caplog.text
    assert tags == _get_log_tags(caplog, msg)
    assert "Traceback (most recent call last):" in caplog.text


def test_splight_logger_log_to_stdout(caplog):
    logger = get_splight_logger()
    logger.addHandler(caplog.handler)
    msg = "Testing splight dev file handler"
    logger.info(msg)
    assert msg in caplog.text


@pytest.mark.parametrize("logger_fun", [getLogger, get_component_logger])
def test_component_logger_log_to_stdout_and_file(tmpdir, caplog, logger_fun):
    file = tmpdir.mkdir("tmp").join("components.log")
    os.environ = {"SPLIGHT_COMPONENT_LOG_FILE": file}

    logger = logger_fun()
    logger.addHandler(caplog.handler)
    msg = "Testing splight components file handler"
    tags = {"foo": "bar"}
    logger.info(msg, tags=tags)

    # check stdout
    assert msg in caplog.text
    assert tags == _get_log_tags(caplog, msg)

    # check file
    with open(file, "r") as f:
        line = f.readline()
        assert msg in line
        assert str(tags) in line


def test_no_splight_logger_log_to_stdout(caplog):
    logger = logging.getLogger()
    logger.setLevel(INFO)
    logger.addHandler(caplog.handler)
    msg = "Test log"
    logger.info(msg)
    assert msg in caplog.text


@pytest.mark.parametrize(
    "logger_fun", [getLogger, get_component_logger, get_splight_logger]
)
@pytest.mark.parametrize("level", [DEBUG, INFO, WARNING, ERROR, CRITICAL])
def test_no_splight_logger_change_level_with_splight_logger(level, logger_fun):
    root_logger = logging.getLogger()
    no_root_logger = logging.getLogger("no_root")

    # check default level
    assert (
        root_logger.getEffectiveLevel() == no_root_logger.getEffectiveLevel()
    )

    # check level change with splight logger
    logger = logger_fun()
    logger.setLevel(level)
    assert (
        logger.level
        == root_logger.getEffectiveLevel()
        == no_root_logger.getEffectiveLevel()
    )
