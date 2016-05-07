"""py.test configuration file."""

import subprocess
import shlex
import time
from pathlib import Path

import pytest

# This list holds the names of the test suites that are available for
# functional testing
FUNCTIONAL_SUITES = [
    "apiso",
    "apiso-inspire",
    "atom",
    "cite",
    "csw30",
    "default",
    "dif",
    "ebrim",
    "fgdc",
    "gm03",
    "harvesting",
    "oaipmh",
    "repofilter",
    "sru",
    "utf-8",
]


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "unit: Run only unit tests"
    )
    config.addinivalue_line(
        "markers",
        "integration: Run only integration tests"
    )
    config.addinivalue_line(
        "markers",
        "functional: Run only functional tests"
    )


def pytest_addoption(parser):
    parser.addoption(
        "--gunicorn-settings-file",
        help="An optional file with configuration options for the gunicorn "
             "wsgi server that is used in local integration tests."
    )
    parser.addoption(
        "--gunicorn-log-dir",
        help="An optional path to the directory to use for storing logs of "
             "the gunicorn wsgi server that is used in local integration "
             "tests."
    )
    parser.addoption(
        "--pycsw-config",
        help="An optional file with configuration options for the pycsw "
             "server that is used in local integration tests"
    )
    parser.addoption(
        "--suite",
        action="append",
        choices=FUNCTIONAL_SUITES,
        default=[],
        help="Suites to run local integration tests against. Specify this "
             "parameter multiple times in order to include several suites. "
             "If this parameter is not specified then all available suites "
             "are tested."
    )


def pytest_generate_tests(metafunc):
    current_path = Path(__file__)
    expected_dir = current_path.parent / "functionaltests" / "expected"
    if metafunc.function.__name__ == "test_suites_post":
        test_data, test_ids = _configure_functional_post_tests(metafunc,
                                                               current_path,
                                                               expected_dir)
        metafunc.parametrize(["test_request", "expected_result"],
                             test_data, ids=test_ids)
    elif metafunc.function.__name__ == "test_suites_get":
        test_data, test_ids = _configure_functional_get_tests(metafunc,
                                                              current_path,
                                                              expected_dir)
        metafunc.parametrize(["test_request_parameters", "expected_result"],
                             test_data, ids=test_ids)


@pytest.fixture(scope="session")
def test_local_server(request):
    """A local pycsw instance running with gunicorn.

    This local server:

    * uses gunicorn config file from the pytest command-line options
    * uses pycsw config file from the pytest command-line options
    * stores logs in the file specified at the pytest command-line options

    """

    gunicorn_config = request.config.getoption("--gunicorn-settings-file")
    config = ("-c {} ".format(gunicorn_config)
              if gunicorn_config is not None else "")
    command_line = ("gunicorn {}-w2 -b 0.0.0.0:8000 pycsw.wsgi:"
                    "application".format(config))
    args = shlex.split(command_line)
    env = {
        "PYCSW_CONFIG": request.config.getoption("--pycsw-config"),
    }
    # FIXME - get the working directory for gunicorn
    gunicorn_main_process = subprocess.Popen(args)
    time.sleep(2)  # give gunicorn some time to start up

    def finalizer():
        gunicorn_main_process.terminate()  # .kill() stops it quickly
        gunicorn_main_process.wait()  # wait for gunicorn to stop completely

    request.addfinalizer(finalizer)
    return "http://localhost:8000"



def _configure_functional_post_tests(metafunc, current_path, expected_dir):
    test_data = []
    test_ids = []
    for suite in metafunc.config.getoption("suite") or FUNCTIONAL_SUITES:
        requests_dir = (current_path.parent / "functionaltests" / "suites" /
                        suite / "post")
        try:
            for request in requests_dir.iterdir():
                expected = (expected_dir / "suites_{}_post_{}".format(
                    suite, request.name))
                if request.is_file() and expected.is_file():
                    test_data.append((str(request), str(expected)))
                    test_name = "{}_{}".format(
                        suite, request.name.replace(request.suffix, ""))
                    test_ids.append(test_name)
        except FileNotFoundError:
            continue
    return test_data, test_ids


def _configure_functional_get_tests(metafunc, current_path, expected_dir):
    test_data = []
    test_ids = []
    for suite in metafunc.config.getoption("suite") or FUNCTIONAL_SUITES:
        requests_file = (current_path.parent / "functioanltests" / "suites" /
                         suite / "get" / "requests.txt")
        try:
            with open(str(requests_file), encoding="utf-8") as fh:
                for line in fh:
                    test_name, sep, test_params = line.partition(",")
                    expected = (
                        expected_dir / "suites_{}_get_{}.xml".format(
                            suite, test_name)
                    )
                    test_data.append((test_params, str(expected)))
                    test_ids.append("{}_{}".format(suite, test_name))
        except FileNotFoundError:
            continue
    return test_data, test_ids
