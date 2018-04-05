from buildbot import locks

slave_cpu_lock = locks.SlaveLock(
    'slave_cpu_lock',
    maxCount = 1
)

master_upload_lock = locks.MasterLock(
    'master_upload_lock'
)

def skipped_or_success(results, step):
    from buildbot.status.results import SKIPPED
    from buildbot.status.results import SUCCESS

    return ((results == SKIPPED) or (results == SUCCESS))

def skipped(results, step):
    from buildbot.status.results import SKIPPED

    return (results == SKIPPED)

def get_cmake_step(link, type, options = []):
    from buildbot.process.properties import Interpolate
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

    build_frameworks = ''
    build_target = ''
    build_sdk = ''
    suffix = ''

    if 'frameworks' in options:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=TRUE'
        suffix = [link, type, 'frameworks']
    else:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=FALSE'
        suffix = [link, type]

    if 'newSDK' in options:
        build_target += '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.11'
        # the SDK is set by CMake
        suffix.append('10.11')

    if 'android' in options:
        build_target += '-DANDROID_ABI=armeabi-v7a'
        build_sdk += '-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/android.toolchain.cmake'

    if 'ios' in options:
        build_sdk += '-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/iOS.toolchain.cmake'

    configure_command = ['cmake', '-G', Interpolate('%(prop:generator)s'), '-DSFML_BUILD_EXAMPLES=TRUE', Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:workdir)s/install'), Interpolate('-DCMAKE_INSTALL_FRAMEWORK_PREFIX=%(prop:workdir)s/install/Library/Frameworks'), build_type, shared_libs, build_frameworks, build_sdk, build_target, '..']

    if 'scan-build' in options:
        configure_command.insert(0, 'scan-build')

    return ShellCommand(
        name = 'cmake',
        description = ['configuring'],
        descriptionSuffix = suffix,
        descriptionDone = ['configure'],
        doStepIf = lambda step : ('scan-build' in options) or ('android' in options) or ('ios' in options) or (((not options) or ('osx' in step.build.getProperty('buildername'))) and (link != 'static' or not ('osx' in step.build.getProperty('buildername')))),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:workdir)s/build/build'),
        command = configure_command,
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s')
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_build_step(link, type, options = []):
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import Compile

    suffix = ''
    target = 'install'

    if 'frameworks' in options:
        suffix = [link, type, 'frameworks']
    else:
        suffix = [link, type]

    if 'newSDK' in options:
        suffix.append('10.11')
        target = 'all'

    if 'scan-build' in options:
        target = 'all'

    build_command = 'cmake --build . --target ' + target

    if 'scan-build' in options:
        build_command = 'scan-build ' + build_command

    if 'Makefiles' in [Interpolate('%(prop:generator)s')]:
        build_command += [' -- -j' + Interpolate('%(prop:parallel)s')]
    else:
        # Not Makefiles, likely a multi-target generator (Xcode, VS, etc.)
        # so we must specify buid config now
        if type == 'debug':
            build_command += ' --config Debug'
        else:
            build_command += ' --config Release'

    return Compile(
        description = ['building'],
        descriptionSuffix = suffix,
        descriptionDone = ['build'],
        doStepIf = lambda step : ('scan-build' in options) or ('android' in options) or ('ios' in options) or (((not options) or ('osx' in step.build.getProperty('buildername'))) and (link != 'static' or not ('osx' in step.build.getProperty('buildername')))),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:workdir)s/build/build'),
        locks = [slave_cpu_lock.access('counting')],
        command = build_command,
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s')
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_env_step():
    from buildbot.steps.slave import SetPropertiesFromEnv

    return [SetPropertiesFromEnv(variables = ['PATH'], hideStepIf = skipped_or_success)]

def get_clone_step():
    from buildbot.steps.source.git import Git
    from buildbot.process.properties import Interpolate

    return [
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
        )
    ]

def get_configuration_build_steps(link, type, options = []):
    from buildbot.steps.slave import RemoveDirectory
    from buildbot.steps.slave import MakeDirectory
    from buildbot.process.properties import Interpolate

    return [
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : (bool(options) and ('osx' in step.build.getProperty('buildername'))),
            hideStepIf = skipped_or_success
        ),
        get_cmake_step(link, type, options),
        get_build_step(link, type, options),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:workdir)s/build/build'),
            doStepIf = lambda step : (bool(options) and ('osx' in step.build.getProperty('buildername'))),
            hideStepIf = skipped_or_success
        )
    ]

def get_android_patch_steps(string, replacement, file):
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = 'patch',
            description = ['patching'],
            descriptionDone = ['patch'],
            hideStepIf = skipped_or_success,
            workdir = Interpolate('%(prop:workdir)s/build'),
            command = Interpolate('sed -i.bak s@' + string + '@' + replacement + '@g ' + file),
            env = {
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')
            },
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        )
    ]

def get_android_example_build_steps(name, description, command):
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = name,
            description = [description],
            descriptionDone = [name],
            workdir = Interpolate('%(prop:workdir)s/build/examples/android'),
            command = Interpolate(command),
            env = {
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
                'NDK_MODULE_PATH' : Interpolate('%(prop:workdir)s/install')
            },
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        )
    ]

def get_cppcheck_steps():
    from buildbot.steps.shell import Compile

    return [
        Compile(
            name = 'cppcheck',
            description = ['cppcheck'],
            descriptionDone = ['cppcheck'],
            command = ['cppcheck', '--std=c++03', '--enable=all', '--inconclusive', '--suppress=unusedFunction', '--suppress=functionStatic', '--suppress=functionConst', '--suppress=noExplicitConstructor', '--suppress=variableHidingTypedef', '--suppress=missingInclude', '--force', '-q', '--template={file}:{line}: warning: ({severity}) {message}', '-I', 'include', '-I', 'src', 'src', 'examples'],
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        )
    ]

def get_artifact_step():
    from buildbot.process.properties import Interpolate
    from buildbot.steps.transfer import DirectoryUpload
    from buildbot.steps.master import MasterShellCommand

    return [
        DirectoryUpload(
            description = ['uploading'],
            descriptionSuffix = ['artifact'],
            descriptionDone = ['upload'],
            slavesrc = Interpolate('%(prop:workdir)s/install'),
            masterdest = Interpolate('%(prop:buildername)s/tmp/%(prop:got_revision)s'),
            compress = 'gz',
            locks = [master_upload_lock.access('exclusive')],
            doStepIf = lambda step : (step.build.getProperty('artifact') and ('external' not in step.build.getProperty('trigger'))),
            hideStepIf = skipped_or_success
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : (step.build.getProperty('artifact') and ('external' not in step.build.getProperty('trigger'))),
            hideStepIf = skipped_or_success,
            command = Interpolate(
                'mkdir -p artifacts/by-revision/%(prop:got_revision)s && '
                'mkdir -p artifacts/by-branch/%(src::branch:-master)s && '
                'cd %(prop:buildername)s/tmp && '
                '%(prop:archive_command)s %(prop:buildername)s%(prop:artifact_extension)s %(prop:got_revision)s/ && '
                'mv %(prop:buildername)s%(prop:artifact_extension)s ../../artifacts/by-revision/%(prop:got_revision)s && '
                'ln -f ../../artifacts/by-revision/%(prop:got_revision)s/%(prop:buildername)s%(prop:artifact_extension)s ../../artifacts/by-branch/%(src::branch:-master)s/%(prop:buildername)s%(prop:artifact_extension)s && '
                'chmod -R a+rX ../../artifacts/by-revision/%(prop:got_revision)s && '
                'chmod -R a+rX ../../artifacts/by-branch/%(src::branch:-master)s'
            )
        ),
        MasterShellCommand(
            name = 'clean master',
            description = ['cleaning master'],
            descriptionDone = ['clean master'],
            alwaysRun = True,
            hideStepIf = skipped_or_success,
            command = Interpolate(
                'rm -rf "%(prop:buildername)s/tmp"'
            )
        )
    ]

def get_clean_step():
    from buildbot.steps.slave import RemoveDirectory
    from buildbot.process.properties import Interpolate

    return [
        RemoveDirectory(
            name = 'clean slave',
            description = ['cleaning slave'],
            descriptionDone = ['clean slave'],
            dir = Interpolate('%(prop:workdir)s'),
            alwaysRun = True,
            hideStepIf = skipped_or_success
        )
    ]

def get_build_factory(builder_name):
    from buildbot.process.factory import BuildFactory

    steps = []

    steps.extend(get_env_step())

    steps.extend(get_clone_step())

    if('static-analysis' in builder_name):
        steps.extend([
            get_cmake_step('static', 'debug', ['scan-build']),
            get_build_step('static', 'debug', ['scan-build'])
        ])

        steps.extend(get_cppcheck_steps())
    elif('android' in builder_name):
        steps.extend(get_android_patch_steps('\${ANDROID_NDK}/sources', '%(prop:workdir)s/install', 'CMakeLists.txt'))
        steps.extend(get_android_patch_steps('\${ANDROID_NDK}/sources', '%(prop:workdir)s/install', 'cmake/Config.cmake'))

        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['android']))
        steps.extend(get_configuration_build_steps('static', 'release', ['android']))

        steps.extend(get_android_example_build_steps('create example project', 'creating example project', 'android update project --target `android list target -c | tail -n 1` --path .'))
        steps.extend(get_android_example_build_steps('ndk-build example project', 'ndk-building example project', 'ndk-build'))
        steps.extend(get_android_example_build_steps('build debug example project', 'building debug example project', 'ant debug'))
        steps.extend(get_android_example_build_steps('build release example project', 'building release example project', 'ant release'))
        steps.extend(get_android_example_build_steps('archive example project', 'archiving example project', 'cp bin/*-debug.apk %(prop:workdir)s/install/. && cp bin/*-release-unsigned.apk %(prop:workdir)s/install/.'))

        steps.extend(get_artifact_step())
    elif('ios' in builder_name):
       # Only static on ios
        steps.extend(get_configuration_build_steps('static', 'debug', ['ios']))
        steps.extend(get_configuration_build_steps('static', 'release', ['ios']))
    else:
        steps.extend(get_configuration_build_steps('dynamic', 'debug'))
        steps.extend(get_configuration_build_steps('static', 'debug'))
        steps.extend(get_configuration_build_steps('dynamic', 'release'))
        steps.extend(get_configuration_build_steps('static', 'release'))

        steps.extend(get_configuration_build_steps('dynamic', 'release', ['frameworks']))
        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['newSDK']))

        steps.extend(get_artifact_step())

    steps.extend(get_clean_step())

    factory = BuildFactory(steps)

    return factory
