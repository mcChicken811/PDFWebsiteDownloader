from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class RecurThreadPoolExecutor:
    def __init__(self, max_workers=20):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_tasks = Queue() 

    # submit a task request
    def submit(self, fn, /, *args, **kwargs):
        task = self.executor.submit(fn, *args, **kwargs)

        self.pending_tasks.put(task)

        # remove pending task when finished
        task.add_done_callback(self._on_task_finished)

    # removes pending task and shut down if no pending tasks
    def _on_task_finished(self, future):
        self.pending_tasks.get(future)

    # hold the main thread until the executor finishes
    def wait(self):
        while not self.pending_tasks.empty():
            continue

        self.executor.shutdown()

