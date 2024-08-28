litp_help = """Usage: litp [-h] [-u USERNAME] [-P PASSWORD]  ...

LITP Command Line

Optional Arguments:
  -h, --help            Show this help message and exit
  -u USERNAME, --username USERNAME
                        Username to connect to LITP service
  -P PASSWORD, --password PASSWORD
                        Password to connect to LITP service

Actions:
  Actions that can be performed on the specified item at the given path. For
  more information on an action, enter the command 'litp <action> -h'.


    create              Adds a new instance of the specified item to the
                        deployment model.
    create_plan         Creates a set of tasks (a plan) used to deploy the
                        deployment model.
    create_snapshot     Creates and executes a set of tasks (a plan) used to
                        create file system snapshots.
    create_reboot_plan  Create a plan to lock, reboot and unlock a single
                        deployed node or all deployed nodes.
    debug               This command is now deprecated; to set the trace
                        logging level to 'debug', use litp update -p
                        /litp/logging -o force_debug=true instead.
    export              Exports the deployment model to a local XML file.
    import              Imports packages into Yum repositories.
    import_iso          Imports packages and VM images from a LITP-compliant
                        ISO, then installs/upgrades management server
                        software.
    inherit             Creates a new path in the deployment model which
                        inherits property values from the source path.
    load                Loads the deployment model from a local XML file.
    prepare_restore     Prepares the full deployment model and management
                        server or a single node for restore in the event of a
                        disaster scenario.
    remove              Removes the specified item and its children from the
                        deployment model.
    remove_plan         Removes the plan from the model.
    remove_snapshot     Creates and executes a set of tasks (a plan) that is
                        used to remove file system snapshots.
    restore_snapshot    Creates and executes a set of tasks (a plan) that is
                        used to restore file system snapshots.
    restore_model       Restores the deployment model to the last successfully
                        completed plan state.
    run_plan            Executes the tasks in a plan to deploy the deployment
                        model.
    show                Displays the item(s) located at the given path.
    show_plan           Displays the status of tasks initiated by the
                        create_plan command or executed by the run_plan
                        command. The tasks are executed in phases determined
                        by the create_plan command.
    stop_plan           Stops the plan execution.
    update              Updates the properties of an item.
    upgrade             Updates the packages on a defined node or cluster to a
                        new version.
    version             Displays the ERIClitpcore version of LITP.
"""

litp_remove_snapshot_help = ['Usage: litp remove_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j] [-f]',
                             '',
                             'Creates and executes a set of tasks (a plan)'
                             ' that is used to remove file',
                             'system snapshots.',
                             '',
                             'Optional Arguments:', '  -h, --help'
                             '            Show this help message and exit',
                             '  -j, --json            Output raw JSON response from server',
                             '  -f, --force           Force remove to ignore unreachable LVM nodes',
                             '',
                             '  -n NAME, --name NAME  Optional snapshot name',
                             '  -e EXCLUDE_NODES, --exclude_nodes EXCLUDE_NODES',
                             '                        Comma separated list of excluded nodes by hostname.',
                             '                        Use only with --name',
                            '', 'Example: litp remove_snapshot', '']
litp_create_snapshot_help = ['Usage: litp create_snapshot [-h] [-n NAME [-e EXCLUDE_NODES]] [-j]',
                             '',
                             'Creates and executes a set of tasks (a plan)'
                             ' used to create file system',
                             'snapshots.',
                             '', 'Optional Arguments:',
                             '  -h, --help            Show this help message and exit',
                             '  -j, --json            Output raw JSON response from server',
                             '',
                             '  -n NAME, --name NAME  Optional snapshot name',
                             '  -e EXCLUDE_NODES, --exclude_nodes EXCLUDE_NODES',
                             '                        Comma separated list of excluded nodes by hostname.',
                             '                        Use only with --name',
                             '', 'Example: litp create_snapshot', '']

litp_create_help = ['Usage: litp create [-h] -t TYPE -p PATH [-o PROPERTIES [PROPERTIES ...]] [-j]',
 '',
 'Adds a new instance of the specified item to the deployment model.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -o PROPERTIES [PROPERTIES ...], --options PROPERTIES [PROPERTIES ...]',
 '                        Properties to create in item',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -t TYPE, --type TYPE  Type of item to create',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 'Example: litp create -t node -p',
 '/deployments/deployment1/clusters/cluster1/nodes/n1 -o hostname=node1',
 '']


litp_create_plan_help = ['Usage: litp create_plan [-h] [-j] [--no-lock-tasks [[...]]]',
 '                        [--initial-lock-tasks]',
 '',
 'Creates a set of tasks (a plan) used to deploy the deployment model.',
 '', 'Optional Arguments:',
'  -h, --help            Show this help message and exit',
'  -j, --json            Output raw JSON response from server',
 '  --no-lock-tasks [ [ ...]]',
 '                        Do not generate lock or unlock tasks for all clusters',
 '                        or specify cluster(s) to have no lock or unlock tasks.',
 '  --initial-lock-tasks  Generate lock and unlock tasks for nodes in Initial',
 '                        state.',
 '',
 'Examples:',
 '',
 'litp create_plan',
 '',
 'litp create_plan --no-lock-tasks',
 '',
 'litp create_plan --no-lock-tasks c1 c2',
 '',
 'litp create_plan --initial-lock-tasks',
 '']

litp_export_help = ['Usage: litp export [-h] -p PATH [-f FILE]',
 '',
 'Exports the deployment model to a local XML file.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -f FILE, --file FILE  XML file to which to export',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 'Example: litp export -p /deployments/dep1 -f dep1.xml',
 '']

litp_import_help = ['Usage: litp import [-h] [-j] source_path destination_path',
 '',
 'Imports packages into Yum repositories.',
 '',
 'Optional Arguments:',
 '  -h, --help        Show this help message and exit',
 '  -j, --json        Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  source_path       Absolute path with rpm packages. This can be a single RPM',
 '                    or a directory of RPMs.',
 '  destination_path  Absolute path to destination repo directory or one of',
 '                    "litp" or "3pp_rhel7" to import RPMs into the LITP or 3PP',
 '                    repo. This should be used for LITP RPMs only.',
 '',
 'Examples:',
 '',
 'litp import /mnt/rhel-iso /var/www/html/os',
 '',
 'litp import /root/libyaml-0.1.3-1.el7.x86_64.rpm /var/www/html/3pp_rhel7/',
 '']

litp_import_iso_help = ['Usage: litp import_iso [-h] [-j] source_path',
 '',
 'Imports packages and VM images from a LITP-compliant ISO, then',
 'installs/upgrades management server software.',
 '',
 'It may also install new packages from the LITP or LITP_PLUGIN repositories and',
 'packages that are newly required by upgraded packages.',
 '',
 'Optional Arguments:',
 '  -h, --help   Show this help message and exit',
 '  -j, --json   Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  source_path  Absolute path of mounted ISO. This should be a LITP-compliant',
 '               directory tree.',
 '',
 'Example: litp import_iso /mnt/my-iso',
 '']

litp_inherit_help = ['Usage: litp inherit [-h] -p PATH -s SOURCE_PATH',
 '                    [-o [PROPERTIES [PROPERTIES ...]]] [-j]',
 '',
 'Creates a new path in the deployment model which inherits property values from',
 'the source path.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -o [PROPERTIES [PROPERTIES ...]], --options [PROPERTIES [PROPERTIES ...]]',
 '                        Properties to override',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of inherit path in the LITP model',
 '  -s SOURCE_PATH, --source-path SOURCE_PATH',
 '                        Location of source item in the LITP model',
 '',
 'Example: litp inherit -p',
 '/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile -s',
 '/infrastructure/storage/storage_profiles/profile1',
 '']

litp_load_help = ['Usage: litp load [-h] -p PATH -f FILE [--merge | --replace] [-j]',
 '',
 'Loads the deployment model from a local XML file.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  --merge               Merge XML file into deployment model,creating items',
 '                        which do not exist and updating model values with',
 '                        values from the file',
 '  --replace             Recreate the active model with contents of the',
 '                        specified XML file, removing items not present in the',
 '                        file',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '  -f FILE, --file FILE  XML file to load',
 '',
 'Example: litp load -p /infrastructure/networking/networks -f networks.xml',
 '']

litp_prepare_restore_help = ['Usage: litp prepare_restore [-h] [-j] [-p PATH] [-f]',
 '',
 'Prepares the full model and management server or a single node for restore in',
 'the event of a disaster scenario.',
 '',
 'After prepare_restore, a plan can be created and run to reinstall the',
 'deployment or node.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -j, --json            Output raw JSON response from server',
 '  -p PATH, --path PATH  Location of node item in the LITP model',
 '  -f, --force-remove-snapshot',
 '                        Force remove snapshot to ignore unreachable nodes',
 '',
 'Examples:',
 'litp prepare_restore',
 'litp prepare_restore -p /deployments/deployment1/clusters/cluster1/nodes/node1',
 '']

litp_prepare_restore_missing_path = 'Usage: litp prepare_restore [-h] [-j] [-p PATH] [-f]\n' + \
'litp prepare_restore: error: argument -p/--path: expected one argument\n'

litp_prepare_restore_one_path = 'Usage: litp prepare_restore [-h] [-j] [-p PATH] [-f]\n' + \
'litp prepare_restore: error: Path may only be specified once\n'

litp_remove_help = ['Usage: litp remove [-h] -p PATH [-j]',
 '',
 'Removes the specified item and its children from the deployment model.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 'Example: litp remove -p /deployments/deployment1/clusters/cluster1',
 '']

litp_restore_snapshot_help = ['Usage: litp restore_snapshot [-h] [-j] [-f]',
 '',
 'Creates and executes a set of tasks (a plan) that is used to restore file',
 'system snapshots.',
 '',
 'Optional Arguments:',
 '  -h, --help   Show this help message and exit',
 '  -j, --json   Output raw JSON response from server',
 "  -f, --force  Force restore to ignore missing snapshots and unreachable nodes",
 '',
 'Example: litp restore_snapshot',
 '']

litp_restore_model_help = ['Usage: litp restore_model [-h] [-j]',
 '',
 'Restores the deployment model to the last successfully completed plan state.',
 '',
 'Optional Arguments:',
 '  -h, --help  Show this help message and exit',
 '  -j, --json  Output raw JSON response from server',
 '',
 'Example: litp restore_model',
 '']

litp_run_plan_help = ['Usage: litp run_plan [-h] [-j] [--resume]',
 '',
 'Executes the tasks in a plan to deploy the deployment model.',
 '',
 'Optional Arguments:',
 '  -h, --help  Show this help message and exit',
 '  -j, --json  Output raw JSON response from server',
 '  --resume    Resume failed plan',
 '',
 'Example: litp run_plan',
 '']

litp_show_help = ['Usage: litp show [-h] -p PATH [-l | -T | -o PROPERTY] [-j] [-r] [-n DEPTH]',
 '',
 'Displays the item(s) located at the given path.',
 '',
 'If no display options are specified, the results are summarised and limited to',
 'items at the path location.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -l, --list            List items at given path',
 '  -T, --tree            List items at given path as a hierarchical tree',
 '  -o PROPERTY, --options PROPERTY',
 '                        Specific property to display',
 '  -j, --json            Output raw JSON response from server',
 '  -r, --recursive       Request children of item specified by path recursively',
 '  -n DEPTH, --depth DEPTH',
 '                        Limit the depth of recursion',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 'Example: litp show -p /deployments -l',
 '']

litp_show_plan_help = ['Usage: litp show_plan [-h] [-j] [-a]',
 '',
 'Displays the status of tasks initiated by the create_plan command or executed',
 'by the run_plan command. The tasks are executed in phases determined by the',
 'create_plan command.',
 '',
 'Optional Arguments:',
 '  -h, --help    Show this help message and exit',
 '  -j, --json    Output raw JSON response from server',
 '  -a, --active  Limit output to active tasks only',
 '',
 'Example: litp show_plan',
 '']

litp_update_help = ['Usage: litp update [-h] -p PATH [-o PROPERTIES [PROPERTIES ...]]',
 '                   [-d PROPERTIES [PROPERTIES ...]] [-j]',
 '',
 'Updates the properties of an item.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 '  -o PROPERTIES [PROPERTIES ...], --options PROPERTIES [PROPERTIES ...]',
 '                        Properties to update in item',
 '  -d PROPERTIES [PROPERTIES ...], --delete PROPERTIES [PROPERTIES ...]',
 '                        Properties to delete in item',
 '',
 'Example: litp update -p /infrastructure/networking/networks/mgmt -o',
 'name=new_network',
 '']

litp_upgrade_help = ['Usage: litp upgrade [-h] -p PATH [-j]',
 '',
 'Updates the packages on a defined node or cluster to a new version.',
 '',
 'Optional Arguments:',
 '  -h, --help            Show this help message and exit',
 '  -j, --json            Output raw JSON response from server',
 '',
 'Required Arguments:',
 '  -p PATH, --path PATH  Location of item in the LITP model',
 '',
 'Example: litp upgrade -p /deployments/deployment1/clusters/cluster1/nodes/n1',
 '']

litp_version_help = ['Usage: litp version [-h] [-a]',
 '',
 'Displays the ERIClitpcore version of LITP.',
 '',
 'If the --all option is specified, the name, version and packager of all',
 'installed LITP packages are also displayed.',
 '',
 'Optional Arguments:',
 '  -h, --help  Show this help message and exit',
 '  -a, --all   Display installed LITP packages',
 '',
 'Examples:',
 '',
 'litp version',
 '',
 'litp version --all',
 '']
