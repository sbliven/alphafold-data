"""Main module."""

import itertools
import logging
from pathlib import Path
from subprocess import CalledProcessError
from typing import Dict

from .sources import Source, latest_sources


class AFData:
    data_dir: Path
    _sources: Dict[str, Source]

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._sources = latest_sources()

    def download(self, force=False):
        # TODO parallelize
        complete = True
        for name, db in self._sources.items():
            try:
                db.download(self.data_dir, force=force)
            except CalledProcessError as err:
                logging.error(f"Error downloading {name}")
                logging.error(str(err))
                logging.error(str(err.stderr))
                complete = False
        return complete

    def decompress(self, force=False):
        complete = True
        for name, db in self._sources.items():
            try:
                db.decompress(self.data_dir, force=force)
            except CalledProcessError as err:
                logging.error(f"Error decompressing {name}")
                logging.error(str(err))
                logging.error(str(err.stderr))
                complete = False

        return complete

    def prune(self):
        for db in self._sources.values():
            db.prune(self.data_dir)
        return True

    def update(self):
        return self.download() and self.decompress()

    def status(self):
        """Print status about current versions"""

        def avail_emoji(val: bool):
            return "✅" if val else "❌"

        def shorten(s, width):
            return s if len(s) <= width else s[: width - 1] + "…"

        header = ("Database", "Version", "Compressed", "Uncompressed")
        widths = 10, 10, 10, 13
        lines = []
        for name, db in self._sources.items():
            lines.append(
                (
                    name,
                    db.version,
                    avail_emoji(db.compressed_available(self.data_dir)),
                    avail_emoji(db.uncompressed_available(self.data_dir)),
                )
            )

        return "\n".join(
            " ".join(
                shorten(str(elem), widths[i]).rjust(widths[i], " ")
                for i, elem in enumerate(line)
            )
            for line in itertools.chain([header], lines)
        )
