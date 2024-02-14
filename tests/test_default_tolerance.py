from pathlib import Path

import pytest
from PIL import Image, ImageDraw

TEST_NAME = "test_base_style"


@pytest.fixture(scope="module")
def baseline_image(tmp_path_factory):
    path = Path(__file__).parent / "baseline" / "2.0.x" / f"{TEST_NAME}.png"
    with Image.open(path) as image:
        draw = ImageDraw.Draw(image)
        draw.rectangle(((0, 0), (100, 100)), fill="red")
        output = tmp_path_factory.mktemp("data") / f"{TEST_NAME}.png"
        image.save(output)
    return output


@pytest.mark.parametrize(
    "ini, cli, kwarg, success_expected",
    [
        (40, None, None, True),
        (30, 40, None, True),
        (30, 30, 40, True),
        (30, 40, 30, False),
        (40, 30, 30, False),
    ],
)
def test_config(pytester, baseline_image, ini, cli, kwarg, success_expected):
    ini = f"mpl-default-tolerance = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-default-style = fivethirtyeight
        mpl-baseline-path = {baseline_image.parent}
        {ini}
        """
    )
    kwarg = f"tolerance={kwarg}" if kwarg else ""
    pytester.makepyfile(
        f"""
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare({kwarg})
        def {TEST_NAME}():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig
        """
    )
    cli = f"--mpl-default-tolerance={cli}" if cli else ""
    result = pytester.runpytest("--mpl", cli)
    if success_expected:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)
