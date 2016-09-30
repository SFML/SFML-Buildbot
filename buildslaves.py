from buildbot.buildslave import BuildSlave

def get_protocols():
    return {'pb': {'port': <port number redacted>}}

def get_slaves():
    return [
        BuildSlave('unassigned', '<password redacted>', properties = {'parallel' : 0}),
        BuildSlave('expl0it3r-windows', '<password redacted>', properties = {'parallel' : 1}),
        BuildSlave('hiura-osx', '<password redacted>', properties = {'parallel' : 3}),
        BuildSlave('master', '<password redacted>', properties = {'parallel' : 3}),
        BuildSlave('master-debian-64', '<password redacted>', properties = {'parallel' : 3}),
        BuildSlave('master-ubuntu-64', '<password redacted>', properties = {'parallel' : 3}),
        BuildSlave('master-windows', '<password redacted>', properties = {'parallel' : 5}),
        BuildSlave('tank-debian-64', '<password redacted>', properties = {'parallel' : 5}),
        BuildSlave('tank-ubuntu-64', '<password redacted>', properties = {'parallel' : 5}),
        BuildSlave('zsbzsb-freebsd-64', '<password redacted>', properties = {'parallel' : 1}),
        BuildSlave('binary1248-debian-64', '<password redacted>', properties = {'parallel' : 13}),
        BuildSlave('binary1248-freebsd-64', '<password redacted>', properties = {'parallel' : 1})
    ]