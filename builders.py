builder_names = []

def slavePriority(builder, slaves):
    for slave in slaves:
        return slave

    return None

def get_builder_names():
    return builder_names

def make_builder(builder_name, slaves, generator, toolchain_path, vc_include, vc_lib, vc_libpath, artifact):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
    builder_names.append(builder_name)

    artifact_extension = '.tar.gz'
    archive_command = 'tar czf'

    if('windows' in builder_name):
        artifact_extension = '.zip'
        archive_command = 'zip -r'

    return BuilderConfig(
        name = builder_name,
        slavenames = slaves,
        nextSlave = slavePriority,
        locks = [],
        factory = buildfactories.get_build_factory(builder_name),
        properties = {
            'generator' : generator,
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
        make_builder('windows-vc11-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc11x86path, paths.vc11x86include, paths.vc11x86lib, paths.vc11x86libpath, True),
        make_builder('windows-vc11-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc11x64path, paths.vc11x64include, paths.vc11x64lib, paths.vc11x64libpath, True),
        make_builder('windows-vc12-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc12x86path, paths.vc12x86include, paths.vc12x86lib, paths.vc12x86libpath, True),
        make_builder('windows-vc12-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc12x64path, paths.vc12x64include, paths.vc12x64lib, paths.vc12x64libpath, True),
        make_builder('windows-vc14-32', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc14x86path, paths.vc14x86include, paths.vc14x86lib, paths.vc14x86libpath, True),
        make_builder('windows-vc14-64', ['master-windows', 'expl0it3r-windows'], 'NMake Makefiles JOM', paths.vc14x64path, paths.vc14x64include, paths.vc14x64lib, paths.vc14x64libpath, True),
        make_builder('windows-gcc-492-tdm-32', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc492tdm32path, '', '', '', True),
        make_builder('windows-gcc-492-tdm-64', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc492tdm64path, '', '', '', True),
        make_builder('windows-gcc-630-mingw-32', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc630mingw32path, '', '', '', True),
        make_builder('windows-gcc-630-mingw-64', ['binary1248-windows', 'master-windows', 'expl0it3r-windows'], 'MinGW Makefiles', paths.gcc630mingw64path, '', '', '', True),
        make_builder('debian-gcc-64', ['binary1248-debian-64', 'master-debian-64'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('android-armeabi-v7a-api13', ['binary1248-debian-64'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('static-analysis', ['binary1248-debian-64'], 'Unix Makefiles', '', '', '', '', False),
        make_builder('freebsd-gcc-64', ['binary1248-freebsd-64', 'zsbzsb-freebsd-64'], 'Unix Makefiles', '', '', '', '', False),
        make_builder('osx-clang-el-capitan', ['hiura-osx'], 'Unix Makefiles', '', '', '', '', True),
        make_builder('ios-clang-el-capitan', ['hiura-osx'], 'Xcode', '', '', '', '', True)
    ]
