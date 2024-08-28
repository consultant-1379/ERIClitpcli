import json
import unittest

import sample_json_output

from litpcli.formatter import CliFormatter


class CliFormatterTests(unittest.TestCase):
    def setUp(self):
        default_host = "localhost"
        default_port = "9999"
        rest_version = "/litp/rest/v1"
        self.url = "".join(("https://", default_host,
                            ":", default_port, rest_version))

    def test_cli_formatter_init(self):
        self.assertRaises(
            TypeError,
            CliFormatter, "http://x:80", ['bad', 'argument'])
        arguments = {"arg": "ok"}
        cli = CliFormatter("http://x", arguments)
        self.assertEqual(arguments, cli.args)

    def test_cb_format_item_type(self):
        data = sample_json_output.item_description
        formatter = CliFormatter(self.url, {'long': True})
        formatted_item = formatter.cb_format_item_type(data)
        expected_string = "/item-types/package-list"
        self.assertEqual(expected_string, formatted_item)
        formatter = CliFormatter(self.url)
        formatted_item = formatter.cb_format_item_type(data)
        expected_string = ("/item-types/package-list"
                           "\n    description: Collection of software packages"
                           " to install"
                           "\n    fields:"
                           "\n            name: packages"
                           "\n                collection of: package"
                           "\n                min: 0"
                           "\n                max: 9999"
                           "\n            name: version"
                           "\n                description: "
                           "\n                required: False"
                           "\n                type: basic_string"
                           "\n            name: name"
                           "\n                description: "
                           "\n                required: False"
                           "\n                type: basic_string")
        self.assertEqual(expected_string, formatted_item)

    def test_cb_format_show_plan(self):
        data = json.loads(sample_json_output.plan_output)
        formatter = CliFormatter(self.url)
        expected = (
            "Phase 1\n\tTask status\n\t-----------\n\tInitial\t\t/ms\n"
            "\t\t\tMock task done on node2\n\n"
            "Tasks: 1 | Initial: 1 | Running: 0 | Success: 0 | Failed: 0"
            " | Stopped: 0\n"
            "Plan Status: Initial"
        )
        print expected
        print formatter.cb_format_show_plan(data)
        self.assertEqual(expected, formatter.cb_format_show_plan(data))
        formatter = CliFormatter(self.url, {"active_only": True})
        expected = (
            "Tasks: 1 | Initial: 1 | Running: 0 | Success: 0 | Failed: 0"
            " | Stopped: 0\n"
            "Plan Status: Initial"
        )
        self.assertEqual(expected, formatter.cb_format_show_plan(data))

    def test_format_paths_as_tree(self):
        data = json.loads(sample_json_output.recursive_ms_output)
        formatter = CliFormatter(self.url)
        expected = (
            "/ms\n"
            "    /services\n"
            "    /items\n"
            "    /ipaddresses\n"
            "        /ip1")

        self.assertEqual(expected, formatter.cb_format_paths_as_tree(data,
                                                            recursive=True))

    def test_format_item_types(self):
        data = json.loads(sample_json_output.item_types_output)
        formatter = CliFormatter(self.url)
        expected = (
            "name: volume-group\n"
            "description: \n\n"
            "name: profile\n"
            "description: Base profile item.")

        self.assertEqual(expected, formatter.cb_format_item_types(data))

    def test_format_property_types(self):
        data = json.loads(sample_json_output.property_types_output)
        formatter = CliFormatter(self.url)
        expected = "name: ipv6_address\nname: selinux_mode"

        self.assertEqual(expected, formatter.cb_format_item_types(data))

    def test_get_plan(self):
        plan_format_item = {
            'indent': '    ',
            'description': 'Mock task done on node2',
            'state': 'Initial',
            'path': '/ms',
            'id': 'a_mock_task'}
        data = json.loads(sample_json_output.plan_output)
        formatter = CliFormatter(self.url)
        returned_tasks = formatter._get_plan(data)
        self.assertEqual([plan_format_item], returned_tasks[0])
        data = sample_json_output.plan_output
        returned_tasks = formatter._get_plan(data)
        self.assertEqual([plan_format_item], returned_tasks[0])

    def test_get_plan_bad_input(self):
        data = sample_json_output.plan_output
        data = data.replace('"', '#')
        formatter = CliFormatter(self.url)
        returned_tasks = formatter._get_plan(data)
        self.assertEqual(0, len(returned_tasks))

    def test_format_property_type(self):
        property_type = {
            "id": "libvirt_ram_size",
            "regex": "^[1-9][0-9]{2,}M$",
            "uri": "https://localhost:9999/litp/rest/v1/property-types/"
                  "libvirt_ram_size"
        }
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_property_type(property_type)
        expected_string = "name: libvirt_ram_size\nregex: ^[1-9][0-9]{2,}M$\n"
        self.assertEqual(expected_string, result)

    def test_format_item_type(self):
        item_type = {
            "description": "Base disk item",
            "_links": {
                "self": {
                    "href": "https://localhost:9999/litp/rest/v1/item-types/disk"
                }
            },
            "properties": {
                "bootable": {
                    "regex": "^(true|false)$",
                    "description": "",
                    "default": "false",
                    "required": False,
                    "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/property-types/basic_boolean"
                        }
                    },
                    "id": "basic_boolean"
                },
                "uuid": {
                    "regex": "^[a-zA-Z0-9_][a-zA-Z0-9_-]*$",
                    "required": True,
                    "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/property-types/disk_uuid"
                        }
                    },
                    "id": "disk_uuid",
                    "description": "UUID of this disk."
                },
                "name": {
                    "regex": "^[a-zA-Z0-9\\-\\._]+$",
                    "required": True,
                    "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/property-types/basic_string"
                        }
                    },
                    "id": "basic_string",
                    "description": "Name of this disk."
                },
                "size": {
                    "regex": "^[1-9][0-9]{0,}[MGT]$",
                    "required": True,
                    "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/property-types/disk_size"
                        }
                    },
                    "id": "disk_size",
                    "description": "Size of this disk."
                }
            },
            "id": "disk"
        }

        expected_output = """/item-types/disk
    description: Base disk item
    fields:
            name: bootable
                description: 
                required: False
                regex: ^(true|false)$
                type: basic_boolean
            name: size
                description: Size of this disk.
                required: True
                regex: ^[1-9][0-9]{0,}[MGT]$
                type: disk_size
            name: uuid
                description: UUID of this disk.
                required: True
                regex: ^[a-zA-Z0-9_][a-zA-Z0-9_-]*$
                type: disk_uuid
            name: name
                description: Name of this disk.
                required: True
                regex: ^[a-zA-Z0-9\-\._]+$
                type: basic_string"""

        formatter = CliFormatter(self.url)
        result = formatter.cb_format_item_type(item_type)
        self.assertEqual(expected_output, result)

    def test_format_plan_phase(self):
        phase = {
            "item-type-name": "phase",
            "_links": {
                "self": {
                    "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/11"
                },
                "item-type": {
                    "href": "https://localhost:9999/litp/rest/v1/item-types/phase"
                }
            },
            "_embedded": {
                "item": [
                    {
                        "item-type-name": "collection-of-task",
                        "_links": {
                            "self": {
                                "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/11/tasks"
                            },
                            "collection-of": {
                                "href": "https://localhost:9999/litp/rest/v1/item-types/task"
                            }
                        },
                        "id": "tasks"
                    }
                ]
            },
            "id": "11"
        }

        expected_output = """
/plans/plan/phases/11
    type: phase
    children:
        /tasks"""

        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(phase)
        self.assertEqual(expected_output, result)

    def test_format_plan_task(self):
        task = {
            "description": "Update node \"node2\" host file header",
            "call_id": "hosts",
            "item-type-name": "task",
            "state": "Initial",
            "_links": {
                "self": {
                    "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/11/tasks/node2__class__hosts"
                },
                "item-type": {
                    "href": "https://localhost:9999/litp/rest/v1/item-types/task"
                },
                "rel": {
                    "href": "https://localhost:9999/litp/rest/v1/deployments/single_blade/clusters/cluster1/nodes/node2"
                }
            },
            "id": "node2__class__hosts",
            "call_type": "class"
        }

        expected_output = """
/plans/plan/phases/11/tasks/node2__class__hosts
    type: task
    state: Initial"""

        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(task)
        self.assertEqual(expected_output, result)

    def test_format_show(self):
        data = sample_json_output.ms_output
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        expected_result = (
            "\n/ms\n"
            "    type: ms\n"
            "    state: Initial\n"
            "    properties:\n"
            "        hostname: ms1\n"
            "\n"
            "    children:\n"
            "        /services\n"
            "        /items\n"
            "        /ipaddresses")

        self.assertEqual(expected_result, result)

    def test_format_show_link(self):
        data = sample_json_output.show_link_output
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        expected_result = (
            "\n/deployments/single_blade/clusters"
            "/cluster1/nodes/node1/system\n"
            "    links to: /infrastructure/system_providers"
            "/libvirt1/systems/vm1\n"
            "    type: libvirt-system\n"
            "    state: Initial\n"
            "    properties:\n"
            "        system_name: VM1\n")

        self.assertEqual(expected_result, result)

    def test_format_show_bad_data(self):
        data = sample_json_output.ms_output
        data = data.replace('"', '#')
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        self.assertEqual(data, result)

    def test_format_error(self):
        data = sample_json_output.invalid_location_output
        formatter = CliFormatter(self.url)
        formatted_item = formatter.cb_format_error(data)
        expected_string = ("/invalid\n"
                           "    InvalidLocationError"
                           "    Item not found")
        self.assertEqual(expected_string, formatted_item)
        data = json.dumps(sample_json_output.invalid_location_output)
        formatted_item = formatter.cb_format_error(data)
        self.assertEqual(expected_string, formatted_item)
        data = json.dumps(sample_json_output.invalid_location_output)
        data = data.replace('"', '#')
        formatted_item = formatter.cb_format_error(data)
        self.assertEqual(data, formatted_item)

    def test_format_inherited_item_no_properties(self):
        data = sample_json_output.show_inherited_output_no_properties
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        expected_result = (
            "\n"
            "/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root\n"
            "    inherited from: /infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root\n"
            "    type: reference-to-file-system\n"
            "    state: Initial"
        )
        self.assertEqual(expected_result, result)

    def test_format_inherited_item_no_overwritten_properties(self):
        data = sample_json_output.show_inherited_output_no_overwritten_properties
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        expected_result = (
            "\n"
            "/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root\n"
            "    inherited from: /infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root\n"
            "    type: reference-to-file-system\n"
            "    state: Initial\n"
            "    properties (inherited properties are marked with asterisk):\n"
            "        mount_point: / [*]\n"
            "        type: ext4 [*]\n"
            "        size: 48G [*]"
        )
        self.assertEqual(expected_result, result)

    def test_format_inherited_item(self):
        data = sample_json_output.show_inherited_output
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_show(data)
        expected_result = (
            "\n"
            "/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root\n"
            "    inherited from: /infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root\n"
            "    type: reference-to-file-system\n"
            "    state: Initial\n"
            "    properties (inherited properties are marked with asterisk):\n"
            "        mount_point: / [*]\n"
            "        type: ext4 [*]\n"
            "        size: 48G"
        )
        self.assertEqual(expected_result, result)

    def test_format_show_completion(self):
        data  = sample_json_output.show_completion_output
        formatter = CliFormatter(self.url)
        result = formatter.cb_format_path_completion(data)
        formatted_completions = result.splitlines()

        expected_completions = [
                '/ms',
                '/ms/items/',
                '/ms/network_interfaces/',

                # /ms/system is a reference to a system type
                '/ms/system:system',
                '/ms/services/',
                '/ms/routes/',
                '/ms/configs/',
                '/ms/file_systems/',
                ]

        self.assertEquals(expected_completions, formatted_completions)
