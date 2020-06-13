import asyncio
import sys

from datetime import datetime, timedelta

sys.path.insert(0, ".")

from aioscheduler import Manager


async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    starting_time = datetime.now()
    manager = Manager(
        5, max_tasks=100, prefer_utc=False
    )  # The number of Schedulers to use
    manager.start()

    for i in range(300):
        manager.schedule(work(i), starting_time + timedelta(seconds=10 + i % 60))

    await asyncio.sleep(70)


asyncio.run(main())
