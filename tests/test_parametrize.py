from speedtest import parametrize


def test_parametrize():
    @parametrize("a,b", [(1, 2), (2, 3)])
    def f(a, b):
        return a + b

    # call with empty args and parametrize.
    for option, result in zip(f, [(1, 2), (2, 3)]):
        assert option() == sum(result)

    @parametrize("a", [1, 2, 3])
    def f2(a):
        return a**2

    # call with empty args and parametrize.
    for option, result in zip(f2, [1, 2, 3]):
        assert option() == result**2
