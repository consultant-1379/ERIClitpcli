import argparse
import re
import sys

PATH_RE = r'^/([a-zA-Z\d_-]/?)*$'
SNAPSHOT_NAME_RE = r'^[a-zA-Z0-9_-]+$'
HOSTNAME_RE = r"([a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])"
EXCLUDE_NODES_RE = (r"^"
        r"("
        + HOSTNAME_RE +
        r",)*"
        + HOSTNAME_RE +
        r"$")


class TypeAction(argparse.Action):
    """
    Validate when issuing create or update that the type parameter has been
    specified on the command line
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        item_type = getattr(namespace, 'type', None)
        if item_type is not None:
            parser.error('Type may only be specified once')
        else:
            setattr(namespace, self.dest, values)


class PathAction(argparse.Action):
    """
    Validate when issuing create or update that the path parameter has been
    specified on the command line
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        path = getattr(namespace, 'path', None)
        if path is not None:
            parser.error('Path may only be specified once')
        else:
            setattr(namespace, self.dest, values)


class PropertyAction(argparse.Action):
    """
    Validate when issueing a show property command that the option parameter
    has been specified only once
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        path = getattr(namespace, 'property', None)
        if path is not None:
            parser.error('-o may only be specified once')
        else:
            setattr(namespace, self.dest, values)


class DeleteAction(argparse.Action):
    """
    Prevent updating and deleting same option in single command.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        delete_values = namespace.delete_properties or []
        for v in values:
            delete_values.extend(s.strip() for s in v.split(",")
                                 if len(s) > 0)
        conflicts = []
        if namespace.properties is not None:
            for properties in namespace.properties:
                for prop in properties:
                    clean = prop.split("=")[0]
                    if clean in delete_values:
                        conflicts.append(clean)

        if conflicts:
            msg = (
                "Updating and deleting %s in the same operation" %
               ', '.join(['"%s"' % prop for prop in conflicts])
            )
            parser.error(msg)

        setattr(namespace, self.dest, delete_values)


class UpdateAction(argparse._AppendAction):
    """
    Prevent updating and deleting same property in single command.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        super(UpdateAction, self).__call__(
            parser, namespace, values, option_string
        )

        conflicts = []
        delete_values = getattr(namespace, 'delete_properties') or []
        if namespace.properties is not None:
            for properties in namespace.properties:
                for prop in properties:
                    clean = prop.split("=")[0]
                    if clean in delete_values:
                        conflicts.append(clean)

        if conflicts:
            msg = (
                "Updating and deleting %s in the same operation" %
               ', '.join(['"%s"' % prop for prop in conflicts])
            )
            parser.error(msg)


class FileAction(argparse.Action):
    """
    Validate when issuing create or update that the type parameter has been
    specified on the command line
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        path = getattr(namespace, 'file', None)
        if path is not None:
            parser.error('File may only be specified once')
        else:
            setattr(namespace, self.dest, values)


class DepthAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        recursive = getattr(namespace, 'recursive', False)
        if not recursive and \
                not ('-r' in sys.argv or '--recursive' in sys.argv):
            parser.error("Depth may not be specified without recursive option")
        else:
            setattr(namespace, self.dest, values)


class ExcludeNodesAction(argparse.Action):
    """
    Validate --exclude_nodes is used with --name
    """
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        name = getattr(namespace, 'name', None)
        if name is None:
            parser.error('exclude_nodes may only be used with --name')
        else:
            setattr(namespace, self.dest, values)


class NoLockTasksAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        values = [orig.replace(',', '') for orig in values]
        values_set = set(values)
        if len(values_set) != len(values):
            parser.error('Duplicate clusters in the list provided')
        else:
            setattr(namespace, self.dest, values)


class InitialLockTasksAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Override argparse.Action's __call__ method
        """
        setattr(namespace, self.dest, values)


def valid_path(path_arg):
    if not re.match(PATH_RE, path_arg):
        msg = "%s is not a valid path argument" % path_arg
        raise argparse.ArgumentTypeError(msg)
    return path_arg


def valid_snapshot_name(name_arg):
    if not re.match(SNAPSHOT_NAME_RE, name_arg):
        msg = 'A Named Backup Snapshot "name" can only contain characters '\
              'in the range "[a-zA-Z0-9_-]"'
        raise argparse.ArgumentTypeError(msg)
    return name_arg


def valid_exclude_nodes(exclude_nodes_arg):
    if not re.match(EXCLUDE_NODES_RE, exclude_nodes_arg):
        msg = '"exclude_nodes" malformed. Valid format: {0}'.format(
                EXCLUDE_NODES_RE)
        raise argparse.ArgumentTypeError(msg)
    return exclude_nodes_arg


def valid_create_path(path_arg):
    if path_arg.endswith('/') and path_arg != '/':
        msg = "%s is not a valid path argument" % path_arg
        raise argparse.ArgumentTypeError(msg)
    return valid_path(path_arg)


def valid_depth(depth_arg):
    value = int(depth_arg)
    if value < 1:
        msg = "%s is not a valid depth argument" % depth_arg
        raise argparse.ArgumentTypeError(msg)
    return value


def validate_opts(opts):
    invalid_opts = []
    if isinstance(opts, list):
        for item in opts:
            invalid_opts.extend([prop for prop in item
                                 if '=' not in prop])
    else:
        if '=' not in opts:
            invalid_opts.append(opts)
    if invalid_opts:
        msg = "invalid option%s : %s" % (
            's' if len(invalid_opts) > 1 else '', invalid_opts)
        raise argparse.ArgumentTypeError(msg)
    return opts
