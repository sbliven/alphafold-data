"""Console script for alphafold_data."""
import logging
import sys
from pathlib import Path

import click
import click_logging  # type: ignore

from .alphafold_data import AFData

logger = logging.getLogger()
click_logging.basic_config(logger)


@click.group()
@click_logging.simple_verbosity_option(logger)
@click.option(
    "--data-dir",
    help="Install directory",
    envvar="ALPHAFOLD_DATA",
    required=True,
    type=click.Path(),
)
@click.pass_context
def main(ctx, data_dir):
    """Shared parameters"""
    ctx.ensure_object(dict)

    logging.debug(f"data_dir={data_dir!r}")
    if not Path(data_dir).is_dir():
        logging.error(f"does not exist or not a directory: {data_dir}")
        return 1
    ctx.obj["data"] = AFData(data_dir)


@main.command(help="Combine all steps")
@click.pass_context
def update(ctx):
    afd = ctx.obj["data"]
    if afd.update():
        return 0
    else:
        return 1


@main.command(help="Download compressed files")
@click.pass_context
def download(ctx):
    "'download' subcommand"
    afd = ctx.obj["data"]
    if afd.download():
        return 0
    else:
        return 1


@main.command(help="Decompress files")
@click.pass_context
def decompress(ctx):
    afd = ctx.obj["data"]
    if afd.decompress():
        return 0
    else:
        return 1


@main.command(help="Clean up compressed data")
@click.pass_context
def prune(ctx):
    afd = ctx.obj["data"]
    if afd.prune():
        return 0
    else:
        return 1


@main.command(help="Link new version")
@click.pass_context
def link(ctx):
    afd = ctx.obj["data"]
    if afd.link():
        return 0
    else:
        return 1


@main.command(help="Summarize installation status")
@click.pass_context
def status(ctx):
    afd = ctx.obj["data"]
    logging.info(afd.status())
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
