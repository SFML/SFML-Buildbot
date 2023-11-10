from buildbot.worker import Worker
from buildbot.plugins import worker

def get_protocols():
    import private

    return {'pb': {'port': private.port}}

def get_slaves():
    import private

    return [
        Worker('unassigned', private.slave_passwords['unassigned'], max_builds = 1, properties = {'parallel' : 0}),

        Worker('macos-64', private.slave_passwords['macos-64'], max_builds = 1, properties = {'parallel' : 3}),
        Worker('macos-arm64', private.slave_passwords['macos-arm64'], max_builds = 1, properties = {'parallel' : 3}),

        Worker('expl0it3r-windows', private.slave_passwords['expl0it3r-windows'], max_builds = 1, properties = {'parallel' : 4}),
        Worker('expl0it3r-raspbian-armhf', private.slave_passwords['expl0it3r-raspbian-armhf'], max_builds = 1, properties = {'parallel' : 3}),

        Worker('binary1248-freebsd-64', private.slave_passwords['binary1248-freebsd-64'], max_builds = 1, properties = {'parallel' : 1}),
        Worker('binary1248-windows', private.slave_passwords['binary1248-windows'], max_builds = 1, properties = {'parallel' : 4}),
        Worker('binary1248-raspbian-armhf', private.slave_passwords['binary1248-raspbian-armhf'], max_builds = 1, properties = {'parallel' : 2}),

        worker.DockerLatentWorker('binary1248-debian', private.slave_passwords['binary1248-debian'], docker_host = 'unix:///var/run/docker.sock', image = 'buildbot-worker-debian', masterFQDN = 'ci.sfml-dev.org', build_wait_timeout = 0, max_builds = 1, properties = {'parallel' : 2}),
        worker.DockerLatentWorker('binary1248-android', private.slave_passwords['binary1248-android'], docker_host = 'unix:///var/run/docker.sock', image = 'buildbot-worker-android', masterFQDN = 'ci.sfml-dev.org', build_wait_timeout = 0, max_builds = 1, properties = {'parallel' : 1}),
        worker.DockerLatentWorker('binary1248-coverity', private.slave_passwords['binary1248-coverity'], docker_host = 'unix:///var/run/docker.sock', image = 'buildbot-worker-coverity', masterFQDN = 'ci.sfml-dev.org', build_wait_timeout = 0, max_builds = 1, properties = {'parallel' : 1})
    ]
