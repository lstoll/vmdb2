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
import stat

import cliapp

import vmdb


class MkpartPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(MkpartStepRunner())


class MkpartStepRunner(vmdb.StepRunnerInterface):

    def get_key_spec(self):
        return {
            'mkpart': str,
            'device': str,
            'start': str,
            'end': str,
            'tag': '',
            'part-tag': '',
            'fs-type': 'ext2',
        }

    def run(self, values, settings, state):
        part_type = values['mkpart']
        device = values['device']
        start = values['start']
        end = values['end']
        tag = values['tag'] or values['part-tag'] or None
        fs_type = values['fs-type']

        orig = self.list_partitions(device)
        vmdb.runcmd(['parted', '-s', device, 'mkpart', part_type, fs_type, start, end])

        state.tags.append(tag)
        if self.is_block_dev(device):
            new = self.list_partitions(device)
            diff = self.diff_partitions(orig, new)
            assert len(diff) == 1
            vmdb.progress('remembering partition {} as {}'.format(diff[0], tag))
            state.tags.set_dev(tag, diff[0])

    def is_block_dev(self, filename):
        st = os.lstat(filename)
        return stat.S_ISBLK(st.st_mode)

    def list_partitions(self, device):
        output = vmdb.runcmd(['parted', '-m', device, 'print'])
        output = output.decode('UTF-8')
        partitions = [
            line.split(':')[0]
            for line in output.splitlines()
            if ':' in line
        ]
        return [
            word if word.startswith('/') else '{}{}'.format(device, word)
            for word in partitions
        ]

    def diff_partitions(self, old, new):
        return [
            line
            for line in new
            if line not in old
        ]
