import json

import pytest
from helpers import pytester_path


@pytest.mark.parametrize(
    "ini, cli, expected",
    [
        ("json", None, {"json"}),
        ("json", "html", {"html"}),
        ("basic-html", "json", {"json"}),
        (None, "json,basic-html,html", {"json", "basic-html", "html"}),
    ],
)
def test_config(pytester, ini, cli, expected):
    path = pytester_path(pytester)
    ini = f"mpl-generate-summary = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-results-path = {path}
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
    cli = f"--mpl-generate-summary={cli}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    result.assert_outcomes(failed=1)

    json_summary = path / "results.json"
    if "json" in expected:
        with open(json_summary) as fp:
            results = json.load(fp)
            assert "test_config.test_mpl" in results
    else:
        assert not json_summary.exists()

    html_summary = path / "fig_comparison.html"
    if "html" in expected:
        with open(html_summary) as fp:
            raw = fp.read()
        assert "bootstrap" in raw
        assert "test_config.test_mpl" in raw
    else:
        assert not html_summary.exists()

    basic_html_summary = path / "fig_comparison_basic.html"
    if "basic-html" in expected:
        with open(basic_html_summary) as fp:
            raw = fp.read()
        assert "bootstrap" not in raw
        assert "test_config.test_mpl" in raw
    else:
        assert not basic_html_summary.exists()
