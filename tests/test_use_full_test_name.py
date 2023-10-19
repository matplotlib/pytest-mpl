import shutil
from pathlib import Path

import pytest
from helpers import pytester_path

FULL_TEST_NAME = "test_config.TestClass.test_mpl"
SHORT_TEST_NAME = "test_mpl"


@pytest.mark.parametrize(
    "ini, cli, expected_baseline_name, success_expected",
    [
        (None, None, SHORT_TEST_NAME, True),
        (False, None, SHORT_TEST_NAME, True),
        (True, None, FULL_TEST_NAME, True),
        (False, True, FULL_TEST_NAME, True),
        (None, True, FULL_TEST_NAME, True),
        (True, True, "bad_name", False),
    ],
)
def test_config(pytester, ini, cli, expected_baseline_name, success_expected):
    path = pytester_path(pytester)
    shutil.copyfile(  # Test will only pass if baseline is at expected path
        Path(__file__).parent / "baseline" / "2.0.x" / "test_base_style.png",
        path / f"{expected_baseline_name}.png",
    )
    ini = f"mpl-use-full-test-name = {ini}" if ini is not None else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-default-style = fivethirtyeight
        mpl-baseline-path = {path}
        {ini}
        """
    )
    pytester.makepyfile(
        """
        import matplotlib.pyplot as plt
        import pytest
        class TestClass:
            @pytest.mark.mpl_image_compare
            def test_mpl(self):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3])
                return fig
        """
    )
    cli = "--mpl-use-full-test-name" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    if success_expected:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)
