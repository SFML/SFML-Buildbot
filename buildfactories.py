def skipped_or_success(results, step):
    from buildbot.process.results import SKIPPED
    from buildbot.process.results import SUCCESS

    return ((results == SKIPPED) or (results == SUCCESS))

def skipped(results, step):
    from buildbot.process.results import SKIPPED

    return (results == SKIPPED)

def get_cmake_step(link, type, options = [], flag = None):
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
    build_system_version = ''
    build_stdlib = ''
    build_c_compiler = ''
    build_cxx_compiler = ''
    exportcommands = ''
    install_prefix = Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:builddir)s/install')
    frameworks_install_directory = ''
    misc_install_directory = ''
    architecture = ''
    ios_platform = ''
    generator = Interpolate('%(prop:generator)s')
    suffix = ''
    build_tests = Interpolate('-DSFML_BUILD_TEST_SUITE=%(prop:build_tests)s')
    display_tests = Interpolate('-DSFML_RUN_DISPLAY_TESTS=%(prop:display_tests)s')
    audio_device_tests = Interpolate('-DSFML_RUN_AUDIO_DEVICE_TESTS=%(prop:audio_device_tests)s')

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
        architecture = Interpolate('-DCMAKE_ANDROID_ARCH_ABI=%(prop:architecture)s')
        install_prefix = Interpolate('')
        build_sdk = Interpolate('-DCMAKE_SYSTEM_NAME=Android')
        build_ndk = Interpolate('-DCMAKE_ANDROID_NDK=%(prop:ANDROID_NDK_ROOT)s')
        build_ndk_toolchain_version += '-DCMAKE_ANDROID_NDK_TOOLCHAIN_VERSION=clang'
        build_stl_type += '-DCMAKE_ANDROID_STL_TYPE=c++_shared'
        build_system_version = Interpolate('-DCMAKE_SYSTEM_VERSION=%(prop:api)s')
        build_tests = Interpolate('-DSFML_BUILD_TEST_SUITE=%(prop:gradlew_exists:#?|%(prop:build_tests)s|False)s')
        display_tests = Interpolate('-DSFML_RUN_DISPLAY_TESTS=%(prop:gradlew_exists:#?|%(prop:display_tests)s|False)s')
        audio_device_tests = Interpolate('-DSFML_RUN_AUDIO_DEVICE_TESTS=%(prop:gradlew_exists:#?|%(prop:audio_device_tests)s|False)s')

    if 'ios' in options:
        build_sdk = Interpolate('%(prop:ios_toolchain_cmake_exists:#?|-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/iOS.toolchain.cmake|-DCMAKE_SYSTEM_NAME=iOS)s')
        architecture = Interpolate('%(prop:ios_toolchain_cmake_exists:#?||-DCMAKE_OSX_ARCHITECTURES=%(prop:architecture)s)s')
        ios_platform = Interpolate('%(prop:ios_toolchain_cmake_exists:#?|-DIOS_PLATFORM=SIMULATOR|)s')
        generator = Interpolate('%(prop:ios_toolchain_cmake_exists:#?|Xcode|%(prop:generator)s)s')

    if 'macos' in options:
        install_prefix = Interpolate('-DCMAKE_INSTALL_PREFIX=%(prop:builddir)s/install/Library/Frameworks')
        frameworks_install_directory = Interpolate('-DSFML_DEPENDENCIES_INSTALL_PREFIX=%(prop:builddir)s/install/Library/Frameworks')
        misc_install_directory = Interpolate('-DSFML_MISC_INSTALL_PREFIX=%(prop:builddir)s/install/share/SFML')
        architecture = Interpolate('-DCMAKE_OSX_ARCHITECTURES=%(prop:architecture)s')

    if ('clang' in options) or ('clang-tidy' in options):
        build_c_compiler += '-DCMAKE_C_COMPILER=clang'
        build_cxx_compiler += '-DCMAKE_CXX_COMPILER=clang++'
        build_stdlib += '-DCMAKE_CXX_FLAGS="-stdlib=libc++"'

    if 'clang-tidy' in options:
        exportcommands += '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'

    if 'drm' in options:
        build_target += '-DSFML_USE_DRM=TRUE'

    configure_command = [
        'cmake',
        '-G',
        generator,
        '-DCMAKE_VERBOSE_MAKEFILE=ON',
        '-DSFML_USE_MESA3D=ON',
        '-DCMAKE_CXX_EXTENSIONS=OFF',
        '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
        '-DSFML_BUILD_EXAMPLES=ON',\
        '-DSFML_ENABLE_STDLIB_ASSERTIONS=ON',
        '-DSFML_WARNINGS_AS_ERRORS=ON',
        build_tests,
        display_tests,
        audio_device_tests,
        architecture,
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
        build_system_version,
        build_c_compiler,
        build_cxx_compiler,
        build_stdlib,
        build_target,
        exportcommands,
        '..'
    ]

    configure_command = list(filter(None, configure_command))

    return ShellCommand(
        name = 'configure (' + link + ' ' + type + ')',
        description = ['configuring'],
        descriptionSuffix = suffix,
        descriptionDone = ['configure'],
        doStepIf = lambda step : (flag is None) or step.build.getProperty(flag),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:builddir)s/build/build'),
        command = configure_command,
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s'),
            'LIBCXX_SHARED_SO' : Interpolate('%(prop:LIBCXX_SHARED_SO)s')
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_build_step(link, type, options = [], flag = None):
    from buildbot.process.properties import Interpolate
    from buildbot.steps.shell import Compile

    compile_command = ''
    suffix = ''
    target = 'install'

    if 'frameworks' in options:
        suffix = [link, type, 'frameworks']
    else:
        suffix = [link, type]

    if 'newSDK' in options:
        suffix.append('10.15')
        target = 'all'

    if 'coverity' in options:
        target = 'all'

    if 'clang-tidy' in options:
        target = 'tidy'

    build_command = 'cmake --build .'

    if 'coverity' in options:
        build_command = 'cov-build --dir cov-int ' + build_command

    # For multi-target generators (Xcode, VS, etc.) we must specify the build configuration
    if type == 'debug':
        build_command += ' --config Debug'
    else:
        build_command += ' --config Release'

    build_command += ' --target ' + target

    if 'android' in options:
        test_command = ' && cmake --build . --target prepare-android-files 2>&1'

        if type == 'debug':
            test_command += ' --config Debug'
        else:
            test_command += ' --config Release'

        test_command += ' && ctest --test-dir . --output-on-failure --repeat until-pass:3'

        if type == 'debug':
            test_command += ' -C Debug'
        else:
            test_command += ' -C Release'

        compile_command = Interpolate('%(kw:build)s %(prop:makefile:#?| -- -k -j %(prop:parallel)s|)s %(prop:gradlew_exists:#?|%(prop:run_tests:#?| && adb connect %(prop:android_tester)s %(kw:test)s|)s|)s', build = build_command, test = test_command)
    else:
        compile_command = Interpolate('%(kw:command)s %(prop:run_tests:#?|runtests|)s %(prop:makefile:#?| -- -k -j %(prop:parallel)s|)s', command = build_command)

    return Compile(
        name = 'build (' + link + ' ' + type + ')',
        description = ['building'],
        descriptionSuffix = suffix,
        descriptionDone = ['build'],
        doStepIf = lambda step : (flag is None) or step.build.getProperty(flag),
        hideStepIf = skipped,
        workdir = Interpolate('%(prop:builddir)s/build/build'),
        command = compile_command,
        env = {
            'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s'),
            'INCLUDE' : Interpolate('%(prop:vc_include)s'),
            'LIB' : Interpolate('%(prop:vc_lib)s'),
            'LIBPATH' : Interpolate('%(prop:vc_libpath)s'),
            'LIBCXX_SHARED_SO' : Interpolate('%(prop:LIBCXX_SHARED_SO)s'),
            'GALLIUM_DRIVER': 'llvmpipe'
        },
        want_stdout = True,
        want_stderr = True,
        logEnviron = False
    )

def get_env_step():
    from buildbot.steps.worker import SetPropertiesFromEnv

    return [SetPropertiesFromEnv(variables = ['PATH', "ANDROID_HOME", "ANDROID_NDK_ROOT", "ANDROID_NDK_VERSION"], hideStepIf = skipped_or_success)]

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

    return [SetPropertyFromCommand(hideStepIf = skipped_or_success, env = {'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')}, command = Interpolate('vcvarsall.bat %(prop:architecture)s > nul && set'), extract_fn = extract_vs_paths)]

def get_android_libcxx_step():
    from buildbot.steps.shell import SetPropertyFromCommand
    from buildbot.process.properties import Interpolate

    return [SetPropertyFromCommand(hideStepIf = skipped_or_success, command = Interpolate('find %(prop:ANDROID_NDK_ROOT)s -path */%(prop:android_libcxx)s'), property = 'LIBCXX_SHARED_SO')]

def get_shallow_clone_step():
    from buildbot.steps.source.git import Git
    from buildbot.steps.master import SetProperty
    from buildbot.process.properties import Interpolate

    return [
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            hideStepIf = skipped_or_success,
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

def get_clone_step():
    from buildbot.steps.source.git import Git
    from buildbot.steps.master import SetProperty
    from buildbot.process.properties import Interpolate

    return [
        Git(
            description = ['cloning'],
            descriptionDone = ['clone'],
            hideStepIf = skipped_or_success,
            repourl = Interpolate('%(prop:repository)s'),
            mode = 'full',
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

def get_configuration_build_steps(link, type, options = [], flag = None):
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
        get_cmake_step(link, type, options, flag),
        get_build_step(link, type, options, flag),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            doStepIf = lambda step : (bool(options) and ('macos' in step.build.getProperty('buildername'))),
            hideStepIf = skipped_or_success
        )
    ]

def get_coverity_steps(link, type):
    from buildbot.steps.worker import RemoveDirectory
    from buildbot.steps.worker import MakeDirectory
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate
    import private

    return [
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            hideStepIf = skipped_or_success
        ),
        get_cmake_step(link, type, ['coverity']),
        get_build_step(link, type, ['coverity']),
        ShellCommand(
            name = 'coverity upload',
            description = ['uploading to coverity'],
            descriptionDone = ['upload to coverity'],
            hideStepIf = skipped_or_success,
            workdir = Interpolate('%(prop:builddir)s/build/build'),
            command = Interpolate('cat cov-int/build-log.txt && tar czvf coverity-data.tgz cov-int && curl --form token=$COVERITY_TOKEN --form email=$COVERITY_EMAIL --form file=@coverity-data.tgz --form version="%(prop:got_revision)s" --form description="Push to master" https://scan.coverity.com/builds?project=SFML%%2FSFML'),
            env = {
                'COVERITY_TOKEN' : private.coverity_token,
                'COVERITY_EMAIL' : private.coverity_email,
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')
            },
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            hideStepIf = skipped_or_success
        )
    ]

def get_sonar_steps():
    from buildbot.steps.worker import RemoveDirectory
    from buildbot.steps.worker import MakeDirectory
    from buildbot.steps.shell import ShellCommand
    from buildbot.steps.shell import Compile
    from buildbot.process.properties import Interpolate
    import private

    return [
        MakeDirectory(
            name = 'create build directory',
            description = ['preparing build directory'],
            descriptionDone = ['create build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            hideStepIf = skipped_or_success
        ),
        ShellCommand(
            name = 'configure',
            description = ['configuring'],
            descriptionDone = ['configure'],
            workdir = Interpolate('%(prop:builddir)s/build'),
            command = Interpolate('cmake -S . -B build -DCMAKE_VERBOSE_MAKEFILE=TRUE -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=FALSE -DSFML_BUILD_EXAMPLES=TRUE -DSFML_BUILD_TEST_SUITE=ON -DSFML_RUN_DISPLAY_TESTS=ON -DCMAKE_INSTALL_PREFIX=%(prop:builddir)s/install'),
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        Compile(
            name = 'build',
            description = ['building'],
            descriptionDone = ['build'],
            workdir = Interpolate('%(prop:builddir)s/build'),
            command = Interpolate('%(kw:command)s %(prop:makefile:#?| -- -k -j %(prop:parallel)s|)s', command = 'build-wrapper-linux-x86-64 --out-dir bw-output cmake --build build/ --target all'),
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        ShellCommand(
            name = 'sonar scanner',
            description = ['running sonar scanner'],
            descriptionDone = ['run sonar scanner'],
            workdir = Interpolate('%(prop:builddir)s/build'),
            command = Interpolate('sonar-scanner -Dsonar.organization=sfml -Dsonar.projectKey=SFML_SFML -Dsonar.sources=. -Dsonar.cfamily.compile-commands=bw-output/compile_commands.json -Dsonar.host.url=https://sonarcloud.io -Dsonar.cfamily.threads=%(prop:parallel)s'),
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        ),
        RemoveDirectory(
            name = 'remove build directory',
            description = ['removing build directory'],
            descriptionDone = ['remove build directory'],
            dir = Interpolate('%(prop:builddir)s/build/build'),
            hideStepIf = skipped_or_success
        ),
        RemoveDirectory(
            name = 'remove bw-output directory',
            description = ['removing bw-output directory'],
            descriptionDone = ['remove bw-output directory'],
            dir = Interpolate('%(prop:builddir)s/build/bw-output'),
            hideStepIf = skipped_or_success
        )
    ]

def get_replace_step():
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = 'replace strings',
            description = ['replacing strings'],
            descriptionDone = ['replace strings'],
            haltOnFailure = True,
            doStepIf = lambda step : (step.build.getProperty('replace_strings_in_files') is not None),
            hideStepIf = skipped_or_success,
            workdir = Interpolate('%(prop:builddir)s/build'),
            command = Interpolate('%(prop:replace_strings_in_files)s'),
            env = {
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')
            },
            want_stdout = False,
            want_stderr = False,
            logEnviron = False
        )
    ]

def get_patch_steps(string, replacement, file):
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = 'patch',
            description = ['patching'],
            descriptionDone = ['patch'],
            hideStepIf = skipped_or_success,
            workdir = Interpolate('%(prop:builddir)s/build'),
            command = Interpolate('if [ -f "' + file + '" ]; then sed -i.bak s@' + string + '@' + replacement + '@g ' + file + '; fi'),
            env = {
                'PATH' : Interpolate('%(prop:toolchain_path)s%(prop:PATH)s')
            },
            want_stdout = True,
            want_stderr = True,
            logEnviron = False
        )
    ]

def get_disable_sound_steps():
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = 'disable sound',
            description = ['disabling sound'],
            descriptionDone = ['disable sound'],
            doStepIf = lambda step : (step.build.getProperty('miniaudio_exists') is True),
            hideStepIf = skipped_or_success,
            command = Interpolate('rm -vf /usr/lib/x86_64-linux-gnu/libasound.so* && rm -vf /usr/lib/x86_64-linux-gnu/libpulse.so* && rm -vf /usr/lib/x86_64-linux-gnu/libjack.so* && rm -vf /usr/lib/x86_64-linux-gnu/libsndio.so* && rm -vf /usr/lib/x86_64-linux-gnu/libaaudio.so* && rm -vf /usr/lib/x86_64-linux-gnu/libOpenSLES.so'),
            logEnviron = False
        )
    ]

def check_file_exists(file, propertyToSet):
    from buildbot.steps.shell import SetPropertyFromCommand

    def stdoutToBool(rc, stdout, stderr):
        if '1' in stdout:
             return {propertyToSet: True}
        return {propertyToSet: False}

    return [
        SetPropertyFromCommand(
            hideStepIf = skipped_or_success,
            command='if [ -f ' + file + ' ]; then echo 1; else echo 0; fi',
            extract_fn=stdoutToBool
        )
    ]

def get_android_steps(name, description, workdir, command, flag = None, invertFlag = False):
    from buildbot.steps.shell import ShellCommand
    from buildbot.process.properties import Interpolate

    return [
        ShellCommand(
            name = name,
            description = [description],
            descriptionDone = [name],
            doStepIf = lambda step : (flag is None) or ((not step.build.getProperty(flag)) if invertFlag else step.build.getProperty(flag)),
            hideStepIf = skipped,
            workdir = Interpolate(workdir),
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
            command = ['cppcheck', Interpolate('-j %(prop:parallel)s'), '--enable=all', '--inconclusive', '--suppress=unusedFunction', '--suppress=functionStatic', '--suppress=functionConst', '--suppress=noConstructor', '--suppress=noExplicitConstructor', '--suppress=missingInclude', '--force', '-q', '--template={file}:{line}: warning: ({severity}) {message}', '-DSFML_SYSTEM_API=', '-DSFML_NETWORK_API=', '-DSFML_AUDIO_API=', '-DSFML_WINDOW_API=', '-DSFML_GRAPHICS_API=', '-I', 'include', '-I', 'src', 'src', 'examples'],
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

    if('coverity' not in builder_name):
        steps.extend(get_shallow_clone_step())
        steps.extend(get_replace_step())

    if('debian' in builder_name):
        steps.extend(check_file_exists('extlibs/headers/miniaudio/miniaudio.h', 'miniaudio_exists'))
        steps.extend(get_disable_sound_steps())

    if('coverity' in builder_name):
        steps.extend(get_clone_step())
        steps.extend(get_replace_step())
        steps.extend(get_coverity_steps('static', 'debug'))
        steps.extend(get_sonar_steps())
    elif('static-analysis' in builder_name):
        # steps.extend(check_file_exists('cmake/Tidy.cmake', 'clang_tidy_config_exists'))
        # steps.extend(get_patch_steps('-clang-tidy-binary', '-j\ %(prop:parallel)s\ -clang-tidy-binary', 'cmake/Tidy.cmake'))
        # steps.extend(get_configuration_build_steps('static', 'debug', ['clang-tidy'], 'clang_tidy_config_exists'))

        steps.extend(get_cppcheck_steps())
    elif('android' in builder_name):
        steps.extend(get_android_libcxx_step())
        steps.extend(check_file_exists('examples/android/gradlew', 'gradlew_exists'))

        # Old
        steps.extend(get_patch_steps('gradle\:[[:digit:]]\.[[:digit:]]\.[[:digit:]]', 'gradle:7.0.0', 'examples/android/build.gradle'))
        steps.extend(get_patch_steps('targetSdkVersion\ [[:digit:]][[:digit:]]*', 'targetSdkVersion\ 29', 'examples/android/app/build.gradle'))
        # New
        # steps.extend(get_patch_steps('version\ =\ \\"[[:digit:]][[:digit:]]*\.[[:digit:]][[:digit:]]*\.[[:digit:]][[:digit:]]*\\"', 'version\ =\ \\"3.26.3\\"', 'examples/android/app/build.gradle.kts'))

        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['android']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['android']))
        steps.extend(get_configuration_build_steps('static', 'release', ['android']))

        # Old
        # steps.extend(get_android_steps('build debug example project', 'building debug example project', '%(prop:builddir)s/build/examples/android', 'gradle assembleDebug', 'gradlew_exists', True))
        # steps.extend(get_android_steps('build release example project', 'building release example project', '%(prop:builddir)s/build/examples/android', 'gradle assembleRelease', 'gradlew_exists', True))
        # New
        steps.extend(get_android_steps('build debug example project', 'building debug example project', '%(prop:builddir)s/build', 'examples/android/gradlew assembleDebug -p examples/android -P ARCH_ABI=%(prop:architecture)s -P MIN_SDK=%(prop:api)s -P NDK_VERSION=%(prop:ANDROID_NDK_VERSION)s', 'gradlew_exists', False))
        steps.extend(get_android_steps('build release example project', 'building release example project', '%(prop:builddir)s/build', 'examples/android/gradlew assembleRelease -p examples/android -P ARCH_ABI=%(prop:architecture)s -P MIN_SDK=%(prop:api)s -P NDK_VERSION=%(prop:ANDROID_NDK_VERSION)s', 'gradlew_exists', False))

        steps.extend(get_android_steps('create install directory', 'creating install directory', '%(prop:builddir)s/build/examples/android', 'mkdir -p %(prop:builddir)s/install'))
        steps.extend(get_android_steps('archive library', 'archiving library', '%(prop:builddir)s/build/examples/android', 'cp -r %(prop:ANDROID_NDK_ROOT)s/sources/third_party/sfml %(prop:builddir)s/install/.'))
        steps.extend(get_android_steps('archive debug example project', 'archiving debug example project', '%(prop:builddir)s/build/examples/android', 'cp app/build/outputs/apk/debug/*-debug.apk %(prop:builddir)s/install/.', 'gradlew_exists', False))
        steps.extend(get_android_steps('archive release example project', 'archiving release example project', '%(prop:builddir)s/build/examples/android', 'cp app/build/outputs/apk/release/*-release-unsigned.apk %(prop:builddir)s/install/.', 'gradlew_exists', False))

        steps.extend(get_artifact_step())
    elif('ios' in builder_name):
        steps.extend(check_file_exists('cmake/toolchains/iOS.toolchain.cmake', 'ios_toolchain_cmake_exists'))

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
    elif('debian-gcc' in builder_name):
        steps.extend(get_configuration_build_steps('dynamic', 'debug'))
        steps.extend(get_configuration_build_steps('static', 'debug'))
        steps.extend(get_configuration_build_steps('dynamic', 'release'))
        steps.extend(get_configuration_build_steps('static', 'release'))

        steps.extend(get_artifact_step())
    elif('drm' in builder_name):
        steps.extend(get_configuration_build_steps('dynamic', 'debug', ['drm']))
        steps.extend(get_configuration_build_steps('static', 'debug', ['drm']))
        steps.extend(get_configuration_build_steps('dynamic', 'release', ['drm']))
        steps.extend(get_configuration_build_steps('static', 'release', ['drm']))

        steps.extend(get_artifact_step())
    elif('freebsd' in builder_name):
        steps.extend(get_configuration_build_steps('dynamic', 'debug'))
        steps.extend(get_configuration_build_steps('static', 'debug'))
        steps.extend(get_configuration_build_steps('dynamic', 'release'))
        steps.extend(get_configuration_build_steps('static', 'release'))

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
