"""
CLI for LITP2.0 REST API.
"""

import argparse
import base64
import getpass
import httplib
import json
import os
import pwd
import socket
import stat
import sys
import textwrap
import urlparse
from ConfigParser import SafeConfigParser, NoOptionError, \
    MissingSectionHeaderError
from gettext import gettext as _
from hashlib import md5
from time import time
import traceback
import ssl

from litpcli.formatter import CliFormatter
from litpcli.help import FormattedHelpArgumentParser, \
    RawDescriptionHelpFormatter, NestedArgumentsGroupHelpFormatter
from litpcli.action import TypeAction, FileAction, DepthAction, PathAction, \
    PropertyAction, DeleteAction, valid_create_path, valid_path, valid_depth, \
    validate_opts, UpdateAction, valid_snapshot_name, ExcludeNodesAction, \
    valid_exclude_nodes, NoLockTasksAction, InitialLockTasksAction
from litpcli.group import NestedArgumentsGroup


DEFAULT_HOST = "localhost"
DEFAULT_PORT = "9999"
REST_VERSION = "/litp/rest/v1"
XML_PATH = "/litp/xml"
XML_URL = "".join(("https://", DEFAULT_HOST, ":", DEFAULT_PORT, XML_PATH))
CONFIG_PATH = "/litp/logging"
UPGRADE_PATH = "/litp/upgrade"
RESTORE_PATH = "/litp/restore_model"
SNAPSHOT_PATH = "/snapshots"
UPGRADE_URL = "".join(
    ("https://", DEFAULT_HOST, ":", DEFAULT_PORT, UPGRADE_PATH))
REST_URL = "".join(("https://", DEFAULT_HOST, ":", DEFAULT_PORT, REST_VERSION))
RESTORE_URL = "".join((REST_URL, RESTORE_PATH))
CREDENTIALS_ERR = "Error 401: Unauthorized access"
AUTH_ERR = "Authentication Failed. Provide Username and Password:"
PERMISSION_DENIED_ERR = "Permission denied"
EXPORT_PLANS_ERR = "Plans cannot be exported"
LITP_SERVICE_ERR = "litp does not appear to be running/accessible"
UNIX_SOCKET = '/var/run/litpd/litpd.sock'
LITPRC_FILENAME = "~/.litprc"
HTTPS = 'https'
UNIX = 'unix'


class AuthenticationException(Exception):
    pass


class UnixSocketConnection(httplib.HTTPConnection):
    def __init__(self, path):
        self.path = path
        # '' is a placeholder
        httplib.HTTPConnection.__init__(self, '')

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


class SortedChoicesArgumentParser(FormattedHelpArgumentParser):
    def _check_value(self, action, value):
        # Converted value must be one of the choices (if specified)
        if action.choices is not None and value not in action.choices:
            tup = value, ', '.join(sorted(repr(c) for c in action.choices))
            msg = _('invalid choice: %r (choose from %s)') % tup
            raise argparse.ArgumentError(action, msg)


class NestedArgumentsEnabledArgumentParser(SortedChoicesArgumentParser):
    def __init__(self, *args, **kwargs):
        super(NestedArgumentsEnabledArgumentParser, self).__init__(
                *args, **kwargs)
        self._nested_groups = []

    def add_nested_arguments_group(self, *args, **kwargs):
        group = NestedArgumentsGroup(self, *args, **kwargs)
        self._nested_groups.append(group)
        return group

    def format_usage(self):
        groups = self._mutually_exclusive_groups + self._nested_groups
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions, groups)
        return formatter.format_help()

    def format_help(self):
        formatter = self._get_formatter()

        # usage
        groups = self._mutually_exclusive_groups + self._nested_groups
        formatter.add_usage(self.usage, self._actions, groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups + self._nested_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    def validate_nested_group(self, group, namespace):
        for parent_action, action in reversed(
                zip(group._group_actions, group._group_actions[1:])):
            if getattr(namespace, parent_action.dest) is None and \
                    getattr(namespace, action.dest) is not None:
                msg = _('argument {0} is required if {1} is set.'.format(
                    parent_action.dest, action.dest))
                self.error(msg)

    def _parse_known_args(self, arg_strings, namespace):
        namespace, extras = super(
                NestedArgumentsEnabledArgumentParser, self)._parse_known_args(
                    arg_strings, namespace)
        for group in self._nested_groups:
            self.validate_nested_group(group, namespace)
        return namespace, extras


class LitpCli(object):
    config = None
    conn = None
    conn_type = None

    def __init__(self):
        """
        Create a LitpCli object
        """
        self.base_url = REST_URL
        self.xml_url = XML_URL
        self.upgrade_url = UPGRADE_URL
        self.path_help = 'Location of item in the LITP model'

        self.args = None
        self.formatter = None
        self.errors = []

        self.parser = NestedArgumentsEnabledArgumentParser(
            prog="litp",
            description='LITP Command Line',
        )

        self.parser.add_argument('--url', help=argparse.SUPPRESS)
        self.parser.add_argument("-u", "--username", dest="username",
                            help="Username to connect to LITP service")
        self.parser.add_argument("-P", "--password", dest="password",
                            help="Password to connect to LITP service")

        subparsers = self.parser.add_subparsers(
            title='Actions',
            description=(
                "Actions that can be performed on the specified item at the"
                " given path. For more information on an action, enter the"
                " command 'litp <action> -h'."),
            help="",
            metavar="")

        self._setup_create_parser(subparsers)
        self._setup_create_plan_parser(subparsers)
        self._setup_create_snapshot_parser(subparsers)
        self._setup_create_reboot_plan_parser(subparsers)
        self._setup_debug_parser(subparsers)
        self._setup_export_parser(subparsers)
        self._setup_import_parser(subparsers)
        self._setup_import_iso_parser(subparsers)
        self._setup_inherit_parser(subparsers)
        self._setup_load_parser(subparsers)
        self._setup_prepare_restore_parser(subparsers)
        self._setup_remove_parser(subparsers)
        self._setup_remove_plan_parser(subparsers)
        self._setup_remove_snapshot_parser(subparsers)
        self._setup_restore_snapshot_parser(subparsers)
        self._setup_restore_model_parser(subparsers)
        self._setup_run_plan_parser(subparsers)
        self._setup_show_parser(subparsers)
        self._setup_show_plan_parser(subparsers)
        self._setup_stop_plan_parser(subparsers)
        self._setup_update_parser(subparsers)
        self._setup_upgrade_parser(subparsers)
        self._setup_version_parser(subparsers)

    def _recursive_get(self, item, depth=None, errors=None):
        if not isinstance(item, list):
            if '_embedded' in item:
                fetched_children = []
                children = item['_embedded'].get('item', [])

                depth_limit = self.get_option('depth')
                if depth_limit:
                    if depth is None:
                        depth = 1
                    else:
                        depth += 1

                for child in children:

                    if '_links' in child:
                        is_unix = self.conn_type == UNIX
                        headers = self._get_auth_headers(is_unix)
                        headers.update({"Content-Type": "application/json"})
                        self.conn.request('GET',
                                          child['_links']['self']["href"],
                                          '', headers)
                        response = self.conn.getresponse()
                        result = response.read()
                        new_item = json.loads(result)

                        if response.status != httplib.OK:
                            if errors is None:
                                errors = []
                            errors.append(new_item)
                        elif depth is None or depth <= depth_limit:
                            retrieved_item, _ = \
                                self._recursive_get(new_item, depth, errors)
                            fetched_children.append(retrieved_item)
                item['_embedded']['item'] = fetched_children
        return item, errors

    def _setup_create_plan_parser(self, subparsers):
        create_parser = subparsers.add_parser(
            "create_plan",
            formatter_class=RawDescriptionHelpFormatter,
            help=("Creates a set of tasks (a plan) used to deploy the"
                  " deployment model."),
            description=("Creates a set of tasks (a plan) used to deploy the"
                         " deployment model."),
            epilog=textwrap.dedent(
                '''\
            Examples:

            litp create_plan

            litp create_plan --no-lock-tasks

            litp create_plan --no-lock-tasks c1 c2

            litp create_plan --initial-lock-tasks
        '''))

        create_parser.set_defaults(func=self.object_create_plan)
        create_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

        create_parser.add_argument("--no-lock-tasks",
                                   dest="no_lock_tasks",
                                   metavar=(''),
                                   nargs='*',
                                   action=NoLockTasksAction,
                                   help=("Do not generate lock or unlock tasks"
                                      " for all clusters\nor specify "
                                      "cluster(s) to have no lock or unlock "
                                      "tasks."))

        create_parser.add_argument("--initial-lock-tasks",
                                   dest="initial_lock_tasks",
                                   metavar=(''),
                                   nargs=0,
                                   action=InitialLockTasksAction,
                                   help=("Generate lock and unlock tasks"
                                         " for nodes in Initial state."))

    def _setup_create_snapshot_parser(self, subparsers):
        create_parser = subparsers.add_parser(
            "create_snapshot",
            formatter_class=NestedArgumentsGroupHelpFormatter,
            help=("Creates and executes a set of tasks (a plan) used to create"
                  " file system snapshots."),
            description=("Creates and executes a set of tasks (a plan) used to"
                         " create file system snapshots."),
            epilog=("Example: litp create_snapshot"))
        create_parser.set_defaults(func=self.object_create_snapshot)
        group = create_parser.add_nested_arguments_group()
        group.add_argument("-n", "--name", dest="name",
                                   type=valid_snapshot_name,
                                   help="Optional snapshot name")
        group.add_argument("-e", "--exclude_nodes",
                               dest="exclude_nodes",
                               action=ExcludeNodesAction,
                               type=valid_exclude_nodes,
                               help="Comma separated list of excluded nodes "
                                    "by hostname. Use only with --name")
        create_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_create_reboot_plan_parser(self, subparsers):
        desc_text = "Create a plan to lock, reboot and unlock a single "\
                    "deployed node or all deployed nodes."
        create_parser = subparsers.add_parser(
            "create_reboot_plan",
            formatter_class=NestedArgumentsGroupHelpFormatter,
            help=(desc_text),
            description=(desc_text),
            epilog="Examples:\nlitp create_reboot_plan\n"
                   "litp create_reboot_plan -p "
                   "/deployments/deployment1/clusters/cluster1/nodes/n1")
        create_parser.set_defaults(func=self.object_create_reboot_plan)
        group = create_parser.add_nested_arguments_group()
        group.add_argument("-p", "--path", dest="path",
                                   type=valid_path,
                                   help="Optional node path")
        create_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_remove_snapshot_parser(self, subparsers):
        remove_parser = subparsers.add_parser(
            "remove_snapshot",
            formatter_class=NestedArgumentsGroupHelpFormatter,
            help=("Creates and executes a set of tasks (a plan) that is used"
                  " to remove file system snapshots."),
            description=("Creates and executes a set of tasks (a plan) that"
                         " is used to remove file system snapshots."),
            epilog=("Example: litp remove_snapshot"))
        remove_parser.set_defaults(func=self.object_remove_snapshot)
        group = remove_parser.add_nested_arguments_group()
        group.add_argument("-n", "--name", dest="name",
                                   type=valid_snapshot_name,
                                   help="Optional snapshot name")
        group.add_argument("-e", "--exclude_nodes",
                               dest="exclude_nodes",
                               action=ExcludeNodesAction,
                               type=valid_exclude_nodes,
                               help="Comma separated list of excluded nodes "
                                    "by hostname. Use only with --name")
        remove_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')
        remove_parser.add_argument('-f', '--force', dest="force",
                                         action="store_true",
                                         help=("Force remove to ignore "
                                               "unreachable LVM nodes"))

    def _setup_restore_snapshot_parser(self, subparsers):
        restore_snap_parser = subparsers.add_parser(
            "restore_snapshot",
            help=("Creates and executes a set of tasks (a plan) that is used"
                  " to restore file system snapshots."),
            description=("Creates and executes a set of tasks (a plan) that"
                         " is used to restore file system snapshots."),
            epilog=("Example: litp restore_snapshot"))
        restore_snap_parser.set_defaults(func=self.object_restore_snapshot)
        restore_snap_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')
        restore_snap_parser.add_argument('-f', '--force', dest="force",
                                         action="store_true",
                                         help=("Force restore to ignore "
                                               "missing snapshots and "
                                               "unreachable nodes"))

    def _setup_import_parser(self, subparsers):
        import_parser = subparsers.add_parser(
            'import',
            formatter_class=RawDescriptionHelpFormatter,
            help='Imports packages into Yum repositories.',
            description=("Imports packages into Yum repositories."),
            epilog=("Examples:\n\nlitp import /mnt/rhel-iso "
                    "/var/www/html/os\n\nlitp import "
                    "/root/libyaml-0.1.3-1.el7.x86_64.rpm"
                    " /var/www/html/3pp_rhel7/\n"))

        import_parser.set_defaults(func=self.object_import)
        required_group = import_parser.add_argument_group("Required Arguments")
        required_group.add_argument(
            'source_path',
            help="Absolute path with rpm packages. This can be a single RPM or"
            " a directory of RPMs."
        )
        required_group.add_argument(
            'destination_path',
            help="Absolute path to destination repo directory or one of"
            " \"litp\" or \"3pp_rhel7\" to import RPMs into the LITP or 3PP"
            " repo. This should be used for LITP RPMs only."
        )
        import_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_import_iso_parser(self, subparsers):
        description = (
            'Imports packages and VM images from a LITP-compliant'
            ' ISO, then installs/upgrades management server software.'
            '\n\n'
            'It may also install new packages from'
            ' the LITP or LITP_PLUGIN repositories and packages'
            ' that are newly required by upgraded packages.')
        import_parser = subparsers.add_parser(
            'import_iso',
            formatter_class=RawDescriptionHelpFormatter,
            help='Imports packages and VM images from a LITP-compliant ISO,'
            ' then installs/upgrades management server software.',
            description=description,
            epilog='Example: litp import_iso /mnt/my-iso')

        import_parser.set_defaults(func=self.object_import_iso)
        required_group = import_parser.add_argument_group("Required Arguments")
        required_group.add_argument(
            'source_path',
            help="Absolute path of mounted ISO. "
            "This should be a LITP-compliant directory tree."
        )
        import_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_remove_plan_parser(self, subparsers):
        remove_parser = subparsers.add_parser(
            "remove_plan",
            help=("Removes the plan from the model."),
            description=("Removes the plan from the model."),
            epilog=("Example: litp remove_plan"))
        remove_parser.set_defaults(func=self.object_remove_plan)
        remove_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_show_plan_parser(self, subparsers):
        show_parser = subparsers.add_parser(
            'show_plan',
            help="Displays the status of tasks initiated by the create_plan"
            " command or executed by the run_plan command. The tasks are"
            " executed in phases determined by the create_plan command.",
            description=("Displays the status of tasks initiated by the"
                         " create_plan command or executed by the run_plan"
                         " command. The tasks are executed in phases"
                         " determined by the create_plan command."),
            epilog="Example: litp show_plan")
        show_parser.set_defaults(func=self.object_show_plan)
        show_parser.add_argument('-j', '--json', dest="raw",
                                 action="store_true",
                                 help='Output raw JSON response from server')
        show_parser.add_argument(
            '-a', '--active', dest="active_only",
            action="store_true",
            help='Limit output to active tasks only')

    def _setup_run_plan_parser(self, subparsers):
        run_parser = subparsers.add_parser(
            'run_plan',
            help="Executes the tasks in a plan to deploy the"
            " deployment model.",
            description=("Executes the tasks in a plan to deploy the"
                         " deployment model."),
            epilog="Example: litp run_plan")

        run_parser.set_defaults(func=self.object_run_plan)
        run_parser.add_argument('-j', '--json', dest="raw",
                                action="store_true",
                                help='Output raw JSON response from server')
        run_parser.add_argument('--resume', dest="resume",
                                action="store_true",
                                help='Resume failed plan')

    def _setup_stop_plan_parser(self, subparsers):
        stop_parser = subparsers.add_parser(
            'stop_plan',
            help="Stops the plan execution.",
            description="Stops the plan execution.",
            epilog="Example: litp stop_plan")

        stop_parser.set_defaults(func=self.object_stop_plan)
        stop_parser.add_argument('-j', '--json', dest="raw",
                                 action="store_true",
                                 help='Output raw JSON response from server')

    def _setup_required_group(self, owning_parser, args, validator=None):
        required_group = owning_parser.add_argument_group("Required Arguments")
        if 'type' in args:
            required_group.add_argument('-t', '--type', dest='type',
                                        action=TypeAction, required="True",
                                        help='Type of item to create')
        if 'path' in args:
            required_group.add_argument(
                '-p', '--path', dest="path", required="True",
                action=PathAction,
                type=validator,
                help='Location of item in the LITP model')

        if 'options' in args and 'delete' in args:
            group = owning_parser.add_argument_group()
            group.add_argument(
                '-o', '--options', dest='properties',
                metavar="PROPERTIES",
                action=UpdateAction,
                nargs="+", type=validate_opts,
                help='Properties to update in item')
            group.add_argument(
                '-d', '--delete', metavar="PROPERTIES",
                dest='delete_properties',
                nargs="+", action=DeleteAction,
                help='Properties to delete in item')

        elif 'options' in args:
            required_group.add_argument(
                '-o', '--options', dest='properties',
                required=True, action="append",
                nargs="+", type=validate_opts,
                help='Properties to update in item')

    def _setup_upgrade_parser(self, subparsers):
        upgrade_parser = subparsers.add_parser(
            'upgrade',
            help=("Updates the packages on a defined node or cluster to"
                  " a new version."),
            description=("Updates the packages on a defined node or"
                         " cluster to a new version."),
            epilog=("Example: litp upgrade -p "
                    "/deployments/deployment1/clusters/cluster1/nodes/n1"))

        self._setup_required_group(upgrade_parser, ['path'],
                                   valid_path)
        upgrade_parser.set_defaults(func=self.object_upgrade)
        upgrade_parser.add_argument('-j', '--json', dest="raw",
                                    action="store_true",
                            help='Output raw JSON response from server')

    def _setup_prepare_restore_parser(self, subparsers):
        prepare_restore_parser = subparsers.add_parser(
            'prepare_restore',
            formatter_class=RawDescriptionHelpFormatter,
            help=("Prepares the full deployment model and management server "
                  "or a single node for restore in the event of a "
                  "disaster scenario."),
            description=(
                "Prepares the full model and management server or a single "
                "node for restore in the event of a disaster scenario."
                "\n\n"
                "After prepare_restore, a plan can be created and"
                " run to reinstall the deployment or node."),
            epilog=("Examples:\nlitp prepare_restore\n"
                    "litp prepare_restore -p "
                    "/deployments/deployment1/clusters/cluster1/nodes/node1"))

        prepare_restore_parser.set_defaults(
            func=self.object_prepare_restore)
        prepare_restore_parser.add_argument('-j', '--json', dest="raw",
                                               action="store_true",
                                               help='Output raw JSON response\
                                                from server')
        prepare_restore_parser.add_argument(
            '-p', '--path', dest="path",
            action=PathAction,
            type=valid_path,
            help='Location of node item in the LITP model')
        prepare_restore_parser.add_argument(
            '-f', '--force-remove-snapshot', dest="force_remove_snapshot",
            action="store_true",
            help=("Force remove snapshot to ignore unreachable nodes"))

    def _setup_restore_model_parser(self, subparsers):
        restore_model_parser = subparsers.add_parser(
            'restore_model',
            help=("Restores the deployment model to the last successfully"
                  " completed plan state."),
            description=("Restores the deployment model to the last"
                         " successfully completed plan state."),
            epilog="Example: litp restore_model")

        restore_model_parser.set_defaults(func=self.object_restore_model)
        restore_model_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_create_parser(self, subparsers):
        create_parser = subparsers.add_parser(
            'create',
            help=("Adds a new instance of the specified item to the"
                  " deployment model."),
            description=("Adds a new instance of the specified item to the"
                         " deployment model."),
            epilog=("Example: litp create -t node "
                "-p /deployments/deployment1/clusters/cluster1/nodes/n1 "
                "-o hostname=node1"))

        self._setup_required_group(create_parser, ['type', 'path'],
                                   valid_path)
        create_parser.set_defaults(func=self.object_create)
        create_parser.add_argument(
            '-o', '--options', dest='properties', action="append",
            nargs="+", type=validate_opts, help='Properties to create in item')
        create_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_show_parser(self, subparsers):
        show_parser = subparsers.add_parser(
            'show',
            formatter_class=RawDescriptionHelpFormatter,
            help="Displays the item(s) located at the given path.",
            description=(
                "Displays the item(s) located at the given path."
                "\n\n"
                "If no display options are specified, the results"
                " are summarised and limited to items at the path"
                " location."),
            epilog="Example: litp show -p /deployments -l")

        show_parser.set_defaults(func=self.object_show)

        self._setup_required_group(show_parser, ['path'], valid_path)
        group = show_parser.add_mutually_exclusive_group()
        group.add_argument(
            '-l', '--list', dest="long",
            action="store_true",
            help='List items at given path')

        group.add_argument(
            '-L', '--completion', dest="completion",
            action="store_true",
            help=argparse.SUPPRESS)

        group.add_argument(
            '-T', '--tree', dest="tree",
            action="store_true",
            help='List items at given path as a hierarchical tree')
        group.add_argument('-o', '--options', dest='property',
                                 action=PropertyAction,
                                 help='Specific property to display')
        show_parser.add_argument('-j', '--json', dest="raw",
                                 action="store_true",
                                 help='Output raw JSON response from server')
        show_parser.add_argument(
            '-r', '--recursive', dest="recursive",
            action="store_true",
            help="Request children of item specified by path recursively")
        show_parser.add_argument(
            '-n', '--depth', dest="depth",
            action=DepthAction,
            type=valid_depth, help='Limit the depth of recursion')

    def _setup_update_parser(self, subparsers):
        update_parser = subparsers.add_parser(
            'update',
            help="Updates the properties of an item.",
            description=("Updates the properties of an item."),
            epilog=("Example: litp update -p /infrastructure/networking"
                    "/networks/mgmt -o name=new_network"))

        update_parser.set_defaults(func=self.object_update)

        self._setup_required_group(update_parser,
                                   ['path', 'options', 'delete'],
                                   valid_path)
        update_parser.add_argument('-j', '--json', dest="raw",
                                   action="store_true",
                                   help='Output raw JSON response from server')

    def _setup_remove_parser(self, subparsers):
        delete_parser = subparsers.add_parser(
            'remove',
            help=("Removes the specified item and its children from the"
                  " deployment model."),
            description=("Removes the specified item and its children from the"
                         " deployment model."),
            epilog=("Example: litp remove -p "
                    "/deployments/deployment1/clusters/cluster1"))
        required_group = delete_parser.add_argument_group("Required Arguments")
        delete_parser.set_defaults(func=self.object_remove)
        required_group.add_argument(
            '-p', '--path', dest="path", type=valid_path,
            action=PathAction,
            required="True",
            help=self.path_help)
        delete_parser.add_argument(
            '-j', '--json', dest="raw", action="store_true",
            help='Output raw JSON response from server')

    def _setup_inherit_parser(self, subparsers):
        inherit_parser = subparsers.add_parser(
            'inherit',
            help=("Creates a new path in the deployment model which inherits"
                  " property values from the source path."),
            description=("Creates a new path in the deployment model which"
                         " inherits property values from the source path."),
            epilog=("Example: litp inherit -p /deployments/deployment1/"
                    "clusters/cluster1/nodes/node1/storage_profile -s"
                    " /infrastructure/storage/storage_profiles/profile1")
        )
        inherit_parser.set_defaults(func=self.object_inherit)
        required_group = inherit_parser.add_argument_group(
            "Required Arguments"
        )
        required_group.add_argument(
            '-p', '--path', dest='path', required="True",
            action=PathAction, type=valid_create_path,
            help="Location of inherit path in the LITP model"
        )
        required_group.add_argument(
            '-s', '--source-path', dest='source_path', required="True",
            type=valid_create_path,
            help="Location of source item in the LITP model"
        )

        inherit_parser.add_argument(
            '-o', '--options', dest='properties',
            action="append", nargs="*", type=validate_opts,
            help='Properties to override'
        )
        inherit_parser.add_argument(
            '-j', '--json', dest="raw", action="store_true",
            help='Output raw JSON response from server')

    def _setup_load_parser(self, subparsers):
        load_parser = subparsers.add_parser(
            'load',
            help=("Loads the deployment model from a local XML file."),
            description=("Loads the deployment model from a local XML file."),
            epilog=("Example: litp load -p /infrastructure/networking/networks"
                    " -f networks.xml"))
        load_parser.set_defaults(func=self.object_load)
        required_group = load_parser.add_argument_group("Required Arguments")
        required_group.add_argument(
            '-p', '--path', dest="path", type=valid_path, action=PathAction,
            required="True", help=self.path_help)
        required_group.add_argument('-f', '--file', dest="file",
                                 required="True", action=FileAction,
                                 help="XML file to load")

        group = load_parser.add_mutually_exclusive_group()
        group.add_argument('--merge', dest="merge",
                           action="store_true",
                           help=("Merge XML file into deployment model,"
                                 "creating items which do not exist and"
                                 " updating model values with values"
                                 " from the file"))

        group.add_argument('--replace', dest="replace",
                           action="store_true",
                           help=("Recreate the active model with contents of"
                                 " the specified XML file, removing items"
                                 " not present in the file"))

        load_parser.add_argument('-j', '--json', dest="raw",
                                 action="store_true",
                                 help='Output raw JSON response from server')

    def _setup_export_parser(self, subparsers):
        export_parser = subparsers.add_parser(
            'export',
            help='Exports the deployment model to a local XML file.',
            description="Exports the deployment model to a local XML file.",
            epilog="Example: litp export -p /deployments/dep1 -f dep1.xml")
        required_group = export_parser.add_argument_group("Required Arguments")
        required_group.add_argument(
            '-p', '--path', dest="path", type=valid_path, action=PathAction,
            required="True",
            help=self.path_help)

        export_parser.set_defaults(func=self.object_export_xml)
        export_parser.add_argument('-f', '--file', dest="file",
                                   action=FileAction,
                                   help="XML file to which to export")

    def _setup_debug_parser(self, subparsers):
        '''deprecated - use litp update -p /litp/logging\
         -o force_debug=true instead '''
        debug_parser = subparsers.add_parser(
            "debug",
            help=("This command is now deprecated; to set the trace logging"
                  " level to 'debug', use litp update -p /litp/logging -o"
                  " force_debug=true instead."),
            description=(
                "This command is now deprecated; to set the trace logging"
                " level to 'debug', use litp update -p /litp/logging -o"
                " force_debug=true instead."))
        debug_parser.set_defaults(func=self.object_debug)
        debug_parser.add_argument("-o", "--option", type=str,
                                  choices=("override", "normal"),
                                  dest="properties",
                                  required=True, help="setting")
        debug_parser.add_argument(
            "-j", "--json", dest="raw", action="store_true",
            help="Output raw JSON response from server")

    def _setup_version_parser(self, subparsers):
        version_parser = subparsers.add_parser(
            "version",
            formatter_class=RawDescriptionHelpFormatter,
            help="Displays the ERIClitpcore version of LITP.",
            description=(
                "Displays the ERIClitpcore version of LITP."
                "\n\n"
                "If the --all option is specified, the name, version and"
                " packager of all installed LITP packages are also"
                " displayed."),
            epilog=textwrap.dedent('''\
                Examples:

                litp version

                litp version --all'''))
        version_parser.set_defaults(func=self.object_version)
        version_parser.add_argument("-a", "--all", dest="all",
                                    action="store_true",
                                    help="Display installed LITP packages")

    def _get_unix_socket_path(self):
        unix_socket_path = None
        filename = os.path.expanduser(LITPRC_FILENAME)
        parser = SafeConfigParser()
        try:
            parser.read(filename)
        except MissingSectionHeaderError:
            pass
        else:
            for section in parser.sections():
                if unix_socket_path is None:
                    try:
                        unix_socket_path = parser.get(section,
                                                      'unix_socket_path')
                    except NoOptionError:
                        pass
        return unix_socket_path or UNIX_SOCKET

    def _get_connection(self):
        if self.args.username is not None and self.args.password is not None:
            self.conn_type = HTTPS
        else:
            unix_socket_path = self._get_unix_socket_path()
            socket_file, self.conn_type = self._choose_connection(
                unix_socket_path)
        if self.conn_type == HTTPS:
            if getattr(self.args, 'url', None) is not None:
                self.base_url = self.args.url
                url_parsed = urlparse.urlparse(self.args.url)
                return self._create_https_connection(url_parsed.netloc)
            else:
                return self._create_https_connection(
                    "".join((DEFAULT_HOST, ':', DEFAULT_PORT)))
        else:
            return self._create_unix_connection(socket_file)

    def run_command(self, args):
        """
        Run the command specified by args in the form of sys.argv
        :param args: list of arguments, typically the contents of sys.argv
        :type args: list
        """
        self.args = self.parser.parse_args(args)
        self.conn = self._get_connection()

        if getattr(self.args, 'path', None) is not None:
            if self.args.path.endswith('/') and len(self.args.path) > 1:
                self.args.path = self.args.path[0:-1]
        self.formatter = CliFormatter(self.base_url, self.args.__dict__)
        return self.args.func()

    def _create_http_connection(self, host):
        return httplib.HTTPConnection(host)

    def _choose_connection(self, path):
        use_socket = (path and  # configuration provides path and allows socket
                      os.path.exists(path) and  # socket exists in FS
                      stat.S_ISSOCK(os.stat(path).st_mode))  # socket is socket
        if use_socket:
            return path, UNIX
        else:
            return None, HTTPS

    def _create_unix_connection(self, socket_file):
        conn = UnixSocketConnection(socket_file)
        return conn

    def _create_https_connection(self, host):
        conn = httplib.HTTPSConnection(host,
                                   context=ssl._create_unverified_context())
        return conn

    def wrapped_run_command(self, args):
        try:
            asciitxt(args)
        except argparse.ArgumentTypeError, e:
            self._print_err("\n".join(e.args))
            return 1

        try:
            return self.run_command(args)
        except (TypeError, AttributeError, argparse.ArgumentError) as ex:
            self._print_err("Error parsing arguments: %s" % (ex))
            return 1
        except AuthenticationException as ex:
            self._print_err(str(ex))
            return 1

    def _print_out(self, msg):
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()

    def _print_err(self, msg):
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()

    def _get_auth_headers(self, unix=False):
        """
        adds an Authorization header to the request, encoding both user and
        password (in plain text *sigh*) in base64
        """
        if unix:
            username = pwd.getpwuid(os.getuid()).pw_name
            password = ''
        else:
            username, password =\
                self.get_user_passwd(self.get_option("username"),
                                     self.get_option("password"))

            self.set_option("username", username)
            self.set_option("password", password)
        val = base64.encodestring(
            "{0}:{1}".format(username, password)).replace('\n', '')
        return {"Authorization": "Basic {0}".format(val)}

    def _request(self, url, method=None, data=None, format_func=None,
                 content_type=None):
        base_url = REST_URL
        if XML_URL in url:
            base_url = XML_URL
        if UPGRADE_URL in url:
            base_url = UPGRADE_URL

        self.formatter.url = base_url

        if format_func is None:
            format_func = self.formatter.cb_format_create_or_update

        if method is None:
            method = 'GET'

        return self._process_request(
            url, method, data, format_func, content_type)

    def get_readable_traceback(self):
        """
        Helper function to return the traceback as a string
        """
        return '\n'.join(traceback.format_exception(*(sys.exc_info())))

    def _execute_request(self, url, method, data, content_type):
        is_unix = self.conn_type == UNIX
        headers = self._get_auth_headers(is_unix)
        if content_type is None:
            content_type = "application/json"
        headers.update({"Content-Type": content_type})
        body = None
        if method in ('POST', 'PUT'):
            if isinstance(data, str):
                body = data
            else:
                body = json.dumps(data)
            headers.update({'Content-Length': len(body)})
        try:
            err = ''
            self.conn.request(method, url, body, headers)
            result = self.conn.getresponse()
        except socket.error:
            result, err = None, self.get_readable_traceback()
        except socket.gaierror:
            result, err = None, self.get_readable_traceback()
        except Exception:
            result, err = None, self.get_readable_traceback()
        return result, err

    def _process_request(self, url, method, data, format_func, content_type):
        response, err = self._execute_request(url, method, data, content_type)
        if err:
            self._print_err(LITP_SERVICE_ERR)
            return 1
        result = response.read()
        self.errors = []
        if response.status not in (200, 201, 202, 205):
            self._print_request_error_msg(result, response.status)
            retcode = 1
        else:
            retcode = self._print_request_ok_msg(result, format_func)
        return retcode

    def _print_request_error_msg(self, result, response_status):
        if response_status == 401:
            result = CREDENTIALS_ERR
        if self.get_option('raw'):
            result = json.dumps(json.loads(result), indent=4)
            self._print_err(result)
        elif response_status == 401:
            self.errors.append(CREDENTIALS_ERR)
            self._print_err(self.errors[0])
        else:
            errstr = self.formatter.cb_format_error(result)
            self.errors.append(errstr)
            if len(errstr) < 1:
                errstr = "Item " + self.args.path + " not found"
            self._print_err(errstr)

    def _print_request_ok_msg(self, result, format_func):
        retcode = 0
        if self.get_option('recursive'):
            item, self.errors = self._recursive_get(
                json.loads(result), errors=self.errors)
            result = json.dumps(item, indent=4)
        if self.get_option('raw'):
            self._print_out(json.dumps(json.loads(result), indent=4))
            if self.errors:
                self._print_err(json.dumps(self.errors, indent=4))
                retcode = 1
        else:
            formatted_output = format_func(
                result, recursive=self.get_option('recursive'))
            retcode = 0
            if formatted_output:
                if "InvalidPropertyError" in formatted_output:
                    self._print_err(formatted_output)
                    sys.stderr.flush()
                    retcode = 1
                else:
                    self._print_out(formatted_output.strip('\n'))
            formatted_errors = '\n' + '\n'.join(
                [self.formatter.cb_format_error(err) for err in
                    self.errors])
            if self.errors:
                self._print_err(formatted_errors)
                sys.stderr.flush()
                retcode = 1
        return retcode

    def get_option(self, option):
        if hasattr(self.args, option):
            return getattr(self.args, option)
        return False

    def set_option(self, option, value):
        if isinstance(self.args, list):
            self.args.append(option)
            self.args.append(value)
        else:
            setattr(self.args, option, value)

    def object_show(self):
        format_func = self.formatter.cb_format_show
        if self.get_option('long'):
            format_func = self.formatter.cb_format_path_list
        if self.get_option('completion'):
            format_func = self.formatter.cb_format_path_completion
        if self.get_option('tree'):
            format_func = self.formatter.cb_format_paths_as_tree
        url = self.base_url + self.args.path
        return self._request(url, format_func=format_func)

    def props_to_dict(self):
        data = {}
        opts = self.get_option('properties')
        if opts:
            if isinstance(opts, list):
                for l in opts:
                    data.update(p.split('=', 1) for p in l if '=' in p)
            else:
                data.update(p.split('=', 1).strip() for p in opts if '=' in p)
        # strip trailing and preceeding spaces on keys and values
        return dict((k.strip(), v.strip())
                    for k, v in data.items())

    def delete_props_to_dict(self):
        data = {}
        opts = self.get_option('delete_properties')
        if opts:
            if isinstance(opts, list):
                for l in opts:
                    if ',' in l:
                        for token in l.split(','):
                            data.update({token.strip(): None})
                    else:
                        data.update({l: None})
            else:
                data.update(p.split(',', 1).strip() for p in opts if '=' in p)
        # strip trailing and preceeding spaces on keys and values
        return dict((k.strip().rstrip(','), v.strip().rstrip(','))
                    if v is not None else (k.strip().rstrip(','), None)
                    for k, v in data.items())

    def object_upgrade(self):
        data = {'path': self.args.path, 'hash': md5(str(time())).hexdigest()}
        return self._request(url=UPGRADE_URL, method='POST', data=data)

    def object_prepare_restore(self):
        path = self.get_option("path")
        if not path:
            path = "/"
        data = {
            "properties": {
                'path': path,
                'actions': 'all',
                'force_remove_snapshot': self.args.force_remove_snapshot
            }
        }
        url = self.base_url + '/litp/prepare-restore'
        return self._request(url, method='PUT', data=data)

    def object_restore_model(self):
        data = {'properties': {'update_trigger': 'yes'}}
        return self._request(url=RESTORE_URL, method='PUT', data=data)

    def object_create(self):
        try:
            if self.args.path.startswith(CONFIG_PATH):
                path = self.args.path
                item = None
            elif self.args.path.startswith(SNAPSHOT_PATH):
                path = self.args.path
                item = self.args.path.rsplit("/", 1)
            else:
                path, item = self.args.path.rsplit("/", 1)
        except ValueError:
            path = self.args.path
            item = None
        data = {'id': item}
        data['type'] = self.args.type

        property_data = {'properties': self.props_to_dict()}
        data.update(property_data)

        url = self.base_url + path
        return self._request(url, method='POST', data=data)

    def object_inherit(self):
        try:
            path, item = self.args.path.rsplit("/", 1)
        except ValueError:
            path = self.args.path
            item = None

        data = {'inherit': self.args.source_path, 'id': item}
        data.update({'properties': self.props_to_dict()})

        url = self.base_url + path
        return self._request(url, method='POST', data=data)

    def object_update(self):
        data = {}
        properties = {}
        properties.update(self.props_to_dict())
        if self.args.delete_properties:
            properties.update(self.delete_props_to_dict())
        data.update({'properties': properties})
        url = self.base_url + self.args.path
        return self._request(url, method='PUT', data=data)

    def object_remove(self):
        path = self.base_url + self.args.path
        return self._request(path, method='DELETE')

    def object_load(self):
        self.formatter = CliFormatter(self.xml_url, self.args.__dict__)
        url = self.xml_url + self.args.path
        if self.get_option("merge"):
            url += "?merge=true"
        elif self.get_option("replace"):
            url += "?replace=true"
        try:
            data = self._load_file(self.args.file)
        except IOError as e:
            self._print_err(str(e))
            return 1
        return self._request(url, method='POST',
                             content_type="application/xml",
                             data=data)

    def _load_file(self, filepath):
        return open(filepath).read()

    def object_show_plan(self):
        url = self.base_url + "/plans/plan?recurse_depth=1000"
        return self._request(
            url,
            format_func=self.formatter.cb_format_show_plan)

    def object_create_plan(self):
        data = {
            'id': 'plan',
            'type': 'plan'
        }
        if self.args.no_lock_tasks != None:
            data['no-lock-tasks'] = 'True'
            if len(self.args.no_lock_tasks) != 0:
                data['no-lock-tasks-list'] = self.args.no_lock_tasks
        if self.args.initial_lock_tasks != None:
            data['initial-lock-tasks'] = 'True'

        url = self.base_url + '/plans'
        return self._request(url, method='POST', data=data)

    def object_create_snapshot(self):
        data = {
            'type': 'snapshot-base',
        }
        exclude_nodes = ''
        if self.args.exclude_nodes:
            exclude_nodes = '?exclude_nodes=' + self.args.exclude_nodes
        name = self.args.name or 'snapshot'
        url = self.base_url + '/snapshots/{0}/{1}'.format(name, exclude_nodes)
        return self._request(url, method='POST', data=data)

    def object_create_reboot_plan(self):
        data = {
            'id': 'plan',
            'type': 'reboot_plan',
        }
        if self.args.path:
            data['path'] = self.args.path
        url = self.base_url + '/plans/'
        return self._request(url, method='POST', data=data)

    def object_remove_snapshot(self):
        if self.args.name:
            name = self.args.name
        else:
            name = 'snapshot'
        exclude_nodes = ''
        if self.args.exclude_nodes:
            exclude_nodes = '?exclude_nodes=' + self.args.exclude_nodes
        url = self.base_url + "/snapshots/{0}/{1}".format(name, exclude_nodes)
        data = {'properties': {
                    'force': self.args.force,
                    'action': 'remove'
                    }
                }
        return self._request(url, method='PUT', data=data)

    def object_restore_snapshot(self):
        data = {'properties': {
                    'force': self.args.force,
                    }
                }
        name = 'snapshot'
        url = self.base_url + '/snapshots/{0}'.format(name)
        return self._request(url, method='PUT', data=data)

    def object_import(self):
        url = self.base_url + '/import'

        if not self.get_option("source_path") or \
           not self.get_option("destination_path"):
            sys.stderr.write(str("source_path and desination_path arg are "
                                 "required for software import\n"))
        else:
            data = {
                'source_path': self.get_option("source_path"),
                'destination_path': self.get_option("destination_path")
            }
            return self._request(url, method='PUT', data=data)

    def object_import_iso(self):
        url = self.base_url + '/litp/import-iso'

        if not self.get_option("source_path"):
            sys.stderr.write(str("source_path arg is "
                                 "required for software import\n"))
        else:
            data = {
                'properties': {
                    'source_path': self.get_option("source_path"),
                }
            }
            return self._request(url, method='PUT', data=data)

    def object_remove_plan(self):
        path = self.base_url + '/plans/plan'
        return self._request(path, method='DELETE')

    def object_debug(self):
        path = self.base_url + '/litp/logging'
        if self.args.properties == "override":
            force_debug = "true"
        else:
            force_debug = "false"
        self._print_out("This command is deprecated. Use 'litp update -p "
            "/litp/logging -o force_debug=%s' instead" % (force_debug))
        return self._request(path, method="PUT",
                             data={"properties": {"force_debug": force_debug}})

    def object_version(self):
        url = self.base_url
        format_func = self.formatter.cb_format_version
        return self._request(url, format_func=format_func)

    def object_run_plan(self):
        url = self.base_url + "/plans/plan"
        plan_properties = {"properties": {"state": "running"}}
        if self.args.resume:
            plan_properties["properties"]["resume"] = "true"

        return self._request(url, method='PUT', data=plan_properties)

    def object_stop_plan(self):
        url = self.base_url + "/plans/plan"
        return self._request(
            url, method='PUT', data={"properties": {"state": "stopped"}})

    def object_export_xml(self):
        format_func = None
        if self.get_option("file"):
            def cb_format_xml_file(data, recursive=False):
                try:
                    with open(self.args.file, 'w') as fobj:
                        fobj.write(data)
                except IOError as ex:
                    self._print_err(str(ex))
                    sys.exit(1)
            format_func = cb_format_xml_file
        url = self.xml_url + self.args.path
        return self._request(url, format_func=format_func,
            content_type="application/xml")

    def get_user_passwd(self, username, password):
        '''
        Returns a list with the user and the password or raises an exception
        if something bad happens.
        '''
        if username and password:
            return username, password
        elif not (username or password):
            # Try to read litprc file
            try:
                litprc = os.path.expanduser(LITPRC_FILENAME)
                if self._can_get_credentials_from_file(litprc):
                    return self._get_user_passwd_from_file(litprc)
                return self._get_user_passwd_from_prompt(True)
            except OSError as e:
                raise Exception(str(e))
        if username and not password:
            # Prompt for password
            return username, self._get_user_passwd_from_prompt(False)[1]
        elif password and not username:
            # Get login
            raise AttributeError("Must supply username when password is\
 given")

    def _can_get_credentials_from_file(self, litprc):
        ''' file needs to exist and have 600 permissions
        @param litprc: full path to the litprc file
        '''
        if not os.path.exists(litprc):
            self._print_err(AUTH_ERR)
            return False
        if not oct(os.stat(litprc).st_mode)[-3:] == "600":
            self._print_err(AUTH_ERR)
            return False
        return True

    def _get_user_passwd_from_prompt(self, prompt_username=False):
        username = ""
        if prompt_username:
            sys.stdin = open('/dev/tty')
            username = raw_input("Username: ")
            if not username:
                raise AttributeError("Username cannot be blank")
        password = getpass.getpass()
        if not password:
            raise AttributeError("Password cannot be blank")
        self.set_option("password", password)
        return username, password

    def _get_user_passwd_from_file(self, filename):
        ''' expected file structure:
        [this_is_a_section]
        option1 = val
        option2 = another_val
        '''
        def read_option(which):
            try:
                return parser.get(section, which)
            except NoOptionError:
                raise Exception(AUTH_ERR)

        parser = SafeConfigParser()
        parser.read(filename)
        expected_options = ['username', 'password']
        if not parser.sections():
            raise AuthenticationException(CREDENTIALS_ERR)
        section = parser.sections()[0]
        options_in_file = parser.options(section)
        if not options_in_file:
            raise Exception(CREDENTIALS_ERR)
        return [read_option(option) for option in expected_options]


def asciitxt(values):
    """Validates if elements of the iterable 'value' are of type ascii."""
    try:
        if isinstance(values, list):
            values = [value.decode('ascii') for value in values]
        elif isinstance(values, basestring):
            values = values.decode('ascii')
#        map((lambda s: s.decode('ascii')), values)
    except UnicodeDecodeError:
        raise argparse.ArgumentTypeError(
            "LITP CLI arguments must be of type ascii.")
    return values

if __name__ == "__main__":
    exit(LitpCli().wrapped_run_command(sys.argv[1:]))
