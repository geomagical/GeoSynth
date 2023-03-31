from rich.progress import Progress


class UrlRetrieveProgressBar:
    def __init__(self, progress: Progress, message: str):
        self.progress = progress
        self.task_id = self.progress.add_task(message, start=False, total=None)
        self.n_calls = 0

    def __call__(self, block_num, block_size, total_size):
        self.n_calls += 1
        if self.n_calls == 1:
            self.update(total=total_size)
            self.start()

        downloaded = block_num * block_size
        self.update(completed=downloaded)

    def update(self, *args, **kwargs):
        return self.progress.update(self.task_id, *args, **kwargs)

    def start(self):
        self.progress.start_task(self.task_id)

    def remove(self):
        self.progress.remove_task(self.task_id)

    def stop(self, description=None):
        if description is not None:
            self.update(description=description)
        self.progress.stop_task(self.task_id)

    def reset(self, *args, **kwargs):
        self.progress.reset(self.task_id, *args, **kwargs)
