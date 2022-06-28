import logging
import os
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Dict


def download_rsync(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "rsync",
        url,
        str(dst),
    ]
    logging.info(" ".join(cmd))
    raise IOError("Not implemented")


def download_curl(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name+".partial")
    cmd = ["curl", "-o", str(tmp), url]
    logging.debug("Running: " + " ".join(cmd))
    result = run(cmd)
    result.check_returncode()
    tmp.rename(dst)


def download_file(url: str, dst: Path) -> None:
    # TODO choose smarter
    download_curl(url, dst)


def decompress_tar(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    cmd = ["tar", "-xf", str(src), "-C", os.path.join(dst, "")]
    logging.debug("Running: " + " ".join(cmd))
    result = run(cmd)
    result.check_returncode()


def decompress_tgz(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    logging.info("decompress tgz")
    raise NotImplementedError()


@dataclass
class Source:
    flag: str
    url: str
    compressed: Path
    uncompressed: Path

    @classmethod
    def _force_download(kls, url: str, dst: Path):
        return download_file(url, dst)

    def download(self, data_dir: Path, force=False):
        "Download compressed files"
        if force or not (
            self.uncompressed_available(data_dir) or self.compressed_available(data_dir)
        ):
            self._force_download(self.url, Path(data_dir, self.compressed))

    @classmethod
    def _force_decompress(kls, src: Path, dst: Path):
        return decompress_tgz(src, dst)

    def decompress(self, data_dir: Path, force=False):
        "Decompress compressed files"
        if not self.compressed_available(data_dir):
            raise IOError(
                f"Compressed file not found: {Path(data_dir,self.compressed)}"
            )
        if force or not self.uncompressed_available(data_dir):
            self._force_decompress(
                Path(data_dir, self.compressed), Path(data_dir, self.uncompressed)
            )

    def prune(self):
        raise NotImplementedError()

    def compressed_available(self, data_dir: Path):
        "Check if compressed files are downloaded"
        out = Path(data_dir, self.compressed)

        # file or non-empty directory
        return out.exists() and (out.is_file() or next(out.iterdir(), None) is not None)

    def uncompressed_available(self, data_dir: Path):
        "Check if uncompressed files are available"
        out = Path(data_dir, self.uncompressed)

        # file or non-empty directory
        return out.exists() and (out.is_file() or next(out.iterdir(), None) is not None)


class ParamSource(Source):
    version: str

    def __init__(self, version: str):
        url = f"https://storage.googleapis.com/alphafold/alphafold_params_{version}.tar"
        compressed = Path(f"compressed/params/{version}/alphafold-params_{version}.tar")
        uncompressed = Path(f"uncompressed/params/{version}/")
        super().__init__(
            flag="param",
            url=url,
            compressed=compressed,
            uncompressed=uncompressed,
        )
        self.version = version

    @classmethod
    def _force_decompress(kls, src: Path, dst: Path):
        return decompress_tar(src, dst)


class BFDSource(Source):
    def __init__(self, version: str):
        if version != "6a634dc6eb105c2e9b4cba7bbae93412":
            raise ValueError(f"URL not known for BDF version {version}")
        super().__init__(
            flag="bfd_database_path",
            url="https://storage.googleapis.com/alphafold-databases/casp14_versions/"
            "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz",
            compressed=Path(
                f"bfd/{version}/"
                "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz"
            ),
            uncompressed=Path(
                f"bfd/{version}/"
                "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt"
            ),
        )
        self.version = version


def latest_sources():
    # TODO detect latest versions
    sources: Dict[str, Source] = {
        "params": ParamSource(version="2021-10-27"),
        "bfd": BFDSource(version="6a634dc6eb105c2e9b4cba7bbae93412"),
    }
    return sources
    # bfd = Source(
    #     version="6a634dc6eb105c2e9b4cba7bbae93412"
    #     flag="bfd_database_path",
    #     url="https://storage.googleapis.com/alphafold-databases/casp14_versions/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz",
    #     path="bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt",
    # )
