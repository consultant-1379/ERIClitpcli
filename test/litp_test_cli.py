import unittest

import urllib2
import httplib
from StringIO import StringIO
import socket
import json
import sys
import argparse
from ConfigParser import SafeConfigParser, NoOptionError

from litpcli import litp
from litpcli.litp import TypeAction, asciitxt
import sample_json_output
import sample_help_output
from mock import Mock, patch

def mock_response(full_url, resp_str, raiseError=False):
    resp = urllib2.addinfourl(StringIO(resp_str), "empty header",
                              full_url)
    resp.code = 200
    resp.msg = "OK"
    if raiseError:
        raise urllib2.HTTPError(full_url, 500, resp_str, "empty_header",
                                StringIO(resp_str))
    return resp


def mock_get_auth_headers(conn_type=litp.UNIX):
    if conn_type == litp.UNIX:
        return {"Authorization": "Basic {0}".format("unix")}
    else:
        return {"Authorization": "Basic {0}".format("auth")}


def mock_format_func(data, recursive=False):
    return json.dumps(data)


class MockHTTPHandler(urllib2.HTTPHandler):
    def __init__(self, response=None):
        urllib2.HTTPHandler.__init__(self)
        self._debuglevel = 1
        self.response = response
        self.raiseError = False

    def open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.fullurl = fullurl
        self.data = data
        if self.raiseError:
            return mock_response(fullurl, self.response, True)
        return mock_response(fullurl, self.response, False)

    def get_full_url(self):
        return self.fullurl

    def read(self):
        return self.response

class MockHTTPRequest():
    def __init__(self, method, url, data, headers):
        self.method = method
        self.url = url
        self.data = data
        self.headers = headers

class MockHTTPResponse():
    def __init__(self, data, status, reason):
        self.data = data
        self.status = status
        self.reason = reason

    def read(self):
        return self.data


class MockHTTPSConnection(httplib.HTTPSConnection):

    def __init__(self, uri, context=None):
        self.expected_responses = []

    def set_expected_response(self, data, status=200, reason='OK'):
        self.data = data
        self.status = status
        self.reason = reason

    def add_to_expected_responses(self, data, status=200, reason='OK'):
        self.expected_responses.insert(
            0, MockHTTPResponse(data, status, reason))

    def getresponse(self):
        if len(self.expected_responses) == 0:
            return MockHTTPResponse(self.data, self.status, self.reason)
        else:
            return self.expected_responses.pop()

    def request(self, method, url, data, headers):
        self.request_received = MockHTTPRequest(method, url, data, headers)


class MockArgumentParser(object):
    def __init__(self, attrs=None):
        if attrs:
            [setattr(self, k, v) for k, v in attrs.items()]


class LitpCLITests(unittest.TestCase):

    def setUp(self):
        self.mock_https_connection = MockHTTPSConnection("http://localhost:9999")
        httplib.HTTPSConnection = MockHTTPSConnection
        litp.getpass.getpass = lambda: "Brick"
        litp.os.getlogin = lambda: "Tamland"

        self.old_stdout = sys.stdout
        sys.stdout = self.stdout = StringIO()

        self.old_stderr = sys.stderr
        sys.stderr = self.stderr = StringIO()
        self.old_argparse_exit = argparse.ArgumentParser.exit

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        argparse.ArgumentParser.exit = self.old_argparse_exit

    def test_valid_path(self):
        self.assertTrue(litp.valid_path("/"))
        try:
            litp.valid_path("*/*")
        except argparse.ArgumentTypeError:
            pass

    def test_type_action_parser_error(self):
        class MockParser(object):
            def error(self, err_str):
                self.err_str = err_str

        class MockNamespace(object):
            pass

        mock_parser = MockParser()
        mock_namespace = MockNamespace()
        mock_namespace.type = "bogus"
        t = TypeAction(None, None)
        t(mock_parser, mock_namespace, None)
        self.assertEqual("Type may only be specified once",
                         mock_parser.err_str)

    def test_ascii_text(self):
        input_string = 'valid'
        self.assertEqual(input_string, asciitxt(input_string))
        invalid_string = '\xe2'
        self.assertRaises(argparse.ArgumentTypeError, asciitxt, invalid_string)

    def test_run_command_bad_ascii_text(self):
        invalid_string = '\xe2'
        cli = litp.LitpCli()
        self.assertEqual(1, cli.wrapped_run_command(invalid_string))
        self.assertEqual('LITP CLI arguments must be of type ascii.\n',
                         self.stderr.getvalue())

    def test_choose_connection_type(self):
        with patch('os.path.exists') as exists:
            exists.return_value = False
            cli = litp.LitpCli()
            socket_file, conn_type = cli._choose_connection(litp.UNIX_SOCKET)
            self.assertEqual(conn_type, litp.HTTPS)
            self.assertEqual(socket_file, None)
            exists.return_value = True
            with patch('os.stat') as stat:
                # not important, just intercept system's
                stat.return_value = Mock(st_mode=0)
                with patch('stat.S_ISSOCK') as issock:
                    issock.return_value = False
                    cli = litp.LitpCli()
                    socket_file, conn_type = cli._choose_connection(litp.UNIX_SOCKET)
                    self.assertEqual(conn_type, litp.HTTPS)
                    self.assertEqual(socket_file, None)
                    issock.return_value = True
                    cli = litp.LitpCli()
                    socket_file, conn_type = cli._choose_connection(litp.UNIX_SOCKET)
                    self.assertEqual(conn_type, litp.UNIX)
                    self.assertEqual(socket_file, litp.UNIX_SOCKET)

    def test_type_action_parser_error_2(self):
        class MockParser(object):
            def error(self, err_str):
                self.err_str = err_str

        class MockNamespace(object):
            pass
        mock_parser = MockParser()
        mock_namespace = MockNamespace()
        mock_namespace.type = "bogus"
        t = TypeAction(None, None)
        t(mock_parser, mock_namespace, None)
        self.assertEqual("Type may only be specified once",
                         mock_parser.err_str)

    def test_ascii_text_2(self):
        input_string = 'valid'
        self.assertEqual(input_string, asciitxt(input_string))
        invalid_string = '\xe2'
        self.assertRaises(argparse.ArgumentTypeError, asciitxt, invalid_string)

    def test_run_command_bad_ascii_text_2(self):
        invalid_string = '\xe2'
        cli = litp.LitpCli()
        self.assertEqual(1, cli.wrapped_run_command(invalid_string))
        self.assertEqual('LITP CLI arguments must be of type ascii.\n',
                         self.stderr.getvalue())

    def test_show_item(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/software"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        expected_string = (
            "/software\n    type: software\n    state: Initial\n    "
            "children:\n        /items\n        /deployables\n        "
            "/profiles\n        /runtimes\n")

        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_show_property_on_item(self):
        data = sample_json_output.ms_ipaddresses_second_output

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p",
                    "/ms/ipaddresses/ip1", "-o", "network_name"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("nodes\n", self.stdout.getvalue())

    def test_show_property_which_does_not_exist_on_item(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/software",
                    "-o", "property"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        expected_string = ('/software\n''    InvalidPropertyError    '
                           'Property "property" is not set\n')

        self.assertEqual(expected_string, self.stderr.getvalue())

    def test_show_trailing_slash(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/software/"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        expected_string = (
            "/software\n    type: software\n    state: Initial\n    "
            "children:\n        /items\n        /deployables\n        "
            "/profiles\n        /runtimes\n")

        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_recursive_show(self):
        first_data = sample_json_output.ms_ipaddresses_first_output
        second_data = sample_json_output.ms_ipaddresses_second_output

        sys.argv = ["-u", "foo", "-P", "bar", "show",
                    "-p", "/ms/ipaddresses", "-rl"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            cli._get_auth_headers = mock_get_auth_headers
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(first_data))
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(second_data))
            cli.run_command(sys.argv)

        expected_string = ("/ms/ipaddresses\n/ms/ipaddresses/ip1\n")

        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_recursive_show_with_depth_limit(self):
        first_data = sample_json_output.ms_ipaddresses_first_output
        second_data = sample_json_output.ms_ipaddresses_second_output

        sys.argv = ["-u", "foo", "-P", "bar", "show",
                    "-p", "/ms/ipaddresses", "-rl", "-n", "1"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            cli._get_auth_headers = mock_get_auth_headers
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(first_data))
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(second_data))
            cli.run_command(sys.argv)

        expected_string = ("/ms/ipaddresses\n/ms/ipaddresses/ip1\n")

        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_recursive_show_with_http_error(self):
        first_data = sample_json_output.ms_ipaddresses_first_output
        second_data = sample_json_output.invalid_location_output

        sys.argv = ["-u", "foo", "-P", "bar", "show",
                    "-p", "/ms/ipaddresses", "-rl"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(first_data))
            self.mock_https_connection.add_to_expected_responses(
                json.dumps(second_data),
                404, "Not found")
            cli._get_auth_headers = mock_get_auth_headers
            cli.run_command(sys.argv)

        expected_string = \
            ('\n/invalid\n    InvalidLocationError    Item not found\n')

        self.assertEqual(expected_string, self.stderr.getvalue())

    def test_create(self):
        data = sample_json_output.create_response

        sys.argv = ["-u", "foo", "-P", "bar", "create", "-p",
                    "/software/profiles/rhel_6_2",
                    "-t",
                    "os-profile",
                    "-o",
                    "name='sample-profile'",
                    "version='6.2'",
                    "path='/profiles/node-iso/'",
                    "arch='x86_64'",
                    "breed='redhat'"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_import(self):
        data = sample_json_output.create_response

        sys.argv = ["-u", "foo", "-P", "bar", "import", "blah",
                    "litp"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_import_fails(self):
        data = sample_json_output.create_response

        sys.argv = ["-u", "foo", "-P", "bar", "import", "blah", "nach"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        self.assertEqual('', self.stderr.getvalue())

    def test_snapshot_with_path(self):
        data = sample_json_output.create_response

        sys.argv = ["-u", "foo", "-P", "bar", "create_snapshot", '-p', '/blah']

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data),
                                                             status=201)
        try:
            cli.run_command(sys.argv)
        except SystemExit:
            # expected: -p isn't supported
            pass
        else:
            self.fail('Should have failed with SystemExit')

        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_prepare_restore(self):
        data = sample_json_output.create_response

        sys.argv = ["-u", "foo", "-P", "bar", "prepare_restore"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_prepare_restore_with_path(self):
        data = sample_json_output.prepare_restore_output

        sys.argv = ["-u", "foo", "-P", "bar", "prepare_restore", "-p", "/"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_prepare_restore_without_path(self):
        data = sample_help_output.litp_prepare_restore_missing_path
        sys.argv = ["-u", "foo", "-P", "bar", "prepare_restore", "-p"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection

        try:
            cli.run_command(sys.argv)
        except SystemExit:
            # expected: -p must have an associated path value
            pass
        else:
            self.fail('Should have failed with SystemExit')

        self.assertEqual(data, self.stderr.getvalue())
        self.assertEqual("", self.stdout.getvalue())

    def test_prepare_restore_with_two_paths(self):
        data = sample_help_output.litp_prepare_restore_one_path
        sys.argv = ["-u", "foo", "-P", "bar", "prepare_restore", "-p", "/node1", "-p", "/node2"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection

        try:
            cli.run_command(sys.argv)
        except SystemExit:
            # expected: -p must be specified once
            pass
        else:
            self.fail('Should have failed with SystemExit')

        self.assertEqual(data, self.stderr.getvalue())
        self.assertEqual("", self.stdout.getvalue())

    def test_prepare_restore_with_invalid_path(self):
        data = sample_json_output.prepare_restore_validation_error_output

        path = '/invalid_path'
        sys.argv = ["-u", "foo", "-P", "bar", "prepare_restore",
                    "-p", "%s" % path]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)
        expected_output = u'ValidationError in property: "path"    Invalid value \'%s\'.' % path
        self.assertEqual(expected_output, self.stdout.getvalue().strip())

    def test_prepare_restore_with_force_remove_snapshot(self):
        data = sample_json_output.prepare_restore_output

        for sys.argv in [["-u", "foo", "-P", "bar", "prepare_restore", "--force-remove-snapshot"],
                         ["-u", "foo", "-P", "bar", "prepare_restore", "-f"]]:
            cli = litp.LitpCli()
            with patch.object(cli, '_get_connection') as _get_connection:
                _get_connection.return_value = self.mock_https_connection
                self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
                cli.run_command(sys.argv)
            expected_output = ""
            self.assertEqual(expected_output, self.stdout.getvalue())

    def test_create_fails(self):
        """
        Test that we fail to create an item at a path that does not exist
        """
        data = sample_json_output.create_fail_response
        sys.argv = ["-u", "foo", "-P", "bar", "create", "-p",
                    "/software/badbranch/profile",
                    "-t",
                    "os-profile",
                    "-o",
                    "name='sample-profile'",
                    "version='6.2'",
                    "path='/profiles/node-iso/'",
                    "arch='x86_64'",
                    "breed='bad'"]
        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=404)
            cli.run_command(sys.argv)
        expected_output = ("/software/badbranch/profile\n"
                           "    InvalidLocationError    Path not found\n")
        self.assertEqual(expected_output, self.stderr.getvalue())

    @patch('litpcli.litp.LitpCli._create_https_connection')
    def test_create_with_url(self, patched_create):
        data = sample_json_output.create_response_from_alt_url
        sys.argv = ["-u", "foo", "-P", "bar",
                    "--url", "https://alt_ms1:9999/litp/rest/v1",
                    "create", "-p",
                    "/software/profiles/rhel_6_2",
                    "-t",
                    "os-profile",
                    "-o",
                    "name='sample-profile'",
                    "version='6.2'",
                    "path='/profiles/node-iso/'",
                    "arch='x86_64'",
                    "breed='redhat'"]

        cli = litp.LitpCli()

        def patch_set_expected_response(host):
            connection = MockHTTPSConnection(host)
            connection.data = json.dumps(data)
            connection.status = 201
            connection.reason = 'OK'
            return connection

        patched_create.side_effect = patch_set_expected_response

        cli.run_command(sys.argv)

        expected_output = ""
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_inherit(self):
        data = sample_json_output.inherit_output
        sys.argv = ["-u", "foo", "-P", "bar", "inherit", "-p",
                    "/deployments/single_blade/nodes/node1/system",
                    "-s",
                    "/infrastructure/system_providers/libvirt1/systems/vm1"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
            cli.run_command(sys.argv)

        expected_string = ""
        self.assertEqual(expected_string, self.stderr.getvalue())

    def test_show_inherited_item_with_no_properties(self):
        data = sample_json_output.show_inherited_output_no_properties

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p",
                    "/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        expected_output = ('/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root\n'
                           '    inherited from: /infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root\n'
                           '    type: reference-to-file-system\n'
                           '    state: Initial\n')
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_show_inherited_item_with_overwritten_properties(self):
        data = sample_json_output.show_inherited_output

        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p",
                    "/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        expected_output = ('/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root\n'
                           '    inherited from: /infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root\n'
                           '    type: reference-to-file-system\n'
                           '    state: Initial\n'
                           '    properties (inherited properties are marked with asterisk):\n'
                           '        mount_point: / [*]\n'
                           '        type: ext4 [*]\n'
                           '        size: 48G\n')
        self.assertEqual(expected_output, self.stdout.getvalue())

    def test_update(self):
        data = sample_json_output.update_output
        sys.argv = ["-u", "foo", "-P", "bar", "update", "-p",
                    "/deployments/single_blade/clusters/cluster1"
                    "/nodes/node1/ipaddresses/ip1",
                    "-o",
                    "network_name='test_network'",
                    "address='10.10.10.10"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data),
                                                            status=201)
        cli.run_command(sys.argv)
        expected_string = ""
        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_update_delete(self):
        data = sample_json_output.update_output
        sys.argv = ["-u", "foo", "-P", "bar", "update", "-p",
                    "/deployments/single_blade/clusters/cluster1"
                    "/nodes/node1/ipaddresses/ip1",
                    "-d network_name,address"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data),
                                                             status=201)
            cli.run_command(sys.argv)
        req = cli.conn.request_received
        expected_string = ""
        data = json.loads(req.data)
        self.assertEqual(expected_string, self.stdout.getvalue())

    def test_update_delete_same_option(self):
        data = sample_json_output.update_output
        sys.argv = ["-u", "foo", "-P", "bar", "update", "-p",
                    "/deployments/single_blade/clusters/cluster1"
                    "/nodes/node1/ipaddresses/ip1",
                    "-o","network_name=test",
                    "-d","network_name,address"]
        self._catch_sys_exit()
        try:
            cli = litp.LitpCli()
            with patch.object(cli, '_get_connection') as _get_connection:
                _get_connection.return_value = self.mock_https_connection
                self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
                cli.wrapped_run_command(sys.argv)
        except Exception as e:
            pass

        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected_string = ('litp update: error: Updating and deleting '
                           '"network_name" in the same operation')
        self.assertTrue(expected_string in result)

    def test_update_delete_same_option_reorder(self):
        data = sample_json_output.update_output
        argv = ["-u", "foo", "-P", "bar", "update", "-p",
                    "/deployments/single_blade/clusters/cluster1"
                    "/nodes/node1/ipaddresses/ip1",
                    "-d","network_name,address",
                    "-o","network_name=test",]
        self._catch_sys_exit()
        try:
            cli = litp.LitpCli()
            with patch.object(cli, '_get_connection') as _get_connection:
                _get_connection.return_value = self.mock_https_connection
                self.mock_https_connection.set_expected_response(json.dumps(data), status=201)
                cli.wrapped_run_command(argv)
        except Exception as e:
            pass

        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected_string = ('litp update: error: Updating and deleting '
                           '"network_name" in the same operation')
        self.old_stderr.write(str(result))
        self.assertTrue(expected_string in result)

    def _catch_sys_exit(self):
        exit_status = 0
        exit_message = ''
        stderr = self.stderr

        def exit(self, status=0, message=None):
            exit_status = status
            exit_message = message
            stderr.seek(0, 2)
            stderr.write(message)
        self.exit = argparse.ArgumentParser.exit
        argparse.ArgumentParser.exit = exit

    def test_bad_command(self):
        sys.argv = ["-u", "foo", "-P", "bar", "badcommand", "-p",
                    "/software/profiles/rhel_6_2"]
        self._catch_sys_exit()
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except Exception as e:
            pass
        result = self.stderr.getvalue().splitlines()[0]
        argparse.ArgumentParser.exit = self.exit
        self.assertEqual("Usage: litp [-h] [-u USERNAME] [-P PASSWORD]  ...",
                         result)

    def test_bad_option(self):
        sys.argv = ["-u", "foo", "-P", "bar", "show", "--X", "-p"
                    "/software/profiles/rhel_6_2"]
        self._catch_sys_exit()
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except Exception as e:
            pass
        result = self.stderr.getvalue().splitlines()[0]
        argparse.ArgumentParser.exit = self.exit
        self.assertEqual("Usage: litp [-h] [-u USERNAME] [-P PASSWORD]  ...",
                         result)

    def test_invalid_path(self):
        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p",
                    "/software*"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass
        result = self.stderr.getvalue().splitlines()[-1]
        self.assertEqual(("litp show: error: argument -p/--path: /software*"
                          " is not a valid path argument"), result)

    def test_invalid_path_param(self):
        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p",
                    "software"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass

        result = self.stderr.getvalue().splitlines()[-1]
        self.assertEqual(("litp show: error: argument -p/--path: software"
                          " is not a valid path argument"), result)

    def test_bad_params(self):
        data = {
            "messages": [
                {
                    "_links": {
                               "self": {
                                        "href": "/software"
                                        }
                    },
                    "type": "InvalidProperty",
                    "property_name": "test",
                    "message": "Invalid property: z"
                }
            ],
            "status": 422
        }

        sys.argv = ["-u", "foo", "-P", "bar", "create", "-p",
                    "/software/profiles/rhel_6_2",
                    "-t", "os-profile", "-o", "z=bad"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data), status=32201)
            cli.run_command(sys.argv)

        expected_string = (
            "/software\n    InvalidProperty in property: \"test\""
            "    Invalid property: z\n\n")
        self.assertEqual(expected_string.rstrip(),
                         self.stderr.getvalue().rstrip())

    def test_process_request_from_dict(self):
        data = {
            "type": "deployment",
            "id": "dep1",
            "properties": {}
        }
        data_response = sample_json_output.create_deployment_response

        def get_option(option):
            if 'recursive' in option:
                return False

        cli = litp.LitpCli()
        cli.get_option = get_option
        cli._get_auth_headers = mock_get_auth_headers
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(data_response, status=201)
            cli.conn = cli._get_connection()
        cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                         'POST', data, mock_format_func, None)
        # This is to do with the weird evals
        # between strings, dicts and json objects
        self.assertEqual(json.loads(json.dumps(data_response)),
                         json.loads(self.stdout.getvalue()))

    def test_process_request_from_string(self):
        data = {
            "type": "deployment",
            "id": "dep1",
            "properties": {}
        }
        data_response = json.loads(sample_json_output.deployments_output)

        cli = litp.LitpCli()
        cli.args = MockArgumentParser()
        cli._get_auth_headers = mock_get_auth_headers
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(data_response, status=201)
            cli.conn = cli._get_connection()
        cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                         'POST', data, mock_format_func, None)
        # This is to do with the weird evals
        # between strings, dicts and json objects
        self.assertEqual(json.loads(json.dumps(data_response)),
                         json.loads(self.stdout.getvalue()))

    def test_process_request_raw_http_error(self):
        data = {
            "type": "deployment",
            "id": "dep1",
            "properties": {}
        }

        cli = litp.LitpCli()
        cli.args = MockArgumentParser({'raw': True})
        cli._get_auth_headers = mock_get_auth_headers
        data_response = sample_json_output.invalid_location_output
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data_response), status=404)
            cli.conn = cli._get_connection()
        cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                         'POST', data, mock_format_func, None)
        # This is to do with the weird evals
        # between strings, dicts and json objects
        stderr_to_dict = json.loads(self.stderr.getvalue())
        self.assertEqual(data_response, stderr_to_dict)

    def test_process_request_raw_success(self):
        data = {
            "type": "deployment",
            "id": "dep1",
            "properties": {}
        }

        cli = litp.LitpCli()
        cli._get_auth_headers = mock_get_auth_headers
        cli.args = MockArgumentParser({'raw': True})
        str_data = json.dumps(data, indent=2)
        data_response = json.loads(sample_json_output.deployments_output)
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data_response), status=201)
            cli.conn = cli._get_connection()
        cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                        'POST', str_data, mock_format_func, None)
        # This is to do with the weird evals
        # between strings, dicts and json objects
        stdout_to_dict = json.loads(self.stdout.getvalue())
        self.assertEqual(data_response, stdout_to_dict)

    def test_process_request_raw_errors(self):
        data = {
            "type": "deployment",
            "id": "dep1",
            "properties": {}
        }

        str_data = json.dumps(data, indent=2)
        data_response = json.loads(sample_json_output.create_plan_error_output)

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            cli._get_auth_headers = mock_get_auth_headers
            cli.args = MockArgumentParser({'raw': True})
            self.mock_https_connection.set_expected_response(
                json.dumps(data_response), status=201)
            cli.conn = cli._get_connection()
            cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                                 'POST', str_data, mock_format_func, None)
        # This is to do with the weird evals
        # between strings, dicts and json objects
        stdout_to_dict = json.loads(self.stdout.getvalue())
        self.assertEqual(data_response, stdout_to_dict)

    def test_litp_help(self):
        expected_string = sample_help_output.litp_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual([s.rstrip() for s in expected_string.split('\n')],
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_remove_snapshot_help(self):
        expected_string = sample_help_output.litp_remove_snapshot_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'remove_snapshot', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        actual = [s.rstrip() for s in self.stdout.getvalue().split('\n')]
        self.assertEqual(expected_string, actual)

    def test_litp_create_snapshot_help(self):
        expected_string = sample_help_output.litp_create_snapshot_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'create_snapshot', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        actual = [s.rstrip() for s in self.stdout.getvalue().split('\n')]
        self.assertEqual(expected_string, actual)

    def test_litp_create_help(self):
        expected_string = sample_help_output.litp_create_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'create', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_create_plan_help(self):
        expected_string = sample_help_output.litp_create_plan_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'create_plan', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                             self.stdout.getvalue().split('\n')])

    def test_litp_export_help(self):
        expected_string = sample_help_output.litp_export_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'export', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_import_help(self):
        expected_string = sample_help_output.litp_import_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'import', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_import_iso_help(self):
        expected_string = sample_help_output.litp_import_iso_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'import_iso', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_inherit_help(self):
        expected_string = sample_help_output.litp_inherit_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'inherit', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_load_help(self):
        expected_string = sample_help_output.litp_load_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'load', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_prepare_restore_help(self):
        expected_string = sample_help_output.litp_prepare_restore_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'prepare_restore', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_remove_help(self):
        expected_string = sample_help_output.litp_remove_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'remove', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_restore_snapshot_help(self):
        expected_string = sample_help_output.litp_restore_snapshot_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'restore_snapshot', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_restore_model_help(self):
        expected_string = sample_help_output.litp_restore_model_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'restore_model', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_run_plan_help(self):
        expected_string = sample_help_output.litp_run_plan_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'run_plan', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_show_help(self):
        expected_string = sample_help_output.litp_show_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'show', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_show_plan_help(self):
        expected_string = sample_help_output.litp_show_plan_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'show_plan', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_update_help(self):
        expected_string = sample_help_output.litp_update_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'update', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_upgrade_help(self):
        expected_string = sample_help_output.litp_upgrade_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'upgrade', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_litp_version_help(self):
        expected_string = sample_help_output.litp_version_help
        self._catch_sys_exit()
        cli = litp.LitpCli()
        sys.argv = ["-u", "foo", "-P", "bar", 'version', "--help"]
        cli.args = sys.argv
        cli.wrapped_run_command(sys.argv)
        self.assertEqual(expected_string,
                         [s.rstrip() for s in
                                    self.stdout.getvalue().split('\n')])

    def test_validate_opts(self):
        """
        Test that we validate the options passed in
        """
        sys.argv = ["-u", "foo", "-P", "bar", "create", "-p",
                    "/software/profile/profile2",
                    "-t", "os-profile",
                    "-o", "bogus"]
        cli = litp.LitpCli()
        self._catch_sys_exit()
        cli.wrapped_run_command(sys.argv)
        expected_string = (
            "Usage: litp create [-h] -t TYPE -p PATH "
            "[-o PROPERTIES [PROPERTIES ...]] [-j]")
        self.assertEqual(
            expected_string,
            self.stderr.getvalue().split('\n')[0])

    """
    Below are all tests associated with authentication
    """
    def gimme_a_random_cli_that_doesnt_kill_argparse(self,
                                                     include_userpass=False):
        if include_userpass:
            sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/software"]
        else:
            sys.argv = ["show", "-p", "/software"]
        cli = litp.LitpCli()
        cli.args = sys.argv
        return cli

    def test_get_user_passwd_from_empty_file(self):
        swp = SafeConfigParser.sections
        try:
            cli = self.gimme_a_random_cli_that_doesnt_kill_argparse()
            cli._can_get_credentials_from_file = lambda: True
            SafeConfigParser.sections = lambda x: []
            self.assertRaises(
                Exception, cli._get_user_passwd_from_file, 'dat_filename')
        finally:
            SafeConfigParser.sections = swp

    def test_get_user_passwd_from_empty_section(self):
        try:
            swp = SafeConfigParser.sections
            swp2 = SafeConfigParser.options
            cli = self.gimme_a_random_cli_that_doesnt_kill_argparse()
            SafeConfigParser.sections = lambda x: ['section']
            SafeConfigParser.options = lambda x, y: []
            self.assertRaises(
                Exception, cli._get_user_passwd_from_file, 'dat_filename')
        finally:
            SafeConfigParser.sections = swp
            SafeConfigParser.options = swp2

    def test_get_user_passwd_with_matches(self):
        def mock_get(self, x, y):
            raise NoOptionError('ha!', 'srry')

        def mock_get_username(self, x, y):
            if y == 'username':
                return 'some_val'
            raise NoOptionError('ha!', 'srry')
        try:
            swp = SafeConfigParser.sections
            swp2 = SafeConfigParser.options
            swp3 = SafeConfigParser.get
            cli = self.gimme_a_random_cli_that_doesnt_kill_argparse()
            SafeConfigParser.sections = lambda x: ['section']
            SafeConfigParser.get = mock_get
            # no matches
            SafeConfigParser.options = lambda x, y: ['option1']
            self.assertRaises(
                Exception, cli._get_user_passwd_from_file, 'dat_filename')
            # 1 match
            SafeConfigParser.options = lambda x, y: ['option1', 'username']
            SafeConfigParser.get = mock_get_username
            self.assertRaises(
                Exception, cli._get_user_passwd_from_file, 'dat_filename')
            # 2 matches
            SafeConfigParser.options = lambda x, y: ['password', 'username']
            SafeConfigParser.get = lambda x, y, z: 'some_val'
            self.assertEquals(
                cli._get_user_passwd_from_file('dat_filename'),
                ['some_val', 'some_val'])
        finally:
            SafeConfigParser.sections = swp
            SafeConfigParser.options = swp2
            SafeConfigParser.get = swp3

    def test_get_user_passwd_from_prompt(self):
        cli = self.gimme_a_random_cli_that_doesnt_kill_argparse(
            include_userpass=True)

        litp.getpass.getpass = lambda: "Fantana"
        self.assertEquals(cli._get_user_passwd_from_prompt()[1], "Fantana")

        litp.getpass.getpass = lambda: ""
        self.assertRaises(AttributeError, cli._get_user_passwd_from_prompt)

    def test_can_get_credentials_from_file(self):
        class MockstatBadPermissions(object):
            st_mode = 33204

        class MockstatGoodPermissions(object):
            st_mode = 33152

        try:
            import os
            swp = os.path.exists
            swp2 = os.stat
            # first try with file not existing
            os.path.exists = lambda x: False
            cli = self.gimme_a_random_cli_that_doesnt_kill_argparse()
            self.assertFalse(cli._can_get_credentials_from_file('filename'))
            # now with wrong permissions
            os.path.exists = lambda x: True
            os.stat = lambda x: MockstatBadPermissions()
            self.assertFalse(cli._can_get_credentials_from_file('filename'))
            # and finally good permissions
            os.stat = lambda x: MockstatGoodPermissions()
            self.assertTrue(cli._can_get_credentials_from_file('filename'))
        finally:
            os.path.exists = swp
            os.stat = swp2

    def test_get_user_passwd(self):
        # again, a bit useless, just for coverage purposes
        cli = self.gimme_a_random_cli_that_doesnt_kill_argparse(
            include_userpass=True)
        cli._can_get_credentials_from_file = lambda x: True
        cli = self.gimme_a_random_cli_that_doesnt_kill_argparse()
        cli._can_get_credentials_from_file = lambda x: True
        cli._get_user_passwd_from_file = lambda x: 'from file'
        self.assertEquals(cli.get_user_passwd("", ""), 'from file')
        cli._can_get_credentials_from_file = lambda x: False
        cli._get_user_passwd_from_prompt = lambda x: ("", "from prompt")
        self.assertEquals(cli.get_user_passwd("Ron", ""),
                          ("Ron", "from prompt"))

    def test_process_request_401_error(self):
        data_response = json.loads(sample_json_output.create_plan_error_output)
        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            cli._get_auth_headers = mock_get_auth_headers
            self.mock_https_connection.set_expected_response(json.dumps(data_response), status=401)
            cli.conn = cli._get_connection()
            cli._process_request('http://localhost:9999/litp/rest/v1/deployments/dep1',
                                 'GET', None, mock_format_func, None)
        stderr_output = self.stderr.getvalue()
        self.assertEqual("Error 401: Unauthorized access\n", stderr_output)

    def test_create_plan(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "create_plan"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    @patch('litpcli.litp.LitpCli._request')
    def test_create_plan_no_lock_tasks(self, patched_request):
        data = sample_json_output.software_output

        def patch_request(url, method=None, data=None, format_func=None,
                 content_type=None):
            self.assertEquals(
                data, {'type': 'plan', 'id': 'plan', 'no-lock-tasks': 'True'})
            return data

        patched_request.side_effect = patch_request

        sys.argv = ["-u", "foo", "-P", "bar", "create_plan", "--no-lock-tasks"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    @patch('litpcli.litp.LitpCli._request')
    def test_create_plan_no_lock_tasks_list(self, patched_request):
        data = sample_json_output.software_output

        def patch_request(url, method=None, data=None, format_func=None,
                 content_type=None):
            self.assertEquals(
                data, {'type': 'plan', 'id': 'plan', 'no-lock-tasks-list': ['svc-1', 'svc-2'], 'no-lock-tasks': 'True'})
            return data

        patched_request.side_effect = patch_request

        sys.argv = ["-u", "foo", "-P", "bar", "create_plan", "--no-lock-tasks", "svc-1" , "svc-2"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    @patch('litpcli.litp.LitpCli._request')
    def test_create_plan_initial_lock_tasks(self, patched_request):
        data = sample_json_output.software_output

        def patch_request(url, method=None, data=None, format_func=None,
                 content_type=None):
            self.assertEquals(
                data, {'type': 'plan', 'id': 'plan', 'initial-lock-tasks': 'True'})
            return data

        patched_request.side_effect = patch_request

        sys.argv = ["-u", "foo", "-P", "bar", "create_plan", "--initial-lock-tasks"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_create_snapshot(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "create_snapshot"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_create_snapshot_exclude_nodes(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "create_snapshot",
                "--name", "snapshot_name", "--exclude_nodes", "node1"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_create_snapshot_exclude_nodes_no_name(self):
        sys.argv = ["-u", "foo", "-P", "bar", "create_snapshot",
                "--exclude_nodes", "node1"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass
        else:
            self.fail('Should have failed with SystemExit')
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected = [
            'Usage: litp create_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j]',
            'litp create_snapshot: error: exclude_nodes may only be used with --name',
            ]
        self.assertEquals(expected, result)

    def test_create_snapshot_exclude_nodes_invalid_list(self):
        sys.argv = ["-u", "foo", "-P", "bar", "create_snapshot",
                "--exclude_nodes", "node1,node2,"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass
        else:
            self.fail('Should have failed with SystemExit')
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected = ['Usage: litp create_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j]',
                 'litp create_snapshot: error: argument -e/--exclude_nodes: '
                 '"exclude_nodes" malformed. Valid format: '
                 '^(([a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9]),)*([a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])$']
        self.assertEquals(expected, result)

    def test_remove_snapshot(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "remove_snapshot"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_remove_snapshot_exclude_nodes(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "remove_snapshot",
                "--name", "snapshot_name", "--exclude_nodes", "node1"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_remove_snapshot_exclude_nodes_no_name(self):
        sys.argv = ["-u", "foo", "-P", "bar", "remove_snapshot",
                "--exclude_nodes", "node1"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass
        else:
            self.fail('Should have failed with SystemExit')
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected = [
            'Usage: litp remove_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j] [-f]',
            'litp remove_snapshot: error: exclude_nodes may only be used with --name',
            ]
        self.assertEquals(expected, result)

    def test_remove_snapshot_exclude_nodes_invalid_list(self):
        sys.argv = ["-u", "foo", "-P", "bar", "remove_snapshot",
                "--exclude_nodes", "node1,node2,"]
        try:
            cli = litp.LitpCli()
            cli.wrapped_run_command(sys.argv)
        except SystemExit, e:
            # expecting this
            pass
        else:
            self.fail('Should have failed with SystemExit')
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected = ['Usage: litp remove_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j] [-f]',
                 'litp remove_snapshot: error: argument -e/--exclude_nodes: '
                 '"exclude_nodes" malformed. Valid format: '
                 '^(([a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9]),)*([a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])$']
        self.assertEquals(expected, result)

    def test_remove_plan(self):
        data = sample_json_output.software_output

        sys.argv = ["-u", "foo", "-P", "bar", "remove_plan"]

        cli = litp.LitpCli()
        with patch.object(cli, '_get_connection') as _get_connection:
            _get_connection.return_value = self.mock_https_connection
            self.mock_https_connection.set_expected_response(json.dumps(data))
            cli.run_command(sys.argv)

        self.assertEqual("", self.stdout.getvalue())

    def test_replace_no_file(self):
        self._catch_sys_exit()
        sys.argv = ["-u", "foo",
                    "-P", "bar",
                    "load",
                    "-p", "/",
                    "--replace",
                    "-f"]

        cli = litp.LitpCli()
        self.assertRaises(TypeError, cli.run_command, sys.argv)
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected_string = ('litp load: error: argument -f/--file: expected '
                           'one argument')
        self.assertTrue(expected_string in result)

    def test_replace_no_path(self):
        self._catch_sys_exit()
        sys.argv = ["-u", "foo",
                    "-P", "bar",
                    "load",
                    "--replace",
                    "-f",
                    "test.xml"]

        cli = litp.LitpCli()
        self.assertRaises(TypeError, cli.run_command, sys.argv)
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected_string = ('litp load: error: argument -p/--path is required')
        self.assertTrue(expected_string in result)

    def test_replace_empty_path(self):
        self._catch_sys_exit()
        sys.argv = ["-u", "foo",
                    "-P", "bar",
                    "load",
                    "-p", "",
                    "--replace",
                    "-f",
                    "test.xml"]

        cli = litp.LitpCli()
        self.assertRaises(TypeError, cli.run_command, sys.argv)
        result = [line.strip() for line in self.stderr.getvalue().splitlines()]
        expected_string = ('litp load: error: argument -p/--path:  is not a '
                           'valid path argument')
        self.assertTrue(expected_string in result)


    def test_merge_and_replace(self):
        self._catch_sys_exit()
        sys.argv = ["-u", "foo",
                    "-P", "bar",
                    "load",
                    "-p", "/",
                    "--replace",
                    "--merge",
                    "-f",
                    "test.xml"]

        cli = litp.LitpCli()
        self.assertRaises(TypeError, cli.run_command, sys.argv)
        expected_string = ['litp load: error: argument --merge: not allowed '
                          'with argument --replace\n']


    def test_load_from_empty_file(self):
        self._catch_sys_exit()
        sys.argv = ["-u", "foo",
                    "-P", "bar",
                    "load",
                    "-p", "/",
                    "-f",
                    "test.xml"]
        cli = litp.LitpCli()
        cli.run_command(sys.argv)
        self.assertEqual(
            "[Errno 2] No such file or directory: 'test.xml'\n",
            self.stderr.getvalue())

urlopen_refused = Mock(side_effect=urllib2.URLError)
urlopen_timedout = Mock(side_effect=socket.timeout)


class ServiceProblemsTestCase(unittest.TestCase):
    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout = StringIO()

        self.old_stderr = sys.stderr
        sys.stderr = self.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    @patch('urllib2.urlopen', urlopen_refused)
    def test_litpd_down(self):
        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/"]
        cli = litp.LitpCli()
        cli.run_command(sys.argv)
        expected = litp.LITP_SERVICE_ERR + "\n"
        self.assertEqual(expected, self.stderr.getvalue())

    @patch('urllib2.urlopen', urlopen_timedout)
    def test_network_down(self):
        sys.argv = ["-u", "foo", "-P", "bar", "show", "-p", "/"]
        cli = litp.LitpCli()
        cli.run_command(sys.argv)
        expected = litp.LITP_SERVICE_ERR + "\n"
        self.assertEqual(expected, self.stderr.getvalue())
