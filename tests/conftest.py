import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--network",
        action="store_true",
        help="Include tests that interact with network (marked with marker @network)",
    )


def pytest_runtest_setup(item):
    if "network" in item.keywords and not item.config.getoption("--network"):
        pytest.skip("need --network option to run this test")
