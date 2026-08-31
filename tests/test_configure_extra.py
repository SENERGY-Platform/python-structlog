#  Copyright 2026 InfAI (CC SES)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
import itertools
import json
import logging
import unittest

import structlog

logging.setLoggerClass(structlog.Logger)

_names = itertools.count()


def _logger(**configure_kwargs):
    """
    A logger writing to a buffer. Each call gets its own name, because
    logging.getLogger caches by name and a reused one would keep the previous
    test's handlers and configuration.
    """
    buffer = io.StringIO()
    logger = logging.getLogger("test_configure_extra_%d" % next(_names))
    logger.propagate = False
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.configure(**configure_kwargs)
    return logger, buffer


def _line(buffer):
    return json.loads(buffer.getvalue().strip().splitlines()[-1])


class TestConfigureExtra(unittest.TestCase):
    def test_extra_appears_on_every_line(self):
        logger, buffer = _logger(project_name="p", organization_name="o",
                                 extra={"smart_service_instance_id": "8fbd0e8a"})
        logger.warning("first")
        self.assertEqual("8fbd0e8a", _line(buffer)["smart_service_instance_id"])
        logger.error("second")
        self.assertEqual("8fbd0e8a", _line(buffer)["smart_service_instance_id"])

    def test_child_logger_inherits_extra(self):
        logger, _ = _logger(project_name="p", extra={"pipeline_id": "3c1f9b42"})
        buffer = io.StringIO()
        child = logger.getChild("child")
        handler = logging.StreamHandler(buffer)
        handler.setFormatter(logging.Formatter("%(message)s"))
        child.addHandler(handler)
        child.warning("from the child")
        self.assertEqual("3c1f9b42", _line(buffer)["pipeline_id"])

    def test_reserved_keys_are_ignored(self):
        # A caller-supplied 'level' or 'time' would make the line unreadable, so
        # the logger's own keys win over anything in extra.
        logger, buffer = _logger(project_name="p", organization_name="o",
                                 extra={"time": "nope", "level": "nope", "msg": "nope",
                                        "organization": "nope", "project": "nope",
                                        "logger_name": "nope"})
        logger.warning("the real message")
        line = _line(buffer)
        self.assertEqual("the real message", line["msg"])
        self.assertEqual("WARNING", line["level"])
        self.assertEqual("o", line["organization"])
        self.assertEqual("p", line["project"])
        self.assertNotEqual("nope", line["time"])

    def test_per_call_fields_win_over_extra(self):
        logger, buffer = _logger(project_name="p", extra={"key": "from extra"})
        logger.warning("message", {"key": "from the call"})
        self.assertEqual("from the call", _line(buffer)["key"])

    def test_extra_is_made_json_safe(self):
        logger, buffer = _logger(project_name="p", extra={42: object()})
        logger.warning("message")
        self.assertIn("42", _line(buffer))

    def test_no_extra_keeps_previous_shape(self):
        logger, buffer = _logger(project_name="p", organization_name="o", logger_name=True)
        logger.warning("message")
        self.assertEqual(["time", "level", "organization", "project", "logger_name", "msg"],
                         list(_line(buffer).keys()))


if __name__ == "__main__":
    unittest.main()
