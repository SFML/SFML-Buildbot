def get_cmake_step(configure, link, type):
    from buildbot.steps.shell import ShellCommand

    build_type = ''

    if type == 'debug':
        build_type += '-DCMAKE_BUILD_TYPE=Debug'
    else:
        build_type += '-DCMAKE_BUILD_TYPE=Release'

    shared_libs = ''

    if link == 'static':
        shared_libs += '-DBUILD_SHARED_LIBS=FALSE'
    else:
        shared_libs += '-DBUILD_SHARED_LIBS=TRUE'

    return ShellCommand(
        name = 'cmake',
        description = ['configuring'],
        descriptionSuffix = [link, type],
        descriptionDone = ['configure'],
        command = [configure, build_type, shared_libs, '.'],
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_build_step(make, link, type):
    from buildbot.steps.shell import Compile

    return Compile(
        description = ['building'],
        descriptionSuffix = [link, type],
        descriptionDone = ['build'],
        command = make,
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )


def get_build_factory(configure, make):
    from buildbot.process.factory import BuildFactory
    from buildbot.process.properties import Interpolate
    from buildbot.steps.source.git import Git
    from buildbot.steps.transfer import DirectoryUpload
    from buildbot.steps.slave import RemoveDirectory
    from buildbot.steps.master import MasterShellCommand
    from buildbot.status.results import SKIPPED

    steps = [
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            repourl = Interpolate('%(prop:repository)s'),
            mode = 'full',
            shallow = True,
            method = 'clobber',
            retry = (30, 5),
            progress = True,
            logEnviron = False
        ),
        get_cmake_step(configure, 'static', 'debug'),
        get_build_step(make, 'static', 'debug'),
        get_cmake_step(configure, 'dynamic', 'debug'),
        get_build_step(make, 'dynamic', 'debug'),
        get_cmake_step(configure, 'static', 'release'),
        get_build_step(make, 'static', 'release'),
        get_cmake_step(configure, 'dynamic', 'release'),
        get_build_step(make, 'dynamic', 'release'),
        DirectoryUpload(
            description = ['uploading'],
            descriptionSuffix = ['artifact'],
            descriptionDone = ['upload'],
            slavesrc = Interpolate('%(prop:workdir)s/install'),
            masterdest = Interpolate('%(prop:buildername)s/tmp/%(prop:got_revision)s'),
            compress = 'bz2',
            doStepIf = lambda step : ('freebsd' not in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        RemoveDirectory(
            name = 'clean',
            description = ['cleaning slave'],
            descriptionDone = ['clean slave'],
            dir = Interpolate('%(prop:workdir)s'),
            alwaysRun = True
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : ('windows' in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
            command = Interpolate(
                """mkdir -p artifacts/by-revision/%(prop:got_revision)s &&
                mkdir -p artifacts/by-branch/%(src::branch:-master)s &&
                cd %(prop:buildername)s/tmp &&
                zip -r %(prop:buildername)s %(prop:got_revision)s &&
                mv %(prop:buildername)s.zip ../../artifacts/by-revision/%(prop:got_revision)s &&
                ln -f ../../artifacts/by-revision/%(prop:got_revision)s/%(prop:buildername)s.zip ../../artifacts/by-branch/%(src::branch:-master)s/%(prop:buildername)s.zip &&
                rm -rf "../tmp" """
            )
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : (('windows' not in step.build.getProperty('buildername')) and ('freebsd' not in step.build.getProperty('buildername'))),
            hideStepIf = lambda results, step : results == SKIPPED,
            command = Interpolate(
                """mkdir -p artifacts/by-revision/%(prop:got_revision)s &&
                mkdir -p artifacts/by-branch/%(src::branch:-master)s &&
                cd %(prop:buildername)s/tmp &&
                tar czf %(prop:buildername)s.tar.gz %(prop:got_revision)s/ &&
                mv %(prop:buildername)s.tar.gz ../../artifacts/by-revision/%(prop:got_revision)s &&
                ln -f ../../artifacts/by-revision/%(prop:got_revision)s/%(prop:buildername)s.tar.gz ../../artifacts/by-branch/%(src::branch:-master)s/%(prop:buildername)s.tar.gz &&
                rm -rf "../tmp" """
            )
        )
    ]

    factory = BuildFactory(steps)

    return factory

def get_unix_build_factory():
    from buildbot.process.properties import Interpolate

    return get_build_factory(
        ['cmake', '-G', 'Unix Makefiles', '-DSFML_BUILD_EXAMPLES=TRUE', Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:workdir)s/install')],
        ['make', '-j', Interpolate('%(prop:parallel)s'), 'install']
    )

def get_msvc_build_factory():
    from buildbot.process.properties import Interpolate

    return get_build_factory(
        ['cmake', '-G', 'NMake Makefiles JOM', '-DSFML_BUILD_EXAMPLES=TRUE', Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:workdir)s/install')],
        ['nmake', '-j', Interpolate('%(prop:parallel)s'), 'install']
    )
