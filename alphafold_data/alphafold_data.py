"""Main module."""

from typing import Dict
from .sources import latest_sources, Source
from pathlib import Path


class AFData:
    data_dir: Path
    _sources: Dict[str, Source]

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._sources = latest_sources()

    def download(self, force=False):
        # TODO parallelize
        for db in self._sources.values():
            db.download(self.data_dir, force=force)
        return True

    def decompress(self, force=False):
        for db in self._sources.values():
            db.decompress(self.data_dir, force=force)
        return True

    def prune(self):
        for db in self._sources.values():
            db.prune(self.data_dir)
        return True

    def update(self):
        return self.download() and self.decompress() and self.prune()
