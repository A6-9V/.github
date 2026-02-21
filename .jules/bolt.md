## 2026-02-21 - [Data Structure Optimization for Trading Bridge]
**Learning:** In-memory lists for trading history and signal queues are performance anti-patterns. They lead to O(n) lookups and memory leaks as data grows.
**Action:** Use `collections.deque` with `maxlen` for fixed-size history buffers and `collections.defaultdict(deque)` for O(1) keyed lookups with FIFO behavior. Always include type hints for these complex collections to maintain code clarity.
