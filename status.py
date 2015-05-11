def get_irc():
    from buildbot.status import words

    return words.IRC(
        host = '<IRC server redacted>',
        nick = '<IRC nick redacted>',
        channels = ['<IRC channels redacted>'],
        notify_events = {
            'started' : 0,
            'finished' : 0,
            'failure' : 1,
            'success' : 0,
            'exception' : 1
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
        http_port = 8010,
        authz = authz_cfg,
        change_hook_dialects = {'github' : True},
        change_hook_auth = ['file:changehook.passwd'],
        revlink = 'http://github.com/SFML/SFML/commit/%s'
    )

def get_status():
    return [get_web(), get_irc()]