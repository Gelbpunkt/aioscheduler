# aioscheduler

aioscheduler is a scalable and high-performance task scheduler for asyncio.

It schedules execution of coroutines at a specific time in a single task, making it lightweight and extremely scalable by adding a manager for multiple schedulers.

Tests have shown that aioscheduler can run up to 10 million timed tasks with up to 20 finishing per second when using 20 schedulers. Single tasks can easily schedule up to 10.000 tasks.

## Installation

`pip install aioscheduler`

## Usage

aioscheduler provides several Scheduler classes that runs a main task to consume coroutines.

There are `QueuedScheduler` and `TimedScheduler`, whereas TimedScheduler is the default for Managers.

The TimedScheduler compares datetime objects to UTC by default, to disable it, pass `prefer_utc=False` to the constructor.

```py
import asyncio
from datetime import datetime, timedelta
from aioscheduler import TimedScheduler

async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")

async def main() -> None:
    starting_time = datetime.utcnow()
    scheduler = TimedScheduler()
    scheduler.start()

    for i in range(60):
        scheduler.schedule(work(i), starting_time + timedelta(seconds=5 + i))

    await asyncio.sleep(65)

asyncio.run(main())
```

In this example, 60 tasks are scheduled to run in 5 seconds from now, 1 of them per second over a time of 1 minute.

The QueuedScheduler works identical, but consumes tasks in scheduling order immediately and only takes a single coroutine as argument to `schedule()`.

To scale even further, aioscheduler offers the Manager (example with QueuedScheduler backend):

```py
import asyncio
from datetime import datetime, timedelta
from aioscheduler import Manager, QueuedScheduler

async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")

async def main() -> None:
    starting_time = datetime.utcnow()
    manager = Manager(5, cls=QueuedScheduler)  # The number of Schedulers to use
                                               # Leaving out cls defaults to TimedScheduler
    manager.start()

    for i in range(30000):
        manager.schedule(work(i))

    await asyncio.sleep(5)

asyncio.run(main())
```

The manager distributes the tasks across multiple schedulers internally and acts as a load-balancer.

## License

MIT
