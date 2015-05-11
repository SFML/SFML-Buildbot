from buildbot.buildslave import BuildSlave

def get_protocols():
    return {'pb': {'port': <port number redacted>}}

def get_slaves():
    return [
        BuildSlave('unassigned', '<password redacted>', properties = {'parallel' : 0}),
        BuildSlave('expl0it3r-win8.1', '<password redacted>', properties = {'parallel' : 8}),
        BuildSlave('hiura-osx', '<password redacted>', properties = {'parallel' : 2}),
        BuildSlave('master', '<password redacted>', properties = {'parallel' : 8}),
        BuildSlave('master-debian-64', '<password redacted>', properties = {'parallel' : 8}),
        BuildSlave('master-ubuntu-64', '<password redacted>', properties = {'parallel' : 8}),
        BuildSlave('master-windows7-64', '<password redacted>', properties = {'parallel' : 8}),
        BuildSlave('tank-debian-64', '<password redacted>', properties = {'parallel' : 4}),
        BuildSlave('tank-ubuntu-64', '<password redacted>', properties = {'parallel' : 4}),
        BuildSlave('zsbzsb-freebsd', '<password redacted>', properties = {'parallel' : 2})
    ]