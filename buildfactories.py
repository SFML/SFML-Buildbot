def skipped_or_success(results, step):
    from buildbot.status.builder import SKIPPED
    from buildbot.status.builder import SUCCESS

    return ((results == SKIPPED) or (results == SUCCESS))

def skipped(results, step):
    from buildbot.status.builder import SKIPPED

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
    build_ndk = ''
    build_ndk_toolchain_version = ''
    build_stl_type = ''
    build_android_api = ''
    build_stdlib = ''
    build_c_compiler = ''
    build_cxx_compiler = ''
    install_prefix = Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:builddir)s/install')
    frameworks_install_directory = Interpolate('')
    misc_install_directory = Interpolate('')
    macos_architecture = Interpolate('')
    ios_platform = ''
    suffix = ''

    if 'frameworks' in options:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=TRUE'
        suffix = [link, type, 'frameworks']
    else:
        build_frameworks += '-DSFML_BUILD_FRAMEWORKS=FALSE'
        suffix = [link, type]

    if 'newSDK' in options:
        build_target += '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.15'
        # the SDK is set by CMake
        suffix.append('10.15')

    if 'android' in options:
        build_target += '-DCMAKE_ANDROID_ARCH_ABI=armeabi-v7a'
        build_sdk += '-DCMAKE_SYSTEM_NAME=Android'
        build_ndk = Interpolate('-DCMAKE_ANDROID_NDK=%(prop:ANDROID_NDK_HOME)s')
        build_ndk_toolchain_version += '-DCMAKE_ANDROID_NDK_TOOLCHAIN_VERSION=clang'
        build_stl_type += '-DCMAKE_ANDROID_STL_TYPE=c++_shared'
        build_android_api += '-DCMAKE_ANDROID_API=26'

    if 'ios' in options:
        build_sdk += '-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/iOS.toolchain.cmake'
        ios_platform = '-DIOS_PLATFORM=SIMULATOR'

    if 'macos' in options:
        install_prefix = Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:builddir)s/install/Library/Frameworks')
        frameworks_install_directory = Interpolate('-DSFML_DEPENDENCIES_INSTALL_PREFIX=%(prop:builddir)s/install/Library/Frameworks')
        misc_install_directory = Interpolate('-DSFML_MISC_INSTALL_PREFIX=%(prop:builddir)s/install/share/SFML')
        macos_architecture = Interpolate('-DCMAKE_OSX_ARCHITECTURES=%(prop:architecture)s')

    if 'clang' in options:
        build_c_compiler += '-DCMAKE_C_COMPILER=clang'
        build_cxx_compiler += '-DCMAKE_CXX_COMPILER=clang++'
        build_stdlib += '-DCMAKE_CXX_FLAGS="-stdlib=libc++"'

    configure_command = [
        'cmake',
        '-G',
        Interpolate('%(prop:generator)s'),
        '-DSFML_BUILD_EXAMPLES=TRUE',
        Interpolate('-DSFML_BUILD_TEST_SUITE=%(prop:run_tests)s'),
        macos_architecture,
        ios_platform,
        install_prefix,
        frameworks_install_directory,
        misc_install_directory,
        build_type,
        shared_libs,
        build_frameworks,
        build_sdk,
        build_ndk,
        build_ndk_toolchain_version,
        build_stl_type,
        build_android_api,
        build_c_compiler,
        build_cxx_compiler,
        build_stdlib,
        build_target,
        '..'
    ]

    if 'scan-build' in options:
        configure_command.insert(0, 'scan-build')

    return ShellCommand(
        name = 'configure (' + link + ' ' + type + ')',
        description = ['configuring'],
        descriptionSuffix = suffix,
        descriptionDone = ['configure'],
        doStepIf = lambda step : ('scan-build' in options) or ('android' in options) or ('ios' in options) or ('clang' in options) or (((not options) or ('macos' in step.build.getProperty('buildername'))) and (link != 'static' or not ('macos' in step.build.getProperty('buildername')))),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:builddir)s/build/build'),
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
        suffix.append('10.15')
        target = 'all'

    if 'scan-build' in options:
        target = 'all'

    build_command = 'cmake --build . --target ' + target

    # For multi-target generators (Xcode, VS, etc.) we must specify the build configuration
    if type == 'debug':
        build_command += ' --config Debug'
    else:
        build_command += ' --config Release'

    # iOS build uses arch arm64
    # if 'ios' in options:
    #     build_command += ' -- -arch arm64'

    if 'scan-build' in options:
        build_command = 'scan-build ' + build_command

    return Compile(
        name = 'build (' + link + ' ' + type + ')',
        description = ['building'],
        descriptionSuffix = suffix,
        descriptionDone = ['build'],
        doStepIf = lambda step : ('scan-build' in options) or ('android' in options) or ('ios' in options) or ('clang' in options) or (((not options) or ('macos' in step.build.getProperty('buildername'))) and (link != 'static' or not ('macos' in step.build.getProperty('buildername')))),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:builddir)s/build/build'),
        command = Interpolate('%(kw:command)s %(prop:makefile:#?| -- -k -j %(prop:parallel)s|)s', command = build_command),
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
    from buildbot.steps.worker import SetPropertiesFromEnv

    return [SetPropertiesFromEnv(variables = ['PATH', "ANDROID_HOME", "ANDROID_NDK_HOME"], hideStepIf = skipped_or_success)]

def extract_vs_paths(rc, stdout, stderr):
    toolchain_path = ''
    vc_include = ''
    vc_lib = ''
    vc_libpath = ''

    for var in stdout.strip().split('\n'):
        var = var.split('=', 1)

        if var[0].strip().upper() == 'PATH':
            toolchain_path = var[1].strip()
        elif var[0].strip().upper() == 'INCLUDE':
            vc_include = var[1].strip()
        elif var[0].strip().upper() == 'LIB':
            vc_lib = var[1].strip()
        elif var[0].strip().upper() == 'LIBPATH':
            vc_libpath = var[1].strip()

    return {
        'toolchain_path' : toolchain_path,
        'vc_include' : vc_include,
        'vc_lib' : vc_lib,
        'vc_libpath' : vc_libpath
    }

def get_vs_env_step():
    from buildbot.steps.shell import SetPropertyFromCommand
    from buildbot.process.properties import Interpolate

    return [SetPropertyFromCommand(env = {'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')}, command = Interpolate('vcvarsall.bat %(prop:architecture)s > nul && set'), extract_fn = extract_vs_paths)]

def get_clone_step():
    from buildbot.steps.source.git import Git
    from buildbot.steps.master import SetProperty
    from buildbot.process.properties import Interpolate

    return [
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            repourl = Interpolate('%(prop:repository)s'),
            mode = 'full',
            shallow = 16,
            method = 'clobber',
            getDescription = {
                'tags' : True
            },
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
    from buildbot.steps.worker import RemoveDirectory
    from buildbot.steps.worker import MakeDirectory
    from buildbot.process.properties import Interpolate

    return [
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            doStepIf = lambda step : (bool(options) and ('macos' in step.build.getProperty('buildername'))),
            hideStepIf = skipped_or_success
        ),
        get_cmake_step(link, type, options),
        get_build_step(link, type, options),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            doStepIf = lambda step : (bool(options) and ('macos' in step.build.getProperty('buildername'))),
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
            workdir = Interpolate('%(prop:builddir)s/build'),
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
            workdir = Interpolate('%(prop:builddir)s/build/examples/android'),
            command = Interpolate(command),
            env = {
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
                'NDK_MODULE_PATH' : Interpolate('%(prop:builddir)s/install')
            },
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        )
    ]

def get_cppcheck_steps():
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import Compile

    return [
        Compile(
            name = 'cppcheck',
            description = ['cppcheck'],
            descriptionDone = ['cppcheck'],
            command = ['cppcheck', Interpolate('-j %(prop:parallel)s'), '--std=c++11', '--enable=all', '--inconclusive', '--suppress=unusedFunction', '--suppress=functionStatic', '--suppress=functionConst', '--suppress=noConstructor', '--suppress=noExplicitConstructor', '--suppress=missingInclude', '--force', '-q', '--template={file}:{line}: warning: ({severity}) {message}', '-DSFML_SYSTEM_API=', '-DSFML_NETWORK_API=', '-DSFML_AUDIO_API=', '-DSFML_WINDOW_API=', '-DSFML_GRAPHICS_API=', '-I', 'include', '-I', 'src', 'src', 'examples'],
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
            workersrc = Interpolate('%(prop:builddir)s/install'),
            masterdest = Interpolate('%(prop:buildername)s/tmp/%(prop:got_revision)s'),
            compress = 'gz',
            doStepIf = lambda step : (step.build.getProperty('artifact') and ('refs/pull/' not in step.build.getProperty('branch'))),
            hideStepIf = skipped_or_success
        ),
        MasterShellCommand(
            name = 'artifact',
            description = ['creating artifact'],
            descriptionDone = ['create artifact'],
            doStepIf = lambda step : (step.build.getProperty('artifact') and ('refs/pull/' not in step.build.getProperty('branch'))),
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
    from buildbot.steps.worker import RemoveDirectory
    from buildbot.process.properties import Interpolate

    return [
        RemoveDirectory(
            name = 'clean slave',
            description = ['cleaning slave'],
            descriptionDone = ['clean slave'],
            dir = Interpolate('%(prop:builddir)s'),
            alwaysRun = True,
            hideStepIf = skipped_or_success
        )
    ]

def get_build_factory(builder_name):
    from buildbot.process.factory import BuildFactory

    steps = []

    steps.extend(get_env_step())

    if('windows-vc' in builder_name):
        steps.extend(get_vs_env_step())

    steps.extend(get_clone_step())

    if('static-analysis' in builder_name):
        steps.extend([
            get_cmake_step('static', 'debug', ['scan-build']),
            get_build_step('static', 'debug', ['scan-build'])
        ])

        steps.extend(get_cppcheck_steps())
    elif('android' in builder_name):
        steps.extend(get_android_patch_steps('\${CMAKE_ANDROID_NDK}/sources/third_party', '%(prop:builddir)s/install', 'CMakeLists.txt'))
        steps.extend(get_android_patch_steps('\${CMAKE_ANDROID_NDK}/sources/third_party', '%(prop:builddir)s/install', 'cmake/Config.cmake'))
        steps.extend(get_android_patch_steps('third_party/sfml', 'sfml', 'examples/android/app/src/main/jni/Android.mk'))
        steps.extend(get_android_patch_steps('third_party/sfml', 'sfml', 'src/SFML/Android.mk'))
        steps.extend(get_android_patch_steps('gradle:3.0.0', 'gradle:7.0.0', 'examples/android/build.gradle'))
        steps.extend(get_android_patch_steps('targetSdkVersion\ 19', 'targetSdkVersion\ 29', 'examples/android/app/build.gradle'))

        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['android']))
        steps.extend(get_configuration_build_steps('static', 'release', ['android']))

        #steps.extend(get_android_example_build_steps('create example project', 'creating example project', 'android update project --target `android list target -c | tail -n 1` --path .'))
        #steps.extend(get_android_example_build_steps('ndk-build example project', 'ndk-building example project', 'ndk-build'))
        #steps.extend(get_android_example_build_steps('build debug example project', 'building debug example project', 'ant debug'))
        #steps.extend(get_android_example_build_steps('build release example project', 'building release example project', 'ant release'))
        steps.extend(get_android_example_build_steps('build debug example project', 'building debug example project', 'gradle assembleDebug'))
        steps.extend(get_android_example_build_steps('build release example project', 'building release example project', 'gradle assembleRelease'))
        #steps.extend(get_android_example_build_steps('archive example project', 'archiving example project', 'cp bin/*-debug.apk %(prop:builddir)s/install/. && cp bin/*-release-unsigned.apk %(prop:builddir)s/install/.'))
        steps.extend(get_android_example_build_steps('archive debug example project', 'archiving debug example project', 'cp app/build/outputs/apk/debug/*-debug.apk %(prop:builddir)s/install/.'))
        steps.extend(get_android_example_build_steps('archive release example project', 'archiving release example project', 'cp app/build/outputs/apk/release/*-release-unsigned.apk %(prop:builddir)s/install/.'))

        steps.extend(get_artifact_step())
    elif('ios' in builder_name):
       # Only static on ios
        steps.extend(get_configuration_build_steps('static', 'debug', ['ios']))
        steps.extend(get_configuration_build_steps('static', 'release', ['ios']))
    elif('macos' in builder_name):
        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['macos']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['macos']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['macos']))
        steps.extend(get_configuration_build_steps('static', 'release', ['macos']))

        steps.extend(get_configuration_build_steps('dynamic', 'release', ['macos', 'frameworks']))
        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['macos', 'newSDK']))

        steps.extend(get_artifact_step())
    elif('debian-clang' in builder_name):
        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['clang']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['clang']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['clang']))
        steps.extend(get_configuration_build_steps('static', 'release', ['clang']))

        steps.extend(get_artifact_step())
    else:
        steps.extend(get_configuration_build_steps('dynamic', 'debug'))
        steps.extend(get_configuration_build_steps('static', 'debug'))
        steps.extend(get_configuration_build_steps('dynamic', 'release'))
        steps.extend(get_configuration_build_steps('static', 'release'))

        steps.extend(get_artifact_step())

    steps.extend(get_clean_step())

    factory = BuildFactory(steps)

    return factory
