"""The toy hash function shared by the slides, so the same word always shows the
same number: the first 4 bytes of SHA-256, read as a little-endian integer.

With m = 16 bits this gives: "cat" -> 7, "dog" -> 13, "kitty" -> 7 (a collision
with "cat", which the slides use to show a false positive).
"""

import hashlib


def h32(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:4], "little")
