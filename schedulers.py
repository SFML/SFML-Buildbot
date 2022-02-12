def get_schedulers() :
    from buildbot.schedulers.basic import SingleBranchScheduler
    from buildbot.schedulers.basic import AnyBranchScheduler
    from buildbot.schedulers.forcesched import ForceScheduler
    from buildbot.schedulers.forcesched import StringParameter
    from buildbot.schedulers.forcesched import FixedParameter
    from buildbot.plugins import util
    import builders

    return [
        SingleBranchScheduler(
            name = 'master',
            reason = 'main repository source code modification',
            builderNames = ['coverity'],
            treeStableTimer = 20,
            change_filter=util.ChangeFilter(branch='master')
        ),
        AnyBranchScheduler(
            name = 'default',
            reason = 'main repository source code modification',
            builderNames = builders.get_builder_names(),
            treeStableTimer = 20
        ),
        ForceScheduler(
            name = 'force',
            reason = StringParameter(name = "reason", default = "manual build", size = 100),
            builderNames = builders.get_builder_names(),
            codebases = [
                util.CodebaseParameter(
                    "",
                    label = "Codebase",
                    branch = StringParameter(name = "branch", default = "master", size = 100),
                    revision = StringParameter(name = "revision", default = "", size = 100),
                    repository = StringParameter(name = "repository", default = "https://github.com/SFML/SFML.git", regex = r"^https://github.com/[\w-]*/[\w-]*\.git$", size = 100),
                    project = StringParameter(name = "project", default = "SFML", size = 100),
                )
            ],
            properties = [
                util.FixedParameter(name = "trigger", default = "force")
            ]
        )
    ]