import shutil
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "ini, cli, kwarg, expected_baseline_path, success_expected",
    [
        ("dir1", None, None, "dir1", True),
        ("dir1", "dir2", None, "dir2", True),
        ("dir1", "dir2", "dir3", "dir3", True),
        ("dir1", "dir2", "dir3", "dir2", False),
        (None, None, "dir3", "dir3", True),
    ],
)
def test_config(pytester, ini, cli, kwarg, expected_baseline_path, success_expected):
    (pytester.path / expected_baseline_path).mkdir()
    shutil.copyfile(  # Test will only pass if baseline is at expected path
        Path(__file__).parent / "baseline" / "2.0.x" / "test_base_style.png",
        pytester.path / expected_baseline_path / "test_mpl.png",
    )
    ini = f"mpl-baseline-path = {pytester.path / ini}" if ini is not None else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-default-style = fivethirtyeight
        {ini}
        """
    )
    kwarg = f"baseline_dir=r'{pytester.path / kwarg}'" if kwarg else ""
    pytester.makepyfile(
        f"""
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare({kwarg})
        def test_mpl():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig
        """
    )
    cli = f"--mpl-baseline-path={pytester.path / cli}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    if success_expected:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)
