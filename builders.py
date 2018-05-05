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

def make_builder(builder_name, workers, generator, toolchain_path, vc_include, vc_lib, vc_libpath, artifact):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
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
            'vc_include' : vc_include,
            'vc_lib' : vc_lib,
            'vc_libpath' : vc_libpath,
            'artifact' : artifact,
            'artifact_extension' : artifact_extension,
            'archive_command' : archive_command
        }
    )

def setup_msvc(version):
    return

def get_builders():
    import paths

    return [
        make_builder('windows-vc12-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc12x86path, paths.vc12x86include, paths.vc12x86lib, paths.vc12x86libpath, True),
        make_builder('windows-vc12-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc12x64path, paths.vc12x64include, paths.vc12x64lib, paths.vc12x64libpath, True),
        make_builder('windows-vc14-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc14x86path, paths.vc14x86include, paths.vc14x86lib, paths.vc14x86libpath, True),
        make_builder('windows-vc14-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc14x64path, paths.vc14x64include, paths.vc14x64lib, paths.vc14x64libpath, True),
        make_builder('windows-vc15-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc15x86path, paths.vc15x86include, paths.vc15x86lib, paths.vc15x86libpath, True),
        make_builder('windows-vc15-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc15x64path, paths.vc15x64include, paths.vc15x64lib, paths.vc15x64libpath, True),
        make_builder('windows-gcc-510-tdm-32', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc510tdm32path, '', '', '', True),
        make_builder('windows-gcc-730-mingw-32', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc730mingw32path, '', '', '', True),
        make_builder('windows-gcc-730-mingw-64', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc730mingw64path, '', '', '', True),
        make_builder('debian-gcc-64', ['binary1248-debian-64'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('android-armeabi-v7a-api13', ['binary1248-debian-64'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('static-analysis', ['binary1248-debian-64'], 'Unix Makefiles', '', '', '', '', False),
        make_builder('freebsd-gcc-64', ['binary1248-freebsd-64'], 'Unix Makefiles', '', '', '', '', False),
        make_builder('osx-clang-el-capitan', ['hiura-osx'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('ios-clang-el-capitan', ['hiura-osx'], 'Xcode', '', '', '', '', True)
    ]
