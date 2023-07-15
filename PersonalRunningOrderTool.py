# Personal Running Order Tool
# Copyright (C) 2022  Tim Lobner
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


import datetime

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

from classes import Band
from classes import LineUp
from classes import Settings
from classes import Stage


from utils import print_running_order
from utils import save_file_as_browser

import os


# The main window
window = Tk()


def add_stages_to_gui(stage_names):
    global stages

    # make sure the global list is not None but a valid list
    if not stages:
        stages = []

    # create stage objects in the global list
    for stage in stage_names:
        s = Stage(stage)
        stages.append(s)

    # add a line with checkbox and label to the main window
    # to enable stage selection
    for stage in stages:
        stage.create_selection_gui(window)


def parse_lineup(file_path) -> LineUp:
    """ Parse the line-up from a file """
    stage_names = []
    bands = []

    # first thing is to increase the line number, so we can set it to 0, then we "start" at 1
    line_number = 0
    for line in open(file_path, 'r', encoding='utf-8'):
        line_number += 1
        if line.startswith('Band') or line.startswith('#') or line == "\n" or not line:
            # ignore the line, as it is only for description or comment
            continue

        data = line.split(',')
        # set up the variables in this scope
        name = ""
        date = ""
        start = ""
        end = ""
        stage = ""
        try:
            name = data[0]
            date = data[1]
            start = data[2]
            end = data[3]
            stage = data[4].replace('\n', '')
        except:
            print("Could not parse line ", line, " at line ", line_number)
        if not stage_names.__contains__(stage):
            stage_names.append(stage)

        date_object = ""
        try:
            date_object = datetime.datetime.strptime(date, '%d.%m.%Y')
        except:
            # TODO: open window showing the user an error occurred and where it occured
            err_msg = 'Could not parse date on line ' + str(line_number) + '\n'
            err_msg += 'Invalid line: ' + line
            messagebox.showerror('Parsing error', err_msg)
            return

        # parse the time and fit the date to it for a correct datetime object
        start_time_object = datetime.datetime.strptime(start, '%H:%M')
        end_time_object = datetime.datetime.strptime(end, '%H:%M')
        date_object = date_object.replace(hour=start_time_object.hour)
        date_object = date_object.replace(minute=start_time_object.minute)
        end_time_object = end_time_object.replace(year=date_object.year)
        end_time_object = end_time_object.replace(month=date_object.month)
        end_time_object = end_time_object.replace(day=date_object.day)

        bands.append(Band(name, stage, date_object, end_time_object))

    # sort the bands into the days
    days = {}
    for band in bands:
        date = band.start
        # for a check if the date was found before (and thus if an entry exists in the dictionary)
        # the time needs to be equal. the days contain no times, therefore set them 0 here as well
        date = date.replace(hour=0).replace(minute=0)

        if not days.__contains__(date):
            days[date] = []

        days[date].append(band)

    return LineUp(stage_names, days, bands)


def browse_files(filetypes=(("All files", "*.*"),), entry_box=None):
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select input data file",
                                          filetypes=filetypes)

    if entry_box is not None:
        entry_box.delete(0, END)
        entry_box.insert(0, filename)

    return filename


def execute_parsing(file_path, buttons_to_activate):
    # we want to write to the global line-up, thus we don't have to carry it about as a parameter
    global lineup
    lineup = parse_lineup(file_path)
    if lineup is not None:
        for button in buttons_to_activate:
            button['state'] = NORMAL

        # add the stages to the main window for en-/disabling and sorting
        add_stages_to_gui(lineup.stages)

def import_selection(bands_selection):
    # first get the file to read the selected bands
    file_types = (("Personal Running Order text file", "*.prot*"), ("Text files", "*.txt*"), ("All files", "*.*"))
    filepath = browse_files(file_types)
    f = open(filepath, "r")

    # the bands are comma separated in just one line
    line = f.read()
    bands = line.split(",")

    # check if any of the bands don#t exist. if so, this is an illegal file and the user should be made aware
    global lineup
    bands_to_remove = []
    for band in bands:
        if not lineup.contains_band(band):
            # TODO: this needs to become a warning window!
            print("There are some bands in your selection, which are not present in the line up!")
            bands_to_remove.append(band)

    # remove illegal bands
    for band in bands_to_remove:
        bands.remove(band)

    for band in bands:
        bands_selection[band].set(1)


# TODO: what about bands / events that take place twice but on different days?
def export_selection(bands_selection):
    selected_bands = []
    for band in bands_selection:
        checkbox = bands_selection[band]
        if checkbox.get() == 1:
            selected_bands.append(band)

    filetypes = (("Personal Running Order text file", "*.prot*"), ("Text file", "*.txt*"))
    filename = save_file_as_browser(filetypes)

    # write list of selected bands to simple text file, separated only by comma
    f = open(filename, "w")
    i = 0
    for band in selected_bands:
        f.write(band)
        if i < len(selected_bands) - 1:
            f.write(',')
        i += 1


def clear_selection(bands_selection):
    for band in bands_selection:
        bands_selection[band].set(0)


def open_band_selection_window():
    selection_window = Toplevel(window)
    selection_window.title("Band selection for Personal Running Order")
    selection_window.wm_attributes('-topmost', 1)

    global lineup
    global settings
    global stages

    # we will want one section with all the bands to choose from, and one with buttons to click
    # to keep them separated and thus not screwing up the layout, put them into individual frames
    band_frame = Frame(selection_window)
    band_frame.grid(row=0, column=0)
    control_frame = Frame(selection_window)
    control_frame.grid(row=1, column=0)

    # sort bands alphabetically. for that, we need an array with just the names
    bands_list = []
    for band in lineup.bands:
        bands_list.append(band.name)
    bands_list.sort()

    # the alphabetical order should be displayed downwards first, then to the right second
    # (e.g:     Aborted             Arch Enemy      Blind Guardian
    #           Amon Amarth         Benediction     Bloodshot Dawn
    #           Anaal Nathrakh      Benighted       Cannibal Corpse)
    #
    # for this to work, we need to know the number of bands before starting to lay them out
    num_bands = len(bands_list)

    # if we set the max_columns we want to use, we can see how many rows we get
    max_columns = 6
    max_rows = int(num_bands / max_columns)

    # store all bands in a dictionary, where the value is the variable
    # the ceckbox's state can be read and written to via the variable
    bands_dict = {}

    # parse all the bands and list them
    row = 0
    column = 0
    for band in bands_list:
        # every band needs a checkbox before its name
        is_checked = IntVar()
        band_checkbox = Checkbutton(master=band_frame, onvalue=1, offvalue=0, variable=is_checked)
        band_checkbox.grid(row=row, column=2*column)
        bands_dict[band] = is_checked

        band_label = Label(master=band_frame, text=band)
        band_label.grid(row=row, column=2*column+1)

        row += 1
        if row > max_rows:
            row = 0
            column += 1

    button_column_start = 0
    button_row_start = 0

    import_button = Button(master=control_frame, text="Import Personal Running Order Selection",
                           command=lambda: import_selection(bands_dict))
    import_button.grid(row=0, column=0)

    export_button = Button(master=control_frame, text="Export Personal Running Order Selection",
                           command=lambda: export_selection(bands_dict))
    export_button.grid(row=0, column=1)

    clear_button = Button(master=control_frame, text="Clear selection",
                          command=lambda: clear_selection(bands_dict))
    clear_button.grid(row=0, column=2)

    save_order_button = Button(master=control_frame, text="Save Personal Running Order",
                               command=lambda: print_running_order(lineup, settings, stages, bands_dict))
    save_order_button.grid(row=0, column=3)


def save_settings(settings_window, is_image, is_pdf, dpi):
    global settings

    settings.save_as_image = is_image.get()
    settings.save_as_pdf = is_pdf.get()
    settings.dpi = int(dpi.get())
    print(is_image.get())
    print(is_pdf.get())
    print(dpi.get())

    settings_window.destroy()


def open_settings_window():
    global settings

    settings_window = Toplevel(window)
    settings_window.title("Settings for Personal Running Order")
    settings_window.wm_attributes('-topmost', 1)

    image_is_checked = IntVar()
    image_is_checked.set(settings.save_as_image)
    save_image_checkbox = Checkbutton(master=settings_window, onvalue=1, offvalue=0, variable=image_is_checked)
    save_image_checkbox.grid(row=0, column=0)
    save_image_label = Label(master=settings_window, text="Save Running Order as .png images")
    save_image_label.grid(row=0, column=1)

    pdf_is_checked = IntVar()
    pdf_is_checked.set(settings.save_as_pdf)
    save_pdf_checkbox = Checkbutton(master=settings_window, onvalue=1, offvalue=0, variable=pdf_is_checked)
    save_pdf_checkbox.grid(row=1, column=0)
    save_pdf_label = Label(master=settings_window, text="Save Running Order as a .pdf")
    save_pdf_label.grid(row=1, column=1)

    dpi = StringVar(settings_window)
    dpi.set(settings.dpi)
    dpi_entry = Entry(master=settings_window, textvariable=dpi)
    dpi_entry.grid(row=2, column=0)
    dpi_label = Label(master=settings_window, text="Resolution for printing in dpi")
    dpi_label.grid(row=2, column=1)

    save_button = Button(master=settings_window, text="Apply Settings",
                         command=lambda: save_settings(settings_window, image_is_checked, pdf_is_checked, dpi))
    save_button.grid(row=3, column=0)

    cancel_button = Button(master=settings_window, text="Discard Changes", command=lambda: settings_window.destroy())
    cancel_button.grid(row=3, column=1)


def setup_gui():
    """ Setup all GUI elements """
    headline = Label(master=window, text="Personal Running Order Tool")
    headline.grid(row=0, column=0, columnspan=4)

    file_path_entry = Entry(master=window)
    file_path_entry.insert(END, '')
    file_path_entry.grid(row=1, column=0, columnspan=2)
    csv_type = (("Comma Separated Values", "*.csv*"),)
    filebrowser_button = Button(master=window, text="...", command=lambda: browse_files(csv_type, file_path_entry))
    filebrowser_button.grid(row=1, column=2)

    # add a button to parse and print the pdf
    global lineup
    global settings
    global stages
    create_running_order_button = Button(master=window, text="Create Complete Running Order",
                                         state=DISABLED,
                                         command=lambda: print_running_order(lineup, settings, stages))
    create_running_order_button.grid(row=2, column=0, columnspan=3)

    create_personal_running_order_button = Button(master=window, text="Create Personal Running Order",
                                           state=DISABLED,
                                           command=lambda: open_band_selection_window())
    create_personal_running_order_button.grid(row=3, column=0, columnspan=3)

    parse_button = Button(master=window, text="parse file",
                          command=lambda: execute_parsing(file_path_entry.get(),
                                                          [create_running_order_button,
                                                           create_personal_running_order_button]))
    parse_button.grid(row=1, column=3)

    settings_button = Button(master=window, text="Settings", command=lambda: open_settings_window())
    settings_button.grid(row=3, column=3)


# prepare the lineup for global access. about every function needs it anyway.
lineup = None
# set up the stages for easy en- and disabling
stages = None
# settings should also be globally accessible
settings = Settings
setup_gui()
window.wm_attributes('-topmost', 1)
window.mainloop()
