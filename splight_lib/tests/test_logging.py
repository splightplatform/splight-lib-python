import os
import pytest
import logging
from splight_lib.logging import (
    SplightLogger,
    getLogger,
    getSplightLogger,
    getComponentLogger,
    standard_output_handler,
)


@pytest.fixture
def logger():
    """This is just a common logger with stdout handler."""
    name = "test"
    level = logging.DEBUG
    logger = SplightLogger(name=name)
    logger.setLevel(level)
    logger.addHandler(standard_output_handler(log_level=level))
    return logger


def test_default_log_level_INFO():
    logger = SplightLogger()
    assert logger.level == logging.INFO


@pytest.mark.skip
@pytest.mark.parametrize("fun", [
    "debug", "info", "warning", "error", "critical"
])
def test_log_massage_and_tags_are_present(caplog, logger, fun):
    msg = f"Testing {fun} level log"
    tags = {fun: "testing"}
    getattr(logger, fun)(msg, tags=tags)
    # TODO: check how to capture log with caplog
    assert msg in caplog.text
    assert tags in caplog.text


def test_exception_log_message_tags_and_trace():
    pass


def test_splight_logger_log_to_file(tmpdir):
    file = tmpdir.mkdir("tmp").join("splight-dev.log")
    os.environ = {"SPLIGHT_DEVELOPER_LOG_FILE": file}

    logger = getSplightLogger()
    msg = "Testing splight dev file handler"
    logger.info(msg)

    with open(file, "r") as f:
        assert msg in f.readline()


def test_component_log_to_stdout_and_file(tmpdir):
    file = tmpdir.mkdir("tmp").join("components.log")
    os.environ = {"SPLIGHT_COMPONENT_LOG_FILE": file}

    logger = getComponentLogger()
    msg = "Testing splight dev file handler"
    logger.info(msg)

    # check stdout
    # TODO: check how to capture log with caplog

    # check file
    with open(file, "r") as f:
        assert msg in f.readline()


# @pytest.mark.parametrize("dev", [True, False])
def test_no_splight_logger_log_to_current_used_file():
    component_logger = getLogger("splight")
    external_logger = logging.getLogger("external")


def test_not_splight_logger_log_with_splight_log_level():
    pass
