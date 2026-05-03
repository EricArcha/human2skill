from packaging.version import Version


def test_package_imports():
    import human2skill

    assert human2skill.__version__
    assert isinstance(human2skill.__version__, str)
    # Verify it's a valid PEP 440 version string.
    Version(human2skill.__version__)
