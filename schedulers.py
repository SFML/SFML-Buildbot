def get_schedulers() :
    from buildbot.schedulers.basic import AnyBranchScheduler
    from buildbot.schedulers.forcesched import ForceScheduler
    from buildbot.schedulers.forcesched import FixedParameter
    from buildbot.schedulers.forcesched import StringParameter
    import builders

    return [
        AnyBranchScheduler(
            name = 'default',
            reason = 'source code modification',
            builderNames = builders.get_builder_names(),
            treeStableTimer = 120
        ),
        ForceScheduler(
            name = 'force',
            reason = StringParameter(name = "reason", default = "force build", size = 100),
            builderNames = builders.get_builder_names(),
            branch = StringParameter(name = "branch", default = "master", size = 100),
            revision = StringParameter(name = "revision", default = "", size = 100),
            repository = StringParameter(name = "repository", default = "https://github.com/SFML/SFML.git", regex = r"^https://github.com/[\w-]*/[\w-]*\.git$", size = 100),
            project = StringParameter(name = "project", default = "SFML", size = 100),
            properties = []
        )
    ]