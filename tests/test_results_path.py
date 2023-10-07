import pytest
from helpers import pytester_path


@pytest.mark.parametrize(
    "ini, cli, expected",
    [
        ("dir1", None, "dir1"),
        ("dir1", "dir2", "dir2"),
        (None, "dir2", "dir2"),
    ],
)
def test_config(pytester, ini, cli, expected):
    ini = f"mpl-results-path = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        {ini}
        """
    )
    pytester.makepyfile(
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
    cli = f"--mpl-results-path={cli}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    result.assert_outcomes(failed=1)
    assert (pytester_path(pytester) / expected / "test_config.test_mpl" / "result.png").exists()
