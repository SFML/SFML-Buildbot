def get_cmake_step(link, type, osxExtra = []):
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import ShellCommand
    from buildbot.status.results import SKIPPED

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

    build_frameworks = ''
    build_target = ''
    build_sdk = ''
    suffix = ''

    if 'frameworks' in osxExtra:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=TRUE'
        suffix = [link, type, 'frameworks']
    else:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=FALSE'
        suffix = [link, type]

    if 'oldSDK' in osxExtra:
        build_target += '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.7'
        build_sdk += '-DCMAKE_OSX_SYSROOT=/Developer/SDKs/MacOSX10.7.sdk'
        suffix.append('10.7')

    return ShellCommand(
        name = 'cmake',
        description = ['configuring'],
        descriptionSuffix = suffix,
        descriptionDone = ['configure'],
        doStepIf = lambda step : ((not osxExtra) or ('osx' in step.build.getProperty('buildername'))) and (link != 'static' or not ('osx' in step.build.getProperty('buildername'))),
        hideStepIf = lambda results, step : results == SKIPPED,
        workdir = Interpolate('%(prop:workdir)s/build/build'),
        command = ['cmake', '-G', Interpolate('%(prop:generator)s'), '-DSFML_BUILD_EXAMPLES=TRUE', Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:workdir)s/install'), Interpolate('-DCMAKE_INSTALL_FRAMEWORK_PREFIX=%(prop:workdir)s/install/Library/Frameworks'), build_type, shared_libs, build_frameworks, build_sdk, build_target, '..'],
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s'),
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_build_step(link, type, osxExtra = []):
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import Compile
    from buildbot.status.results import SKIPPED

    suffix = ''
    target = 'install'

    if 'frameworks' in osxExtra:
        suffix = [link, type, 'frameworks']
    else:
        suffix = [link, type]

    if 'oldSDK' in osxExtra:
        suffix.append('10.7')
        target = 'all'

    return Compile(
        description = ['building'],
        descriptionSuffix = suffix,
        descriptionDone = ['build'],
        doStepIf = lambda step : ((not osxExtra) or ('osx' in step.build.getProperty('buildername'))) and (link != 'static' or not ('osx' in step.build.getProperty('buildername'))),
        hideStepIf = lambda results, step : results == SKIPPED,
        workdir = Interpolate('%(prop:workdir)s/build/build'),
        command = [Interpolate('%(prop:maker)s'), '-j', Interpolate('%(prop:parallel)s'), target],
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s'),
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )


def get_build_factory():
    from buildbot.steps.slave import SetPropertiesFromEnv
    from buildbot.process.factory import BuildFactory
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import ShellCommand
    from buildbot.steps.source.git import Git
    from buildbot.steps.transfer import DirectoryUpload
    from buildbot.steps.slave import RemoveDirectory
    from buildbot.steps.slave import MakeDirectory
    from buildbot.steps.master import MasterShellCommand
    from buildbot.status.results import SKIPPED

    steps = [
        SetPropertiesFromEnv(
            variables = ['PATH'],
            hideStepIf = True
        ),
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            repourl = Interpolate('%(prop:repository)s'),
            mode = 'full',
            shallow = True,
            method = 'clobber',
            retry = (1, 120),
            progress = True,
            env = {
                'GIT_CURL_VERBOSE' : '1',
                'GIT_TRACE' : '1'
            },
            logEnviron = False
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        get_cmake_step('dynamic', 'debug'),
        get_build_step('dynamic', 'debug'),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        get_cmake_step('static', 'debug'),
        get_build_step('static', 'debug'),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        get_cmake_step('dynamic', 'release'),
        get_build_step('dynamic', 'release'),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        get_cmake_step('static', 'release'),
        get_build_step('static', 'release'),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build')
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : ('osx' in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        get_cmake_step('dynamic', 'release', ['frameworks']),
        get_build_step('dynamic', 'release', ['frameworks']),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : ('osx' in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : ('osx' in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        get_cmake_step('dynamic', 'debug', ['oldSDK']),
        get_build_step('dynamic', 'debug', ['oldSDK']),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : ('osx' in step.build.getProperty('buildername')),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        DirectoryUpload(
            description = ['uploading'],
            descriptionSuffix = ['artifact'],
            descriptionDone = ['upload'],
            slavesrc = Interpolate('%(prop:workdir)s/install'),
            masterdest = Interpolate('%(prop:buildername)s/tmp/%(prop:got_revision)s'),
            compress = 'bz2',
            doStepIf = lambda step : (('https://github.com/SFML/SFML.git' in step.build.getProperty('repository')) and ('freebsd' not in step.build.getProperty('buildername'))),
            hideStepIf = lambda results, step : results == SKIPPED,
        ),
        RemoveDirectory(
            name = 'clean slave',
            description = ['cleaning slave'],
            descriptionDone = ['clean slave'],
            dir = Interpolate('%(prop:workdir)s'),
            alwaysRun = True,
            hideStepIf = True
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : (('https://github.com/SFML/SFML.git' in step.build.getProperty('repository')) and ('windows' in step.build.getProperty('buildername'))),
            hideStepIf = True, # lambda results, step : results == SKIPPED,
            command = Interpolate(
                'mkdir -p artifacts/by-revision/%(prop:got_revision)s && '
                'mkdir -p artifacts/by-branch/%(src::branch:-master)s && '
                'cd %(prop:buildername)s/tmp && '
                'zip -r %(prop:buildername)s.zip %(prop:got_revision)s && '
                'mv %(prop:buildername)s.zip ../../artifacts/by-revision/%(prop:got_revision)s && '
                'ln -f ../../artifacts/by-revision/%(prop:got_revision)s/%(prop:buildername)s.zip ../../artifacts/by-branch/%(src::branch:-master)s/%(prop:buildername)s.zip && '
                'chmod -R a+rX ../../artifacts/by-revision/%(prop:got_revision)s && '
                'chmod -R a+rX ../../artifacts/by-branch/%(src::branch:-master)s && '
            )
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : (('https://github.com/SFML/SFML.git' in step.build.getProperty('repository')) and (('windows' not in step.build.getProperty('buildername')) and ('freebsd' not in step.build.getProperty('buildername')))),
            hideStepIf = True, # lambda results, step : results == SKIPPED,
            command = Interpolate(
                'mkdir -p artifacts/by-revision/%(prop:got_revision)s && '
                'mkdir -p artifacts/by-branch/%(src::branch:-master)s && '
                'cd %(prop:buildername)s/tmp && '
                'tar czf %(prop:buildername)s.tar.gz %(prop:got_revision)s/ && '
                'mv %(prop:buildername)s.tar.gz ../../artifacts/by-revision/%(prop:got_revision)s && '
                'ln -f ../../artifacts/by-revision/%(prop:got_revision)s/%(prop:buildername)s.tar.gz ../../artifacts/by-branch/%(src::branch:-master)s/%(prop:buildername)s.tar.gz && '
                'chmod -R a+rX ../../artifacts/by-revision/%(prop:got_revision)s && '
                'chmod -R a+rX ../../artifacts/by-branch/%(src::branch:-master)s && '
            )
        ),
        MasterShellCommand(
            name = 'clean master',
            description = ['cleaning master'],
            descriptionDone = ['clean master'],
            alwaysRun = True,
            hideStepIf = True,
            command = Interpolate(
                'rm -rf "%(prop:buildername)s/tmp"'
            )
        )
    ]

    factory = BuildFactory(steps)

    return factory

def get_static_analysis_build_factory():
    from buildbot.steps.source.git import Git
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import ShellCommand
    from buildbot.steps.shell import Compile
    from buildbot.steps.slave import RemoveDirectory
    from buildbot.process.factory import BuildFactory

    steps = [
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            repourl = Interpolate('%(prop:repository)s'),
            mode = 'full',
            shallow = True,
            method = 'clobber',
            retry = (1, 120),
            progress = True,
            env = {
                'GIT_CURL_VERBOSE' : '1',
                'GIT_TRACE' : '1'
            },
            logEnviron = False
        ),
        ShellCommand(
            name = 'scan-build configure',
            description = ['scan-build configuring'],
            descriptionDone = ['scan-build configure'],
            command = ['scan-build', 'cmake', '-G', 'Unix Makefiles', '-DSFML_BUILD_EXAMPLES=TRUE', Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:workdir)s/install'), '-DCMAKE_BUILD_TYPE=Debug', '-DBUILD_SHARED_LIBS=FALSE', '.'],
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        Compile(
            name = 'scan-build make',
            description = ['scan-build building'],
            descriptionDone = ['scan-build make'],
            command = ['scan-build', 'make', '-j', Interpolate('%(prop:parallel)s')],
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        Compile(
            name = 'cppcheck',
            description = ['cppcheck'],
            descriptionDone = ['cppcheck'],
            command = ['cppcheck', '--std=c++03', '--enable=all', '--inconclusive', '--suppress=unusedFunction', '--suppress=functionStatic', '--suppress=functionConst', '--suppress=noExplicitConstructor', '--suppress=variableHidingTypedef', '--suppress=missingInclude', '--force', '-q', '--template={file}:{line}: warning: ({severity}) {message}', '-I', 'include', '-I', 'src', 'src', 'examples'],
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        RemoveDirectory(
            name = 'clean',
            description = ['cleaning slave'],
            descriptionDone = ['clean slave'],
            dir = Interpolate('%(prop:workdir)s'),
            alwaysRun = True,
            hideStepIf = True
        )
    ]

    factory = BuildFactory(steps)

    return factory
