import json
import re
import textwrap


class CliFormatter(object):

    def __init__(self, url, args=None):
        self.url = url
        if not args:
            self.args = {}
        else:
            if not isinstance(args, dict):
                raise TypeError("args argument requires a dict")
            self.args = args

    def _get_option(self, option):
        if option in self.args:
            return self.args[option]
        return False

    @staticmethod
    def _get_children(data):
        children = []
        if data.get('_embedded'):
            children = data['_embedded'].get("item", [])
            children += data['_embedded'].get("item-type", [])
            children += data['_embedded'].get("property-type", [])
        return children

    def cb_format_show_plan(self, item, recursive=False, indent=4):
        plan_objects = self._get_plan(item, indent)
        plan_state = self._get_state(item)

        metrics = {
            'total': 0,
            'initial': 0,
            'running': 0,
            'success': 0,
            'failed': 0,
            'stopped': 0,
        }

        def indent_line(count=1, line='', indent_char=' '):
            return count * indent_char + str(line)

        def format_status_line(task):
            max_path_length = 50
            replacement = "..."

            if len(task['path']) <= max_path_length - len(replacement):
                replacement = ""
            state = task['state']
            tabs = "\t\t"
            path_str = replacement + task['path'][-max_path_length:]
            line = state + tabs + path_str
            return indent_line(1, line, '\t')

        def format_description(task):
            output_list = []
            if task['description']:
                task['description'] = "{0} {1}".format(
                    task['description'], '')
                for line in textwrap.wrap(task['description'], 53):
                    output_list.append(indent_line(3, line, '\t'))
            return '\n'.join(output_list)

        def format_task(task):
            return '\n'.join([format_status_line(task),
                              format_description(task)])

        plan = []
        for phase in plan_objects:
            task_list = []
            for task in phase:
                metrics['total'] += 1
                metrics[task['state'].lower()] += 1
                if not self._get_option("active_only") or \
                        'Running' in task['state']:
                    task_list.append(task)
            plan.append(task_list)

        out = []
        for phase_no, phase_tasks in enumerate(plan):
            if phase_tasks:
                out.append("Phase %d" % (phase_no + 1))
                out.append("\tTask status\n\t-----------")
            for task in phase_tasks:
                out.append(format_task(task))
            if phase_tasks:
                out.append("")

        out.append("Tasks: %(total)s | Initial: %(initial)s"
                   " | Running: %(running)s | Success: %(success)s"
                   " | Failed: %(failed)s | Stopped: %(stopped)s" % metrics)
        snapshot = self._deserialize_data(item)
        if snapshot.get('snapshot'):
            out.append(snapshot['snapshot'])
        out.append("Plan Status: %s" % plan_state.capitalize())

        return "\n".join(out)

    def _get_plan(self, item, indent=4):
        formatted_items = []
        self._get_plan_formatted(item, formatted_items, indent)
        return formatted_items

    def _get_state(self, item):
        data = item
        if not isinstance(item, dict):
            try:
                data = json.loads(item)
            except ValueError:
                data = {'properties': {'state': 'none'}}
        try:
            state = data['properties']['state']
        except ValueError:
            state = 'none'
        return state

    def _get_plan_formatted(self, item, formatted_items, indent=4):
        try:
            data = self._deserialize_data(item)
        except ValueError:
            return item
        dtype = data['item-type-name']
        if 'phase' == dtype:
            formatted_items.append([])
        elif 'task' == dtype:
            task = {
                "indent": indent * ' ',
                "id": data['id'],
                "path": data['_links']['rel']['href'].replace(self.url, ''),
                "description": data['description'],
                "state": data['state']
            }
            formatted_items[-1].append(task)
        children = self._get_children(data)
        for child in children:
            self._get_plan_formatted(child, formatted_items, indent)

    def cb_format_item_type(self, data, indent=4):
        ret = [data['_links']['self']['href'].replace(self.url, '')]
        if not self._get_option("long"):
            ret.append("%sdescription: %s" % ((indent * ' '),
                                    data['description']))

            children = self._get_children(data)
            if data.get('properties'):
                for prop_id, structure in data['properties'].items():
                    structure["id"] = prop_id
                    children.append(structure)

            if children:
                ret.append("%sfields:" % (indent * ' '))
                for field in children:
                    if 'collection-of' in field["_links"]:
                        ret.append(
                            "%sname: %s" % ((indent * 3 * ' '), field['id']))

                        coll_type_uri = \
                                    field['_links']['collection-of']['href']
                        ret.append(
                            "%scollection of: %s" % (
                                (indent * 4 * ' '),
                                coll_type_uri.rsplit('/', 1)[-1]))

                        ret.append("%smin: %s" % ((indent * 4 * ' '),
                                                  field['min']))
                        ret.append("%smax: %s" % ((indent * 4 * ' '),
                                                  field['max']))
                    elif 'ref-collection-of' in field["_links"]:
                        ret.append(
                            "%sname: %s" % ((indent * 3 * ' '), field['id']))

                        coll_type_uri = \
                            field['_links']['ref-collection-of']['href']
                        ret.append(
                            "%sref-collection of: %s" % (
                                (indent * 4 * ' '),
                                coll_type_uri.rsplit('/', 1)[-1]))

                        ret.append("%smin: %s" % ((indent * 4 * ' '),
                                                  field['min']))
                        ret.append("%smax: %s" % ((indent * 4 * ' '),
                                                  field['max']))
                    elif 'reference-to' in field["_links"]:
                        ret.append("%sname: %s" % ((indent * 3 * ' '),
                                                   field['id']))
                        if 'description' in field:
                            ret.append(
                                "%sdescription: %s" % ((indent * 4 * ' '),
                                                       field['description']))
                        if 'required' in field:
                            ret.append("%srequired: %s" % ((indent * 4 * ' '),
                                                       field['required']))
                        if 'site_specific' in field:
                            ret.append("%ssite specific: %s" % (
                                (indent * 4 * ' '),
                                field['site_specific']))
                        if 'regex' in field:
                            ret.append("%sregex: %s" % ((indent * 4 * ' '),
                                                        field['regex']))
                        ret.append("%stype: %s" % (
                            (indent * 4 * ' '),
                            field['_links']['reference-to']['href'].rsplit(
                                                            '/', 1)[-1]))
                    else:
                        ret.append("%sname: %s" % ((indent * 3 * ' '),
                                                   field['id']))
                        if 'description' in field:
                            ret.append(
                                "%sdescription: %s" % ((indent * 4 * ' '),
                                                       field['description']))
                        if 'required' in field:
                            ret.append("%srequired: %s" % ((indent * 4 * ' '),
                                                       field['required']))
                        if 'site_specific' in field:
                            ret.append("%ssite specific: %s" % (
                                (indent * 4 * ' '),
                                field['site_specific']))
                        if 'regex' in field:
                            ret.append("%sregex: %s" % ((indent * 4 * ' '),
                                                        field['regex']))
                        ret.append("%stype: %s" % (
                            (indent * 4 * ' '),
                            field['_links']['self']['href'].rsplit(
                                                            '/', 1)[-1]))
            # this is a property type
            elif 'regex' in data:
                ret.append("regex: %s\n" % data['regex'])
        return "\n".join(ret)

    def cb_format_property_type(self, data):
        formatted_string = "name: %s\n" % data['id']
        formatted_string += "regex: %s\n" % data['regex']
        return formatted_string

    def cb_format_item_types(self, item):
        if not isinstance(item, dict):
            item = json.loads(item)
        data = item
        if not self._get_option("long"):
            ret = []
            children = self._get_children(data)
            for child in children:
                msg = "name: %s" % child['id']
                if 'description' in child:
                    msg += "\ndescription: %s\n" % child['description']
                ret.append(msg)
        else:
            ret = [child['_links']['self']['href'].replace(self.url, '')
                   for child in data['_embedded']['item-type']]
        ret = "\n".join(ret).rstrip()
        return ret

    def cb_format_show(self, item, recursive=False, indent=4):
        ret = []
        try:
            data = self._deserialize_data(item)
        except ValueError:
            return item
        if data.get('id', '') in ["item-types", "property-types"]:
            return self.cb_format_item_types(item)
        self_uri = data.get("_links", {}).get("self", {}).get("href", "")
        if 'item-types' in self_uri:
            return self.cb_format_item_type(data)
        if 'property-types' in self_uri:
            return self.cb_format_property_type(data)

        ret.append(data['_links']['self']['href'].replace(self.url, '\n'))
        if data['_links'].get("reference-to"):
            ret.append("%slinks to: %s" % (
                ' ' * indent,
                data['_links']['reference-to']['href'].replace(self.url, ''))
            )
        if data['_links'].get("inherited-from"):
            ret.append("%sinherited from: %s" % (
                ' ' * indent,
                data['_links']['inherited-from']['href'].replace(self.url, ''))
            )

        if 'item-type-name' in data:
            ret.append("%stype: %s" % (' ' * indent, data['item-type-name']))

        if 'version' in data:
            ret.append("%sversion: %s" % (' ' * indent, data['version']))

        if 'state' in data:
            indeterminable = ''
            if 'applied_properties_determinable' in data \
                    and not data['applied_properties_determinable']:
                indeterminable = ' (deployment of properties indeterminable)'
            ret.append("%sstate: %s%s" % \
                (' ' * indent, data['state'], indeterminable)
            )

        properties = data.get('properties')
        if properties:
            if data['_links'].get("inherited-from"):
                properties_overwritten = data.get('properties-overwritten', [])
                ret.append(
                    ('%sproperties (inherited properties are marked '
                     'with asterisk):' % (' ' * indent))
                )
                for key, value in properties.iteritems():
                    if key in properties_overwritten:
                        format_str = '%s%s: %s'
                    else:
                        format_str = '%s%s: %s [*]'
                    ret.append(
                        format_str % (
                            ' ' * 2 * indent,
                            key, value
                        )
                    )

            else:
                ret.append('%sproperties:' % (' ' * indent))
                ret.append(''.join([
                    '%s%s: %s\n' % (' ' * 2 * indent, key, value)
                    for key, value in properties.iteritems()
                ]))

        children = self._get_children(data)
        if recursive:
            for child in children:
                ret.append(self.cb_format_show(child,
                                               recursive=True))
        else:
            if children:
                ret.append('%schildren:' % (' ' * indent))
                for child in children:
                    child_url = child['_links']['self']['href'].replace(
                                    data['_links']['self']['href'], '')

                    if not child_url.startswith("/"):
                        child_url = "/" + child_url
                    ret.append(' ' * 2 * indent + child_url)

        if self.args.get('property') is not None:
            if self.args['property'] in data.get('properties', {}).keys():
                ret = [str(data['properties'][self.args['property']])]
            else:
                ret = [data['_links']['self']['href'].replace(self.url, '')]
                ret.append('%s%s%sProperty "%s" is not set' %
                           (' ' * indent, "InvalidPropertyError",
                            ' ' * indent, self.args['property']))

        return '\n'.join(ret)

    def cb_format_version(self, item, recursive=False, indent=4):
        ret = []
        try:
            data = self._deserialize_data(item)
        except ValueError:
            return item
        if 'version' in data:
            ret.append("%sLITP2 %s" % (' ' * indent, data['version']))

        if self._get_option("all") and data.get('litp-packages'):
            ret.append('\n%sAdd-on packages:' % (' ' * indent))
            ret.append(''.join(['%s%s: %s %s %s\n' % (' ' * 2 * indent,
                       pkg.get('name'),
                       pkg.get('version'),
                       pkg.get('cxp'),
                       pkg.get('packager'))
                       for pkg in data['litp-packages']]))

        return '\n'.join(ret)

    def cb_format_paths_as_tree(self, item, parent=None,
                                recursive=False, indent=0):
        ret = []
        if isinstance(parent, basestring):
            if parent == '/':
                indent = 4
            else:
                indent += (len(parent.split('/')) - 1) * 4

        if isinstance(item, basestring):
            item = json.loads(item)

        if item.get('id', '') == "item-types" or 'description' in item:
            return self.cb_format_item_types(item)

        if isinstance(item, list):
            return self.cb_format_show(item)

        path = item['_links']['self']['href'].replace(self.url, '')
        path = path.split(parent, 1)[-1]

        if not path.startswith('/'):
            path = '/' + path

        ret.append(' ' * indent + path)

        children = self._get_children(item)
        for child in children:
            if not recursive:
                ret.append(child['_links']['self']['href'].replace(self.url,
                                                                   ''))
            else:
                ret.append(self.cb_format_paths_as_tree(
                    child, parent=path, recursive=True,
                    indent=indent))

        return "\n".join(ret)

    def cb_format_path_list(self, item, parent=None, recursive=False):
        ret = []
        if isinstance(item, basestring):
            item = json.loads(item)
        data = item
        if '_links' not in data:
            return self.cb_format_item_types(item)

        if isinstance(data, list):
            return self.cb_format_show(item, recursive=False)

        ret.append(data['_links']['self']['href'].replace(self.url, ''))

        children = self._get_children(data)
        for child in children:
            if not recursive:
                ret.append(child['_links']['self']['href'].replace(self.url,
                                                                   ''))
            else:
                ret.append(self.cb_format_path_list(child, recursive=True))

        return '\n'.join(ret)

    def cb_format_path_completion(self, item, parent=None, recursive=False):
        ret = []
        if isinstance(item, basestring):
            item = json.loads(item)
        data = item
        if '_links' not in data:
            return self.cb_format_item_types(item)

        if isinstance(data, list):
            return self.cb_format_show(item, recursive=False)

        ret.append(data['_links']['self']['href'].replace(self.url, ''))

        children = self._get_children(data)
        for child in children:
            trailing_slash = False
            append_item_type = False
            if not recursive:
                trail_elements = [key in child['_links'] for key in
                        ('ref-collection-of', 'collection-of')
                    ]

                if any(trail_elements):
                    trailing_slash = True
                else:
                    # We'll let the completion logic figure out whether to add
                    # a trailing slash by querying the child's item type
                    append_item_type = True

                list_entry = child['_links']['self']['href'].replace(self.url,
                                                                   '')
                if trailing_slash:
                    list_entry += '/'

                if append_item_type:
                    type_name = child['item-type-name']
                    if type_name.startswith('reference-to-'):
                        type_name = type_name[len('reference-to-'):]
                    list_entry += ':' + type_name

                ret.append(list_entry)
            else:
                ret.append(
                        self.cb_format_path_completion(child, recursive=True)
                    )

        return '\n'.join(ret)

    def cb_format_create_or_update(self, result, recursive=False):
        return self.cb_format_error(result)

    def cb_format_error(self, response, indent=4):
        try:
            data = self._deserialize_data(response)
        except ValueError:
            return response

        output_tokens = []

        if 'error' in data:
            output_tokens.append(data['error'])
        else:
            messages = data.get('messages', [])

            for message in messages:
                message['indent'] = indent * ' '
                if '_links' in message:
                    message['rel_path'] = re.sub(
                        self.url, '', message['_links']['self']['href'])
                    output_tokens.append('%(rel_path)s' % message)

                if 'property_name' in message:
                    output_tokens.append(
                        '%(indent)s%(type)s in property: "%(property_name)s"'
                        '%(indent)s%(message)s' % message)
                else:
                    output_tokens.append(
                        '%(indent)s%(type)s%(indent)s%(message)s' % message)
        return '\n'.join(output_tokens)

    def _deserialize_data(self, data):
        if not isinstance(data, dict):
            data = json.loads(data)
        else:
            data = data
        return data
