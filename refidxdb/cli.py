# Guide: https://medium.com/clarityai-engineering/how-to-create-and-distribute-a-minimalist-cli-tool-with-python-poetry-click-and-pipx-c0580af4c026
import logging
import sys
from multiprocessing import current_process, get_context
from pathlib import Path

import click
import plotext as plt
import polars as pl
from streamlit import runtime
from streamlit.web import cli as stcli
from tqdm import tqdm

from refidxdb.refidxdb import RefIdxDB
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

databases = {
    item.__name__.lower(): item
    for item in [
        Aria,
        RefIdx,
    ]
}


@click.group()
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
        raise Exception("Cleaning is not yet implemented.")


def _download(Src):
    worker_id = current_process()._identity[0]
    db = Src()
    db.download(position=worker_id)


def download_db(dbs: str):
    if dbs == "all":
        download_list = list(databases.values())
    else:
        db_list = [item.lower() for item in dbs.split(",")]
        download_list = [databases[item] for item in db_list]

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

    click.echo("All databases downlaoded!")
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
            raise Exception("Bounds need to have two values separated by a comma.")
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
            raise Exception("Unsupported display option")


def parse_source(db, data) -> RefIdxDB:  # pragma: no cover
    match str.lower(db):
        case "refidx":
            return RefIdx(path=data)
        case "aria":
            return Aria(path=data)
        case _:
            raise Exception(f"Provided {db} is not supported!")


@cli.command(help="""Explore data using Streamlit""")
def explore():  # pragma: no cover
    # if not runtime.exists():
    #     print(Path(__file__).parent)
    #     sys.argv = ["streamlit", "run", f"{Path(__file__).parent}/app.py"]
    #     sys.exit(stcli.main())

    # logger = create_logger(logging.INFO)
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
        # app_path = Path(__file__).parent / "pyfracval" / "app.py"
        app_path = Path(__file__).parent / "app.py"
        if not app_path.exists():
            print(f"Error: Streamlit app not found at expected location: {app_path}")
            print("Please ensure app.py exists within the pyfracval directory.")
            sys.exit(1)

        print(f"Launching Streamlit app: {app_path}")
        sys.argv = ["streamlit", "run", str(app_path)]
        sys.exit(stcli.main())
    else:
        print(
            "Streamlit runtime already exists (maybe running from within Streamlit?)."
        )
