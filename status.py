from buildbot.plugins import util

@util.renderer
def get_github_app_token(props):
    # https://github.com/vaspapadopoulos/github-app-auth
    import datetime
    import requests
    import jwt
    import private

    with open(private.github_app_private_key_file, "r") as key_file:
        key = key_file.read()

    now = int(datetime.datetime.now().timestamp())
    payload = {
        "iat": now - 60,
        "exp": now + 60 * 8, # expire after 8 minutes
        "iss": private.github_app_id,
        "alg": "RS256"
    }
    encoded = jwt.encode(payload=payload, key=key, algorithm="RS256")
    response = requests.post(f"https://api.github.com/app/installations/{private.github_app_installation_id}/access_tokens", headers={"Authorization": f"Bearer {encoded}"})

    return response.json()["token"]

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
            token = get_github_app_token,
            context = Interpolate("%(prop:buildername)s"),
            verbose = True
        )
    ]
