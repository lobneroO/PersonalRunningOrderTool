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
from datetime import datetime   # needed for access to strptime
import os

from tkinter import END
from tkinter import filedialog
from tkinter import messagebox

from custom_table import CustomTable

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.backends.backend_pdf as backend_pdf

from classes import LineUp


def get_timeless_date(dt) -> datetime:
    # make a copy of the date, so as to not overwrite the original info
    new_dt = copy.deepcopy(dt)
    new_dt = new_dt.replace(hour=0)
    new_dt = new_dt.replace(minute=0)

    return new_dt


def get_day_str(date: datetime) -> str:
    return date.strftime('%a')


def browse_files(filetypes=(("All files", "*.*"),), entry_box=None):
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select input data file",
                                          filetypes=filetypes)

    if entry_box is not None:
        entry_box.delete(0, END)
        entry_box.insert(0, filename)

    return filename


def save_settings(settings, settings_window, is_image, is_pdf, dpi,
                  band_time_size, band_name_size, stage_name_size):
    settings.save_as_image = is_image.get()
    settings.save_as_pdf = is_pdf.get()
    settings.dpi = int(dpi.get())
    settings.band_time_font_size = int(band_time_size.get())
    settings.band_name_font_size = int(band_name_size.get())
    settings.stage_name_font_size = int(stage_name_size.get())

    settings_window.destroy()


def save_file_as_browser(filetypes=(("All files", "*.*"),)):
    filename = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                            title="Select path and name for the file to be saved to",
                                            filetypes=filetypes)

    ext = os.path.splitext(filename)[1]
    if "." not in ext:
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


def correct_row_keys(table: CustomTable):
    data = table.model.data

    # when deleting a row, the keys (which are just one based numbers for the rows)
    # have to be reset. tkintertable does not do this itself, it will keep the old keys
    # and then break when adding a new row (e.g. keys 0,1 exist, 0 is deleted, 1 remains,
    # tkintertable will see one entry and therefore try to add key 1 a second time m( )
    # furthermore, when adding a row on 0-based keys, it will just add the row key
    # by the number of rows (e.g. keys 0,1 exist, an addRow will add key 3 m( m( m( )
    row_num = 0
    corrected_data = {}
    for key, value in data.items():
        corrected_data[row_num] = value
        row_num += 1

    table.model.data = {}
    table.model.importDict(corrected_data)


def get_alias_table_data(table: CustomTable):
    alias_dict = {}
    data = table.model.data

    print(data)

    # empty the band alias dict and refill it
    rows = table.model.getRowCount()
    for row in range(rows):
        # for some reason, tkintertables adds from base 1
        if row in data:
            if 'Band alias' in data[row] and 'Band name' in data[row]:
                alias_dict[data[row]['Band name']] = data[row]['Band alias']

    return alias_dict


def prepare_data_for_alias_table(data: dict) -> dict:

    # layout of the data has to look like this
    # data = {0: {'Band name': 'Heaven Shall Burn', 'Band alias': 'HSB'},
    #        1: {'Band name': 'Killswitch Engage', 'Band alias': 'Killswitch'}}

    out_data = {}
    # for tkintertables to work correctly, keys have to be 1 based, not 0 based
    key = 0
    for band_name, band_alias in data.items():
        out_data[key] = {'Band name': band_name, 'Band alias': band_alias}
        key += 1

    print(out_data)
    return out_data


def import_alias_settings(table: CustomTable):
    file_types = (("PRO Alias Files", "*.paf"), ("All files", "*.*"))

    # first get the file to read the aliased names
    file_path = browse_files(file_types)

    table.clear_data_no_interaction()
    table.importCSV(file_path, sep=',')


def export_alias_settings(table: CustomTable):
    file_types=(("PRO Alias Files", "*.paf"), ("All files", "*.*"))
    file_path = save_file_as_browser(file_types)

    # don't use the tables export function, as it will only write to a csv file,
    # but won't allow for custom extension setting

    data = get_alias_table_data(table)

    f = open(file_path, "w")
    i = 0

    # write the column headers, otherwise the import won't work
    f.write('Band name,Band alias\n')

    # write list of aliases to simple "csv" file, one line per band and alias
    for band_name, band_alias in data.items():
        f.write(band_name)
        f.write(',')
        f.write(band_alias)
        if i < len(data) - 1:
            f.write('\n')
        i += 1


def get_multi_bands(lineup: LineUp) -> dict:
    # create a dictionary of all bands that present multiple times
    # with their name as key and all the times as value
    out = {}
    for i in range(len(lineup.bands)):
        band_i = lineup.bands[i]
        # case 1: band_i.name is no in out
        #           in that case, find all occurrences and add them to out
        # case 2: band_i.name is already in out
        #           in that case, all occurrences have been found

        if band_i.name in out:
            continue

        # band_i is not in list yet, therefore add all occurrences
        # it is safe to assume, that all occurrences come _after_ the current one
        out[band_i.name] = [band_i]
        for j in range(i+1, len(lineup.bands)):
            band_j = lineup.bands[j]

            if band_i.name == band_j.name:
                out[band_i.name].append([band_j])

    # now remove all entries with just one time
    bands_to_remove = []
    for name, band_list in out.items():
        if len(band_list) == 1:
            bands_to_remove.append(name)

    for name in bands_to_remove:
        del out[name]

    return out


def clear_selection(bands_selection):
    for band in bands_selection:
        bands_selection[band].set(0)


def import_selection(lineup, bands_selection):
    # first get the file to read the selected bands
    file_types = (("Personal Running Order text file", "*.prot*"), ("Text files", "*.txt*"), ("All files", "*.*"))
    filepath = browse_files(file_types)
    f = open(filepath, "r")

    # the bands are one line each with the data and time comma separated as the next values
    selection = []
    for line in f:
        split = line.split(",")
        band_name = split[0]
        date = split[1] + ' ' + split[2].removesuffix('\n')
        date_time = datetime.strptime(date, "%x %X")

        selection.append((band_name, date_time))

    # check if any of the bands don't exist. if so, this is an illegal file and the user should be made aware
    bands_to_remove = []
    for band in selection:
        if not lineup.contains_band(band[0]):
            err_msg = 'There are some bands in your selection, which are not present in the line up!'
            messagebox.showerror('Selection error', err_msg)
            bands_to_remove.append(band)

    # remove illegal bands
    for band in bands_to_remove:
        selection.remove(band)

    for band in selection:
        # the band in selection is read out of the file, i.e. it  is only a tuple containing name and start date
        # but the bands in the band_selection are from the full line up, therefore these don't match.
        # get the correct line-up band first and then set the checkbox accordingly
        b = lineup.get_full_info(band[0], band[1])
        if b in bands_selection:
            bands_selection[b].set(1)
        else:
            print("Could not find band ", band[0])


def export_selection(lineup: LineUp, bands_selection: dict):
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
        f.write(band.name)
        f.write(',')
        date_str = band.start.strftime('%x')
        f.write(date_str)
        f.write(',')
        time_str = band.start.strftime('%X')
        f.write(time_str)
        if i < len(selected_bands) - 1:
            f.write('\n')
        i += 1


def get_time_clashing_bands(selection, lineup):
    # for every band that is selected, read out the start and end time.
    # sort by day, then compare within each day each selected band
    clashing_bands = []
    selection_full_info = {}

    for date in lineup.dates:
        selection_full_info[date] = []  # list[Band]

    for band in selection:
        band_date = get_timeless_date(band.start)
        selection_full_info[band_date].append(band)

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
                    if not clashing_bands.__contains__(band_i):
                        clashing_bands.append(band_i)
                    if not clashing_bands.__contains__(band_j):
                        clashing_bands.append(band_j)

    return clashing_bands


def get_band_name(band_alias_dict: dict, band_name: str):
    if band_name in band_alias_dict:
        return band_alias_dict[band_name]

    return band_name


def print_running_order(lineup, settings, stages, bands_dict=None, band_alias_dict=None):
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
    clashing_bands = get_time_clashing_bands(selection, lineup)

    stage_names = lineup.stages
    for stage in stages:
        if not stage.is_enabled() and stage.name in stage_names:
            stage_names.remove(stage.name)
    print(stage_names)
    figures = []

    # set the stage name font size
    plt.rc('xtick', labelsize=settings.stage_name_font_size)

    # loop all days, each day gets its own image
    for day in lineup.dates:
        # create the basic plot figure
        fig = plt.figure(figsize=(11.69, 8.27))
        # disable the plot's axes, they will be added in subplots
        plt.axis('off')

        # this is a bit hacky, but it gives out the correct time stamps for the wacken 2023 example
        # and should work as long as the y_lim is kept to 27.3 - 10.9
        hours = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00", "0:00", "2:00"]

        # for readability of the resulting plot, offset the x position by 0.5
        x_offset_axis = 0.5

        # set axes (for bottom left first, then mirror for upper right)
        axis_bl = fig.add_subplot(111)
        axis_bl.yaxis.grid()
        axis_bl.set_xlim(x_offset_axis, len(stage_names) + x_offset_axis)
        # it will be read downwards, therefore invert the time labels on the axis
        axis_bl.set_ylim(27.3, 10.9)
        axis_bl.set_xticks(range(1, len(stage_names) + 1))
        axis_bl.set_xticklabels(stage_names, rotation=30)
        axis_bl.set_ylabel('Time')
        axis_bl.set_yticklabels(hours)

        axis_ur = axis_bl.twiny().twinx()
        axis_ur.set_xlim(axis_bl.get_xlim())
        axis_ur.set_ylim(axis_bl.get_ylim())
        axis_ur.set_xticks(axis_bl.get_xticks())
        # TODO: rotation doesn't work here, for whatever reason
        axis_ur.set_xticklabels(axis_bl.get_xticklabels())
        axis_ur.set_ylabel('Time')
        axis_ur.set_yticklabels(axis_bl.get_yticklabels())

        # add all the band plots
        for band in lineup.dates[day]:
            stage = band.stage
            if stage not in stage_names:
                continue
            start = band.start.time().hour + band.start.time().minute / 60
            # assume that no band will play after 4!
            # this is a bit hacky, but we need some time wrap around at 23:59->0:00
            if start < 4:
                start += 24
            end = band.end.time().hour + band.end.time().minute / 60
            if end < 4:
                end += 24

            # plot the band onto the correct stage
            col = 'lightgray'
            if selection.__contains__(band):
                if clashing_bands.__contains__(band):
                    col = 'red'
                else:
                    col = 'green'
            # the rectangle_width is "normalized" to number of stages. i.e. 1 is exactly one stage width, scaling
            # with the number of stages. with 1, there would be no space between tow adjoining stages
            rectangle_width = 0.95
            # take into consideration the x_offset used for the x-axis
            x_offset = x_offset_axis + (1 - rectangle_width) * 0.5
            band_rectangle = patches.Rectangle([stage_names.index(stage) + x_offset, start], rectangle_width,
                                               end - start, color=col, linewidth=0.5)
            axis_bl.add_patch(band_rectangle)

            # print the actual start time to make it legible
            y_margin = 0.05
            start_time_str = str(band.start.time().hour) + ':' + str(band.start.time().minute).zfill(2)
            plt.text(stage_names.index(stage) + x_offset, start + y_margin, start_time_str,
                     va='top', fontsize=settings.band_time_font_size)
            # also the end time on the opposite corner (thus preventing it from writing over the start time)
            # first, just plot the time to get the size of it (and plot it somewhere where it can't be seen)
            end_time_str = str(band.end.time().hour) + ':' + str(band.end.time().minute).zfill(2)
            t = plt.text(-10, -10, end_time_str,
                          va='top', fontsize=settings.band_time_font_size)
            bb = t.get_window_extent(renderer=fig.canvas.get_renderer()).transformed(
                axis_bl.transData.inverted())

            # now print it into the plot at the correct position
            # that is: x = end_of_rectangle.x-text_width + x_offset
            # (where the x_offset is the one used for the x-axis)
            # and: y = end_of_rectangle.y-text_height
            x_coord = stage_names.index(stage) + rectangle_width - bb.width + x_offset
            # for whatever reason, the bbox y value is negative, therefore add it here to avoid a double negative
            y_coord = end + bb.height

            plt.text(x_coord, y_coord,
                     end_time_str,
                     va='top', fontsize=settings.band_time_font_size)

            # print the name of the band
            band_name = get_band_name(band_alias_dict, band.name)
            plt.text(stage_names.index(stage)+1, (start + end) * 0.5, band_name, ha='center', va='center',
                     fontsize=settings.band_name_font_size)

        day_str = day.strftime("%d.%m.%Y")
        plt.title(day_str, y=1.07)
        if settings.save_as_image:
            file_path = os.path.join(save_dir, '{0}-{1}.png'.format(file_name, day_str))
            plt.savefig(file_path, dpi=settings.dpi)
            print('saving {0}'.format(file_path))
        figures.append(fig)

    # print it all as one pdf
    if settings.save_as_pdf:
        if not save_path.endswith('.pdf'):
            save_path += '.pdf'
        pdf = backend_pdf.PdfPages(save_path)
        for fig in figures:
            pdf.savefig(fig)

        pdf.close()

    # close the figures
    plt.close('all')
