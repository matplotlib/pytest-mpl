import json

import pytest
from helpers import pytester_path


def test_skip_hash(pytester):
    """Test that skip_hash=True skips hash comparison and uses baseline instead."""
    path = pytester_path(pytester)
    hash_library = path / "hash_library.json"
    baseline_dir = path / "baseline"

    # Generate baseline image (no hash library needed for generation)
    pytester.makepyfile(
        """
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare()
        def test_mpl():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([1, 3, 2])
            return fig
        """
    )
    pytester.runpytest(f"--mpl-generate-path={baseline_dir}")

    # Create hash library with bad hash
    with open(hash_library, "w") as fp:
        json.dump({"test_skip_hash.test_mpl": "bad-hash-value"}, fp)

    # Without skip_hash: should fail (hash mismatch)
    result = pytester.runpytest("--mpl",
                                f"--mpl-hash-library={hash_library}",
                                f"--mpl-baseline-path={baseline_dir}")
    result.assert_outcomes(failed=1)

    # With skip_hash=True: should pass (uses baseline comparison, skips hash)
    pytester.makepyfile(
        """
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare(skip_hash=True)
        def test_mpl():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([1, 3, 2])
            return fig
        """
    )
    result = pytester.runpytest("--mpl",
                                f"--mpl-hash-library={hash_library}",
                                f"--mpl-baseline-path={baseline_dir}")
    result.assert_outcomes(passed=1)


def test_skip_hash_not_generated(pytester):
    """Test that skip_hash=True tests are not included in generated hash library."""
    path = pytester_path(pytester)
    hash_library = path / "hash_library.json"

    pytester.makepyfile(
        """
        import matplotlib.pyplot as plt
        import pytest

        @pytest.mark.mpl_image_compare()
        def test_normal():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([1, 2, 3])
            return fig

        @pytest.mark.mpl_image_compare(skip_hash=True)
        def test_skip():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([3, 2, 1])
            return fig
        """
    )
    pytester.runpytest(f"--mpl-generate-hash-library={hash_library}")

    # Check generated hash library
    with open(hash_library) as fp:
        hashes = json.load(fp)

    # test_normal should be in the hash library
    assert "test_skip_hash_not_generated.test_normal" in hashes
    # test_skip should NOT be in the hash library
    assert "test_skip_hash_not_generated.test_skip" not in hashes


@pytest.mark.parametrize(
    "ini, cli, kwarg, success_expected",
    [
        ("bad", None, None, False),
        ("good", None, None, True),
        ("bad", "good", None, True),
        ("bad", "bad", "good", False),  # Note: CLI overrides kwarg
        ("bad", "good", "bad", True),
    ],
)
def test_config(pytester, ini, cli, kwarg, success_expected):
    path = pytester_path(pytester)
    hash_libraries = {
        "good": path / "good_hash_library.json",
        "bad": path / "bad_hash_library.json",
    }
    ini = f"mpl-hash-library = {hash_libraries[ini]}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-deterministic: true
        {ini}
        """
    )
    kwarg = f"hash_library=r'{hash_libraries[kwarg]}'" if kwarg else ""
    pytester.makepyfile(
        f"""
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare({kwarg})
        def test_mpl():
            fig, ax = plt.subplots()
            ax.plot([1, 3, 2])
            return fig
        """
    )
    pytester.runpytest(f"--mpl-generate-hash-library={hash_libraries['good']}")
    with open(hash_libraries["bad"], "w") as fp:
        json.dump({"test_config.test_mpl": "bad-value"}, fp)
    cli = f"--mpl-hash-library={hash_libraries[cli]}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    if success_expected:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)


