from typing import List, Callable

fast_latency: List[Callable[[float], str]] = ...
slow_latency: List[Callable[[float], str]] = ...
