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

import logging
import structlog

# IMPORTANT set logger class to 'structlog.Logger'
logging.setLoggerClass(structlog.Logger)

logger: structlog.Logger = logging.getLogger('my_logger')
logger.configure(organization_name='my_orga', project_name='my_project', time_utc=True, logger_name=True)

logger.warning('my message',{"key_a": 123, "key_b": "test"})
# {"time":"2025-12-02T12:47:16.862855+00:00","level":"WARNING","organization":"my_orga","project":"my_project","logger_name":"my_logger","msg":"my message","key_a":123,"key_b":"test"}

logger.warning('my message 2')
# {"time":"2025-12-02T12:47:16.862961+00:00","level":"WARNING","organization":"my_orga","project":"my_project","logger_name":"my_logger","msg":"my message 2"}

child_logger = logger.getChild('child')
child_logger.warning('my message 3',{"key_a": 456})
# {"time":"2025-12-02T12:47:16.863002+00:00","level":"WARNING","organization":"my_orga","project":"my_project","logger_name":"my_logger.child","msg":"my message 3","key_a":456}