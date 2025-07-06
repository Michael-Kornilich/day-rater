from daemon.daemon import *


class TestDBWriter:
    pass


def test_get_season():
    io = {
        1: "winter",
        2: "winter",
        3: "spring",
        4: "spring",
        5: "spring",
        6: "summer",
        7: "summer",
        8: "summer",
        9: "autumn",
        10: "autumn",
        11: "autumn",
        12: "winter"
    }
    for i, o in io.items():
        assert get_season(datetime(year=2025, month=i, day=5)) == o
