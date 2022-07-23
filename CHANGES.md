## v0.16.1 - 2022-07-23

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Fixes

- Fix tests which exit before returning a figure or use `unittest.TestCase` by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/171

#### Other Changes

- Rename default branch to `main` by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/169

**Full Changelog**: https://github.com/matplotlib/pytest-mpl/compare/v0.16.0...v0.16.1

## v0.16.0 - 2022-06-14

### Fixes

- Make summary log message about test results in general instead of failures by @neutrinoceros in https://github.com/matplotlib/pytest-mpl/pull/148
- Add support for classes with pytest 7 by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/164
- Note that this change necessitated a minor breaking change for figure tests within classes only, and the following will need to be done:
- - Hash library test names will need to be regenerated/updated to include the class name.
- - If the undocumented `mpl-use-full-test-name` ini option is enabled, the the baseline images will need to be regenerated, or have their filename updated to include the class name.

### Other Changes

- Improve parametrized test names in HTML summaries by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/165

### Infrastructure Changes

- Pin tox environment `mpl35` to matplotlib 3.5.1 by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/162
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci in https://github.com/matplotlib/pytest-mpl/pull/167
- Improve `tests/subtests` by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/163

**Full Changelog**: https://github.com/matplotlib/pytest-mpl/compare/v0.15.1...v0.16.0

## v0.15.1 - 2022-04-22

### Fixes

- Add test for image shape mismatch and fix bug by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/145

**Full Changelog**: https://github.com/matplotlib/pytest-mpl/compare/v0.15.0...v0.15.1

## v0.15.0 - 2022-04-21

### Features

- Remove Python 2 from package classifiers by @dopplershift in https://github.com/matplotlib/pytest-mpl/pull/137
- Downloadable hash library in HTML summary by @ConorMacBride in https://github.com/matplotlib/pytest-mpl/pull/138

### Fixes

- No need to warn when falling back to other URL by @pllim in https://github.com/matplotlib/pytest-mpl/pull/139
- Automatically update changelog in the repo after release by @Cadair in https://github.com/matplotlib/pytest-mpl/pull/143

**Full Changelog**: https://github.com/matplotlib/pytest-mpl/compare/v0.14.0...v0.15.0

## 0.14 (2022-02-09)

- Add `--mpl-results-always` flag which disables removing of test images for
- tests which pass. Test images are also stored and generated for hash tests
- when a baseline dir is also provided. [#108]
- 
- When generating a HTML summary page, the `--mpl-results-always` flag is
- automatically applied. [#131]
- 
- Add a `--mpl-generate-summary=json` option which saves a JSON summary of the
- image comparison results. [#127]
- 
- Add a significantly improved HTML summary page, and rename the old simple
- summary page to `basic-html`. [#128]
- 
- Various bugfixes, test improvements and documentation updates [#134]
- 

## 0.13 (2021-07-02)

- Ensure all test files are included in the sdist. [#109]
- 
- Print hash for new figure tests. [#111]
- 
- Do not error if a baseline image can not be retrieved when using figure hashes. [#118]
- 
- Allow generation of hash library and testing against hash library simultaneously. [#121]
- 

## 0.12.1 (2021-07-02)

- Fix specification of required Python version in setup.cfg. [#122]

## 0.12 (2020-11-05)

- Fix passing a https url for baseline images from the CLI. [#89]
- 
- Added `--mpl-baseline-relative` option to specify baseline images relative to the test path. [#96]
- 
- Add option to do comparisons against a json library of sha256 hashes. [#98]
- 
- Drop support for matplotlib 1.5 and Python < 3.6. [#100]
- 
- Add support for generating a HTML summary of test faliures. [#101]
- 
- Add support for falling back to baseline image comparison if hash comparison fails. [#101]
- 

## 0.11 (2019-11-15)

- Improve error message if image shapes don't match. [#79]
- 
- Properly register mpl_image_compare marker with pytest. [#83]
- 
- Drop support for Python 3.5 and earlier, and Matplotlib 1.5. [#87]
- 

## 0.10 (2018-09-25)

- Improve error message when baseline image is not found. [#76]
- 
- Update compatibility with pytest 3.6. [#72]
- 
- Only close figures if they are a valid Matplotlib figure. [#66]
- 
- Improve tests to not assume pytest executable is called py.test. [#65]
- 
- Make sure local matplotlib files are completely ignored. [#64]
- 

## 0.9 (2017-10-12)

- Fix compatibility with Matplotlib 2.1. [#54]
- 
- Allow baseline_dir to be comma-separated URL list to allow mirrors to
- be specified. [#59]
- 
- Make sure figures get closed even if not running with the --mpl
- option, and only close actual Matplotlib Figure objects. [#60]
- 

## 0.8 (2017-07-19)

- Fixed use of mpl_image_compare on methods of test classes that also
- use setup_method. [#51]
- 
- Make it possible to specify the directory in which to put the results
- from the tests using --mpl-results-path. [#39]
- 
- Only import Matplotlib if the plugin is actually used. [#47]
- 
- Make sure figures are closed after saving. [#46]
- 
- Allow the backend to be set on a per-test basis. [#38]
- 
- If test name contains slashes (normally from parameters in
- parametrized tests), replace with _. [#50]
- 

## 0.7 (2016-11-26)

- Properly define dependencies in setup.py. [#32]

## 0.6 (2016-11-22)

- Added `style` and `remove_text` options. [#20]
- 
- Properly support parametrized tests. [#24]
- 

## 0.5 (2016-05-06)

- Minor fixes to detection of remote baseline directories.
- 
- Minor improvements to documentation.
- 

## 0.4 (2016-05-04)

- Add support for remote baseline images. [#18]
- 
- When providing two conflicting options, warn instead of raising an
- exception. [#19]
- 

## 0.3 (2015-06-26)

- Changed default tolerance from 10 to 2. [#9]
- 
- Added `tox.ini`.
- 
- Improvements to documentation
- 

## 0.2 (2015-06-25)

- Added globally-configurable baseline directory with the
- `--mpl-baseline-dir` option. [#8]
- 
- Added `baseline_dir` and `filename` options in decorator.
- 
- Improvements to documentation
- 

## 0.1 (2015-06-25)

- Initial version
