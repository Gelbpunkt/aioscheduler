import asyncio
import sys

sys.path.insert(0, ".")

from aioscheduler import QueuedScheduler


async def work(n: int) -> None:
    await asyncio.sleep(60)
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    scheduler = QueuedScheduler()
    scheduler.start()
    tasks = []

    for i in range(50):
        tasks.append(scheduler.schedule(work(i)))

    await asyncio.sleep(10)
    print(scheduler._tasks.qsize())
    # Task is running
    print(scheduler.cancel(tasks[0]))
    # Task is scheduled
    print(scheduler.cancel(tasks[-1]))
    print(scheduler._cancelled)
    await asyncio.sleep(120)


asyncio.run(main())
