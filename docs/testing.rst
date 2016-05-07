.. _testing:

Testing
=======

The pycsw tests framework (in ``tests``) is a collection of testsuites to
perform automated regression testing of the codebase.  Test are run against
all pushes to the GitHub repository via `Travis CI`_.


.. _ogc-cite:

OGC CITE
--------

Compliance benchmarking is done via the OGC `Compliance & Interoperability
Testing & Evaluation Initiative`_.  The pycsw
`wiki <https://github.com/geopython/pycsw/wiki/OGC-CITE-Compliance>`_
documents testing procedures and status.


Running Locally
^^^^^^^^^^^^^^^

The pycsw testing suites use `pytest`_. Tests are executed using the
standard `py.test` tool:

.. code:: bash

   cd /path/to/pycsw/tests
   py.test  # you can add several optional arguments here

Tests are tagged with the following marks:

* unit - Unit tests. These are small and focused on testing isolated
  functionality;

  .. code:: bash

     py.test -m unit

* integration - Integration tests. They combine pieces of code and test
  them together;

  .. code:: bash

     py.test -m integration

* functional - Functional tests. These perform requests as an outside client
  would and therefore test the whole pycsw codebase. These are used in
  verifying that pycsw conforms to the requirements of several standards.

  .. code:: bash

     py.test -m functional

There are lots of options that can be passed to pytest in order to configure
the testing process. For example, in order to run just the unit tests with
full output logs and create an html page showing results:

.. code:: bash

   py.test -m unit --capture=no --verbose --html=report.html


Configuration of tests
^^^^^^^^^^^^^^^^^^^^^^

Unit and integration tests do not require any configuration. Functional tests
can be configured by providing command line options to the `py.test` tool



The tests perform HTTP GET and POST requests against
``http://localhost:8000``.  The expected output for each test can be found
in ``expected``.  Results are categorized as ``passed``, ``failed``, or
``initialized``.  A summary of results is output at the end of the run.

Failed Tests
^^^^^^^^^^^^

If a given test has failed, the output is saved in ``results``.  The
resulting failure can be analyzed by running
``diff tests/expected/name_of_test.xml tests/results/name_of_test.xml`` to
find variances.  The Paver task returns a status code which indicates the
number of tests which have failed (i.e. ``echo $?``).

Test Suites
^^^^^^^^^^^

The tests framework is run against a series of 'suites' (in ``tests/suites``),
each of which specifies a given configuration to test various functionality
of the codebase.  Each suite is structured as follows:

* ``tests/suites/suite/default.cfg``: the configuration for the suite
* ``tests/suites/suite/post``: directory of XML documents for HTTP POST requests
* ``tests/suites/suite/get/requests.txt``: directory and text file of KVP for HTTP GET requests
* ``tests/suites/suite/data``: directory of sample XML data required for the test suite.  Database and test data are setup/loaded automatically as part of testing

When the tests are invoked, the following operations are run:

* pycsw configuration is set to ``tests/suites/suite/default.cfg``
* HTTP POST requests are run against ``tests/suites/suite/post/*.xml``
* HTTP GET requests are run against each request in ``tests/suites/suite/get/requests.txt``

The CSV format of ``tests/suites/suite/get/requests.txt`` is
``testname,request``, with one line for each test.  The ``testname`` value is a unique test name (this value sets the name of the output file in the test results).  The ``request`` value is the HTTP GET request.  The ``PYCSW_SERVER`` token is replaced at runtime with the URL to the pycsw install.

Adding New Tests
^^^^^^^^^^^^^^^^

To add tests to an existing suite:

* for HTTP POST tests, add XML documents to ``tests/suites/suite/post``
* for HTTP GET tests, add tests (one per line) to ``tests/suites/suite/get/requests.txt``
* run ``paver test``

To add a new test suite:

* create a new directory under ``tests/suites`` (e.g. ``foo``)
* create a new configuration in ``tests/suites/foo/default.cfg``

  * Ensure that all file paths are relative to ``path/to/pycsw``
  * Ensure that ``repository.database`` points to an SQLite3 database called ``tests/suites/foo/data/records.db``.  The database *must* be called ``records.db`` and the directory ``tests/suites/foo/data`` *must* exist

* populate HTTP POST requests in ``tests/suites/foo/post``
* populate HTTP GET requests in ``tests/suites/foo/get/requests.txt``
* if the testsuite requires test data, create ``tests/suites/foo/data`` are store XML file there
* run ``paver test`` (or ``paver test -s foo`` to test only the new test suite)

The new test suite database will be created automatically and used as part of tests.

Web Testing
^^^^^^^^^^^

You can also use the pycsw tests via your web browser to perform sample requests against your pycsw install.  The tests are is located in ``tests/``.  To generate the HTML page:

.. code-block:: bash

  $ paver gen_tests_html

Then navigate to ``http://host/path/to/pycsw/tests/index.html``.

.. _Compliance & Interoperability Testing & Evaluation Initiative: http://cite.opengeospatial.org/
.. _Travis CI: http://travis-ci.org/geopython/pycsw
.. _Paver: http://paver.github.io/paver/
.. _pytest: http://pytest.org/latest/
