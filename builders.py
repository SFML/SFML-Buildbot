from buildbot import locks

builder_names = []

slave_lock = locks.SlaveLock(
    'slave_lock',
    maxCount = 1
)

def get_builder_names():
    return builder_names

def make_builder(builder_name, slaves, slave_build_directory, generator, maker, toolchain_path, vc_include, vc_lib, vc_libpath):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
    builder_names.append(builder_name)

    return BuilderConfig(
        name = builder_name,
        slavenames = slaves,
        slavebuilddir = slave_build_directory,
        locks = [slave_lock.access('counting')],
        factory = buildfactories.get_build_factory(),
        properties = {
            'generator' : generator,
            'maker' : maker,
            'toolchain_path' : toolchain_path,
            'vc_include' : vc_include,
            'vc_lib' : vc_lib,
            'vc_libpath' : vc_libpath
        }
    )

def make_static_analysis_builder(builder_name, slaves, slave_build_directory):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
    builder_names.append(builder_name)

    return BuilderConfig(
        name = builder_name,
        slavenames = slaves,
        slavebuilddir = slave_build_directory,
        locks = [slave_lock.access('counting')],
        factory = buildfactories.get_static_analysis_build_factory()
    )

def setup_msvc(version):
    return

def get_builders():
    import paths

    return [
        make_builder('windows-vc11-32', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc11x86path, paths.vc11x86include, paths.vc11x86lib, paths.vc11x86libpath),
        make_builder('windows-vc11-64', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc11x64path, paths.vc11x64include, paths.vc11x64lib, paths.vc11x64libpath),
        make_builder('windows-vc12-32', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc12x86path, paths.vc12x86include, paths.vc12x86lib, paths.vc12x86libpath),
        make_builder('windows-vc12-64', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc12x64path, paths.vc12x64include, paths.vc12x64lib, paths.vc12x64libpath),
        make_builder('windows-vc14-32', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc14x86path, paths.vc14x86include, paths.vc14x86lib, paths.vc14x86libpath),
        make_builder('windows-vc14-64', ['master-windows', 'expl0it3r-windows'], 'tmp', 'NMake Makefiles JOM', 'jom', paths.vc14x64path, paths.vc14x64include, paths.vc14x64lib, paths.vc14x64libpath),
        make_builder('debian-gcc-64', ['master-debian-64', 'binary1248-debian-64'], 'tmp', 'Unix Makefiles', 'make', '', '', '', ''),
        make_builder('freebsd-gcc-64', ['zsbzsb-freebsd-64', 'binary1248-freebsd-64'], 'tmp', 'Unix Makefiles', 'make', '', '', '', ''),
        make_builder('osx-clang-el-capitan', ['hiura-osx'], 'tmp', 'Unix Makefiles', 'make', '', '', '', ''),
        make_builder('windows-gcc-492-tdm-32', ['master-windows', 'expl0it3r-windows'], 'tmp', 'MinGW Makefiles', 'mingw32-make', paths.gcc492tdm32path, '', '', ''),
        make_builder('windows-gcc-492-tdm-64', ['master-windows', 'expl0it3r-windows'], 'tmp', 'MinGW Makefiles', 'mingw32-make', paths.gcc492tdm64path, '', '', ''),
        make_builder('windows-gcc-610-mingw-32', ['master-windows', 'expl0it3r-windows'], 'tmp', 'MinGW Makefiles', 'mingw32-make', paths.gcc610mingw32path, '', '', ''),
        make_builder('windows-gcc-610-mingw-64', ['master-windows', 'expl0it3r-windows'], 'tmp', 'MinGW Makefiles', 'mingw32-make', paths.gcc610mingw64path, '', '', ''),
        make_static_analysis_builder('static-analysis', ['binary1248-debian-64'], 'tmp')
    ]
