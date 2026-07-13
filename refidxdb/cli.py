# Guide: https://medium.com/clarityai-engineering/how-to-create-and-distribute-a-minimalist-cli-tool-with-python-poetry-click-and-pipx-c0580af4c026
import logging
import shutil
import sys
from multiprocessing import current_process, get_context
from pathlib import Path

import click
import plotext as plt
import polars as pl
from rich.traceback import install
from tqdm import tqdm

from refidxdb import __version__
from refidxdb.refidxdb import RefIdxDB
from refidxdb.sources import DATABASES
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)-8s - %(levelname)s - %(message)s",
)

# Rich tracebacks are an application concern, so they are installed here at the
# CLI entry point rather than inside the importable library modules.
_ = install(show_locals=True)


@click.group()
@click.version_option(__version__, prog_name="refidxdb")
def cli() -> None:
    pass


@cli.command(
    help="""Manage databases.
    Use commas for multiple entries.
    The input `all` processes all available databases."""
)
@click.option(
    "--download",
    help="Download provided databases.",
)
@click.option(
    "--clean",
    help="Remove provided databases.",
)
def db(download, clean) -> None:
    if download is not None:
        download_db(download)
    if clean is not None:
        clean_db(clean)


def resolve_dbs(dbs: str):
    if dbs == "all":
        return list(DATABASES.values())
    resolved = []
    for item in dbs.split(","):
        key = item.strip().lower()
        try:
            resolved.append(DATABASES[key])
        except KeyError:
            raise click.BadParameter(
                f"Unknown database: {item.strip()!r} "
                f"(choose from {', '.join(DATABASES)} or 'all')"
            ) from None
    return resolved


def clean_db(dbs: str):
    for Src in resolve_dbs(dbs):
        cache_dir = Src().cache_dir
        if Path(cache_dir).exists():
            shutil.rmtree(cache_dir, ignore_errors=True)
            click.echo(f"Removed cache for {Src.__name__} at {cache_dir}")
        else:
            click.echo(f"No cache found for {Src.__name__} at {cache_dir}")
    click.echo("Bye :)")


def _download(Src):
    # _identity is a 1-based tuple in pool workers and empty in the main process.
    identity = current_process()._identity
    worker_id = identity[0] if identity else 0
    db = Src()
    db.download(position=worker_id)


def download_db(dbs: str):
    download_list = resolve_dbs(dbs)

    # Use with 3.14: with Pool(processes=2) as pool:
    # Polars can get deadlock if fork() is used
    # Using spawn() fixes this for now
    # Should be fixed in 3.14
    with get_context("spawn").Pool(processes=2) as pool:
        for _ in tqdm(
            pool.imap(_download, download_list),
            total=len(download_list),
            desc="TOTAL",
            position=0,
        ):
            pass

    click.echo("All databases downloaded!")
    click.echo("Bye :)")


@cli.command(help="""Display data from a database.""")
@click.option(
    "--db",
    help="Database to be used.",
)
@click.option(
    "--data",
    help="Data to be used from the database.",
)
@click.option(
    "--display",
    default="table",
    show_default=True,
    help="How to display the data: table or graph.",
)
@click.option(
    "--bounds",
    help="Bounds for the graph. Two values separated by a comma, e.g., `1.5,3.56`",
)
def show(db, data, display, bounds) -> None:  # pragma: no cover
    scale = 1e-6
    df = parse_source(db, data)
    nk = df.nk.with_columns(pl.col("w").truediv(scale))
    if bounds is not None:
        bounds = [float(val) for val in bounds.split(",")]
        if len(bounds) != 2:
            raise click.BadParameter(
                "Bounds need to have two values separated by a comma.",
                param_hint="--bounds",
            )
        nk = nk.filter((pl.col("w") > bounds[0]) & (pl.col("w") < bounds[1]))
    match str.lower(display):
        case "table":
            with pl.Config(tbl_rows=1000):
                click.echo(nk)
        case "graph":
            if "n" in df.nk.columns:
                plt.plot(nk["w"], nk["n"], label="n")
            if "k" in df.nk.columns:
                plt.plot(nk["w"], nk["k"], label="k")
            plt.title("Refractive index values")
            plt.xlabel(f"Wavelength in {scale}")
            plt.ylabel("Values")
            plt.show()
        case _:
            raise click.BadParameter(
                "Unsupported display option", param_hint="--display"
            )


def parse_source(db, data) -> RefIdxDB:  # pragma: no cover
    match str.lower(db):
        case "refidx":
            return RefIdx(path=data)
        case "aria":
            return Aria(path=data)
        case _:
            raise click.BadParameter(
                f"Provided {db} is not supported!", param_hint="--db"
            )


@cli.command(help="""Explore data using Streamlit""")
def explore():  # pragma: no cover
    logger = logging.getLogger(__name__)

    try:
        from streamlit import runtime
        from streamlit.web import cli as stcli
    except ImportError:
        logger.info(
            "Error: Streamlit is not installed. Please install it: pip install streamlit"
        )
        sys.exit(1)

    if not runtime.exists():
        app_path = Path(__file__).parent / "app.py"
        if not app_path.exists():
            print(f"Error: Streamlit app not found at expected location: {app_path}")
            print("Please ensure app.py exists within the refidxdb directory.")
            sys.exit(1)

        print(f"Launching Streamlit app: {app_path}")
        sys.argv = ["streamlit", "run", str(app_path)]
        sys.exit(stcli.main())
    else:
        print(
            "Streamlit runtime already exists (maybe running from within Streamlit?)."
        )
