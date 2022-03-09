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

def make_builder(builder_name, workers, generator, toolchain_path, architecture, artifact, run_tests):
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
            'artifact' : artifact,
            'artifact_extension' : artifact_extension,
            'archive_command' : archive_command,
            'run_tests': run_tests
        }
    )

def setup_msvc(version):
    return

def get_builders():
    import paths

    return [
        make_builder('windows-vc16-32', ['binary1248-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc16path, 'x86', True, True),
        make_builder('windows-vc16-64', ['binary1248-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc16path, 'amd64', True, True),
        make_builder('windows-vc17-32', ['binary1248-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc17path, 'x86', True, True),
        make_builder('windows-vc17-64', ['binary1248-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc17path, 'amd64', True, True),
        make_builder('windows-gcc-1120-mingw-32', ['binary1248-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc1120mingw32path, '', True, True),
        make_builder('windows-gcc-1120-mingw-64', ['binary1248-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc1120mingw64path, '', True, True),
        make_builder('debian-gcc-64', ['binary1248-debian'], 'Unix Makefiles', '', '', True, True),
        make_builder('debian-clang-64', ['binary1248-debian'], 'Unix Makefiles', '', '', True, True),
        make_builder('raspbian-gcc-armhf', ['expl0it3r-raspbian-armhf'], 'Unix Makefiles', '', '', True, True),
        make_builder('raspbian-gcc-armhf-drm', ['expl0it3r-raspbian-armhf'], 'Unix Makefiles', '', '', True, True),
        make_builder('android-armeabi-v7a', ['binary1248-android'], 'Unix Makefiles', '', '', True, False),
        make_builder('static-analysis', ['binary1248-debian'], 'Unix Makefiles', '', '', False, False),
        make_builder('coverity', ['binary1248-coverity'], 'Unix Makefiles', '', '', False, False),
        make_builder('freebsd-gcc-64', ['binary1248-freebsd-64'], 'Unix Makefiles', '', '', False, True),
        make_builder('macos-clang-64', ['macos-64'], 'Unix Makefiles', '', 'x86_64', True, True),
        make_builder('ios-clang-64', ['macos-64'], 'Xcode', '', '', True, False),
        make_builder('macos-clang-arm64', ['macos-arm64'], 'Unix Makefiles', '', 'arm64', True, False),
    ]
