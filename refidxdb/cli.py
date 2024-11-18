# Guide: https://medium.com/clarityai-engineering/how-to-create-and-distribute-a-minimalist-cli-tool-with-python-poetry-click-and-pipx-c0580af4c026

import click

from .refidx import RefIdx
from .aria import Aria

@click.command()
@click.option("--download", default=False, show_default=True, is_flag=True, help="Download the databases")
def cli(download) -> None:
    if download:
        download_db()

def download_db() ->None:
    for Source in [RefIdx, Aria]:
        db = Source()
        db.download()
