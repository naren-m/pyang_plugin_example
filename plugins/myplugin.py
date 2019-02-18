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
            optparse.make_option("--my-plugin-help",
                                 dest="my-plugin_help",
                                 action="store_true",
                                 help="Print help on my-plugin symbols and exit"),
            optparse.make_option("--my-plugin-tree-path",
                                 dest="my-plugin_tree_path",
                                 help="Subtree to print"),
            optparse.make_option("--my-plugin-tree-no-expand-uses",
                                 dest="my-plugin_tree_no_expand_uses",
                                 action="store_false",
                                 default=False,
                                 help="Do not expand uses of groupings"),
        ]
        g = optparser.add_option_group("my-plugin output specific options")
        g.add_options(optlist)
    
    def setup_ctx(self, ctx):
        if ctx.opts.my-plugin_help:
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
        emit_tree(ctx, modules, fd, ctx.opts.tree_depth,
                  ctx.opts.tree_line_length, path)

def emit_tree(ctx, modules, fd, depth, llen, path):
    print('Emitting tree dummy')

    for module in modules:
        printed_header = False

        def print_header():
            bstr = ""
            b = module.search_one('belongs-to')
            if b is not None:
                bstr = " (belongs-to %s)" % b.arg
            fd.write("%s: %s%s\n" % (module.keyword, module.arg, bstr))
            printed_header = True

        chs = [ch for ch in module.i_children
               if ch.keyword in statements.data_definition_keywords]

        if path is not None and len(path) > 0:
            chs = [ch for ch in chs if ch.arg == path[0]]
            chpath = path[1:]
        else:
            chpath = path

        print("chpath", chpath)

        if len(chs) > 0:
            if not printed_header:
                print_header()
        print_children(chs, module, fd, '', chpath, 'data', depth, llen,
                           ctx.opts.my-plugin_tree_no_expand_uses,
                           prefix_with_modname=ctx.opts.modname_prefix)

def print_children(i_children, module, fd, prefix, path, mode, depth,
                   llen, no_expand_uses=False, width=0, prefix_with_modname=False):
    print(i_children)
    print(prefix)
    print(path)
    print(depth)
    print(no_expand_uses)

    if depth == 0:
        if i_children: fd.write(prefix + '     ...\n')
        return
    
    if no_expand_uses:
        i_children = unexpand_uses(i_children)

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