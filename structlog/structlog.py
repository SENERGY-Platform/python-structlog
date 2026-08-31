#  Copyright 2025 InfAI (CC SES)
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

import datetime
import json
import logging
import warnings

_TIME_KEY = 'time'
_LEVEL_KEY = 'level'
_MSG_KEY = 'msg'
_ORGA_KEY = 'organization'
_PROJECT_KEY = 'project'
_LOGGER_NAME_KEY = 'logger_name'
__STACKLEVEL_KEY = 'stacklevel'
_RESERVED_KEYS = frozenset((_TIME_KEY, _LEVEL_KEY, _MSG_KEY, _ORGA_KEY, _PROJECT_KEY, _LOGGER_NAME_KEY))

class Logger(logging.Logger):

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.__meta = dict()
        self.__time_utc = False

    def debug(self, msg, *args, **kwargs):
        super().debug(self.__gen_msg(logging.DEBUG, msg, args), *(), **kwargs)

    def info(self, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().info(self.__gen_msg(logging.INFO, msg, args), *(), **kwargs)

    def warning(self, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().warning(self.__gen_msg(logging.WARNING, msg, args), *(), **kwargs)

    def warn(self, msg, *args, **kwargs):
        warnings.warn("The 'warn' method is deprecated, "
                      "use 'warning' instead", DeprecationWarning, 2)
        _add_stack_level(kwargs)
        super().warning(self.__gen_msg(logging.WARNING, msg, args), *(), **kwargs)

    def error(self, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().error(self.__gen_msg(logging.ERROR, msg, args), *(), **kwargs)

    def critical(self, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().critical(self.__gen_msg(logging.CRITICAL, msg, args), *(), **kwargs)

    def fatal(self, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().fatal(self.__gen_msg(logging.FATAL, msg, args), *(), **kwargs)

    def log(self, level, msg, *args, **kwargs):
        _add_stack_level(kwargs)
        super().log(level, self.__gen_msg(level, msg, args), *(), **kwargs)

    def getChild(self, suffix):
        child = super().getChild(suffix)
        child.__time_utc = self.__time_utc
        meta = self.__meta.copy()
        if _LOGGER_NAME_KEY in meta:
            meta[_LOGGER_NAME_KEY] = child.name
        child.__meta = meta
        return child

    def configure(self, project_name='', organization_name='', time_utc=False, logger_name=False, extra=None):
        """
        Configure the static fields every log line of this logger carries.

        'extra' is a mapping of further static fields, for context that belongs to
        the whole process rather than to a single call — the OpenTelemetry baggage
        a service was started with, for instance. Fields passed per call still win
        over these, and the keys this logger owns ('time', 'level', 'msg',
        'organization', 'project', 'logger_name') are ignored in 'extra', because a
        line whose level or timestamp came out of caller-supplied context is no
        longer readable.
        """
        meta = dict()
        if organization_name is not None and organization_name != '':
            meta[_ORGA_KEY] = organization_name
        if project_name is not None and project_name != '':
            meta[_PROJECT_KEY] = project_name
        if extra:
            for key, value in _json_safe(extra).items():
                if key in _RESERVED_KEYS:
                    continue
                meta[key] = value
        if logger_name:
            meta[_LOGGER_NAME_KEY] = self.name
        self.__meta = meta
        self.__time_utc = time_utc

    def __gen_msg(self, level, msg, args):
        try:
            msg = msg.__str__() % args
        except TypeError:
            pass
        items = {_TIME_KEY: _gen_timestamp(self.__time_utc), _LEVEL_KEY: logging.getLevelName(level), **self.__meta, _MSG_KEY: msg}
        for arg in args:
            if isinstance(arg, dict):
                items.update(_json_safe(arg))
        return json.dumps(items, separators=(",", ":"))


def _gen_timestamp(utc=False):
    if utc:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    return datetime.datetime.now().isoformat()


def _add_stack_level(kwargs):
    if __STACKLEVEL_KEY in kwargs:
        kwargs[__STACKLEVEL_KEY] += 1
        return
    kwargs[__STACKLEVEL_KEY] = 2

def _json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [_json_safe(v) for v in obj]
    elif isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)