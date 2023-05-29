import concurrent.futures
import threading
import time
from concurrent.futures import ThreadPoolExecutor


def task(x):
    thread_id = threading.get_ident()
    print(f"Task {x} executed by Thread {thread_id % 100}\n")
    time.sleep(5)

    result = x * x
    print(f"Execute {thread_id % 100} task: {result}")
    print(f"_________{thread_id % 100}_____________")
    return result


def fast_task():
    time.sleep(2)
    print("Execute fast task")


class ThreadService:
    def instance_task(self):
        print("Execute Class")


if __name__ == "__main__":

    # for i in range(5):
    #     thread = threading.Thread(target=task, args=(i, ))
    #     thread.start()

    # thread = threading.Thread(target=fast_task)
    # thread.start()
    #
    # service = ThreadService()
    # t = threading.Thread(target=service.instance_task)
    # t.start()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(task, x=i) for i in range(10)]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(f"Resalt: {result}")
            print(' \n')
    print("Done!")
