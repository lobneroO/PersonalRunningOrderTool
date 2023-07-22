# Table of Contents
- [PersonalRunningOrderTool Description](#personalrunningordertool-description)
- [What does it do](#what-does-it-do)
- [Releases](#releases)
- [Usage](#usage)
  * [Line Up .csv file](#line-up-csv-file)
    + [Bands playing after 0:00 AM](#bands-playing-after-0-00-am)
  * [The GUI](#the-gui)
    + [Main window](#main-window)
    + [Settings window](#settings-window)
    + [alias_band_names_window](#alias-band-names-window)
    + [Band selection for Personal Running Order window](#band-selection-for-personal-running-order-window)
- [What problems may occur](#what-problems-may-occur)
- [Building the project](#building-the-project)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


# PersonalRunningOrderTool Description
A tool to create personalized running orders of events, such as festivals. 

# What does it do
In Personal Running Order Tool (or "PRO"), you can read in the line-up of a festival as a csv file. 
Once PRO has parsed this information, you can print the running order in a timetable manner.
You can also mark all the bands you want to see at the festival, which will then be marked (currently in green).
If two bands clash in their times, the marking will reflect that (currently in red).

Here is an example of what it might look like (with the Summer-Breeze Line Up of 2022 on that given day).
![docu-17 08 2022](https://user-images.githubusercontent.com/17877050/182021209-8dd4ed3d-d114-409d-8f4d-f76aad437d36.png)


Once you have created a selection of bands, you can also export this list, and later reimport it. 
You can import multiple selection files.
The export can be done in any file format you want to, as it is just a text file of band names separated by commas.
However, the default will be ".prot" such that you can easily see that it belongs to PRO.

# Releases
The releases are created on Arch Linux, since that is what I use.
I assume the Linux executable will work on any distribution, but I cannot test this at the moment.

For Windows, I create the .exe file in wine, so some things may fail or some differences my go unnoticed by me.
It should work for the most part, but you can run the script directly in python or create your own executable if it doesn't.
If you notice an error that would prevent Windows execution, please do share. 

Both Linux and Windows executables are created with [PyInstaller](https://pyinstaller.org/en/stable/).

# Usage
The usage is fairly simple. First you create a line-up .csv file, which you will then import. 
You can then choose to save the line-up for your event as a .pdf, or first select bands to mark before saving.

## Line Up .csv file
The line-up .csv file needs to be formatted thus:
1. You may choose to add a header line for orientation:

    `Band,Date,Start,End,Stage`
2. You may add comments withing the file. Every line that starts with a '#' character will be ignored
3. You then enter every band name, the date on which they play, the starting time and ending time (currently only German notation is supported) 
and finally the stage the band will play on (if you edit this file in Excel, Calc or a similar spreadsheet editor, make sure the dates and times are not auto formatted!).
Each band must be on its own line.

    `Fleshgod Apocalypse,17.08.2022,23:40,00:25,T-Stage`
    
For every stage found in this file, a new column in the output graphics will be created. Thus, if you have a typo in this file for one band, it may end up in its own column.
### Bands playing after 0:00 AM
If you have a band, that plays after midnight, like at 1:00 AM, you will probably not want to associate it with the next day, even though that would technically be correct.
Therefore, if your band is playing on 18.08.2022 at 1:00 AM, you will still want to give it the date 17.08.2022 to associate it with that day.
For every start and end time < 4 (i.e. 4 AM), 24 hours will be added in the timetable (although the time stamps will show the correct time). 
E.g. consider this entry in the line-up .csv file:

    `Igorrr,20.08.2022,2:15,3:00,T-Stage`
    
In the pdf it would appear in the timetable for 20.08.2022 at the very end:
![image](https://user-images.githubusercontent.com/17877050/182021244-3e153f9b-4cd7-497d-9f53-8e6be6ba7f35.png)


## The GUI
The GUI should be somewhat self-explanatory. 
Do note however, that "Export" in the selection tab means to export the selected bands to a text based files. 
That is: For every selection you made, an entry is made into the chosen text file. The entries are comma separated
"Save" means to save the timetables as a .pdf file. This won't be editable in general. 

If you want to change your selection, you would have to import your earlier export, or select differently in the GUI and then save again.

### Main window
Upon start, this window should greet you:

![image](https://github.com/lobneroO/PersonalRunningOrderTool/assets/17877050/b6ba8cf6-88b8-4baa-a887-79568b8ab5a8)


You can either enter a path to a .csv file with the line-up manually into the text box on the left, or you can browse to it with a file browser by clicking the "..." button.
Once you have chosen a file, click "parse file" in order to load it into PRO.
If your line-up file was correctly parsed, the two buttons "Create Complete Running Order" and "Create Personal Running Order" will activate, and you can now click them.
Furthermore, a list of stages will appear that you can individually select or deselect. 
Only selected stages will be printed to your running order files.
This way, if you won't need a stage, you can deselect it and get more space for all other stages.
![image](https://github.com/lobneroO/PersonalRunningOrderTool/assets/17877050/d5f1d27f-7674-412c-a558-82378de3a5f0)




"Create Complete Running Order" will open a file browser for your output .pdf file. You can choose any destination and name you want, as long as you have writing rights in the chosen directory.
Once a path was chosen, it will start to render the timetable and write it out. At the moment, there will be no success message (nor failure, for that matter). 
You can simply check the directory you have chosen for saving.
Per default, the directory of the program is selected, so if you are unsure where to look, start here.

"Create Personal Running Order" will open the Band selection for Personal Running Order window. 

"Settings" will open the settings window.

### Settings window
The settings window will let you make a few settings.

![image](https://github.com/lobneroO/PersonalRunningOrderTool/assets/17877050/2ff4f5d8-478b-4322-be88-6b9f25dfc5a7)


First, you can choose how to save your running order - either as a .pdf or as several .png files (or both).

Note that you can disable both and still choose to save your results later on. 
A filebrowser will open, and you can choose a path and name, however since you enabled neither .pdf nor .png, no files will actually be created.

The default settings are to save the .pdf file only.

You can choose the dpi resolution used for the plots (i.e. the images / pdf).
The default size of the image / pdf will be A4 with a 200dpi resolution, which should suffice.
If you plan to print this as a bigger file (say A3), you may want to increase the dpi to still get a feasible quality.

You also have font size choices for band start and end times, band names and stage names.

The "Apply Settings" will apply your chosen settings and close the settings window.
The "Discard Changes" button will discard any changes you made and close the settings window.

The default is a setting of 200 dpi, font size 7 for times, font size 9 for bands and font size 10 for stages.

Settings will not be saved after closing the program yet. If you make changes and restart the program, you will have to make the same changes again.

### alias band names window
"alias band names" offers the ability to change names from how they are written in the input file to something you'd like.
This is useful mostly when bands have long names that don't fit their printed boxes.
E.g. you can shorten "Heaven Shall Burn" to "HSB" here without having to edit the input file.
The aliasing will not take effect in the band selection window, but only in the printed output.

![image](https://github.com/lobneroO/PersonalRunningOrderTool/assets/17877050/2c78d3c7-3c16-44aa-96ee-98b63a547edd)

The aliasing settings can be exported and reused (even on other festivals), such that you can create a personal database
and reuse it everytime.

### Band selection for Personal Running Order window
This window contains in a grid all the bands of the line-up in alphabetical order. 
On the left side of each band is its associated checkbox. 
If you would like a band marked in the output .pdf, select its checkbox here.

![image](https://user-images.githubusercontent.com/17877050/182021125-1f733a46-b08d-4c7d-b579-6d0681b8f2a6.png)

If you want to edit this selection later on, you need to export it. 
In order to export it, use the "Export Personal Running Order Selection" button. 
It will open a file browser where you can enter a file name and choose a path for where to store the selection.

If you have exported your selection in a previous session, you will want to import it.
For this, use the "Import Personal Running Order Selection" button. 
It will open a file browser where you can choose your previous export.

If you import a file with band names, which are not listed in the festival, these band names will be ignored. 
At the moment, you won't get a warning either.
If you have bands selected and import a previous selection, the new selection will use all bands out of your current and your imported selections.

If you want to clear all selected bands, use the "Clear selection" button.

Once you are satisfied with your selection, you can save the running order with markings to a .pdf.
Use the "Save Personal Running Order" button to do so. 
It will open a file browser where you can enter a file name and choose a path for where to save your timetable.

# What problems may occur
While the basic functionality of PRO can give you a very helpful timetable, there are a few limitations and problems.

- _The time stamps in the timetable are writing over the band's name_

  With very short slots, there is very little place to put the stamps. 
  Currently, no check for space is implemented, thus the name and time stamps will write into their positions every time.
  If you need a workaround, shorten the band names in the "alias band names" settings.
  (e.g. "Fleshgod Apocalypse" can become "Fleshgod" or simply "FA").
- _The time axes (y axes) is fixed_

  In a future version, I will base this on the times given in the line-up .csv file. 
  If your event needs times outside the current range, you can find the limits in the script in main.py in the `print_running_order` function
      `axis_bl.set_ylim(27.3, 10.9)`
  Change these limits to what you need. Note that a wrap around for the clock is not yet supported, so if a band plays from 23:00 to 1:00,
  your limit would be at 25 rather than 1 (though it is advisable to add a bit of a margin, e.g. 25.3).


# Building the project
The project releases are created with PyInstaller on Arch Linux and through Wine on Windows.
You should be able to use any tool of your choosing suited for this task, but if you have a similar setup
(i.e. you use Linux and have wine installed, as well as PyInstaller for both), then you can run the create_release.sh script
to create a single-file release of your own.
A dist folder should be created next to the PersonalRunningOrderTool.py script, in which then lies one executable for 
Linux and one for Windows
