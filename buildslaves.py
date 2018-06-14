from buildbot.worker import Worker

def get_protocols():
    import private

    return {'pb': {'port': private.port}}

def get_slaves():
    import private

    return [
        Worker('unassigned', private.slave_passwords['unassigned'], max_builds = 1, properties = {'parallel' : 0}),
        Worker('expl0it3r-windows', private.slave_passwords['expl0it3r-windows'], properties = {'parallel' : 1}),
        Worker('hiura-osx', private.slave_passwords['hiura-osx'], max_builds = 1, properties = {'parallel' : 3}),
        Worker('binary1248-debian-64', private.slave_passwords['binary1248-debian-64'], max_builds = 1, properties = {'parallel' : 5}),
        Worker('binary1248-freebsd-64', private.slave_passwords['binary1248-freebsd-64'], max_builds = 1, properties = {'parallel' : 1}),
        Worker('binary1248-windows', private.slave_passwords['binary1248-windows'], max_builds = 1, properties = {'parallel' : 8})
    ]