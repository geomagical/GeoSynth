import typer
from typer import Option

import geosynth

from .download import download

app = typer.Typer(
    no_args_is_help=True, pretty_exceptions_enable=False, add_completion=False
)
app.command()(download)


def version_callback(value: bool):
    if not value:
        return
    print(geosynth.__version__)
    raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Display GeoSynth version.",
    ),
):
    pass


def run_app(*args, **kwargs):
    app(*args, **kwargs)
