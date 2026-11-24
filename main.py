#!/usr/bin/env python3
"""make.fun entry for "Sum up 23 November's world news in one image".

The repository holds the finished front-page image (entry.png, built from
that day's wire reports — see NEWS.md). Running this program copies it to
/output/entry.png, world-readable, as the bounty rules require.
"""

import os
import shutil
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
DEST_DIR = "/output"
DEST = os.path.join(DEST_DIR, "entry.png")


def main() -> int:
    os.umask(0o022)
    os.makedirs(DEST_DIR, mode=0o755, exist_ok=True)
    try:
        os.chmod(DEST_DIR, 0o755)
    except OSError:
        pass
    shutil.copyfile(SOURCE, DEST)
    os.chmod(DEST, 0o644)
    print(f"wrote {DEST} ({os.path.getsize(DEST)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
