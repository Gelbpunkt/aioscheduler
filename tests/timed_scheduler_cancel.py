import asyncio
import sys

from datetime import datetime, timedelta

sys.path.insert(0, ".")

from aioscheduler import TimedScheduler


async def work(n: int) -> None:
    await asyncio.sleep(60)
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    starting_time = datetime.utcnow()
    scheduler = TimedScheduler()
    scheduler.start()
    tasks = []

    for i in range(50):
        tasks.append(
            scheduler.schedule(work(i), starting_time + timedelta(seconds=5 + i))
        )

    await asyncio.sleep(10)
    print(len(scheduler._running))
    print(len(scheduler._tasks))
    # Task is running
    print(scheduler.cancel(tasks[0]))
    # Task is scheduled
    print(scheduler.cancel(tasks[-1]))
    print(len(scheduler._running))
    print(len(scheduler._tasks))
    await asyncio.sleep(5)


asyncio.run(main())
