This repository contains the files used to configure SFML's Buildbot.

Only files that have been modified or added to the default set after creation of
the buildmaster directory are checked into this repository. Simply create a new
buildmaster and paste/overwrite any existing files with the ones in this
repository. Sensitive information has been redacted.

Tested with the Buildbot 0.8.9 package on Debian Jessie.

Because the GitHub API has changed since Buildbot 0.8.9 was released, replacing
the default version of the GitHub webhook at buildbot/status/web/hooks/github.py
with a more recent version from the official repository at
https://github.com/buildbot/buildbot/blob/master/master/buildbot/status/web/hooks/github.py
will be necessary.

If you want to contribute to the SFML project by providing additional builder
resources, contact one of the project maintainers or simply post on the SFML forum.

Buildbot is licensed under the GNU General Public License version 2.

This configuration is licensed under the Creative Commons
Attribution-NonCommercial-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-nd/4.0/.