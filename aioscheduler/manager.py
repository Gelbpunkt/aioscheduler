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
from typing import Any, Type, Union

from .scheduler import QueuedScheduler, TimedScheduler
from .task import Task


class Manager:
    """
    A manager for multiple Schedulers
    to balance load.
    Can run up to ~20 schedulers
    and ~1-10 million jobs just fine,
    depending on the concurrent finishing
    jobs and on the Scheduler backend.
    """

    def __init__(
        self,
        tasks: int = 1,
        cls: Union[Type[TimedScheduler], Type[QueuedScheduler]] = TimedScheduler,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._schedulers = []
        for i in range(tasks):
            self._schedulers.append(cls(*args, **kwargs))  # type: ignore
            # mypy does not like args and kwargs

    def start(self) -> None:
        for sched in self._schedulers:
            sched.start()

    def cancel(self, task: Task) -> bool:
        for sched in self._schedulers:
            if sched.cancel(task):
                return True
        return False

    def schedule(self, *args: Any, **kwargs: Any) -> Task:
        # Find the scheduler with less load
        sorted_by_load = sorted(self._schedulers, key=lambda x: x._task_count)
        return sorted_by_load[0].schedule(*args, **kwargs)
