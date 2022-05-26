from pathlib import Path
from unittest.mock import sentinel

import pytest

from pytest_mpl.kernels import (DEFAULT_HAMMING_TOLERANCE, DEFAULT_HASH_SIZE,
                                DEFAULT_HIGH_FREQUENCY_FACTOR, KERNEL_PHASH, KERNEL_SHA256, Kernel,
                                KernelPHash, KernelSHA256, kernel_factory)

HASH_SIZE = sentinel.hash_size
HAMMING_TOLERANCE = sentinel.hamming_tolerance
HIGH_FREQUENCY_FACTOR = sentinel.high_freq_factor

#: baseline hash (32-bit)
HASH_BASE_32 = "01234567"

#: baseline hash (64-bit)
HASH_BASE = "0123456789abcdef"

#: baseline hash with 2-bit delta (64-bit)
#            ---X------------
HASH_2BIT = "0120456789abcdef"

#: baseline with 4-bit delta (64-bit)
#            --XX-----------X
HASH_4BIT = "0100456789abcdee"


#: Absolute path to test baseline image
baseline_image = Path(__file__).parent / "baseline" / "2.0.x" / "test_base_style.png"

#: Verify availabilty of test baseline image
baseline_unavailable = not baseline_image.is_file()

#: Convenience skipif reason
baseline_missing = f"missing baseline image {str(baseline_image)!r}"


class DummyMarker:
    def __init__(self, hamming_tolerance=None):
        self.kwargs = dict(hamming_tolerance=hamming_tolerance)


class DummyPlugin:
    def __init__(self, hash_size=None, hamming_tolerance=None, high_freq_factor=None):
        self.hash_size = hash_size
        self.hamming_tolerance = hamming_tolerance
        self.high_freq_factor = high_freq_factor


def test_kernel_abc():
    emsg = "Can't instantiate abstract class Kernel"
    with pytest.raises(TypeError, match=emsg):
        Kernel(None)


def test_phash_name():
    for name, factory in kernel_factory.items():
        assert name == factory.name


#
# KernelPHash
#


def test_phash_init__set():
    plugin = DummyPlugin(
        hash_size=HASH_SIZE,
        hamming_tolerance=HAMMING_TOLERANCE,
        high_freq_factor=HIGH_FREQUENCY_FACTOR,
    )
    kernel = KernelPHash(plugin)
    assert kernel.hash_size == HASH_SIZE
    assert kernel.hamming_tolerance == HAMMING_TOLERANCE
    assert kernel.high_freq_factor == HIGH_FREQUENCY_FACTOR
    assert kernel.equivalent is None
    assert kernel.hamming_distance is None


def test_phash_init__default():
    plugin = DummyPlugin()
    kernel = KernelPHash(plugin)
    assert kernel.hash_size == DEFAULT_HASH_SIZE
    assert kernel.hamming_tolerance == DEFAULT_HAMMING_TOLERANCE
    assert kernel.high_freq_factor == DEFAULT_HIGH_FREQUENCY_FACTOR
    assert kernel.equivalent is None
    assert kernel.hamming_distance is None


def test_phash_option():
    assert KernelPHash(DummyPlugin()).option == "hamming_tolerance"


@pytest.mark.parametrize(
    "baseline,equivalent,distance",
    [
        (HASH_BASE, True, 0),
        (HASH_2BIT, True, 2),
        (HASH_4BIT, False, 4),
        (HASH_BASE_32, False, None),
    ],
)
def test_phash_equivalent(baseline, equivalent, distance):
    kernel = KernelPHash(DummyPlugin())
    assert kernel.equivalent_hash(HASH_BASE, baseline) is equivalent
    assert kernel.equivalent is equivalent
    assert kernel.hamming_distance == distance


def test_phash_equivalent__tolerance():
    hamming_tolerance = 10
    plugin = DummyPlugin(hamming_tolerance=hamming_tolerance)
    kernel = KernelPHash(plugin)
    assert kernel.equivalent_hash(HASH_BASE, HASH_4BIT)
    assert kernel.equivalent is True
    assert kernel.hamming_tolerance == hamming_tolerance
    assert kernel.hamming_distance == 4


@pytest.mark.parametrize(
    "tolerance,equivalent",
    [(10, True), (3, False)],
)
def test_phash_equivalent__marker(tolerance, equivalent):
    marker = DummyMarker(hamming_tolerance=tolerance)
    kernel = KernelPHash(DummyPlugin())
    assert kernel.hamming_tolerance == DEFAULT_HAMMING_TOLERANCE
    assert kernel.equivalent_hash(HASH_BASE, HASH_4BIT, marker=marker) is equivalent
    assert kernel.equivalent is equivalent
    assert kernel.hamming_tolerance == tolerance
    assert kernel.hamming_distance == 4


@pytest.mark.skipif(baseline_unavailable, reason=baseline_missing)
@pytest.mark.parametrize(
    "hash_size,hff,expected",
    [
        (
            DEFAULT_HASH_SIZE,
            DEFAULT_HIGH_FREQUENCY_FACTOR,
            "800bc0555feab05f67ea8d1779fa83537e7ec0d17f9f003517ef200985532856",
        ),
        (
            DEFAULT_HASH_SIZE,
            8,
            "800fc0155fe8b05f67ea8d1779fa83537e7ec0d57f9f003517ef200985532856",
        ),
        (8, DEFAULT_HIGH_FREQUENCY_FACTOR, "80c05fb1778d79c3"),
        (
            DEFAULT_HASH_SIZE,
            16,
            "800bc0155feab05f67ea8d1779fa83537e7ec0d57f9f003517ef200985532856",
        ),
    ],
)
def test_phash_generate_hash(hash_size, hff, expected):
    plugin = DummyPlugin(hash_size=hash_size, high_freq_factor=hff)
    kernel = KernelPHash(plugin)
    fh = open(baseline_image, "rb")
    actual = kernel.generate_hash(fh)
    assert actual == expected


@pytest.mark.parametrize("message", (None, "", "one"))
@pytest.mark.parametrize("equivalent", (None, True))
def test_phash_update_status__none(message, equivalent):
    kernel = KernelPHash(DummyPlugin())
    kernel.equivalent = equivalent
    result = kernel.update_status(message)
    assert isinstance(result, str)
    expected = 0 if message is None else len(message)
    assert len(result) == expected


@pytest.mark.parametrize("message", ("", "one"))
@pytest.mark.parametrize("distance", (10, 20))
@pytest.mark.parametrize("tolerance", (1, 2))
def test_phash_update_status__equivalent(message, distance, tolerance):
    plugin = DummyPlugin(hamming_tolerance=tolerance)
    kernel = KernelPHash(plugin)
    kernel.equivalent = False
    kernel.hamming_distance = distance
    result = kernel.update_status(message)
    assert isinstance(result, str)
    template = "Hash hamming distance of {} bits > hamming tolerance of {} bits."
    status = template.format(distance, tolerance)
    expected = f"{message} {status}" if message else status
    assert result == expected


@pytest.mark.parametrize(
    "summary,distance,tolerance,count",
    [({}, None, DEFAULT_HAMMING_TOLERANCE, 3), (dict(one=1), 2, 3, 4)],
)
def test_phash_update_summary(summary, distance, tolerance, count):
    plugin = DummyPlugin(hamming_tolerance=tolerance)
    kernel = KernelPHash(plugin)
    kernel.hamming_distance = distance
    kernel.update_summary(summary)
    assert summary["kernel"] == KernelPHash.name
    assert summary["hamming_distance"] == distance
    assert summary["hamming_tolerance"] == tolerance
    assert len(summary) == count


#
# KernelSHA256
#


@pytest.mark.parametrize(
    "baseline, equivalent",
    [(HASH_BASE, True), (HASH_2BIT, False), (HASH_4BIT, False)],
)
def test_sha256_equivalent(baseline, equivalent):
    kernel = KernelSHA256(DummyPlugin())
    assert kernel.equivalent_hash(HASH_BASE, baseline) is equivalent


@pytest.mark.skipif(baseline_unavailable, reason=baseline_missing)
def test_sha256_generate_hash():
    kernel = KernelSHA256(DummyPlugin())
    fh = open(baseline_image, "rb")
    actual = kernel.generate_hash(fh)
    expected = "2dc4d32eefa5f5d11c365b10196f2fcdadc8ed604e370d595f9cf304363c13d2"
    assert actual == expected


def test_sha256_update_status():
    kernel = KernelSHA256(DummyPlugin())
    message = sentinel.message
    result = kernel.update_status(message)
    assert result is message


def test_sha256_update_summary():
    kernel = KernelSHA256(DummyPlugin())
    summary = {}
    kernel.update_summary(summary)
    assert len(summary) == 1
    assert "kernel" in summary
    assert summary["kernel"] == KernelSHA256.name
