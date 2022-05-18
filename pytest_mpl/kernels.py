"""
This module contains the supported hashing kernel implementations.

"""
import hashlib
from abc import ABC, abstractmethod

import imagehash
from PIL import Image

#: The default hamming distance bit tolerance for "similar" imagehash hashes.
DEFAULT_HAMMING_TOLERANCE = 2

#: The default imagehash hash size (N), resulting in a hash of N**2 bits.
DEFAULT_HASH_SIZE = 16

#: Level of image detail (high) or structure (low) represented by phash .
DEFAULT_HIGH_FREQUENCY_FACTOR = 4

#: Registered kernel names.
KERNEL_SHA256 = "sha256"
KERNEL_PHASH = "phash"

__all__ = [
    "DEFAULT_HAMMING_TOLERANCE",
    "DEFAULT_HASH_SIZE",
    "DEFAULT_HIGH_FREQUENCY_FACTOR",
    "KERNEL_PHASH",
    "KERNEL_SHA256",
    "KernelPHash",
    "KernelSHA256",
    "kernel_factory",
]


class Kernel(ABC):
    """
    Kernel abstract base class (ABC) which defines a simple common kernel API.

    """

    def __init__(self, plugin):
        # Containment of the plugin allows the kernel to cherry-pick required state
        self._plugin = plugin

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

    def update_status(self, message):
        """
        Append the kernel status message to the provided message.

        Parameters
        ----------
        message : str
            The existing status message.

        Returns
        -------
        str
            The updated status message.

        """
        return message

    def update_summary(self, summary):
        """
        Refresh the image comparison summary with relevant kernel entries.

        Parameters
        ----------
        summary : dict
            Image comparison test report summary.

        Returns
        -------
        dict
            The updated image comparison summary.

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
        # keep state of equivalence result
        self.equivalent = None
        # keep state of hash hamming distance (whole number) result
        self.hamming_distance = None
        # value may be overridden by py.test marker kwarg
        self.hamming_tolerance = (
            self._plugin.hamming_tolerance or DEFAULT_HAMMING_TOLERANCE
        )
        # the hash-size (N) defines the resultant N**2 bits hash size
        self.hash_size = self._plugin.hash_size
        # the level of image detail or structure represented by perceptual hash
        self.high_freq_factor = (
            self._plugin.high_freq_factor or DEFAULT_HIGH_FREQUENCY_FACTOR
        )
        # py.test marker kwarg
        self.option = "hamming_tolerance"

    def equivalent_hash(self, actual, expected, marker=None):
        if marker:
            self.hamming_tolerance = int(marker.kwargs.get(self.option))
        actual = imagehash.hex_to_hash(actual)
        expected = imagehash.hex_to_hash(expected)
        self.hamming_distance = actual - expected
        self.equivalent = self.hamming_distance <= self.hamming_tolerance
        return self.equivalent

    def generate_hash(self, buffer):
        buffer.seek(0)
        data = Image.open(buffer)
        phash = imagehash.phash(
            data, hash_size=self.hash_size, highfreq_factor=self.high_freq_factor
        )
        return str(phash)

    def update_status(self, message):
        result = str() if message is None else str(message)
        if self.equivalent is False:
            msg = (
                f"Hash hamming distance of {self.hamming_distance} bits > "
                f"hamming tolerance of {self.hamming_tolerance} bits."
            )
            result = f"{message} {msg}" if len(result) else msg
        return result

    def update_summary(self, summary):
        summary["hamming_distance"] = self.hamming_distance
        summary["hamming_tolerance"] = self.hamming_tolerance
        return summary


class KernelSHA256(Kernel):
    """
    A simple kernel that calculates a 256-bit SHA hash of an image.

    """

    name = KERNEL_SHA256

    def equivalent_hash(self, actual, expected, marker=None):
        return actual == expected

    def generate_hash(self, buffer):
        buffer.seek(0)
        data = buffer.read()
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()


#: Registry of available hashing kernel factories.
kernel_factory = {
    KernelPHash.name: KernelPHash,
    KernelSHA256.name: KernelSHA256,
}
