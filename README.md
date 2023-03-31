<h1 align="center">
   <img src="https://raw.githubusercontent.com/geomagical/geosynth/main/assets/banner.jpg" width="600">
</h1><br>

# GeoSynth: A Photorealistic Synthetic Indoor Dataset for Scene Understanding

[![pypi](https://img.shields.io/pypi/v/geosynth.svg)](https://pypi.python.org/pypi/geosynth)
[![paper](https://img.shields.io/badge/ieee%20vr-paper-green)](https://ieeexplore.ieee.org/document/10050341)
[![Documentation Status](https://readthedocs.org/projects/geosynth/badge/?version=latest)](https://geosynth.readthedocs.io/en/latest/?badge=latest)


Deep learning has revolutionized many scene perception tasks
over the past decade. Some of these improvements can be attributed
to the development of large labeled datasets. The creation of such
datasets can be an expensive, time-consuming, and is an imperfect
process. To address these issues, we introduce GeoSynth, a diverse
photorealistic synthetic dataset for indoor scene perception tasks.
Each GeoSynth exemplar contains rich labels, including segmentation,
geometry, camera parameters, surface material, lighting, and
more. We demonstrate that supplementing real training data with
GeoSynth can significantly improve network performance on
perception tasks, like semantic segmentation.

GeoSynth is used internally at [Geomagical Labs](https://www.geomagical.com) to help power the [IKEA Kreativ](https://www.ikea.com/us/en/home-design/) home design experience.


# Installation
GeoSynth requires Python ``>=3.8`` and can be installed via:

```bash
pip install geosynth
```

This installs:
1. The `geosynth` python library, providing a pythonic interface for
   reading and processing GeoSynth data.
2. The `geosynth` command-line tool, which offers a convenient way of
   downloading the geosynth dataset.

Some optional visualization tools will require `matplotlib`.

# Dataset Download

**Attention!** Currently only the `demo` variant is available, the full dataset and additional datatypes will be released in the near future.

<!---
To download all non-hdr dataset, run:

```bash
geosynth download non-hdr --variant=full
```
-->

To download just a few scenes of the dataset, download the `demo` variant.
The `demo` variant is the default `--variant` option:


```bash
geosynth download non-hdr --variant=demo
```

If you also wish to include HDR data, specify `all`, instead.
The HDR data more than doubles the size of the download, so only download it if you need it.
It is recommended to only specify the data types you need.

By default, the contents will be downloaded to `~/data/geosynth/`.
To specify an alternative download location, specify the `--dst` argument.

See all download options by running `geosynth download --help`:

```bash
$ geosynth download --help

Usage: geosynth download [OPTIONS] DTYPES...

 Download the GeoSynth data.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────╮
│ *    dtypes      DTYPES...  Assets to download. Either specify "non-hdr", "all", or  │
│                             a subset of: [cube_environment_map, depth, extrinsics,   │
│                             gravity, hdr_cube_environment_map, hdr_reflectance,      │
│                             hdr_residual, hdr_rgb, hdr_shading,                      │
│                             hdr_sphere_environment_map, instance_segmentation,       │
│                             intrinsics, layout_lines_full, layout_lines_occluded,    │
│                             layout_lines_visible, lighting, normals, reflectance,    │
│                             residual, rgb, semantic_segmentation, shading,           │
│                             sphere_environment_map]).                                │
│                             [required]                                               │
╰──────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────╮
│ --dst                        PATH         GeoSynth download directory.               │
│                                           [default: ~/data/geosynth]                 │
│ --variant                    [demo|full]  Variant of dataset to download.            │
│                                           [default: demo]                            │
│ --force      --no-force                   Force a re-download, despite locally       │
│                                           cached files.                              │
│                                           [default: no-force]                        │
│ --cleanup    --no-cleanup                 Delete zip files after unzipping.          │
│                                           [default: cleanup]                         │
│ --help                                    Show this message and exit.                │
╰──────────────────────────────────────────────────────────────────────────────────────╯
```

<!---
Currently, the following data types have been released:

* `rgb`
* `hdr_rgb`
* `depth`
* `normals`
* `intrinsics`
* `gravity`
* `semantic_segmentation`
* `instance_segmentation`
* `shading`
* `reflectance`
* `residual`
* `hdr_shading`
* `hdr_reflectance`
* `hdr_residual`
-->


# Usage
Once the dataset has been downloaded, data can be accessed in python:

```python
from geosynth import GeoSynth

geosynth = GeoSynth("PATH_TO_DATA")  # or leave empty for default "~/data/geosynth/".

print(f"GeoSynth has {len(geosynth)} scenes.")

scene = geosynth[100]  # Data can be accessed via indexing like a list.

# or iterated over in a for loop:
for scene in dataset:
    # Each Scene object contains attributres for each datatype.
    # Contents can be read from disk via the ``read`` method.
    rgb = scene.rgb.read()  # (H, W, 3) np.ndarray
    depth = scene.depth.read()  # (H, W) np.ndarray
    intrinsics = scene.intrinsics.read()  # (3, 3) camera intrinsics
    instances = scene.instance_segmentation.read()  # dictionary of instance masks.

    # many datatypes have a ``visualize`` method
    depth_viz = scene.depth.visualize(depth)  # Returns a (H,W,3) turbo-colorized image.
    instances_viz = scene.instance_segmentation.visualize(instances, rgb=rgb)
```

# License
The GeoSynth **code** is released under the [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html).

The GeoSynth **data** provided at https://storage.googleapis.com/geomagical-geosynth-public is available under the [Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
