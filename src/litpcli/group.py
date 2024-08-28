import argparse


class NestedArgumentsGroup(argparse._ArgumentGroup):
    def __init__(self, container, title=None,
                 description=None, required=False, **kwargs):
        super(NestedArgumentsGroup, self).__init__(
                container, title, description, **kwargs)
        self.required = required
