import pytest
from helpers import pytester_path


@pytest.mark.parametrize(
    "ini, cli, kwarg, expected",
    [
        ("sty1", None, None, "sty1"),
        ("sty1", "sty2", None, "sty2"),
        ("sty1", "sty2", "sty3", "sty3"),
    ],
)
def test_config(pytester, ini, cli, kwarg, expected):
    ini = "mpl-default-style = " + ini if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-baseline-path = {pytester_path(pytester)}
        {ini}
        """
    )
    kwarg = f"style='{kwarg}'" if kwarg else ""
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

    cli = "--mpl-default-style=" + cli if cli else ""
    result = pytester.runpytest("--mpl", cli)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([f"*OSError: *'{expected}'*"])
