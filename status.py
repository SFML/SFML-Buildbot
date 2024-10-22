def get_www():
    from buildbot.plugins import util
    from twisted.cred import strcred
    import private

    return dict(
        port = "unix:/home/buildbot/buildbot.sock",
        plugins = dict(
            waterfall_view = True,
            console_view = True,
            grid_view = True,
            badges = {}
        ),
        auth = util.GitHubAuth(
            private.github_client_id,
            private.github_client_secret,
            apiVersion = 4,
            getTeamsMembership = True
        ),
        authz = util.Authz(
            allowRules = [
                util.AnyControlEndpointMatcher(role = "SFML")
            ],
            roleMatchers = [
                util.RolesFromGroups()
            ]
        ),
        change_hook_dialects = {'base': True, 'github' : {}},
        change_hook_auth = [strcred.makeChecker("file:changehook.passwd")],
        ws_ping_interval = 15
    )

def get_github_status():
    from buildbot.process.properties import Interpolate
    from buildbot.plugins import reporters
    import private

    return [
        reporters.GitHubStatusPush(
            token = private.github_status_token,
            context = Interpolate("%(prop:buildername)s"),
            verbose = True
        )
    ]
