from buildbot import locks

builder_names = []

# slave_lock = locks.WorkerLock(
#     'slave_lock',
#     maxCount = 1
# )

def workerPriority(builder, workers, requests):
    for worker in workers:
        if('binary1248' in worker.worker.workername):
            return worker

    for worker in workers:
        return worker

    return None

def get_builder_names():
    return builder_names

def make_builder(builder_name, workers, generator, toolchain_path, architecture, api, android_libcxx, android_tester, artifact, build_tests, run_tests, display_tests, audio_device_tests):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names

    if('coverity' not in builder_name):
        builder_names.append(builder_name)

    makefile = ''
    artifact_extension = '.tar.gz'
    archive_command = 'tar czf'

    if('Makefile' in generator):
        makefile = 'makefile'

    if('ios' in builder_name):
        makefile = ''

    if('windows' in builder_name):
        artifact_extension = '.zip'
        archive_command = 'zip -r'

    return BuilderConfig(
        name = builder_name,
        workernames = workers,
        nextWorker = workerPriority,
        # locks = [slave_lock.access('counting')],
        factory = buildfactories.get_build_factory(builder_name),
        properties = {
            'generator' : generator,
            'makefile' : makefile,
            'toolchain_path' : toolchain_path,
            'architecture' : architecture,
            'api' : api,
            'android_libcxx' : android_libcxx,
            'android_tester' : android_tester,
            'artifact' : artifact,
            'artifact_extension' : artifact_extension,
            'archive_command' : archive_command,
            'build_tests' : build_tests,
            'run_tests': run_tests,
            'display_tests': display_tests,
            'audio_device_tests': audio_device_tests
        }
    )

def setup_msvc(version):
    return

def get_builders():
    import paths

    android_libcxx = dict([
        ('x86',         'i686-linux-android/libc++_shared.so'   ),
        ('x86_64',      'x86_64-linux-android/libc++_shared.so' ),
        ('armeabi-v7a', 'arm-linux-androideabi/libc++_shared.so'),
        ('arm64-v8a',   'aarch64-linux-android/libc++_shared.so'),
    ])

    android_tester = dict([
        ('x86',         ''          ),
        ('x86_64',      ''          ),
        ('armeabi-v7a', '10.12.48.2'),
        ('arm64-v8a',   '10.12.48.2'),
    ])

    return [
        #            Name                         Workers                                                    Generator              Toolchain Path            Architecture   API   Android libc++ Subpath         Android Tester                 Artifact Build  Run    Display Audio
        #                                                                                                                                                                                                                                                 Tests  Tests  Tests   Tests
        make_builder('windows-vc16-32',           ['binary1248-windows', 'expl0it3r-windows'],               'NMake Makefiles JOM', paths.vc16path,           'x86',         '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('windows-vc16-64',           ['binary1248-windows', 'expl0it3r-windows'],               'NMake Makefiles JOM', paths.vc16path,           'amd64',       '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('windows-vc17-32',           ['binary1248-windows', 'expl0it3r-windows'],               'NMake Makefiles JOM', paths.vc17path,           'x86',         '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('windows-vc17-64',           ['binary1248-windows', 'expl0it3r-windows'],               'NMake Makefiles JOM', paths.vc17path,           'amd64',       '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('windows-gcc-1220-mingw-32', ['binary1248-windows', 'expl0it3r-windows'],               'MinGW Makefiles',     paths.gcc1220mingw32path, '',            '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('windows-gcc-1220-mingw-64', ['binary1248-windows', 'expl0it3r-windows'],               'MinGW Makefiles',     paths.gcc1220mingw64path, '',            '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('debian-gcc-64',             ['binary1248-debian'],                                     'Unix Makefiles',      '',                       '',            '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('debian-clang-64',           ['binary1248-debian'],                                     'Unix Makefiles',      '',                       '',            '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('raspbian-gcc-armhf',        ['expl0it3r-raspbian-armhf', 'binary1248-raspbian-armhf'], 'Unix Makefiles',      '',                       '',            '',   '',                            '',                            True,    True,  True,  False,  False),
        make_builder('raspbian-gcc-armhf-drm',    ['expl0it3r-raspbian-armhf', 'binary1248-raspbian-armhf'], 'Unix Makefiles',      '',                       '',            '',   '',                            '',                            True,    True,  True,  False,  False),
        make_builder('android-armeabi-v7a',       ['binary1248-android'],                                    'Unix Makefiles',      '',                       'armeabi-v7a', '29', android_libcxx['armeabi-v7a'], android_tester['armeabi-v7a'], True,    True,  True,  False,  True ),
        make_builder('static-analysis',           ['binary1248-debian'],                                     'Unix Makefiles',      '',                       '',            '',   '',                            '',                            False,   True,  True,  True,   True ),
        make_builder('coverity',                  ['binary1248-coverity'],                                   'Unix Makefiles',      '',                       '',            '',   '',                            '',                            False,   False, False, False,  False),
        make_builder('freebsd-gcc-64',            ['binary1248-freebsd-64'],                                 'Unix Makefiles',      '',                       '',            '',   '',                            '',                            False,   True,  True,  False,  False),
        make_builder('macos-clang-64',            ['macos-64'],                                              'Unix Makefiles',      '',                       'x86_64',      '',   '',                            '',                            True,    True,  True,  True,   True ),
        make_builder('ios-clang-64',              ['macos-64'],                                              'Unix Makefiles',      '',                       'arm64',       '',   '',                            '',                            True,    False, False, False,  False),
        make_builder('macos-clang-arm64',         ['macos-arm64'],                                           'Unix Makefiles',      '',                       'arm64',       '',   '',                            '',                            True,    True,  True,  True,   True ),
    ]
