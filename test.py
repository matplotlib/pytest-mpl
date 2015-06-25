from decorator import decorator

import os
import shutil
import inspect
import tempfile
import matplotlib.pyplot as plt
from matplotlib.testing.compare import compare_images


# Note: Baseline images are stored in a 'baseline' directory relative to the
# test file

def image_comparison(func):

    def wrapper(func, *args, **kwargs):

        generate = None

        # Run test and get figure object
        fig = func(*args, **kwargs)

        # Find test name to use as plot name
        name = func.__name__ + '.png'

        # What we do now depends on whether we are generating the reference
        # images or simply running the test.
        if generate is None:

            # Save the figure
            result_dir = tempfile.mkdtemp()
            test_image = os.path.abspath(os.path.join(result_dir, name))

            fig.savefig(test_image)

            # Find path to baseline image
            baseline_image_ref = os.path.join(os.path.dirname(__file__), 'baseline', name)

            if not os.path.exists(baseline_image_ref):
                raise Exception("""Image file not found for comparision test
                                Generated Image:
                                \t{test}
                                This is expected for new tests.""".format(
                                    test=test_image))

            # distutils may put the baseline images in non-accessible places,
            # copy to our tmpdir to be sure to keep them in case of failure
            baseline_image = os.path.abspath(os.path.join(result_dir, 'baseline-'+name))
            shutil.copyfile(baseline_image_ref, baseline_image)

            msg = compare_images(baseline_image, test_image, tol=10)

            if msg is None:
                shutil.rmtree(result_dir)
            else:
                raise Exception(msg)

        else:

            fig.savefig(os.path.abspath(os.path.join(generate, name)))
            pytest.skip("Skipping test, since generating data")

    return decorator(wrapper, func)


@image_comparison
def test_figure():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
    return fig
