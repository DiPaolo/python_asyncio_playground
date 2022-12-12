import asyncio
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


SITES_TO_SCREENSHOT = [
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
    'http://rsdn.org',
    'http://apple.com',
    'http://time.is',
    'https://mantine.dev',
    'http://github.com',
]


def parse_page(driver, url: str, worker_id, screenshot_name):
    print(f"{worker_id}:{url} is about to start...")
    driver.get(url)
    # clock = driver.find_element(By.XPATH, "//time[@id='clock']")
    print(f"{worker_id}:{url} title is '{driver.title}'")
    driver.save_screenshot(screenshot_name)
    print(f"{worker_id}:{url} done")


async def worker(name, queue):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    idx = 0
    while True:
        # Get a "work item" out of the queue.
        url = await queue.get()

        # Sleep for the "sleep_for" seconds.
        # await asyncio.sleep(sleep_for)
        await asyncio.gather(asyncio.to_thread(parse_page, driver, url, name, f'{name}_{idx:02}.png'))
        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(parse_page(driver, 'http://time.is', name))

        # Notify the queue that the "work item" has been processed.
        queue.task_done()
        idx += 1
        # print(f'{name} has slept for {sleep_for:.2f} seconds')

    driver.close()


async def main():
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    for url in SITES_TO_SCREENSHOT:
        queue.put_nowait(url)

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(6):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
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
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    # print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


def sync_main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    idx = 0
    for url in SITES_TO_SCREENSHOT:
        print(f"sync:{url} is about to start...")
        driver.get(url)
        print(f"sync:{url} title is '{driver.title}'")
        driver.save_screenshot(f'sync_{idx:02}.png')
        print(f"sync:{url} done")

        idx += 1

    driver.close()


def async_main():
    asyncio.run(main())


if __name__ == '__main__':
    s = time.perf_counter()

    sync_main()
    # async_main()

    elapsed = time.perf_counter() - s
    print(f"\n"
          f"{elapsed:0.2f} sec")

