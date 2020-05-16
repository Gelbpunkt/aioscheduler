# aioscheduler

aioscheduler is a scalable and high-performance task scheduler for asyncio.

It schedules execution of coroutines at a specific time in a single task, making it lightweight and extremely scalable by adding a manager for multiple schedulers.

Tests have shown that aioscheduler can run up to 10 million timed tasks with up to 20 finishing per second when using 20 schedulers. Single tasks can easily schedule up to 10.000 tasks.

## Usage

aioscheduler provides a Scheduler class that runs a main task to consume coroutines.

```py
import asyncio
from datetime import datetime, timedelta
from aioscheduler import Scheduler

async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")

async def main() -> None:
    starting_time = datetime.utcnow()
    scheduler = Scheduler()
    scheduler.start()

    for i in range(60):
        scheduler.schedule(work(i), starting_time + timedelta(seconds=5 + i))

    await asyncio.sleep(65)

asyncio.run(main())
```

In this example, 60 tasks are scheduled to run in 5 seconds from now, 1 of them per second over a time of 1 minute.

To scale even further, aioscheduler offers the Manager:

```py
import asyncio
from datetime import datetime, timedelta
from aioscheduler import Manager

async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")

async def main() -> None:
    starting_time = datetime.utcnow()
    manager = Manager(5)  # The number of Schedulers to use
    manager.start()

    for i in range(300):
        manager.schedule(work(i), starting_time + timedelta(seconds=10 + i % 60))

    await asyncio.sleep(70)

asyncio.run(main())
```

The manager distributes the tasks across multiple schedulers internally and acts as a load-balancer.

## License

MIT
