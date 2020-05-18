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

from datetime import datetime
from typing import Any, Awaitable, List, Optional, Tuple


class TimedScheduler:
    """
    A clever scheduler for scheduling coroutine execution
    at a specific datetime within a single task
    """

    def __init__(self, prefer_utc: bool = True) -> None:
        # A list of all tasks, elements are (coro, datetime)
        self._tasks: List[Tuple[Awaitable[Any], datetime]] = []
        # The internal loop task
        self._task: Optional[asyncio.Task[None]] = None
        self._task_count = 0
        # The next task to run, (coro, datetime)
        self._next: Optional[Tuple[Awaitable[Any], datetime]] = None
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
            assert self._next is not None  # mypy fix
            coro, time = self._next
            # Sleep until task will be executed
            done, pending = await asyncio.wait(
                [
                    asyncio.sleep((time - self._datetime_func()).total_seconds()),
                    self._restart.wait(),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            fut = done.pop()
            if fut.result() is True:  # restart event
                continue
            # Run it
            asyncio.create_task(coro)
            # Get the next task sorted by time
            next_tasks = sorted(enumerate(self._tasks), key=lambda elem: elem[1][1])
            if next_tasks:
                idx, task = next_tasks[0]
                self._next = task
                del self._tasks[idx]
                self._task_count -= 1
            else:
                self._next = None
                self._task_count = 0

    def schedule(self, coro: Awaitable[Any], when: datetime) -> None:
        if when < self._datetime_func():
            raise ValueError("May only be in the future.")
        self._task_count += 1
        if self._next:
            if when < self._next[1]:
                self._tasks.append(self._next)
                self._next = coro, when
                self._restart.set()
                self._restart.clear()
            else:
                self._tasks.append((coro, when))
        else:
            self._next = coro, when
            self._added.set()
            self._added.clear()


class QueuedScheduler:
    """
    A dumb scheduler for scheduling coroutine execution
    in a queue of infinite length
    """

    def __init__(self) -> None:
        # A list of all tasks, elements are (coro, datetime)
        self._tasks: asyncio.Queue[Awaitable[Any]] = asyncio.Queue()
        # The internal loop task
        self._task: Optional[asyncio.Task[None]] = None
        self._task_count = 0

    def start(self) -> None:
        self._task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            coro = await self._tasks.get()
            # Run it in the current task
            # else this scheduler would be pointless
            await coro
            self._task_count -= 1

    def schedule(self, coro: Awaitable[Any]) -> None:
        self._task_count += 1
        self._tasks.put_nowait(coro)


class LifoQueuedScheduler(QueuedScheduler):
    """
    A dumb scheduler like QueuedScheduler,
    but uses a Last-in-first-out queue
    """

    def __init__(self) -> None:
        super().__init__()
        self._tasks: asyncio.LifoQueue[Awaitable[Any]] = asyncio.LifoQueue()
