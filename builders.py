builder_names = []

def get_builder_names():
    return builder_names

def make_unix_builder(builder_name, slaves, slave_build_directory):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
    builder_names.append(builder_name)

    return BuilderConfig(
        name = builder_name,
        slavenames = slaves,
        slavebuilddir = slave_build_directory,
        factory = buildfactories.get_unix_build_factory()
    )

def make_msvc_builder(builder_name, slaves, slave_build_directory):
    from buildbot.config import BuilderConfig
    import buildfactories

    global builder_names
    builder_names.append(builder_name)

    return BuilderConfig(
        name = builder_name,
        slavenames = slaves,
        slavebuilddir = slave_build_directory,
        factory = buildfactories.get_msvc_build_factory()
    )

def get_builders():
    return [
        make_unix_builder('debian-gcc-64-bit', ['master-debian-64', 'tank-debian-64'], 'tmp'),
        make_unix_builder('linux-gcc-32-bit', ['unassigned'], 'tmp'),
        make_unix_builder('linux-gcc-64-bit', ['master-ubuntu-64', 'tank-ubuntu-64'], 'tmp'),
        make_unix_builder('freebsd-gcc-64-bit', ['zsbzsb-freebsd'], 'tmp'),
        make_unix_builder('osx-clang-universal', ['hiura-osx'], 'tmp'),
        make_msvc_builder('windows-vc10-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_msvc_builder('windows-vc11-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_msvc_builder('windows-vc12-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.7.1-tdm-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.8.1-tdm-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.9.2-mingw-32-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_msvc_builder('windows-vc10-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_msvc_builder('windows-vc11-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_msvc_builder('windows-vc12-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.7.1-tdm-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.8.1-tdm-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp'),
        make_unix_builder('windows-gcc-4.9.2-mingw-64-bit', ['master-windows7-64', 'expl0it3r-win8.1'], 'tmp')
    ]