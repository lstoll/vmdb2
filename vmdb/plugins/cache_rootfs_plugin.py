# Copyright 2017  Lars Wirzenius
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


import os

import vmdb


class CacheRootFSPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(MakeCacheStepRunner())


class MakeCacheStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"cache-rootfs": str, "options": "--one-file-system"}

    def run(self, values, settings, state):
        fs_tag = values["cache-rootfs"]
        rootdir = state.tags.get_builder_mount_point(fs_tag)
        tar_path = settings["rootfs-tarball"]
        opts = values["options"].split()
        if not tar_path:
            raise Exception("--rootfs-tarball MUST be set")
        dirs = self._find_cacheable_mount_points(state.tags, rootdir)

        tags = state.tags
        for tag in tags.get_tags():
            vmdb.progress(
                "tag {} mounted {} cached {}".format(
                    tag, tags.get_builder_mount_point(tag), tags.is_cached(tag)
                )
            )

        vmdb.progress("caching rootdir {}".format(rootdir))
        vmdb.progress("caching relative {}".format(dirs))
        if not os.path.exists(tar_path):
            vmdb.runcmd(["tar"] + opts + ["-C", rootdir, "-caf", tar_path] + dirs)

    def _find_cacheable_mount_points(self, tags, rootdir):
        return list(
            sorted(
                self._make_relative(rootdir, tags.get_builder_mount_point(tag))
                for tag in tags.get_tags()
                if tags.is_cached(tag)
            )
        )

    def _make_relative(self, rootdir, dirname):
        assert dirname == rootdir or dirname.startswith(rootdir + "/")
        if dirname == rootdir:
            return "."
        return dirname[len(rootdir) + 1 :]
