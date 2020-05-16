import asyncio
import sys

sys.path.insert(0, ".")

from aioscheduler import QueuedScheduler


async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    scheduler = QueuedScheduler()
    scheduler.start()

    for i in range(60):
        scheduler.schedule(work(i))

    await asyncio.sleep(5)


asyncio.run(main())
