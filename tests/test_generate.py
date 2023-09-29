PYFILE = (
    """
    import matplotlib.pyplot as plt
    import pytest
    @pytest.mark.mpl_image_compare
    def test_mpl():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        return fig
    """
)


def test_generate_baseline_images(pytester):
    pytester.makepyfile(PYFILE)
    baseline_dir = pytester.path / "alternative_baseline"
    result = pytester.runpytest(f"--mpl-generate-path={baseline_dir}")
    result.assert_outcomes(skipped=1)
    assert (baseline_dir / "test_mpl.png").exists()


def test_generate_baseline_hashes(pytester):
    pytester.makepyfile(PYFILE)
    hash_library = pytester.path / "alternative_baseline" / "hash_library_1.json"
    result = pytester.runpytest(
        f"--mpl-generate-hash-library={hash_library}",
        f"--mpl-results-path={pytester.path}",
    )
    result.assert_outcomes(failed=1)  # this option enables --mpl
    assert hash_library.exists()
    assert (pytester.path / "test_generate_baseline_hashes.test_mpl" / "result.png").exists()


def test_generate_baseline_images_and_hashes(pytester):
    pytester.makepyfile(PYFILE)
    baseline_dir = pytester.path / "alternative_baseline"
    hash_library = pytester.path / "alternative_baseline" / "hash_library_1.json"
    result = pytester.runpytest(
        f"--mpl-generate-path={baseline_dir}",
        f"--mpl-generate-hash-library={hash_library}",
    )
    result.assert_outcomes(skipped=1)
    assert (baseline_dir / "test_mpl.png").exists()
    assert hash_library.exists()
