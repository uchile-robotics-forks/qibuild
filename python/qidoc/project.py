import abc

class DocProject(object):

    __metaclass__ = abc.ABCMeta
    doc_type = None

    def __init__(self, doc_worktree, project, name,
                 depends=None):

        self.name = name
        self.src = project.src
        self.path = project.path
        if not depends:
            depends = list()
        self.depends = list()

    def __repr__(self):
        return "<%s %s in %s>" % (self.doc_type.capitalize() + "Project",
                                  self.name, self.src)

