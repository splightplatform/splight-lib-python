import sys


def bar_progress(current: float, total: float, width: int = 80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (
        current / total * 100,
        current,
        total,
    )
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()
