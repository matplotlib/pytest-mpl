This is a plugin to facilitate image comparison for
`Matplotlib <http://www.matplotlib.org>`__ figures in pytest.

For each figure to test, the reference image is subtracted from the
generated image, and the RMS of the residual is compared to a
user-specified tolerance. If the residual is too large, the test will
fail (this is implemented using helper functions from
``matplotlib.testing``).
