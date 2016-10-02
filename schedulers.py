def main_repository(repository) :
    return bool('github.com/SFML/SFML' in repository)

def foreign_repository(repository) :
    return not main_repository(repository)

def get_schedulers() :
    from buildbot.schedulers.basic import AnyBranchScheduler
    from buildbot.schedulers.forcesched import ForceScheduler
    from buildbot.schedulers.forcesched import FixedParameter
    from buildbot.schedulers.forcesched import StringParameter
    from buildbot.plugins import util
    import builders

    return [
        AnyBranchScheduler(
            name = 'default',
            reason = 'main repository source code modification',
            builderNames = builders.get_builder_names(),
            treeStableTimer = 120,
            change_filter = util.ChangeFilter(
                repository_fn = main_repository
            )
        ),
        AnyBranchScheduler(
            name = 'foreign',
            builderNames = builders.get_builder_names(),
            change_filter = util.ChangeFilter(
                repository_fn = foreign_repository
            )
        ),
        ForceScheduler(
            name = 'force',
            reason = StringParameter(name = "reason", default = "manual build", size = 100),
            builderNames = builders.get_builder_names(),
            branch = StringParameter(name = "branch", default = "master", size = 100),
            revision = StringParameter(name = "revision", default = "", size = 100),
            repository = StringParameter(name = "repository", default = "https://github.com/SFML/SFML.git", regex = r"^https://github.com/[\w-]*/[\w-]*\.git$", size = 100),
            project = StringParameter(name = "project", default = "SFML", size = 100),
            properties = []
        )
    ]