## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.error
import qitest.conf

import pytest
import mock

from qisys.test.conftest import skip_on_win

test_gtest_one = {
    "name" : "gtest_one",
    "cmd" : ["/path/to/test_one", "--gtest_output", "foo.xml"],
    "timeout" : 2,
}

test_perf_one = {
    "name" : "perf_one",
    "cmd" : ["/path/to/perf_one"],
    "perf" : True
}

def test_can_add_tests(tmpdir):
    qitest_json_path = tmpdir.join("qitest.json").strpath
    qitest.conf.add_test(qitest_json_path, **test_gtest_one)
    qitest.conf.add_test(qitest_json_path, **test_perf_one)
    assert qitest.conf.parse_tests(qitest_json_path) == [test_gtest_one,
                                                         test_perf_one]

def test_errors(tmpdir):
    qitest_json_path = tmpdir.join("qitest.json").strpath
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qitest.conf.add_test(qitest_json_path, name="foo")
    assert "Should provide a test cmd" in e.value.message
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qitest.conf.add_test(qitest_json_path, cmd="foo")
    assert "Should provide a test name" in e.value.message
    qitest.conf.add_test(qitest_json_path, name="foo", cmd=["/path/to/foo"])
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qitest.conf.add_test(qitest_json_path, name="foo", cmd=["/path/to/bar"])
    assert "A test named 'foo' already exists" in e.value.message

@skip_on_win
def test_relocate_posix():
    proj = mock.Mock()
    proj.sdk_directory = "/path/to/sdk"
    tests = [
        {
            "name" : "test_one",
            "cmd" : ["/path/to/sdk/bin/test_one", "/path/to/sdk/share/foo/one.txt"]
        },
        {
            "name" : "test_two",
            "cmd" : ["/path/to/sdk/bin/test_two", "/some/other/path"]
        }
    ]

    qitest.conf.relocate_tests(proj, tests)
    assert tests == [
            {
                "name" : "test_one",
                "cmd" : ["bin/test_one", "share/foo/one.txt"]
            },
            {
                "name" : "test_two",
                "cmd" : ["bin/test_two", "/some/other/path"],
           }
    ]

# pylint: disable-msg=E1101
@pytest.mark.skipif(os.name != "nt", reason="This test is Windows-specific")
def test_relocate_win():
    proj = mock.Mock()
    proj.sdk_directory = r"c:\path\to\sdk"
    tests = [
        {
            "name" : "test_one",
            "cmd" : [r"c:\path\to\sdk\bin\test_one.exe", r"c:\path\to\sdk\share\foo\one.txt"]
        },
        {
            "name" : "test_two",
            "cmd" : [r"c:\path\to\sdk\bin\test_two.exe", r"c:\some\other\path"]
        }
    ]

    qitest.conf.relocate_tests(proj, tests)
    assert tests == [
            {
                "name" : "test_one",
                "cmd" : [r"bin\test_one.exe", r"share\foo\one.txt"]
            },
            {
                "name" : "test_two",
                "cmd" : [r"bin\test_two.exe", r"c:\some\other\path"],
           }
    ]
