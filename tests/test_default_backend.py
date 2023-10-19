import pytest


@pytest.mark.parametrize(
    "ini, cli, kwarg, expected",
    [
        ("backend1", None, None, "backend1"),
        ("backend1", "backend2", None, "backend2"),
        ("backend1", "backend2", "backend3", "backend3"),
    ],
)
def test_config(pytester, ini, cli, kwarg, expected):
    ini = f"mpl-default-backend = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        {ini}
        """
    )
    kwarg = f"backend='{kwarg}'" if kwarg else ""
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
    cli = f"--mpl-default-backend={cli}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    result.assert_outcomes(failed=1)
    result.stdout.re_match_lines([f".*(ModuleNotFound|Value)Error: .*{expected}.*"])
