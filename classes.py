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

import string
import enum
import datetime
from dataclasses import dataclass
from tkinter import Checkbutton
from tkinter import Label
from tkinter import IntVar

@dataclass
class Band:
    """ Class for the bands that will play with their start and end date and time,
    stage they will play on, as well as name """
    name: string
    stage: enum
    start: datetime
    end: datetime


@dataclass
class LineUp:
    """ The entire line up """
    # TODO: currently bands are listed twice, stages is only convenience. clean this up
    stages: list[string]
    dates: dict[datetime, list[string]]
    bands: list[Band]

    def contains_band(self, band_name) -> bool:
        for band in self.bands:
            if band.name == band_name:
                return True

        return False

    def get_full_info(self, band_name) -> Band:
        for band in self.bands:
            if band.name == band_name:
                return band

        return None


@dataclass
class Settings:
    save_as_image: int = 0
    save_as_pdf: int = 1
    dpi: int = 200
    band_time_font_size: int = 7
    band_name_font_size: int = 9
    stage_name_font_size: int = 10


@dataclass
class Stage:

    def __init__(self, name):
        self.name = name
        self.checkbox = Checkbutton()
        self.isEnabled = IntVar(value=1)

    def create_selection_gui(self, parent):
        row = parent.grid_size()[1]
        tk_name = self.name.replace(".", "").replace(" ", "")
        self.checkbox = Checkbutton(master=parent, onvalue=1, offvalue=0, variable=self.isEnabled,
                                    name="checkbox"+tk_name)
        self.checkbox.grid(row=row, column=0)
        self.checkbox.select()
        self.label = Label(master=parent, text=self.name, name="label"+tk_name)
        self.label.grid(row=row, column=1)

    def is_enabled(self) -> bool:
        try:
            return self.isEnabled.get() == 1
        except:
            print("fuck")

    # TODO: enable ordering
    checkbox: Checkbutton = None
    label: Label = None
    isEnabled: IntVar = None
    name: string = ""
