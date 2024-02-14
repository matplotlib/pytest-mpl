import matplotlib
import matplotlib.pyplot as plt
import pytest
from helpers import pytester_path, skip_if_format_unsupported
from packaging.version import Version
from PIL import Image

MPL_VERSION = Version(matplotlib.__version__)

METADATA = {
    "png": {"Software": None},
    "pdf": {"Creator": None, "Producer": None, "CreationDate": None},
    "eps": {"Creator": "test"},
    "svg": {"Date": None},
}


def test_multiple_cli_flags(pytester):
    result = pytester.runpytest("--mpl", "--mpl-deterministic", "--mpl-no-deterministic")
    result.stderr.fnmatch_lines(
        ["*ValueError: Only one of `--mpl-deterministic` and `--mpl-no-deterministic` can be set.*"]
    )


def test_warning(pytester):
    path = pytester_path(pytester)
    hash_library = path / "hash_library.json"
    kwarg = f"hash_library=r'{hash_library}'"
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
    result = pytester.runpytest(f"--mpl-generate-hash-library={hash_library}")
    result.stdout.fnmatch_lines(["*FutureWarning: deterministic option not set*"])
    result.assert_outcomes(failed=1)


@pytest.mark.parametrize("file_format", ["eps", "pdf", "png", "svg"])
@pytest.mark.parametrize(
    "ini, cli, kwarg, success_expected",
    [
        ("true", "", None, True),
        ("false", "--mpl-deterministic", None, True),
        ("true", "--mpl-no-deterministic", None, False),
        ("", "--mpl-no-deterministic", True, True),
        ("true", "", False, False),
    ],
)
@pytest.mark.skipif(MPL_VERSION < Version("3.3.0"), reason="Test unsupported: Default metadata is different in MPL<3.3")
def test_config(pytester, file_format, ini, cli, kwarg, success_expected):
    skip_if_format_unsupported(file_format, using_hashes=True)

    path = pytester_path(pytester)
    baseline_dir = path / "baseline"
    hash_library = path / "hash_library.json"

    ini = f"mpl-deterministic = {ini}" if ini else ""
    pytester.makeini(
        f"""
        [pytest]
        mpl-hash-library = {hash_library}
        {ini}
        """
    )

    kwarg = f", deterministic={kwarg}" if isinstance(kwarg, bool) else ""
    pytester.makepyfile(
        f"""
        import matplotlib.pyplot as plt
        import pytest
        @pytest.mark.mpl_image_compare(savefig_kwargs={{'format': '{file_format}'}}{kwarg})
        def test_mpl():
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3])
            return fig
        """
    )

    # Generate baseline hashes
    assert not hash_library.exists()
    pytester.runpytest(
        f"--mpl-generate-path={baseline_dir}",
        f"--mpl-generate-hash-library={hash_library}",
        cli,
    )
    assert hash_library.exists()
    baseline_image = baseline_dir / f"test_mpl.{file_format}"
    assert baseline_image.exists()
    deterministic_metadata = METADATA[file_format]

    if file_format == "svg":  # The only format that is reliably non-deterministic between runs
        result = pytester.runpytest("--mpl", f"--mpl-baseline-path={baseline_dir}", cli)
        if success_expected:
            result.assert_outcomes(passed=1)
        else:
            result.assert_outcomes(failed=1)

    elif file_format == "pdf":
        with open(baseline_image, "rb") as fp:
            file = str(fp.read())
        for metadata_key in deterministic_metadata.keys():
            key_in_file = fr"/{metadata_key}" in file
            if success_expected:  # metadata keys should not be in the file
                assert not key_in_file
            else:
                assert key_in_file

    else:  # "eps" or "png"
        with Image.open(str(baseline_image)) as image:
            actual_metadata = image.info
        for k, expected in deterministic_metadata.items():
            actual = actual_metadata.get(k, None)
            if success_expected:  # metadata keys should not be in the file
                if expected is None:
                    assert actual is None
                else:
                    assert actual == expected
            else:  # metadata keys should still be in the file
                if expected is None:
                    assert actual is not None
                else:
                    assert actual != expected
