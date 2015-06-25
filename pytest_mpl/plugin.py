from functools import wraps

import pytest
import os
import shutil
import tempfile

from matplotlib.testing.compare import compare_images


def pytest_addoption(parser):
    parser.addoption('--generate-images-path', help="directory to generate reference images in", action='store')


def pytest_configure(config):
    config.pluginmanager.register(ImageComparison(config))


class ImageComparison(object):

    def __init__(self, config):
        self.config = config

    def pytest_runtest_setup(self, item):

        compare = item.keywords.get('mpl_image_compare')

        if compare is None:
            return
            
        tolerance = compare.kwargs.get('tolerance',10)

        original = item.function

        @wraps(item.function)
        def item_function_wrapper(*args, **kwargs):

            generate_path = self.config.getoption("--generate-images-path")

            # Run test and get figure object
            fig = original(*args, **kwargs)

            # Find test name to use as plot name
            name = original.__name__ + '.png'

            # What we do now depends on whether we are generating the reference
            # images or simply running the test.
            if generate_path is None:

                # Save the figure
                result_dir = tempfile.mkdtemp()
                test_image = os.path.abspath(os.path.join(result_dir, name))

                fig.savefig(test_image)

                # Find path to baseline image
                baseline_image_ref = os.path.abspath(os.path.join(os.path.dirname(item.fspath.strpath), 'baseline', name))

                if not os.path.exists(baseline_image_ref):
                    raise Exception("""Image file not found for comparison test
                                    Generated Image:
                                    \t{test}
                                    This is expected for new tests.""".format(
                                        test=test_image))

                # distutils may put the baseline images in non-accessible places,
                # copy to our tmpdir to be sure to keep them in case of failure
                baseline_image = os.path.abspath(os.path.join(result_dir, 'baseline-'+name))
                shutil.copyfile(baseline_image_ref, baseline_image)

                msg = compare_images(baseline_image, test_image, tol=tolerance)

                if msg is None:
                    shutil.rmtree(result_dir)
                else:
                    raise Exception(msg)

            else:

                if not os.path.exists(generate_path):
                    os.makedirs(generate_path)

                fig.savefig(os.path.abspath(os.path.join(generate_path, name)))
                pytest.skip("Skipping test, since generating data")

        if item.cls is not None:
            setattr(item.cls, item.function.__name__, item_function_wrapper)

        else:
            item.obj = item_function_wrapper
