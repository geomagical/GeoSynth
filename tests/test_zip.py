import filecmp
import zipfile
from pathlib import Path

import pytest

from geosynth.data import Gravity


@pytest.mark.network
def test_download_zip(tmp_path):
    expected_zip_file = Path("tests/zip/gravity.zip")
    actual_zip_file = Gravity.download_zip(tmp_path, variant="demo")
    assert filecmp.cmp(expected_zip_file, actual_zip_file)


def test_download_zip_invalid_variant(tmp_path):
    with pytest.raises(ValueError) as e:
        Gravity.download_zip(tmp_path, variant="foobar")
    assert (
        str(e.value)
        == "Variant \"foobar\" not in valid. Choose one of: ['demo', 'full']."
    )
