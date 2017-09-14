0.9 (unreleased)
----------------

- Changed so that style now doesn't default to 'classic' as some
  packages might want to make sure their packages works well with
  the default style (and it is easier to set a style than unset it).

0.8 (2017-07-19)
----------------

- Fixed use of mpl_image_compare on methods of test classes that also
  use setup_method. [#51]

- Make it possible to specify the directory in which to put the results
  from the tests using --mpl-results-path. [#39]

- Only import Matplotlib if the plugin is actually used. [#47]

- Make sure figures are closed after saving. [#46]

- Allow the backend to be set on a per-test basis. [#38]

- If test name contains slashes (normally from parameters in
  parametrized tests), replace with _. [#50]

0.7 (2016-11-26)
----------------

- Properly define dependencies in setup.py. [#32]

0.6 (2016-11-22)
----------------

- Added ``style`` and ``remove_text`` options. [#20]

- Properly support parametrized tests. [#24]

0.5 (2016-05-06)
----------------

- Minor fixes to detection of remote baseline directories.

- Minor improvements to documentation.

0.4 (2016-05-04)
----------------

- Add support for remote baseline images. [#18]

- When providing two conflicting options, warn instead of raising an
  exception. [#19]

0.3 (2015-06-26)
----------------

- Changed default tolerance from 10 to 2. [#9]

- Added ``tox.ini``.

- Improvements to documentation

0.2 (2015-06-25)
----------------

- Added globally-configurable baseline directory with the
  ``--mpl-baseline-dir`` option. [#8]

- Added ``baseline_dir`` and ``filename`` options in decorator.

- Improvements to documentation

0.1 (2015-06-25)
----------------

- Initial version
