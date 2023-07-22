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
from tkinter import messagebox

from classes import Band
from classes import LineUp
from classes import Settings
from classes import Stage

from utils import get_day_str
from utils import browse_files
from utils import get_multi_bands
from utils import clear_selection
from utils import export_selection
from utils import import_selection
from utils import print_running_order
from utils import save_settings
from utils import get_alias_table_data
from utils import prepare_data_for_alias_table
from utils import correct_row_keys
from utils import import_alias_settings
from utils import export_alias_settings

from custom_table import CustomTable


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


def execute_parsing(file_path, buttons_to_activate):
    # we want to write to the global line-up, thus we don't have to carry it about as a parameter
    global lineup
    lineup = parse_lineup(file_path)
    if lineup is not None:
        for button in buttons_to_activate:
            button['state'] = NORMAL

        # add the stages to the main window for en-/disabling and sorting
        add_stages_to_gui(lineup.stages)


def use_table_data(alias_window, table: CustomTable):
    global band_alias_dict
    band_alias_dict = get_alias_table_data(table)

    print(band_alias_dict)
    if len(band_alias_dict) == 0:
        print("fuck")
    alias_window.destroy()


def remove_table_line(table: CustomTable):
    table.deleteRow()

    correct_row_keys(table)
    table.redraw()


def add_table_line(table: CustomTable):
    table.addRow()

    correct_row_keys(table)
    table.redraw()


def open_band_alias_window():
    alias_window = Toplevel(window)
    alias_window.title("Aliasing bands for the print")
    alias_window.wm_attributes('-topmost', 1)
    alias_window.protocol("WM_DELETE_WINDOW", lambda: alias_window.destroy())

    global band_alias_dict

    # add two frames, one for the table (with header)
    # and one for the controls to the side
    table_frame = Frame(alias_window)
    table_frame.grid(row=0, column=0)
    control_frame = Frame(alias_window)
    control_frame.grid(row=0, column=1)

    data = prepare_data_for_alias_table(band_alias_dict)
    if len(data) == 0:
        # ensure the table can be worked with. for that, it needs at least an empty entry
        data[1] = {'Band name': '', 'Band alias': ''}

    # define tree early for the button interaction
    table = CustomTable(table_frame, data=data)
    table.show()
    # these do jack shit
    table.autoResizeColumns()
    table.adjustColumnWidths()

    # set up the controls
    plus_button = Button(master=control_frame, text="+",
                         command=lambda: add_table_line(table))
    plus_button.grid(row=0, column=0)
    minus_button = Button(master=control_frame, text="-",
                          command=lambda: remove_table_line(table))
    minus_button.grid(row=0, column=1)

    use_button = Button(master=control_frame, text="Use alias settings",
                        command=lambda: use_table_data(alias_window, table))
    use_button.grid(row=1, column=0)
    cancel_button = Button(master=control_frame, text="Cancel", command=lambda: alias_window.destroy())
    cancel_button.grid(row=1, column=1)

    import_button = Button(master=control_frame, text="Import alias settings",
                           command=lambda: import_alias_settings(table))
    import_button.grid(row=2, column=0)
    export_button = Button(master=control_frame, text="Export alias settings",
                           command=lambda: export_alias_settings(table))
    export_button.grid(row=2, column=1)


def open_band_selection_window():
    selection_window = Toplevel(window)
    selection_window.title("Band selection for Personal Running Order")
    selection_window.wm_attributes('-topmost', 1)
    selection_window.protocol("WM_DELETE_WINDOW", lambda: selection_window.destroy())

    global lineup
    global settings
    global stages

    # we will want one section with all the bands to choose from, and one with buttons to click
    # to keep them separated and thus not screwing up the layout, put them into individual frames
    band_frame = Frame(selection_window)
    band_frame.grid(row=0, column=0)
    control_frame = Frame(selection_window)
    control_frame.grid(row=1, column=0)

    # get every band that is featured more than once
    multi_bands = get_multi_bands(lineup)

    # sort bands alphabetically primarily and for start date secondarily
    bands_list = []
    for band in lineup.bands:
        bands_list.append(band)
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
    # the checkbox's state can be read and written to via the variable
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

        label = band.name
        if band.name in multi_bands:
            label += ' (' + get_day_str(band.start) + ')'

        band_label = Label(master=band_frame, text=label)
        band_label.grid(row=row, column=2*column+1)

        row += 1
        if row > max_rows:
            row = 0
            column += 1

    import_button = Button(master=control_frame, text="Import Personal Running Order Selection",
                           command=lambda: import_selection(lineup, bands_dict))
    import_button.grid(row=0, column=0)

    export_button = Button(master=control_frame, text="Export Personal Running Order Selection",
                           command=lambda: export_selection(lineup, bands_dict))
    export_button.grid(row=0, column=1)

    clear_button = Button(master=control_frame, text="Clear selection",
                          command=lambda: clear_selection(bands_dict))
    clear_button.grid(row=0, column=2)

    print_order_button = Button(master=control_frame, text="Print Personal Running Order",
                                command=lambda:
                                print_running_order(lineup, settings, stages, bands_dict, band_alias_dict))
    print_order_button.grid(row=0, column=3)


def open_settings_window():
    global settings

    settings_window = Toplevel(window)
    settings_window.title("Settings for Personal Running Order")
    settings_window.wm_attributes('-topmost', 1)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: settings_window.destroy())

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

    # let the user choose the font sizes for bands and stages
    band_time_size = StringVar(settings_window)
    band_time_size.set(settings.band_time_font_size)
    band_time_size_entry = Entry(master=settings_window, textvariable=band_time_size)
    band_time_size_entry.grid(row=3, column=0)
    band_time_size_label = Label(master=settings_window, text="Font size of time in band rectangles")
    band_time_size_label.grid(row=3, column=1)

    band_name_size = StringVar(settings_window)
    band_name_size.set(settings.band_name_font_size)
    band_name_size_entry = Entry(master=settings_window, textvariable=band_name_size)
    band_name_size_entry.grid(row=4, column=0)
    band_name_size_label = Label(master=settings_window, text="Font size of band name in rectangles")
    band_name_size_label.grid(row=4, column=1)

    stage_name_size = StringVar(settings_window)
    stage_name_size.set(settings.stage_name_font_size)
    stage_name_size_entry = Entry(master=settings_window, textvariable=stage_name_size)
    stage_name_size_entry.grid(row=5, column=0)
    stage_name_size_label = Label(master=settings_window, text="Font size of stage names on x axis")
    stage_name_size_label.grid(row=5, column=1)

    save_button = Button(master=settings_window, text="Apply Settings",
                         command=lambda: save_settings(
                             settings, settings_window, image_is_checked, pdf_is_checked, dpi,
                             band_time_size, band_name_size, stage_name_size))
    save_button.grid(row=6, column=0)

    cancel_button = Button(master=settings_window, text="Discard Changes", command=lambda: settings_window.destroy())
    cancel_button.grid(row=6, column=1)


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
                                         command=lambda:
                                         print_running_order(lineup, settings, stages, None, band_alias_dict))
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

    alias_button = Button(master=window, text="alias band names",
                          command=lambda: open_band_alias_window())
    alias_button.grid(row=2, column=3)

    settings_button = Button(master=window, text="Settings", command=lambda: open_settings_window())
    settings_button.grid(row=3, column=3)


# prepare the lineup for global access. about every function needs it anyway.
lineup = None
# set up the stages for easy en- and disabling
stages = None
# settings should also be globally accessible
settings = Settings
# allow band aliases for better printing if the names are too long
band_alias_dict = dict()
setup_gui()
window.wm_attributes('-topmost', 1)
window.mainloop()
