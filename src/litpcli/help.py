import itertools
import argparse
import textwrap
import re
from litpcli.group import NestedArgumentsGroup

from gettext import gettext as _


class HelpFormatter(argparse.HelpFormatter):
    """
    Implements capitalized usage prefix.
    """
    def add_usage(self, usage, actions, groups, prefix=None):
        if usage is not argparse.SUPPRESS:
            if prefix is None:
                prefix = _('Usage: ')
        super(HelpFormatter, self).add_usage(usage, actions, groups, prefix)


class RawDescriptionHelpFormatter(HelpFormatter,
                                  argparse.RawDescriptionHelpFormatter):
    """
    argparse.RawDescriptionHelpFormatter inheriting Usage
    """
    def _fill_text(self, text, width, indent):
        paragraphs = []
        for x in text.splitlines():
            paragraphs.append(textwrap.fill(x, width))
        return "\n".join(paragraphs)


class FormattedHelpArgumentParser(argparse.ArgumentParser):
    """
    Implements capitalized help string and section name, wires up formatter.
    """
    def __init__(self, *args, **kwargs):
        super(FormattedHelpArgumentParser, self).__init__(*args, **kwargs)

        self._optionals.title = _('Optional Arguments')

        for action in self._actions:
            if action.dest == 'help':
                action.help = _("Show this help message and exit")
                break
        if 'formatter_class' not in kwargs:
            self.formatter_class = HelpFormatter


class NestedArgumentsGroupHelpFormatter(HelpFormatter):
    @staticmethod
    def _get_action_parts(actions, groups):
        action_parts = actions[:]

        # groups are either mutually_exclusive_group or nested_arguments_group
        for group in groups:
            try:
                start = action_parts.index(group._group_actions[0])
            except ValueError:
                continue
            end = start + len(group._group_actions)
            action_parts[start:end] = [group]

        return action_parts

    def _format_action_part(self, action_part, in_group=False):
        # suppressed arguments are marked with None
        # remove | separators for suppressed arguments
        action = action_part
        part = None
        if action.help is argparse.SUPPRESS:
            part = None

        # produce all arg strings
        elif not action.option_strings:
            part = self._format_args(action, action.dest)

            # if it's in a group, strip the outer []
            if in_group:
                if part[0] == '[' and part[-1] == ']':
                    part = part[1:-1]

        # produce the first way to invoke the option in brackets
        else:
            option_string = action.option_strings[0]

            # if the Optional doesn't take a value, format is:
            #    -s or --long
            if action.nargs == 0:
                part = '%s' % option_string

            # if the Optional takes a value, format is:
            #    -s ARGS or --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                part = '%s %s' % (option_string, args_string)

            # make it look optional if it's not required or in a group
            if not action.required and not in_group:
                part = '[%s]' % part

        return part

    def _format_group_action_part(self, group):
        flatten = itertools.chain.from_iterable
        parts = []
        start, end = ('(', ')') if group.required else ('[', ']')
        for action in group._group_actions:
            parts.append(self._format_action_part(action, in_group=True))
        separated_parts = [[part, '|'] for part in parts]
        parts = list(flatten(separated_parts))[:-1]
        parts.insert(0, start)
        parts.append(end)
        return parts

    def _format_nested_group_action_part(self, group):
        parts = []
        start, end = ('(', ')') if group.required else ('[', ']')
        stack = []

        for action in group._group_actions:
            if not action.required:
                parts.append('[')
                stack.append(']')
            else:
                parts.append('(')
                stack.append(')')
            parts.append(self._format_action_part(action, in_group=True))

        parts.extend(reversed(stack))
        if parts[0] != '[':
            parts.insert(0, start)
            parts.append(end)
        return parts

    def _get_parts(self, action_parts):
        parts = []
        for action_part in action_parts:
            if isinstance(action_part, argparse.Action):
                part = self._format_action_part(action_part)
                parts.append(part)
            elif isinstance(action_part, NestedArgumentsGroup):
                parts.extend(
                        self._format_nested_group_action_part(action_part))
            elif isinstance(action_part, argparse._ArgumentGroup):
                parts.extend(self._format_group_action_part(action_part))
        return parts

    def _format_actions_usage(self, actions, groups):
        action_parts = self._get_action_parts(actions, groups)
        parts = self._get_parts(action_parts)

        text = ' '.join([item for item in parts if item is not None])
        return self._clean_up_separators(text)

    @staticmethod
    def _clean_up_separators(text):
        _open = r'[\[(]'
        close = r'[\])]'
        text = re.sub(r'(%s) ' % _open, r'\1', text)
        text = re.sub(r' (%s)' % close, r'\1', text)
        text = re.sub(r'%s *%s' % (_open, close), r'', text)
        text = re.sub(r'\(([^|]*)\)', r'\1', text)
        text = text.strip()
        return text
