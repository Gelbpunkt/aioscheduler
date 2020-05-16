import asyncio
import sys

sys.path.insert(0, ".")

from aioscheduler import Manager, QueuedScheduler


async def work(n: int) -> None:
    print(f"I am doing heavy work: {n}")


async def main() -> None:
    manager = Manager(5, cls=QueuedScheduler)  # The number of Schedulers to use
    # and force use of a QueuedScheduler
    manager.start()

    for i in range(300):
        manager.schedule(work(i))

    await asyncio.sleep(5)


asyncio.run(main())
