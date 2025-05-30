# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import os
import sys
from enum import Enum

from airflow_breeze.utils.shared_options import get_forced_answer

STANDARD_TIMEOUT = 10


class Answer(Enum):
    YES = "y"
    NO = "n"
    QUIT = "q"


def user_confirm(
    message: str,
    timeout: float | None = None,
    default_answer: Answer | None = Answer.NO,
    quit_allowed: bool = True,
) -> Answer:
    """Ask the user for confirmation.

    :param message: message to display to the user (should end with the question mark)
    :param timeout: time given user to answer
    :param default_answer: default value returned on timeout. If no default - is set, the timeout is ignored.
    :param quit_allowed: whether quit answer is allowed
    """
    from inputimeout import TimeoutOccurred, inputimeout

    allowed_answers = "y/n/q" if quit_allowed else "y/n"
    while True:
        try:
            force = get_forced_answer() or os.environ.get("ANSWER")
            if force:
                user_status = force
                print(f"Forced answer for '{message}': {force}")
            else:
                if default_answer:
                    # Capitalise default answer
                    allowed_answers = allowed_answers.replace(
                        default_answer.value, default_answer.value.upper()
                    )
                    timeout_answer = default_answer.value
                else:
                    timeout = None
                    timeout_answer = ""
                message_prompt = f"\n{message} \nPress {allowed_answers}"
                if default_answer and timeout:
                    message_prompt += (
                        f". Auto-select {timeout_answer} in {timeout} seconds "
                        f"(add `--answer {default_answer.value}` to avoid delay next time)"
                    )
                message_prompt += ": "
                user_status = inputimeout(
                    prompt=message_prompt,
                    timeout=timeout,
                )
                if user_status == "":
                    if default_answer:
                        return default_answer
                    continue
            if user_status.upper() in ["Y", "YES"]:
                return Answer.YES
            if user_status.upper() in ["N", "NO"]:
                return Answer.NO
            if user_status.upper() in ["Q", "QUIT"] and quit_allowed:
                return Answer.QUIT
            print(f"Wrong answer given {user_status}. Should be one of {allowed_answers}. Try again.")
        except TimeoutOccurred:
            if default_answer:
                return default_answer
            # timeout should only occur when default_answer is set so this should never happened
        except KeyboardInterrupt:
            if quit_allowed:
                return Answer.QUIT
            sys.exit(1)


def confirm_action(
    message: str,
    timeout: float | None = None,
    default_answer: Answer | None = Answer.NO,
    quit_allowed: bool = True,
    abort: bool = False,
) -> bool:
    answer = user_confirm(message, timeout, default_answer, quit_allowed)
    if answer == Answer.YES:
        return True
    if abort:
        sys.exit(1)
    elif answer == Answer.QUIT:
        sys.exit(1)
    return False
