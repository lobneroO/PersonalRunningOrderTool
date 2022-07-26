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

import copy
import datetime
import enum
import string
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.backends.backend_pdf as backend_pdf
from tkinter import *
from tkinter import filedialog

# TODO: debug, delete
import os


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


# The main window
window = Tk()


def get_timeless_date(dt) -> datetime:
    # make a copy of the date, so as to not overwrite the original info
    new_dt = copy.deepcopy(dt)
    new_dt = new_dt.replace(hour=0)
    new_dt = new_dt.replace(minute=0)

    return new_dt


def parse_lineup(file_path) -> LineUp:
    """ Parse the line up from a file """
    stages = []
    bands = []

    for line in open(file_path, 'r', encoding='utf-8'):
        if line.startswith('Band') or line.startswith('#'):
            # ignore the line, as it is only for description or comment
            continue

        data = line.split(',')
        name = data[0]
        date = data[1]
        start = data[2]
        end = data[3]
        stage = data[4].replace('\n', '')
        if not stages.__contains__(stage):
            stages.append(stage)

        date_object = datetime.datetime.strptime(date, '%d.%m.%Y')

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

    return LineUp(stages, days, bands)


def get_time_clashing_bands(selection):
    # for every band that is selected, read out the start and end time.
    # sort by day, then compare within each day each selected band
    clashing_bands = []
    global lineup
    selection_full_info = {}

    for date in lineup.dates:
        selection_full_info[date] = []  # list[Band]

    for band in selection:
        band_full_info = lineup.get_full_info(band)
        band_date = get_timeless_date(band_full_info.start)
        selection_full_info[band_date].append(band_full_info)

    for date in selection_full_info:
        bands_on_date = selection_full_info[date]
        for i in range(len(bands_on_date)):
            for j in range(i + 1, len(bands_on_date)):
                band_i = bands_on_date[i]
                band_j = bands_on_date[j]

                # a band clashes, if either start or end of band_i is between start and end of band_j
                # (or vice versa)
                start_i = band_i.start.time().hour + band_i.start.time().minute / 60
                end_i = band_i.end.time().hour + band_i.end.time().minute / 60
                start_j = band_j.start.time().hour + band_j.start.time().minute / 60
                end_j = band_j.end.time().hour + band_j.end.time().minute / 60

                # take care of a time wrap around at 0:00 AM! consider everything <4 as playing later, really
                # this is not a clean approach (due to hardcoded 4), but should work in most cases
                if start_i < 4:
                    start_i += 24
                if end_i < 4:
                    end_i += 24
                if start_j < 4:
                    start_j += 24
                if end_j < 4:
                    end_j += 24

                if (
                    ((start_i > start_j and start_i < end_j) or (end_i > start_j and end_i < end_j)) or\
                    ((start_j > start_i and start_j < end_i) or (end_j > start_i and end_j < end_i))
                    ):
                    # there is a clash between these bands. add both to the clashing list
                    if not clashing_bands.__contains__(band_i.name):
                        clashing_bands.append(band_i.name)
                    if not clashing_bands.__contains__(band_j.name):
                        clashing_bands.append(band_j.name)

    return clashing_bands


def print_running_order(bands_dict=None):
    global lineup
    global settings
    # TODO: make this alternating for a stage
    colors = ['lightgray', 'darkgray']

    # get the output path first. all images can be stored accordingly as individual files
    save_path = save_file_as_browser()
    if save_file_as_browser == "":
        # probably the user canceled. therefore, just return here
        return

    save_dir = os.path.dirname(save_path)
    file_name = os.path.basename(save_path)

    # read out the selected bands
    selection = []
    if bands_dict is not None:
        for band in bands_dict:
            if bands_dict[band].get() == 1:
                selection.append(band)

    # get the selected bands with time clashes
    clashing_bands = get_time_clashing_bands(selection)

    stages = lineup.stages
    print(stages)
    figures = []

    # loop all days, each day gets its own image
    for day in lineup.dates:
        # create the basic plot figure
        fig = plt.figure(figsize=(11.69, 8.27))
        # disable the plot's axes, they will be added in subplots
        plt.axis('off')

        # TODO: maybe try to hardcode time stamps to get the wrapping at 24/0 o'clock right
        hours = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00",
                 "19:00", "20:00", "21:00", "22:00", "23:00", "0:00", "1:00", "2:00", "3:00", "4:00"]

        # for readability of the resulting plot, offset the x position by 0.5
        x_offset_axis = 0.5

        # set axes (for bottom left first, then mirror for upper right)
        axis_bl = fig.add_subplot(111)
        axis_bl.yaxis.grid()
        axis_bl.set_xlim(x_offset_axis, len(stages) + x_offset_axis)
        # it will be read downwards, therefore invert the time labels on the axis
        axis_bl.set_ylim(27.3, 10.9)
        axis_bl.set_xticks(range(1, len(stages) + 1))
        axis_bl.set_xticklabels(stages)
        axis_bl.set_ylabel('Time')
        # axis_bl.set_yticks(range(1, len(hours) + 1))
        # axis_bl.set_yticklabels(hours)

        axis_ur = axis_bl.twiny().twinx()
        axis_ur.set_xlim(axis_bl.get_xlim())
        axis_ur.set_ylim(axis_bl.get_ylim())
        axis_ur.set_xticks(axis_bl.get_xticks())
        axis_ur.set_xticklabels(stages)
        axis_ur.set_ylabel('Time')
        # axis_ur.set_yticks(axis_bl.get_yticks())
        # axis_ur.set_yticklabels(axis_bl.get_yticklabels())

        # add all the band plots
        for band in lineup.dates[day]:
            start = band.start.time().hour + band.start.time().minute / 60
            # assume that no band will play after 4!
            # this is a bit hacky, but we need some time wrap around at 23:59->0:00
            if start < 4:
                start += 24
            end = band.end.time().hour + band.end.time().minute / 60
            if end < 4:
                end += 24
            stage = band.stage

            # plot the band onto the correct stage
            col = 'lightgray'
            if selection.__contains__(band.name):
                if clashing_bands.__contains__(band.name):
                    col = 'red'
                else:
                    col = 'green'
            # the rectangle_width is "normalized" to number of stages. i.e. 1 is exactly one stage width, scaling
            # with the number of stages. with 1, there would be no space between tow adjoining stages
            rectangle_width = 0.95
            # take into consideration the x_offset used for the x-axis
            x_offset = x_offset_axis + (1 - rectangle_width) * 0.5
            band_rectangle = patches.Rectangle([stages.index(stage) + x_offset, start], rectangle_width, end - start,
                                               color=col,  # colors[int(band.start.time().hour % len(colors))],
                                               linewidth=0.5)
            axis_bl.add_patch(band_rectangle)

            # print the actual start time to make it legible
            y_margin = 0.05
            time_font_size = 7
            plt.text(stages.index(stage) + x_offset, start + y_margin,
                     '{0}:{1:0>2}'.format(band.start.time().hour, band.start.time().minute),
                     va='top', fontsize=time_font_size)
            # also the end time on the opposite corner (thus preventing it from writing over the start time)
            # first, just plot the time to get the size of it (and plot it somewhere where it can't be seen)
            t = plt.text(-10, -10, '{0}:{1:0<2}'.format(band.end.time().hour, band.end.time().minute),
                          va='top', fontsize=time_font_size)
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer()).transformed(
                axis_bl.transData.inverted())

            # now print it into the plot at the correct position
            # that is: x = end_of_rectangle.x-text_width + x_offset
            # (where the x_offset is the one used for the x-axis)
            # and: y = end_of_rectangle.y-text_height
            x_coord = stages.index(stage) + rectangle_width - bb.width + x_offset
            # for whatever reason, the bbox y value is negative, therefore add it here to avoid a double negative
            y_coord = end + bb.height

            plt.text(x_coord, y_coord,
                     '{0}:{1:0<2}'.format(band.end.time().hour, band.end.time().minute),
                     va='top', fontsize=time_font_size)

            # print the name of the band
            plt.text(stages.index(stage)+1, (start + end) * 0.5, band.name, ha='center', va='center',
                     fontsize=9)

        day_str = day.strftime("%d.%m.%Y")
        plt.title(day_str, y=1.07)
        if settings.save_as_image:
            file_path = os.path.join(save_dir, '{0}-{1}.png'.format(file_name, day_str))
            plt.savefig(file_path, dpi=settings.dpi)
            print('saving {0}'.format(file_path))
        figures.append(fig)

    # print it all as one pdf
    if settings.save_as_pdf:
        pdf = backend_pdf.PdfPages(save_path + '.pdf')
        for fig in figures:
            pdf.savefig(fig)

        pdf.close()


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


def browse_files(filetypes=(("All files", "*.*"),), entry_box=None):
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select input data file",
                                          filetypes=filetypes)

    if entry_box is not None:
        entry_box.delete(0, END)
        entry_box.insert(0, filename)

    return filename


def execute_parsing(file_path, buttons_to_activate):
    # we want to write to the global line up, thus we don't have to carry it about as a parameter
    global lineup
    lineup = parse_lineup(file_path)
    if lineup is not None:
        for button in buttons_to_activate:
            button['state'] = NORMAL


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
                               command=lambda: print_running_order(bands_dict))
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
    create_running_order_button = Button(master=window, text="Create Complete Running Order",
                                         state=DISABLED,
                                         command=lambda: print_running_order())
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
# settings should also be globally accessible
settings = Settings
setup_gui()
window.wm_attributes('-topmost', 1)
window.mainloop()
