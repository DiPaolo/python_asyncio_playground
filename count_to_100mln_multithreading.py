# doesn't work in such way;
# there is no difference between sync and async at all!
# multiprocessing should be used instead

import psutil
import asyncio
import time
from task import do_count_to_100millions


async def worker(worker_idx, queue):
    while True:
        # Get a "work item" out of the queue.
        url = await queue.get()

        # Sleep for the "sleep_for" seconds.
        # await asyncio.sleep(sleep_for)
        await asyncio.gather(asyncio.to_thread(do_count_to_100millions))

        # Notify the queue that the "work item" has been processed.
        queue.task_done()
        # print(f'{name} has slept for {sleep_for:.2f} seconds')

    driver.close()


async def main(count):
    queue = asyncio.Queue()

    for i in range(count):
        queue.put_nowait(i)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(8):
        task = asyncio.create_task(worker(i, queue))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print('====')
    print(f'N workers slept in parallel for {total_slept_for:.2f} seconds')
    # print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


def async_main(count):
    asyncio.run(main(count))


def sync_main(count):
    for _ in range(count):
        do_count_to_100millions()


if __name__ == '__main__':
    s = time.perf_counter()

    count = 10

    # sync_main(count)
    async_main(count)

    elapsed = time.perf_counter() - s
    print(f"\n"
          f"{elapsed:0.2f} sec")
