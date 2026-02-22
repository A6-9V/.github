## 2026-02-22 - [Optimized Signal Bridge Data Structures]
**Learning:** In a high-frequency trading bridge, linear search in a global list for symbol-specific signals becomes a bottleneck as the number of active symbols or pending signals grows. Using `defaultdict(deque)` keyed by symbol provides O(1) lookup. Additionally, `collections.deque` with `maxlen` is essential for memory safety in long-running processes, but care must be taken with slicing (`list(d)` is O(N)).
**Action:** Always prefer mapped data structures for per-key lookups and use indexed access from ends of deques for O(limit) tail retrieval.

## 2026-02-22 - [Agent Observation Truncation]
**Learning:** Tool outputs (especially `read_file`) are truncated at 1000 characters. This can lead to hallucinations about the remaining code if not explicitly checked.
**Action:** Use `wc -c` to check file size and read in chunks using `sed` or offsets if the file exceeds 1KB.
