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
    tmp = dst.with_name(dst.name + ".partial")
    curl = os.environ.get("CURL_EXE", "curl")
    cmd = [curl, "-o", str(tmp), url]
    logging.debug("Running: " + " ".join(cmd))
    result = run(cmd)
    result.check_returncode()
    tmp.rename(dst)


def _has_aria2c():
    if "ARIA2C_EXE" in os.environ:
        return True
    try:
        run(["aria2c", "--version"], capture_output=True)
        return True
    except FileNotFoundError:
        return False


def download_aria2c(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".partial")
    aria2c = os.environ.get("ARIA2C_EXE", "aria2c")
    cmd = [
        aria2c,
        url,
        "--out",
        str(tmp),
        "--max-connection-per-server=5",
    ]
    logging.debug("Running: " + " ".join(cmd))
    result = run(cmd)
    result.check_returncode()
    tmp.rename(dst)


_file_downloader = None


def download_file(url: str, dst: Path) -> None:
    """Download a file

    Uses aria2c if possible, otherwise curl

    Args:
    - url: url of the file
    - dst: filename to save as. Must be a file, not a directory.
    """
    global _file_downloader
    if _file_downloader is None:
        if _has_aria2c():
            _file_downloader = download_aria2c
        else:
            _file_downloader = download_curl
    _file_downloader(url, dst)


def decompress_tar(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    cmd = [
        "tar",
        "-xvf",
        str(src),
        "-C",
        os.path.join(dst, ""),
        "--preserve-permissions",
    ]
    logging.debug("Running: " + " ".join(cmd))
    result = run(cmd)
    result.check_returncode()


def decompress_gunzip(src: Path, dst: Path) -> None:
    raise NotImplementedError()


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
    def _force_decompress(kls, src: Path, dst: Path) -> None:
        return decompress_tgz(src, dst)

    def decompress(self, data_dir: Path, force=False) -> None:
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
        compressed = Path(f"compressed/params/{version}/alphafold-params.tar")
        uncompressed = Path(f"uncompressed/params/{version}/")
        super().__init__(
            flag="param",
            url=url,
            compressed=compressed,
            uncompressed=uncompressed,
        )
        self.version = version

    @classmethod
    def _force_decompress(kls, src: Path, dst: Path) -> None:
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
                f"compressed/bfd/{version}/"
                "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz"
            ),
            uncompressed=Path(
                f"uncompressed/bfd/{version}/"
                "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt"
            ),
        )
        self.version = version

    # TODO check md5 hash in download


class MgnifySource(Source):
    def __init__(self, version: str):
        super().__init__(
            flag="mgnify_database_path",
            url="https://storage.googleapis.com/alphafold-databases/casp14_versions/"
            f"mgy_clusters_{version}.fa.gz",
            compressed=Path(f"compressed/mgnify/{version}/mgy_clusters.fa.gz"),
            uncompressed=Path(f"uncompressed/mgnify/{version}/" "mgy_clusters.fa"),
        )
        self.version = version

    @classmethod
    def _force_decompress(kls, src: Path, dst: Path) -> None:
        return decompress_gunzip(src, dst)


# class TemplateMMcifSource(Source):
#     def __init__(self, version: str):
#         super().__init__(
#             flag="template_mmcif_dir",
#             url="rsync.rcsb.org::ftp_data/structures/divided/mmCIF/",
#             compressed=Path(
#                 f"compressed/mgnify/{version}/"
#                 "mgy_clusters_{version}.fa.gz"
#             ),
#             uncompressed=Path(
#                 f"uncompressed/mgnify/{version}/"
#                 "mgy_clusters.fa"
#             ),
#         )
#         self.version = version

# class PDB70Source(Source):
#     def __init__(self, version: str):
#         super().__init__(
#             flag="template_mmcif_dir",
#             url="http://wwwuser.gwdg.de/~compbiol/data/hhsuite/databases/hhsuite_dbs/"
#             f"old-releases/pdb70_from_mmcif_{version}.tar.gz"
#             compressed=Path(
#                 f"compressed/pdb70/{version}/"
#                 "pdb70_from_mmcif.tar.gz"
#             ),
#             uncompressed=Path(
#                 f"uncompressed/mgnify/{version}/"
#                 "pdb70_from_mmcif"
#             ),
#         )
#         self.version = version


def latest_sources():
    # TODO detect latest versions
    sources: Dict[str, Source] = {
        "params": ParamSource("2022-03-02"),
        "bfd": BFDSource("6a634dc6eb105c2e9b4cba7bbae93412"),
        "mgnify": MgnifySource("2018_12"),
    }
    return sources
    # bfd = Source(
    #     version="6a634dc6eb105c2e9b4cba7bbae93412"
    #     flag="bfd_database_path",
    #     url="https://storage.googleapis.com/alphafold-databases/casp14_versions/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt.tar.gz",
    #     path="bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt",
    # )
