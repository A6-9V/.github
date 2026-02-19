## 2026-02-19 - [Memory Efficiency & Queue Optimization]
**Learning:** Python's `list` grows unboundedly and `list.pop(0)` is O(N). For a long-running trading bridge, using `collections.deque(maxlen=N)` prevents memory leaks while maintaining O(1) appends. Splitting a global signal queue into a `defaultdict(deque)` per symbol converts O(N) linear searches into O(1) lookups.
**Action:** Always prefer bounded `deque` for history logs and dictionary-based lookups for per-key queues in high-frequency bridges.
