import numpy as np

from geosynth.models.lighting import (
    AmbientLight,
    DirectionalLight,
    Lighting,
    LightSource,
    PointLight,
)


def test_light_source():
    light = LightSource(
        color=(0.1, 0.2, 0.3),  # pyright: ignore[reportGeneralTypeIssues]
        intensity=0.42,
    )
    assert isinstance(light.color, np.ndarray)
    assert light.color.dtype == np.float32
    assert light.color.shape == (3,)


def test_ambient_light():
    light = AmbientLight(
        color=(0.1, 0.2, 0.3),  # pyright: ignore[reportGeneralTypeIssues]
        intensity=0.42,
    )
    assert isinstance(light.color, np.ndarray)
    assert light.color.dtype == np.float32
    assert light.color.shape == (3,)


def test_point_light():
    light = PointLight(
        color=(0.1, 0.2, 0.3),  # pyright: ignore[reportGeneralTypeIssues]
        intensity=0.42,
        position=(1, 2, 3),  # pyright: ignore[reportGeneralTypeIssues]
    )

    assert isinstance(light.position, np.ndarray)
    assert light.position.dtype == np.float32
    assert light.position.shape == (3,)


def test_directional_light():
    light = DirectionalLight(
        color=(0.1, 0.2, 0.3),  # pyright: ignore[reportGeneralTypeIssues]
        intensity=0.42,
        direction=(1, 0, 0),  # pyright: ignore[reportGeneralTypeIssues]
        volume=[
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ],  # pyright: ignore[reportGeneralTypeIssues]
    )

    assert isinstance(light.direction, np.ndarray)
    assert light.direction.dtype == np.float32
    assert light.direction.shape == (3,)

    assert isinstance(light.volume, np.ndarray)
    assert light.volume.dtype == np.float32
    assert light.volume.shape == (3, 3)


def test_lighting_whole_model():
    definition = {
        "ambient": {"color": (0.0, 0.0, 0.0), "intensity": 0.0},
        "directionals": [
            {
                "color": (1.0, 0.4588235294117647, 0.21568627450980393),
                "intensity": 0.008176614881439084,
                "direction": [
                    -3.4646946005523205e-05,
                    0.9992689490318298,
                    0.03823035582900047,
                ],
                "volume": [
                    [1.3297369480133057, -0.0016325851902365685, 0.04387778043746948],
                    [9.441948350286111e-05, -2.724630355834961, -0.10423829406499863],
                    [0.0, 0.0, 0.0],
                ],
            },
            {
                "color": (1.0, 0.4588235294117647, 0.21568627450980393),
                "intensity": 0.008176614881439084,
                "direction": [
                    -3.4646946005523205e-05,
                    0.9992689490318298,
                    0.03823035582900047,
                ],
                "volume": [
                    [-0.09387559443712234, -0.10869316756725311, 2.8409478664398193],
                    [9.474962280364707e-05, -2.7769644260406494, -0.10624206066131592],
                    [0.0, 0.0, 0.0],
                ],
            },
        ],
        "points": [
            {
                "color": (1.0, 0.7764705882352941, 0.7058823529411765),
                "intensity": 0.030662305805396566,
                "position": [
                    -0.8580608367919922,
                    -0.28282231092453003,
                    5.766456604003906,
                ],
            },
            {
                "color": (1.0, 0.7764705882352941, 0.7058823529411765),
                "intensity": 0.030662305805396566,
                "position": [
                    -0.864791750907898,
                    -0.2906154692173004,
                    5.970149040222168,
                ],
            },
        ],
    }
    Lighting(**definition)
