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


import logging

import vmdb


class EchoPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(EchoStepRunner())


class EchoStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"echo": str, "teardown": ""}

    def run(self, values, settings, state):
        text = values["echo"]
        vmdb.progress("{}".format(text))

    def teardown(self, values, settings, state):
        text = values["teardown"]
        if text:
            vmdb.progress("{}".format(text))
            logging.info("%s", text)
