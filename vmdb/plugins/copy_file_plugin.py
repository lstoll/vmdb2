# Copyright 2019 Gunnar Wolf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =*= License: GPL-3+ =*=

import vmdb
import os
import logging


class CopyFilePlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(CopyFileStepRunner())


class CopyFileStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"copy-file": str, "src": str, "perm": 0o644, "uid": 0, "gid": 0}

    def run(self, values, settings, state):
        root = state.tags.get_builder_from_target_mount_point("/")
        newfile = values["copy-file"]
        src = values["src"]
        perm = values["perm"]
        uid = values["uid"]
        gid = values["gid"]

        filename = "/".join([root, newfile])

        logging.info(
            "Copying file %s to %s, uid %d, gid %d, perms %o"
            % (src, filename, uid, gid, perm)
        )

        dirname = os.path.dirname(filename)
        os.makedirs(dirname, mode=0o511, exist_ok=True)
        with open(src, "rb") as inp:
            with open(filename, "wb") as output:
                contents = inp.read()
                output.write(contents)

        os.chown(filename, uid, gid)
        os.chmod(filename, perm)
