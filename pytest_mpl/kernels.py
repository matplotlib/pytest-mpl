"""
This module contains the supported hashing kernel implementations.

"""
from PIL import Image
from abc import ABC, abstractmethod
import hashlib
import imagehash


KERNEL_SHA256 = "sha256"
KERNEL_PHASH = "phash"

__all__ = [
    "KERNEL_PHASH",
    "KERNEL_SHA256",
    "KernelPHash",
    "KernelSHA256",
    "kernel_factory",
]


class Kernel(ABC):
    """
    Kernel abstract base class (ABC) which defines a common kernel API.

    """

    def __init__(self, plugin):
        self._plugin = plugin

    @abstractmethod
    def generate_hash(self, buffer):
        """
        Computes the hash of the image from the in-memory/open byte stream
        buffer.

        Parameters
        ----------
        buffer : stream
            The in-memory/open byte stream of the image.

        Returns
        -------
        str
            The string representation (hexdigest) of the image hash.

        """

    @abstractmethod
    def equivalent_hash(self, actual, expected, marker=None):
        """
        Determine whether the kernel considers the provided actual and
        expected hashes as similar.

        Parameters
        ----------
        actual : str
            The hash of the test image.
        expected : str
            The hash of the baseline image.
        marker : pytest.Mark
            The test marker, which may contain kwarg options to be
            applied to the equivalence test.

        Returns
        -------
        bool
            Whether the actual and expected hashes are deemed similar.

        """

    def update_summary(self, summary):
        """
        Refresh the image comparison summary with relevant kernel entries.

        Parameters
        ----------
        summary : dict

        Returns
        -------
        dict
            The image comparison summary.

        """
        return summary


class KernelPHash(Kernel):
    """
    Kernel that calculates a perceptual hash of an image for the
    specified hash size (N).

    Where the resultant perceptual hash will be composed of N**2 bits.

    """

    name = KERNEL_PHASH

    def __init__(self, plugin):
        super().__init__(plugin)
        self.hash_size = self._plugin.hash_size
        # py.test marker kwarg
        self.option = "hamming_tolerance"
        # value may be overridden by py.test marker kwarg
        self.hamming_tolerance = self._plugin.hamming_tolerance
        # keep state of hash hamming distance (whole number) result
        self.hamming_distance = None

    def generate_hash(self, buffer):
        buffer.seek(0)
        data = Image.open(buffer)
        phash = imagehash.phash(data, hash_size=self.hash_size)
        return str(phash)

    def equivalent_hash(self, actual, expected, marker=None):
        if marker:
            self.hamming_tolerance = int(marker.kwargs.get(self.option))
        actual = imagehash.hex_to_hash(actual)
        expected = imagehash.hex_to_hash(expected)
        self.hamming_distance = actual - expected
        return self.hamming_distance <= self.hamming_tolerance

    def update_summary(self, summary):
        summary["hamming_distance"] = self.hamming_distance
        summary["hamming_tolerance"] = self.hamming_tolerance
        return summary


class KernelSHA256(Kernel):
    """
    A simple kernel that calculates a 256-bit SHA hash of an image.

    """

    name = KERNEL_SHA256

    def generate_hash(self, buffer):
        buffer.seek(0)
        data = buffer.read()
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

    def equivalent_hash(self, actual, expected, marker=None):
        return actual == expected


#: Registry of available hashing kernel factories.
kernel_factory = {
    KernelPHash.name: KernelPHash,
    KernelSHA256.name: KernelSHA256,
}
