import time
import logging
import io
import sys
import queue
from logging.handlers import QueueHandler, QueueListener

class SlowStream(io.StringIO):
    def write(self, s):
        time.sleep(0.0001) # Simulate 0.1ms latency
        return super().write(s)

def benchmark_print(n):
    old_stdout = sys.stdout
    sys.stdout = SlowStream()
    start = time.perf_counter()
    for i in range(n):
        print(f"[{time.time()}] Received data for EURUSD: 1.0850")
    duration = time.perf_counter() - start
    sys.stdout = old_stdout
    return duration

def benchmark_logging_async(n):
    logger = logging.getLogger("async_logger")
    logger.setLevel(logging.INFO)

    log_queue = queue.Queue(-1)
    stream = SlowStream()
    handler = logging.StreamHandler(stream)

    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    listener = QueueListener(log_queue, handler)
    listener.start()

    start = time.perf_counter()
    for i in range(n):
        logger.info(f"Received data for EURUSD: 1.0850")
    duration = time.perf_counter() - start

    # In a real app, the listener runs in background.
    # Here we measure how fast the MAIN loop can continue.

    listener.stop()
    logger.removeHandler(queue_handler)
    return duration

if __name__ == "__main__":
    N = 1000
    print(f"Running benchmark with {N} iterations and simulated 0.1ms I/O latency...")

    t_print = benchmark_print(N)
    print(f"Print (blocking): {t_print:.4f}s ({N/t_print:.2f} req/s)")

    t_async = benchmark_logging_async(N)
    print(f"Async Logging (non-blocking for main thread): {t_async:.4f}s ({N/t_async:.2f} req/s)")

    improvement = (t_print - t_async) / t_print * 100
    print(f"Main thread latency improvement: {improvement:.2f}%")
