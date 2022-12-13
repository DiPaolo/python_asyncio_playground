import psutil


def do_count_to_100millions():
    p = psutil.Process()
    print(f"start process '{p.name()}'")
    count = 0
    for _ in range(100000000):
        count += 1
    print(f"end process '{p.name()}'")
