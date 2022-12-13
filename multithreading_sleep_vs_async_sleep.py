import asyncio
import time


async def foo():
    print('Running in foo')
    time.sleep(6)
    await asyncio.sleep(2)
    print('Done foo')


async def bar():
    print('Running in bar')
    time.sleep(5)
    await asyncio.sleep(1)
    print('Done bar')


s = time.perf_counter()

ioloop = asyncio.get_event_loop()
tasks = [ioloop.create_task(foo()), ioloop.create_task(bar())]
wait_tasks = asyncio.wait(tasks)
ioloop.run_until_complete(wait_tasks)
ioloop.close()

elapsed = time.perf_counter() - s
print(f"\n"
      f"{elapsed:0.2f} sec")
