import asyncio
import sys

from datetime import datetime, timedelta

sys.path.insert(0, ".")

from aioscheduler import Scheduler


async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    starting_time = datetime.utcnow()
    scheduler = Scheduler()
    scheduler.run()

    for i in range(60):
        scheduler.schedule(work(i), starting_time + timedelta(seconds=5 + i))

    await asyncio.sleep(65)


asyncio.run(main())
