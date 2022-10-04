from .. import __version__


def test_Version():
    assert isinstance(__version__, str)
    assert len(__version__) > len("#.#.#")
