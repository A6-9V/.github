## 2026-02-18 - Signal Queue Optimization

**Learning:** Using a linear list for symbol-specific signal retrieval in a trading bridge leads to O(N) performance degradation as the number of active symbols or signals grows. In a high-frequency trading environment, this can introduce significant latency. Additionally, unbounded in-memory history leads to memory leaks.

**Action:**
- Replaced `List[Signal]` with `defaultdict(deque)` for O(1) lookup and O(1) pop.
- Used `.get()` when retrieving from the dictionary to avoid unintentional memory growth from creating empty deques for non-existent symbols.
- Capped history with `deque(maxlen=1000)` to ensure predictable memory usage.
- Maintained backward compatibility by preserving original API response fields (e.g., `queue_size`).
