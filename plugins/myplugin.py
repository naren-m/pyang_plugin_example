import optparse
import sys

from pyang import plugin
from pyang import statements


def pyang_plugin_init():
    plugin.register_plugin(MyPluginPyangPlugin())


class MyPluginPyangPlugin(plugin.PyangPlugin):
    def __init__(self):
        plugin.PyangPlugin.__init__(self, 'my-plugin')

    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['my-plugin'] = self

    def add_opts(self, optparser):
        # you can add additional cmd line options here.
        optlist = [
            optparse.make_option(
                "--my-plugin-help",
                dest="my_plugin_help",
                action="store_true",
                help="Print help on my-plugin symbols and exit"),
            optparse.make_option(
                "--my-plugin-tree-path",
                dest="my_plugin_tree_path",
                help="Subtree to print"),
            optparse.make_option(
                "--my-plugin-tree-no-expand-uses",
                dest="my_plugin_tree_no_expand_uses",
                action="store_false",
                default=False,
                help="Do not expand uses of groupings"),
        ]
        g = optparser.add_option_group("my-plugin output specific options")
        g.add_options(optlist)

    def setup_ctx(self, ctx):
        if ctx.opts.my_plugin_help:
            print_help()
            sys.exit(0)

    def setup_fmt(self, ctx):
        ctx.implicit_errors = False

    def emit(self, ctx, modules, fd):
        if ctx.opts.tree_path is not None:
            path = ctx.opts.tree_path.split('/')
            if path[0] == '':
                path = path[1:]
        else:
            path = None
        emit_tree(ctx, modules, fd, ctx.opts.tree_line_length, path)


class Metric:
    def __init__(self, name):
        self.name = name
        self.fields = list()

    def append(self, metric):
        if metric not in self.fields:
            self.fields.append(metric)

    def __eq__(self, other):
        if other is None:
            return False
        return (self.name == other.name)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "{'name': %s, 'fields': %s}" % (self.name, str(self.fields))

    def __contains__(self, metric):
        for m in self.fields:
            if m == metric:
                return True

        return False

    def print(self):
        print(self.name)
        for f in self.fields:
            print('    ', f)


def emit_tree(ctx, modules, fd, llen, path):
    for module in modules:
        chs = [
            ch for ch in module.i_children
            if ch.keyword in statements.data_definition_keywords
        ]

        if path is not None and len(path) > 0:
            chs = [ch for ch in chs if ch.arg == path[0]]
            chpath = path[1:]
        else:
            chpath = path

        print("chpath", chpath)

        print_children(chs, module, fd, chpath, 'data', llen,
                       ctx.opts.my_plugin_tree_no_expand_uses)


def print_children(i_children,
                   module,
                   fd,
                   path,
                   llen,
                   no_expand_uses=False,
                   width=0,
                   metric=None):
    if no_expand_uses:
        i_children = unexpand_uses(i_children)

    for ch in i_children:
        if ((ch.keyword == 'input' or ch.keyword == 'output')
                and len(ch.i_children) == 0):
            continue
        print_node(
            ch, module, fd, path, llen, no_expand_uses, width, metric=metric)


def print_node(s, module, fd, path, llen, no_expand_uses, width, metric=None):
    if s.i_module.i_modulename == module.i_modulename:
        name = s.arg
    else:
        name = s.i_module.i_prefix + ':' + s.arg

    m = Metric(name)

    # if s.keyword == 'container':
    if s.keyword in ['container', 'list']:
        if metric is None:
            metric = m
        else:
            metric.append(m)
    elif s.keyword == 'leaf':
        metric.append(m)

    print(s.keyword, name)

    if hasattr(s, 'i_children') and s.keyword != 'uses':
        chs = s.i_children
        if path is not None and len(path) > 0:
            chs = [ch for ch in chs if ch.arg == path[0]]
            path = path[1:]
        if s.keyword in ['container', 'list']:
            print_children(
                chs, module, fd, path, llen, no_expand_uses, metric=m)
        else:
            print_children(
                chs, module, fd, path, llen, no_expand_uses, metric=metric)
    print('In Print node', metric)


def unexpand_uses(i_children):
    res = []
    uses = []
    for ch in i_children:
        if hasattr(ch, 'i_uses'):
            g = ch.i_uses[0].arg
            if g not in uses:
                # first node from this uses
                uses.append(g)
                res.append(ch.i_uses[0])
        else:
            res.append(ch)
    return res


def print_help():
    print("""
    Sample test help
    """)
