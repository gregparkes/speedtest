from speedtest import parametrize


def test_parametrize():
    @parametrize("a,b", [(1, 2), (2, 3)])
    def f(a, b):
        return a + b

    # call with empty args and parametrize.
    for option in f:
        pass

    @parametrize("a", [1, 2, 3])
    def f2(a):
        return a**2

    # call with empty args and parametrize.
    for option in f2:
        pass
