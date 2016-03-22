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
            treeStableTimer = 10
        ),
        ForceScheduler(
            name = 'force',
            reason = FixedParameter(name = "reason", default = "force build"),
            builderNames = builders.get_builder_names(),
            branch = StringParameter(name = "branch", default = "master"),
            revision = FixedParameter(name = "revision", default = ""),
            repository = FixedParameter(name = "repository", default = "git://github.com/SFML/SFML.git"),
            project = FixedParameter(name = "project", default = "SFML"),
            properties = []
        )
    ]