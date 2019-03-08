from jinja2.ext import Extension
import re
class RelativeInclude(Extension):
    """Allows to import relative template names"""
    tags = set(['include2'])

    def __init__(self, environment):
        super(RelativeInclude, self).__init__(environment)
        self.matcher = re.compile("\.*")

    def parse(self, parser):
        node = parser.parse_include()
        template = node.template.as_const()
        if template.startswith("."):
            # determine the number of go ups
            up = len(self.matcher.match(template).group())
            # split the current template name into path elements
            # take elements minus the number of go ups
            seq = parser.name.split("/")[:-up]
            print(seq)
            # extend elements with the relative path elements
            seq.extend(template.split("/")[1:])
            template = template.lstrip(".")
            seq.append(template)
            template = "/".join(seq)  
            node.template.value = template
        return node