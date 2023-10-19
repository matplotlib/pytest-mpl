from pathlib import Path

import pytest
from helpers import pytester_path


@pytest.mark.parametrize(
    "ini, cli, enabled_expected",
    [
        (None, None, False),
        (True, None, True),
        (False, None, False),
        (False, True, True),
        (True, True, True),
    ],
)
def test_config(pytester, ini, cli, enabled_expected):
    path = pytester_path(pytester)
    ini = f"mpl-results-always = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-default-style = fivethirtyeight
        mpl-baseline-path = {Path(__file__).parent / "baseline" / "2.0.x"}
        mpl-results-path = {path}
        {ini}
        """
    )
    pytester.makepyfile(
        """
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare
        def test_base_style():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig
        """
    )
    cli = "--mpl-results-always" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    result.assert_outcomes(passed=1)
    assert (path / "test_config.test_base_style" / "result.png").exists() == enabled_expected
