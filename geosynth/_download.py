import zipfile
from pathlib import Path
from typing import Iterable, Optional
from urllib.error import HTTPError

from rich import print
from rich.progress import Progress

from .common import DEFAULT_DATASET_PATH, PathLike
from .data import Data
from .progress import UrlRetrieveProgressBar


def _validate_dtypes(dtypes: Iterable):
    for dtype in dtypes:
        if dtype not in Data:
            raise ValueError(
                f'Specifided dtype "{dtype}" is invalid. Must be one of: {list(Data).sort()}.'
            )


def download(
    dst: Optional[PathLike] = None,
    dtypes: Optional[Iterable[str]] = None,
    variant: str = "demo",
    force: bool = False,
    cleanup: bool = True,
    progress: Optional[Progress] = None,
) -> Path:
    """Download the GeoSynth dataset.

    Parameters
    ----------
    dst : PathLike
        If ``None``, downloads to default location ``~/data/geosynth``.
    dtype : Iterable
        List of data types to download. For example::

            ["rgb", "depth"]

        Defaults to downloading all non-hdr datatypes.
    variant: str
        Variant of the GeoSynth dataset to download.
    force: bool
        Force a redownload, despite cached files.
        Defaults to ``False``.
    cleanup: bool
        Delete downloaded zipfile(s) after downloading & unzipping.
        Defaults to ``True``.
    progress: Optional[rich.progress.Progress]
        Optional Rich Progress object to update with progress.

    Returns
    -------
    dst: Path
        The destination download directory.
    """
    if dst is None:
        dst = DEFAULT_DATASET_PATH
    dst = Path(dst).expanduser()

    if not dtypes or "non-hdr" in dtypes:
        # All non-hdr types
        dtypes = [x for x in Data if "hdr_" not in x]
    elif "all" in dtypes:
        dtypes = list(Data)

    _validate_dtypes(dtypes)

    progress_bars = {}

    if progress:
        # Start up all the Progress Bar Tasks
        for dtype in dtypes:
            progress_bars[dtype] = UrlRetrieveProgressBar(
                progress, f"{dtype} downloading"
            )

    for dtype in dtypes:
        try:
            zip_path = Data[dtype].download_zip(
                dst,
                variant=variant,
                force=force,
                reporthook=progress_bars.get(dtype),
            )
        except HTTPError as e:
            http_error_code = e.getcode()
            if http_error_code == 404:
                print(
                    f'[bold red]{dtype} for variant "{variant}" has not been uploaded yet.\n'
                    "    Please check back later.[/bold red]"
                )
            else:
                raise

            if progress:
                progress_bars[dtype].stop(f"[bold red]{dtype} Unavailable.[/bold red]")

            continue

        progress_bar = progress_bars.get(dtype)
        if zip_path.stat().st_size:
            with zipfile.ZipFile(zip_path, "r") as f:
                if progress_bar:
                    progress_bar.update(
                        description=f"{dtype} extracting",
                        total=len(f.namelist()),
                        completed=0,
                    )
                for member in f.namelist():
                    f.extract(member, path=dst / variant)
                    if progress_bar:
                        progress_bar.update(advance=1)

            if cleanup:
                zip_path.unlink()
                zip_path.touch()  # So that subsequent download calls know to not download.

        if progress_bar:
            progress_bar.update(description=f"{dtype} complete")

    return dst / variant
