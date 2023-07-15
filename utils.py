# Personal Running Order Tool
# Copyright (C) 2023  Tim Lobner
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


import copy
import datetime
import os

from tkinter import filedialog


def get_timeless_date(dt) -> datetime:
    # make a copy of the date, so as to not overwrite the original info
    new_dt = copy.deepcopy(dt)
    new_dt = new_dt.replace(hour=0)
    new_dt = new_dt.replace(minute=0)

    return new_dt


def save_file_as_browser(filetypes=(("All files", "*.*"),)):
    filename = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                            title="Select path and name for the file to be saved to",
                                            filetypes=filetypes)

    ext = os.path.splitext(filename)
    if not ext.__contains__('.'):
        # the user didn't enter an extension. add one here (unless *.* is allowed)
        # there seems to be no way to query the last selected extension in the file browser
        # therefore just add the default extension (i.e. the first one in filetypes)

        is_empty_allowed = False
        for filetype in filetypes:
            if filetype[1] == "*.*":
                is_empty_allowed = True
                break

        if not is_empty_allowed:
            filename += filetypes[0][1].removesuffix('*').removeprefix('*')
    else:
        # check if the extension is a "legal" one (i.e. contained in filetypes)
        is_legal = False
        for filetype in filetypes:
            if ext in filetype[1] or filetype[1] == "*.*":
                is_legal = True
                break

        if not is_legal:
            # not a legal filetype, default to the default
            filename += filetypes[0][1].removesuffix('*').removeprefix('*')

    print(filename)
    return filename
