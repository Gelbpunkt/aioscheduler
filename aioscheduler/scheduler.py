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
from __future__ import annotations

import asyncio
import heapq

from datetime import datetime
from functools import partial
from typing import Any, Awaitable, List, Optional, Set, Tuple
from uuid import UUID, uuid4

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
        # All running tasks
        self._running: List[Tuple[Task, asyncio.Task[Any]]] = []
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
            next_ = self._next
            assert next_ is not None and isinstance(
                next_.priority, datetime
            )  # mypy fix
            # Sleep until task will be executed
            done, pending = await asyncio.wait(
                [
                    asyncio.sleep(
                        (next_.priority - self._datetime_func()).total_seconds()
                    ),
                    self._restart.wait(),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            fut = done.pop()
            if fut.result() is True:  # restart event
                continue
            # Run it
            task = asyncio.create_task(next_.callback)
            self._running.append((next_, task))
            task.add_done_callback(partial(self._callback, task_obj=next_))
            # Get the next task sorted by time
            try:
                self._next = heapq.heappop(self._tasks)
                self._task_count -= 1
            except IndexError:
                self._next = None
                self._task_count = 0

    def _callback(self, task: asyncio.Task[Any], task_obj: Task) -> None:
        for idx, (running_task, asyncio_task) in enumerate(self._running):
            if running_task.uuid == task_obj.uuid:
                del self._running[idx]

    def cancel(self, task: Task) -> bool:
        for idx, (running_task, asyncio_task) in enumerate(self._running):
            if running_task.uuid == task.uuid:
                del self._running[idx]
                asyncio_task.cancel()
                return True
        for idx, scheduled_task in enumerate(self._tasks):
            if scheduled_task.uuid == task.uuid:
                del self._tasks[idx]
                heapq.heapify(self._tasks)
                return True
        return False

    def schedule(self, coro: Awaitable[Any], when: datetime) -> Task:
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
        return task


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
        # current running task
        self._current_uuid: Optional[UUID] = None
        self._current_task: Optional[asyncio.Task[Any]] = None
        # cancelled UUIDs
        self._cancelled: Set[UUID] = set()

    def start(self) -> None:
        self._task = asyncio.create_task(self.loop())

    async def loop(self) -> None:
        while True:
            task = await self._tasks.get()
            if task.uuid in self._cancelled:
                continue
            # Run it in the current task
            # else this scheduler would be pointless
            self._current_task = asyncio.create_task(task.callback)
            self._current_uuid = task.uuid
            try:
                await self._current_task
            except asyncio.CancelledError:
                self._task_count -= 1
                continue
            self._task_count -= 1

    def cancel(self, task: Task) -> bool:
        if task.uuid == self._current_uuid and self._current_task:
            self._current_task.cancel()
        else:
            self._cancelled.add(task.uuid)
        return True

    def schedule(self, coro: Awaitable[Any]) -> Task:
        task = Task(priority=0, uuid=uuid4(), callback=coro)
        self._task_count += 1
        self._tasks.put_nowait(task)
        return task


class LifoQueuedScheduler(QueuedScheduler):
    """
    A dumb scheduler like QueuedScheduler,
    but uses a Last-in-first-out queue
    """

    def __init__(self) -> None:
        super().__init__()
        self._tasks: asyncio.LifoQueue[Task] = asyncio.LifoQueue()
