"""Main module."""

import logging
from subprocess import CalledProcessError
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
        for name, db in self._sources.items():
            try:
                db.download(self.data_dir, force=force)
            except CalledProcessError as err:
                logging.error(f"Error downloading {name}")
                logging.error(str(err))
                logging.error(str(err.stderr))
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
