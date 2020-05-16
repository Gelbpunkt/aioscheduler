"""
MIT License

Copyright (c) 2020 Jens Reidel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from datetime import datetime
from typing import Any, Awaitable

from .scheduler import Scheduler


class Manager:
    """
    A manager for multiple Schedulers
    to balance load.
    Can run up to ~20 schedulers
    and ~1-10 million jobs just fine,
    depending on the concurrent finishing
    jobs.
    """

    def __init__(self, tasks: int = 1) -> None:
        self._schedulers = []
        for i in range(tasks):
            self._schedulers.append(Scheduler())

    def start(self) -> None:
        for sched in self._schedulers:
            sched.start()

    def schedule(self, coro: Awaitable[Any], when: datetime) -> None:
        # Find the scheduler with less load
        sorted_by_load = sorted(self._schedulers, key=lambda x: x._task_count)
        sorted_by_load[0].schedule(coro, when)
