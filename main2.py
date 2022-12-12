import asyncio
import json
import os
import random
import time
from asyncio import Queue
from typing import Optional

from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager



BASE_URL = 'https://ru.wikipedia.org/wiki/'
URLS_TO_PARSE = list()

WORKERS_CUR_IDX = dict()

# Create a queue that we will use to store our "workload".
queue = Optional[Queue]


def create_queue():
    global queue
    queue = asyncio.Queue()


def add_url_to_queue(url: str):
    global queue
    print(f'==> {url}', flush=True)
    queue.put_nowait(url)


def get_random_word():
    with open('data.json', 'rt') as f:
        data = json.load(f)
        return random.choice(list(data.keys()))


def get_random_article():
    return BASE_URL + get_random_word()


def parse_page(driver, url: str, worker_idx, screenshots_dir):
    print(f"{'      ' * worker_idx}{worker_idx}::{url} is about to start...", flush=True)

    driver.get(url)
    print(f"{'      ' * worker_idx}{worker_idx}::{url} title is '{driver.title}'", flush=True)

    driver.save_screenshot(os.path.join(screenshots_dir, f'{WORKERS_CUR_IDX[worker_idx]:06}.png'))
    WORKERS_CUR_IDX[worker_idx] += 1

    try:
        driver.find_element(By.ID, 'noarticletext')
        article_exists = False
    except NoSuchElementException:
        article_exists = True

    if article_exists:
        link_elems = driver.find_elements(By.XPATH, "//div[@id='mw-content-text']//a")
        print(f"{'      ' * worker_idx}{worker_idx}::{url} link count={len(link_elems)}", flush=True)
        while True:
            link = link_elems[random.randint(0, len(link_elems) - 1)].get_attribute('href')
            print(f"{'      ' * worker_idx}{worker_idx}::{url} link={link}", flush=True)
            if link and link.startswith(BASE_URL) \
                    and not link.startswith(BASE_URL + 'Википедия:') \
                    and not link.startswith(BASE_URL + 'Файл:'):
                break
    else:
        link = get_random_article()

    print(f"{'      ' * worker_idx}{worker_idx}::{url} about to add link '{link}'", flush=True)
    add_url_to_queue(link)

    print(f"{'      ' * worker_idx}{worker_idx}::{url} done", flush=True)


async def worker(worker_idx, queue):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.set_window_size(1280, 720)

    screenshots_dir = os.path.abspath(f'worker_{worker_idx:02}')
    os.makedirs(screenshots_dir)

    idx = 0
    while True:
        # Get a "work item" out of the queue.
        url = await queue.get()

        # Sleep for the "sleep_for" seconds.
        # await asyncio.sleep(sleep_for)
        await asyncio.gather(asyncio.to_thread(parse_page, driver, url, worker_idx, screenshots_dir))
        # print(f'!!!!!!!!!!!!!!!!!!!!!!!!! {link}')
        # loop = asyncio.get_event_loop()
        # loop.run_in_executor(parse_page(driver, 'http://time.is', name))

        # Notify the queue that the "work item" has been processed.
        queue.task_done()
        idx += 1
        # print(f'{name} has slept for {sleep_for:.2f} seconds')

    driver.close()


async def main():
    create_queue()

    add_url_to_queue(get_random_article())

    # Create three worker tasks to process the queue concurrently.
    tasks = []
    for i in range(4):
        WORKERS_CUR_IDX[i] = 0
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
    print(f'3 workers slept in parallel for {total_slept_for:.2f} seconds')
    # print(f'total expected sleep time: {total_sleep_time:.2f} seconds')


def async_main():
    asyncio.run(main())


if __name__ == '__main__':
    s = time.perf_counter()

    # sync_main()
    async_main()

    elapsed = time.perf_counter() - s
    print(f"\n"
          f"{elapsed:0.2f} sec")

