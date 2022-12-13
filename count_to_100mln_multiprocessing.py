# perfectly works!

import time
from multiprocessing import Pool

from task import do_count_to_100millions


def async_main(count):
    with Pool() as p:
        p.starmap(do_count_to_100millions, [() for _ in range(count)])


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
