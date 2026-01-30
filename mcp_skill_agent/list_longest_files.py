#!/usr/bin/env python3
"""
list_longest_files.py

Print the 20 longest regular files under one or more supplied root directories.
If no directory is given the script uses the current working directory.

Usage:
    python list_longest_files.py /path/to/project1 /path/to/project2 ...

The output is a simple newline‑separated list of absolute file paths,
ordered from longest to shortest (largest size first).

Optionally, add `--size` or `-s` after the command line arguments to also
display each file’s length in bytes:

    python list_longest_files.py --size /my/project

"""

import os
import sys
import argparse
import heapq
from pathlib import Path


def iter_files(root_paths):
    """Yield (absolute_path, size_in_bytes) for every regular file under *root_paths*."""
    for root in root_paths:
        # Convert to an absolute Path object once so we can join with filenames later.
        root = Path(root).resolve()
        if not root.is_dir():
            print(f"⚠️  Skipping non‑directory: {root}", file=sys.stderr)
            continue

        for dirpath, _, filenames in os.walk(root):
            # Convert the *dirpath* to a Path once – this avoids repeated str operations.
            base = Path(dirpath).resolve()
            for name in filenames:
                candidate = base / name
                try:
                    # Skip broken symlinks, sockets, etc.  Only regular files matter.
                    if not candidate.is_file():
                        continue

                    size = candidate.stat().st_size
                    yield str(candidate), size
                except (OSError, PermissionError) as exc:
                    # Most common reason: race condition on a file that disappears
                    # between os.walk and the stat call.  Ignoring is fine here.
                    continue


def top_n_files(iterable, n=20):
    """Return the *n* longest (path, size) tuples using heapq.nlargest."""
    return heapq.nlargest(n, iterable, key=lambda item: item[1])


def main():
    parser = argparse.ArgumentParser(
        description="Print the 20 longest files under given directories."
    )
    parser.add_argument(
        "directories",
        nargs="*",
        default=["."],
        help="One or more root directories to scan. If omitted, '.' (current dir) is used.",
    )
    parser.add_argument(
        "-s",
        "--size",
        action="store_true",
        help="Also print each file's size in bytes alongside its name.",
    )
    args = parser.parse_args()

    root_paths = args.directories or ["."]
    files_iter = iter_files(root_paths)

    top_20 = top_n_files(files_iter, n=20)

    for path, size in top_20:
        if args.size:
            print(f"{size}\t{path}")
        else:
            print(path)


if __name__ == "__main__":
    main()