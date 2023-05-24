import asyncio
import random
import sys

from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")

from aioscheduler import TimedScheduler


async def work(n: int) -> None:
    await asyncio.sleep(5)
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    starting_time = datetime.now(timezone.utc)
    scheduler = TimedScheduler(timezone_aware=True)
    scheduler.start()
    tasks = []

    for i in range(60):
        tasks.append(
            scheduler.schedule(
                work(i),
                starting_time.astimezone(timezone(timedelta(hours=random.randint(-12, 12)))) + timedelta(seconds=5 + i)
            )
        )

    await asyncio.sleep(65)


asyncio.run(main())
