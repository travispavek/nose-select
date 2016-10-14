import logging
import os
import sys
from nose.plugins.base import Plugin
from nose.util import tolist
from nose.plugins.collect import CollectOnly
import re
import json
import io

log = logging.getLogger('nose.plugins.tag')
compat_24 = sys.version_info >= (2, 4)
prefix = os.environ.get('NOSE_TAG_PREFIX', 'tst')

def remove_prefix(attr):
    return re.sub('^%s_' % prefix, '', attr)
    
def add_prefix(attr):
    return '%s_%s' % (prefix, attr)

def tag(*args, **kwargs):
    """Decorator that adds tags to classes or functions
    for use with the Tag (-t) plugin.
    """
    def wrap_ob(ob):
        for name in args:
            setattr(ob, add_prefix(name), True)
        for name, value in kwargs.iteritems():
            setattr(ob, add_prefix(name), value)
        return ob
    return wrap_ob

attr = tag

def get_method_attr(method, cls, attr_name, default = False):
    """Look up an attribute on a method/ function. 
    If the attribute isn't found there, looking it up in the
    method's class, if any.
    """
    Missing = object()
    value = getattr(method, attr_name, Missing)
    if value is Missing and cls is not None:
        value = getattr(cls, attr_name, Missing)
    if value is Missing:
        return default
    return value


class ContextHelper:
    """Object that can act as context dictionary for eval and looks up
    names as attributes on a method/ function and its class. 
    """
    def __init__(self, method, cls):
        self.method = method
        self.cls = cls

    def __getitem__(self, name):
        return get_method_attr(self.method, self.cls, add_prefix(name))


class TagSelector(Plugin):
    """Selects test cases to be run based on their attributes.
    """
    name = 'tag-selector'
    
    def __init__(self):
        Plugin.__init__(self)
        self.attribs = []

    def options(self, parser, env):
        """Register command line options"""
        parser.add_option("-t", "--tag",
                          dest="tag", action="append",
                          default=env.get('NOSE_TAG'),
                          metavar="TAG",
                          help="Run only tests that have attributes "
                          "specified by ATTR [NOSE_TAG]")
        
        # disable in < 2.4: eval can't take needed args
        if compat_24:
            parser.add_option("-T", "--eval-tag",
                              dest="eval_tag", metavar="TAG_EXPR", action="append",
                              default=env.get('NOSE_EVAL_TAG'),
                              help="Run only tests for whose tags "
                              "the Python expression TAG_EXPR evaluates "
                              "to True [NOSE_EVAL_TAG]")

    def configure(self, options, config):
        """Configure the plugin and system, based on selected options.

        attr and eval_attr may each be lists.

        self.attribs will be a list of lists of tuples. In that list, each
        list is a group of attributes, all of which must match for the rule to
        match.
        """
        self.attribs = []

        # handle python eval-expression parameter
        if compat_24 and options.eval_tag:
            eval_tag = tolist(options.eval_tag)
            for tag in eval_tag:
                # "<python expression>"
                # -> eval(expr) in attribute context must be True
                def eval_in_context(expr, obj, cls):
                    return eval(expr, None, ContextHelper(obj, cls))
                self.attribs.append([(tag, eval_in_context)])

        # attribute requirements are a comma separated list of
        # 'key=value' pairs
        if options.tag:
            std_tag = tolist(options.tag)
            for tag in std_tag:
                # all attributes within an attribute group must match
                tag_group = []
                for attrib in tag.strip().split(","):
                    # don't die on trailing comma
                    if not attrib:
                        continue
                    items = attrib.split("=", 1)
                    if len(items) > 1:
                        # "name=value"
                        # -> 'str(obj.name) == value' must be True
                        key, value = items
                    else:
                        key = items[0]
                        if key[0] == "!":
                            # "!name"
                            # 'bool(obj.name)' must be False
                            key = key[1:]
                            value = False
                        else:
                            # "name"
                            # -> 'bool(obj.name)' must be True
                            value = True
                    tag_group.append((key, value))
                self.attribs.append(tag_group)
        if self.attribs:
            self.enabled = True

    def validateTag(self, method, cls = None):
        """Verify whether a method has the required attributes
        The method is considered a match if it matches all attributes
        for any attribute group.
        ."""
        # TODO: is there a need for case-sensitive value comparison?
        any = False
        for group in self.attribs:
            match = True
            for key, value in group:
                attr = get_method_attr(method, cls, add_prefix(key))
                if callable(value):
                    if not value(key, method, cls):
                        match = False
                        break
                elif value is True:
                    # value must exist and be True
                    if not bool(attr):
                        match = False
                        break
                elif value is False:
                    # value must not exist or be False
                    if bool(attr):
                        match = False
                        break
                elif type(attr) in (list, tuple):
                    # value must be found in the list attribute
                    if not str(value).lower() in [str(x).lower()
                                                  for x in attr]:
                        match = False
                        break
                else:
                    # value must match, convert to string and compare
                    if (value != attr
                        and str(value).lower() != str(attr).lower()):
                        match = False
                        break
            any = any or match
        if any:
            # not True because we don't want to FORCE the selection of the
            # item, only say that it is acceptable
            return None
        return False

    def wantFunction(self, function):
        """Accept the function if its attributes match.
        """
        return self.validateTag(function)

    def wantMethod(self, method):
        """Accept the method if its attributes match.
        """
        try:
            cls = method.im_class
        except AttributeError:
            return False
        return self.validateTag(method, cls)


class TagCollector(CollectOnly):
    """
    Collect and output test names only, don't run any tests.
    """
    name = "tag-collector"
    enableOpt = "tag_collector"

    #def configure(self, option, conf):
     #  self.attributes = dict()
    def __init__(self):
        super(TagCollector, self).__init__()
        self.cases = dict()
        
    def options(self, parser, env):
        """Register commandline options.
        """
        parser.add_option('--get-tags',
                          dest=self.enableOpt,
                          action='store_true',
                          help="Enable get-tags: %s [GET_TAGS]" %
                          (self.help()))

    def startTest(self, test):
        is_test = re.compile('^test_\S+')
        
        method_name = filter(is_test.match, dir(test))[0]
        class_name = test.__class__.__name__
        module_name = test.__module__
        tags = self.get_tags(getattr(test, method_name))
        self.cases['{}.{}.{}'.format(module_name, class_name, method_name)] = tags
        
    def setOutputStream(self, stream):
        return stream
        class NoStream(object):
            def writeln(self, *arg):
                pass
            write = writeln
        return NoStream()
    
    def get_tags(self, method):
        tmp = dict()
        is_attr = re.compile('^%s_\S+' % prefix)
        # Get method attributes
        for attribute in filter(is_attr.match, dir(method)):
            tmp[remove_prefix(attribute)] = getattr(method, attribute)

        # Get class attributes
        for attribute in filter(is_attr.match, dir(method.im_class)):
            tmp[remove_prefix(attribute)] = getattr(method.im_class, attribute)
        return tmp

    def finalize(self, result):
        json.dump(self.cases, sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))

