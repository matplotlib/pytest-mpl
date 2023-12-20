import json

import pytest
from helpers import pytester_path


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
