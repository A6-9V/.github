## 2025-05-22 - Storage Optimization in Jules Cloud Bridge
**Learning:** In-memory storage using basic Python lists for history and signal queues leads to two major performance bottlenecks:
1. Unbounded growth of the history list creates a memory leak over time.
2. Linear search ($O(n)$) for signals by symbol becomes increasingly slow as the queue size grows, impacting high-frequency trading responsiveness.
**Action:** Use `collections.deque` with `maxlen` for bounded history and `collections.defaultdict(deque)` for $O(1)$ signal lookups by symbol.
