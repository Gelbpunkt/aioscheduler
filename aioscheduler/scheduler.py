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
import asyncio
import heapq

from datetime import datetime
from typing import Any, Awaitable, List, Optional
from uuid import uuid4

from .task import Task


class TimedScheduler:
    """
    A clever scheduler for scheduling coroutine execution
    at a specific datetime within a single task
    """

    def __init__(self, prefer_utc: bool = True) -> None:
        # A list of all tasks
        self._tasks: List[Task] = []
        # The internal loop task
        self._task: Optional[asyncio.Task[None]] = None
        self._task_count = 0
        # The next task to run, (datetime, coro)
        self._next: Optional[Task] = None
        # Event fired when a initial task is added
        self._added = asyncio.Event()
        # Event fired when the loop needs to reset
        self._restart = asyncio.Event()
        if prefer_utc:
            self._datetime_func = datetime.utcnow
        else:
            self._datetime_func = datetime.now

    def start(self) -> None:
        self._task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            if self._next is None:
                # Wait for a task
                await self._added.wait()
            assert self._next is not None and isinstance(
                self._next.priority, datetime
            )  # mypy fix
            # Sleep until task will be executed
            done, pending = await asyncio.wait(
                [
                    asyncio.sleep(
                        (self._next.priority - self._datetime_func()).total_seconds()
                    ),
                    self._restart.wait(),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            fut = done.pop()
            if fut.result() is True:  # restart event
                continue
            # Run it
            asyncio.create_task(self._next.callback)
            # Get the next task sorted by time
            try:
                self._next = heapq.heappop(self._tasks)
                self._task_count -= 1
            except IndexError:
                self._next = None
                self._task_count = 0

    def schedule(self, coro: Awaitable[Any], when: datetime) -> None:
        if when < self._datetime_func():
            raise ValueError("May only be in the future.")
        self._task_count += 1
        task = Task(priority=when, uuid=uuid4(), callback=coro)
        if self._next:
            assert isinstance(self._next.priority, datetime)  # mypy fix
            if when < self._next.priority:
                heapq.heappush(self._tasks, self._next)
                self._next = task
                self._restart.set()
                self._restart.clear()
            else:
                heapq.heappush(self._tasks, task)
        else:
            self._next = task
            self._added.set()
            self._added.clear()


class QueuedScheduler:
    """
    A dumb scheduler for scheduling coroutine execution
    in a queue of infinite length
    """

    def __init__(self) -> None:
        # A list of all tasks, elements are (coro, datetime)
        self._tasks: asyncio.Queue[Task] = asyncio.Queue()
        # The internal loop task
        self._task: Optional[asyncio.Task[None]] = None
        self._task_count = 0

    def start(self) -> None:
        self._task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            task = await self._tasks.get()
            # Run it in the current task
            # else this scheduler would be pointless
            await task.callback
            self._task_count -= 1

    def schedule(self, coro: Awaitable[Any]) -> None:
        task = Task(priority=0, uuid=uuid4(), callback=coro)
        self._task_count += 1
        self._tasks.put_nowait(task)


class LifoQueuedScheduler(QueuedScheduler):
    """
    A dumb scheduler like QueuedScheduler,
    but uses a Last-in-first-out queue
    """

    def __init__(self) -> None:
        super().__init__()
        self._tasks: asyncio.LifoQueue[Task] = asyncio.LifoQueue()
