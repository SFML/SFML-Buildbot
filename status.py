def get_irc():
    from buildbot.status import words

    return words.IRC(
        host = '<IRC server redacted>',
        nick = '<IRC nick redacted>',
        channels = ['<IRC channels redacted>'],
        notify_events = {
            'started' : 1,
            'finished' : 1,
            'failure' : 1,
            'success' : 1,
            'exception' : 1
        }
    )

def get_other_irc():
    from buildbot.status import words

    return words.IRC(
        host = '<IRC server redacted>',
        nick = '<IRC nick redacted>',
        channels = ['<IRC channels redacted>'],
        notify_events = {
            'started' : 0,
            'finished' : 0,
            'failure' : 0,
            'success' : 0,
            'exception' : 0
        }
    )

def get_web():
    from buildbot.status import html
    from buildbot.status.web import authz, auth
    import users

    users = users.get_users()

    authz_cfg = authz.Authz(
        auth = auth.BasicAuth(users),
        view = True,
        forceBuild = 'auth',
        forceAllBuilds = 'auth',
        pingBuilder = 'auth',
        gracefulShutdown = False,
        pauseSlave = 'auth',
        stopBuild = 'auth',
        stopAllBuilds = 'auth',
        cancelPendingBuild = 'auth',
        cancelAllPendingBuilds = 'auth',
        stopChange = 'auth',
        cleanShutdown = False,
        showUsersPage = 'auth'
    )

    return html.WebStatus(
        http_port = "tcp:8010:interface=127.0.0.1",
        authz = authz_cfg,
        change_hook_dialects = {'base': True, 'github' : {}},
        change_hook_auth = ['file:changehook.passwd']
    )

def get_github_status():
    from buildbot.process.properties import Interpolate
    from buildbot.status.github import GitHubStatus

    return GitHubStatus(
        token = '<token redacted>',
        repoOwner = 'SFML',
        repoName = 'SFML',
        sha = Interpolate("%(prop:got_revision)s"),
        startDescription = Interpolate("Build #%(prop:buildnumber)s started."),
        endDescription = Interpolate("Build #%(prop:buildnumber)s done."),
    )

def get_status():
    return [get_web(), get_irc(), get_other_irc(), get_github_status()]