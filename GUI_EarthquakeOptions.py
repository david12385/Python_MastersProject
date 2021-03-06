# David Lindsey - GISC 6389 - Master's Project
# Contact: dcl160230@utdallas.edu
# The following code represents the functionality for Earthquake Options.

# All import statements for utilized modules, excluding arcpy.
# Arcpy module will be imported at a later time.

import tkinter
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import sys
import os
import shutil
import time
import csv
import numpy
from urllib import request
from urllib.error import HTTPError
from urllib.error import URLError
import zipfile
import calendar
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import collections
from collections import OrderedDict
import traceback
from time import sleep  # careful - this can freeze the GUI
from threading import Thread # this is used to unfreeze the GUI
from statistics import mode, StatisticsError
from GUI_FrameLifts import FrameLifts

# For Python 2.7 consideration:
# import Tkinter as tkinter
# import tkFileDialog as filedialog
# import ttk
# import tkMessageBox as messagebox
# import ScrolledText as scrolledtext
# from urllib2 import HTTPError
# from urllib2 import URLError
# from dummy_threading import Thread
# import pip
# pip.main(["install", "statistics"])
# from statistics import mode, StatisticsError

# Programmer-defined parameters for width/height of GUI
guiWindow_EarthquakeOptions_Width = 470
guiWindow_EarthquakeOptions_Height = 225

# Tuple for populating earthquake timespan text values within the combo box.
textCombo_EarthquakeTimespan = ("Select...", "Past Hour", "Past Day",
                               "Past 7 Days", "Past 30 Days", "Custom...")

# Tuple for populating earthquake magnitude text values within the combo box.
textCombo_EarthquakeMagnitude = \
    ("Select...", "All", "1.0+", "2.5+", "4.5+", "Custom...")

# Tuple for populating the timespan combobox for monthly integer values when
# the custom timespan option is selected.
intCombo_Months = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

# Tuple for populating the magnitude combobox with interger values for the
# custom magnitude option.
dbl_Combo_Magnitudes = (-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0,
                        4.5, 5.0,5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5,
                        10.0)

# Formula to acquire the current year in YYYY format.
int_curYear = int(datetime.datetime.today().strftime("%Y"))

# The following code populates a list of years beginning with 1900 and ending
# with the current year derived from the previous step. This list will be used
# to populate the custom timespan combo box.
intList_Years = []
while int_curYear >= 1900:
    intList_Years.append(int_curYear)
    int_curYear = int_curYear - 1

# Dictionary showing Census FIPs codes assigned to state abbreviation.
# This is used for the Census-derived polygon shapefile manipulations.
dict_StateName_StateFIPs = {"AL":"01", "AK":"02", "AZ":"04", "AR":"05",
                            "CA":"06", "CO":"08", "CT":"09", "DE":"10",
                            "DC":"11", "FL":"12", "GA":"13", "HI":"15",
                            "ID":"16", "IL":"17", "IN":"18", "IA":"19",
                            "KS":"20", "KY":"21", "LA":"22", "ME":"23",
                            "MD":"24", "MA":"25", "MI":"26", "MN":"27",
                            "MS":"28", "MO":"29", "MT":"30", "NE":"31",
                            "NV":"32", "NH":"33", "NJ":"34", "NM":"35",
                            "NY":"36", "NC":"37", "ND":"38", "OH":"39",
                            "OK":"40", "OR":"41", "PA":"42", "RI":"44",
                            "SC":"45", "SD":"46", "TN":"47", "TX":"48",
                            "UT":"49", "VT":"50", "VA":"51", "WA":"53",
                            "WV":"54", "WI":"55", "WY":"56"}

# Key/Values from Dictionary, sorted by Value (state abbreviation).
# To be used to populate the State combo box under Clipping Options (as string).
dictKeys_StateNames = sorted(dict_StateName_StateFIPs)

# Dictionary remains intact and unchanged (not string), only sorted.
# This is used for dictionary iterations with the UpdateCursor operations.
dictKeys_OrderedDict_StateNames = OrderedDict(dict_StateName_StateFIPs)

# Generic header for any error messages received.
errorMessage_Header = "Error Message"

# Parameter found within the USGS CSV file, within the "type" column.
# This parameter is used to extract ONLY the earthquakes from those CSV files
# (this selection will exclude manmade explosions, ice quakes, among other
# non-earthquake types).
csv_Parameter_Earthquake = "earthquake"

# This string represents the static portion of the URL path for accessing the
# earthquake CSVs from USGS website (used for non-custom parameter inputs only).
earthquake_siteURL = \
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"

# This string represents the static portion of the URL path for accessing the
# the earthquake CSVs from USGS website (used for custom parameter inputs only).
earthquake_Custom_siteURL_CSV = \
    "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"

# Additional string parameters used to access CUSTOM timespan/magnitude URLs.
earthquake_Custom_siteURL_StartTime = "&starttime="
earthquake_Custom_siteURL_EndTime = "&endtime="
earthquake_Custom_siteURL_Min_Magnitude = "&minmagnitude="
earthquake_Custom_siteURL_Max_Magnitude = "&maxmagnitude="

# Comma-delimited header names for the USGS earthquake CSVs.
quake_headers = "time" + "," + "latitude" + "," + "longitude" + "," + "depth" +\
                "," + "mag" + "," + "magType" + "," + "nst" + "," + "gap" +\
                "," + "dmin" + "," + "rms" + "," + "net" + "," + "id" + "," +\
                "updated" + "," + "place" + "," + "type" + "," +\
                "horizontalError" + "," + "depthError" + "," + "magError" +\
                "," + "magNst" + "," + "status" + "," + "locationSource" +\
                "," + "magSource"

# Text that will display within the URL textbox prior to a web URL link being
# created by the user.
urlDialog_Message = "URL will populate once Timespan and Magnitude have been " \
                    "selected."

# Text that will display within the output folder textbox prior to an output
# workspace being selected by the user.
folderDialog_Message = "Output workspace folder path will display here..."

# Various components of output naming conventions to be used.
usgs = "usgs"
quake = "quake"
fileExtCSV = ".csv"
fileExtZip = ".zip"
fileExtShp = ".shp"
fileExtText = ".txt"

# Color variables for use with ScrolledText box output text.
# Red for errors, orange for warning, and blue for geoprocessing messages.
color_Red = "red"
color_Orange = "orange"
color_Blue = "blue"

# Name/variable used for creating the output File GDB for GIS data creation.
nameFileGDB = "GIS_Output.gdb"

# The current date (__YYYYMMDD) will be attached to the end of most output
# naming conventions.
curDate = "__" + datetime.datetime.today().strftime("%Y%m%d")

# The actual name of the US States shapefile downloaded/utilized from the Census
# Bureau website.
census_URL_CountyShapefile_FileName = "cb_2017_us_county_500k"

# The URL string with combined variables to access the Census Bureau shapefile.
census_URL_CountyShapefile = "http://www2.census.gov/geo/tiger/GENZ2017/shp/" +\
                             census_URL_CountyShapefile_FileName + fileExtZip

# Column header for US state FIPS code found within the Census Bureau shapefile.
census_Shapefile_Field_StateFIPS = "STATEFP"

# Column header for US county names found within the Census Bureau shapefile.
census_Shapefile_Field_CountyName = "NAME"

# Static output name for the extracted US-and-DC-only polygon feature class.
# This naming convention is used for the Shapefile-to-feature-class conversion.
featureClass_50States_and_DC_only = "USA_50_and_DC_only"

# Column header from CSV file for magnitude, used as an input parameter for the
# various ArcPy analyses.
analysis_Mag_Field = "mag"

# ArcPy module is imported at this location so as to check for any runtime
# errors (due to potential internet connection issues and/or licensing issues).
# This issue is handled within the GUI_ApplicationDriver.py file.
# If the user chooses to proceed with the application after receiving a
# "Runtime Error", the same error will be ignored/passed within this .py file.
try:

    # If ArcPy available, import it.
    import arcpy

    # Universal parameters for assigning the Projected Coordinate System to the
    # earthquake and polygon feature classes.
    # WGS84 Web Mercator Auxiliary Sphere with -30.0 offset of Central Meridian.
    # These parameters were chosen to fix the extent issues created by Alaska
    # appearing "split". This extent problem was causing issues with some
    # geoprocessing tasks (Spline especially).
    spatialRef = arcpy.SpatialReference()

    # 3857 = WGS_1984_Web_Mercator_Auxiliary_Sphere
    spatialRef.createFromFile(3857)
    spatialRef_3857 = spatialRef.exportToString()
    spatialRef_3857 = \
        spatialRef_3857.replace("PARAMETER['Central_Meridian',0.0]",
                          "PARAMETER['Central_Meridian',-30.0]")
    pcsReference = arcpy.SpatialReference()
    pcsReference.loadFromString(spatialRef_3857)
    pcsReferenceString = "WGS_1984_Web_Mercator_Auxiliary_Sphere"

except RuntimeError:

    # Example: "Not signed into Portal or ArcGIS Pro not installed."

    # If ArcPy not available, skip it.
    # This allows the data to still be downloaded without ArcGIS functionality.
    pass

# Class for the Earthquake Options GUI functionality.
class EarthquakeOptions(FrameLifts):

    def __init__(self, *args, **kwargs):
        FrameLifts.__init__(self, *args, **kwargs)

        # Universal parameters used throughout various functions of this class.
        # Setting values to None and later testing for None alleviates potential
        # "Attribute Errors" later on, as some variables will not be used if
        # certain tasks are not needed.

        self.timespan_url = None
        self.magnitude_url = None
        self.comboFrame_Custom_Timespan = None
        self.comboFrame_Custom_Magnitude = None
        self.custom_magnitude_url = None
        self.custom_timespan_url = None
        self.intCustomTimespan_Year_From = None
        self.intCustomTimespan_Year_To = None
        self.intCustomTimespan_Month_From = None
        self.intCustomTimespan_Month_To = None
        self.doubleCustom_Magnitude_Min = None
        self.doubleCustom_Magnitude_Max = None
        self.textCustomMagFrom = None
        self.textCustomMagTo = None
        self.text_eq_Custom_siteURL = None
        self.custom_Mag_Naming = None
        self.customSelection_Height = None
        self.folderDialogPath = None
        self.analysisOptionsFrame = None
        self.scrollBoxFrame = None
        self.progressBarFrame = None
        self.radioButton_Selection = None
        self.subFolder_GIS = None
        self.comboFrame_State = None
        self.comboFrame_Counties = None
        self.combo_State_Name = None
        self.combo_County_Name = None
        self.stringState_Name = None
        self.stringCounty_Name = None
        self.nameFeatureClass_FromCSV = None

        # Settings and configuration for the Earthquake Options GUI window.
        self.winfo_toplevel().title("Earthquake Options")
        self.winfo_toplevel().geometry("%dx%d" %
                                        (guiWindow_EarthquakeOptions_Width,
                                         guiWindow_EarthquakeOptions_Height))

        # The GUI frame that all child frames will be placed.
        self.winFrame = tkinter.Frame(self.winfo_toplevel())
        self.winFrame.grid(
            column=0, row=0, padx=0, pady=0, columnspan=2, sticky=tkinter.NW)

        # Frame that displays the initial Earthquake dialog layout.
        self.initialFrame = tkinter.Frame(self.winFrame)
        self.initialFrame.grid(column=0, row=0, sticky=tkinter.NW)

        # Frame that displays the additional options if the user selects the
        # "More Options" checkbox.
        self.optionsFrame = tkinter.Frame(self.winFrame)
        self.optionsFrame.grid(column=1, row=0, columnspan=2, sticky=tkinter.NW)

        # Frame that displays the scrolled text box and progress bar after a
        # user clicks the OK button.
        self.processingFrame = tkinter.Frame(self.winFrame)
        self.processingFrame.grid(
            column=0, row=1, columnspan=2, sticky=tkinter.SW)

        # Executes the function controlling the Timespan/Magnitude comboboxes
        self.func_ComboFrame()

        # Executes the function controlling the URL display text functionality.
        self.func_URLFrame()

        # Executes the function controlling the Workspace Folder dialog/text.
        self.func_WorkspaceFolderFrame()

        # Executes the function controlling the Exit/Back/OK buttons.
        self.func_ButtonFrame()

    def func_ComboFrame(self):

        # This function controls the display of the combobox frame.

        # Widget frame housing the combobox items for Timespan/Magnitude.
        self.comboFrame = tkinter.Frame(self.initialFrame)
        self.comboFrame.grid(column=0, row=0, padx=40, pady=5, sticky=tkinter.W)

        # Label for Timespan combobox.
        comboLabel_Timespan = ttk.Label(self.comboFrame, text="Timespan (UTC):")
        comboLabel_Timespan.grid(column=0, row=0, sticky=tkinter.W)

        # Label for Magnitude combobox.
        comboLabel_Magnitude = ttk.Label(self.comboFrame, text="Magnitude:")
        comboLabel_Magnitude.grid(column=2, row=0, sticky=tkinter.W)

        # Combobox requirements for Timespan.
        self.stringEarthquakeTimespan = tkinter.StringVar()
        self.combo_EarthquakeTimespan = ttk.Combobox(self.comboFrame, width=12,
                                    textvariable=self.stringEarthquakeTimespan,
                                    state="readonly")
        self.combo_EarthquakeTimespan["values"] = (textCombo_EarthquakeTimespan)
        self.combo_EarthquakeTimespan.grid(column=0, row=1, sticky=tkinter.W)

        # GIF icon to symbolize Earthquakes within the GUI.
        dirFolder = os.path.dirname(__file__)
        gifPath = os.path.join(dirFolder, "Icon_Earthquake.gif")
        self.photo_Earthquake_Icon = \
            tkinter.PhotoImage(file=gifPath)
        colorCode_Black = "black"
        self.subSampleImage = self.photo_Earthquake_Icon.subsample(4, 4)
        self.label_for_icon = ttk.Label(self.comboFrame, borderwidth=2,
                                        relief="solid",
                                        background=colorCode_Black,
                                        image=self.subSampleImage)
        self.label_for_icon.photo = self.photo_Earthquake_Icon
        self.label_for_icon.grid(column=1, row=0, padx=0,
                                 pady=5, sticky=tkinter.EW, rowspan=2)

        # Combobox requirements for Magnitude.
        self.stringEarthquakeMagnitude = tkinter.StringVar()
        self.combo_EarthquakeMagnitude = ttk.Combobox(self.comboFrame, width=12,
                                    textvariable=self.stringEarthquakeMagnitude,
                                    state="readonly")
        self.combo_EarthquakeMagnitude["values"] = \
            (textCombo_EarthquakeMagnitude)
        self.combo_EarthquakeMagnitude.grid(column=2, row=1, sticky=tkinter.W)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_EarthquakeTimespan.bind("<<ComboboxSelected>>",
                                      self.func_PopulateURLField_Timespan)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_EarthquakeMagnitude.bind("<<ComboboxSelected>>",
                                       self.func_PopulateURLField_Magnitude)

        # For all items in the comboFrame, configure their grids the same way.
        for child in self.comboFrame.winfo_children():
            child.grid_configure(padx=25, pady=1)

        # Display first index for Timespan (Select...).
        self.combo_EarthquakeTimespan.current(0)

        # Display first index for Magnitude (Select...).
        self.combo_EarthquakeMagnitude.current(0)

    def func_ComboCustomTimespan(self):

        # This function controls the display of the custom combobox frame
        # controlling the custom Timespan.

        # If the custom timespan combobox frame already exists (is visible)...
        if self.comboFrame_Custom_Timespan is not None:

            # Remove the frame.
            self.comboFrame_Custom_Timespan.grid_remove()

        # Widget frame for custom timespan.
        self.comboFrame_Custom_Timespan = tkinter.Frame(self.initialFrame)
        self.comboFrame_Custom_Timespan.grid(column=0, row=1, padx=10, pady=5,
                             sticky=tkinter.W)

        # Label frame for the FROM custom timespan comboboxes.
        self.comboLabelFrameCustomTimespan_From = \
            ttk.LabelFrame(self.comboFrame_Custom_Timespan, text="From:",
                           labelanchor=tkinter.N)
        self.comboLabelFrameCustomTimespan_From.grid(column=0, row=0, padx=5,
                                                     pady = 5, sticky=tkinter.W)

        # Label for YEAR FROM combobox.
        comboLabel_CustomTimespan_Year_From = ttk.Label(
            self.comboLabelFrameCustomTimespan_From,
            text="Year:")
        comboLabel_CustomTimespan_Year_From.grid(column=0, row=0,
                                                 sticky=tkinter.W)

        # Label for MONTH FROM combobox.
        comboLabel_CustomTimespan_Month_From = \
            ttk.Label(self.comboLabelFrameCustomTimespan_From, text="Month:")
        comboLabel_CustomTimespan_Month_From.grid(column=1, row=0,
                                                  sticky=tkinter.E)

        # Combobox requirements for YEAR FROM.
        self.intCustomTimespan_Year_From = tkinter.IntVar()
        self.combo_CustomTimespan_Year_From = ttk.Combobox(
            self.comboLabelFrameCustomTimespan_From,
            width=4,
            textvariable=self.intCustomTimespan_Year_From,
            state="readonly")
        self.combo_CustomTimespan_Year_From["values"] = (intList_Years)
        self.combo_CustomTimespan_Year_From.grid(column=0, row=1,
                                            sticky=tkinter.W)

        # Combobox requirements for MONTH FROM.
        self.intCustomTimespan_Month_From = tkinter.IntVar()
        self.combo_CustomTimespan_Month_From = \
            ttk.Combobox(self.comboLabelFrameCustomTimespan_From, width=2,
                         textvariable=self.intCustomTimespan_Month_From,
                         state="readonly")
        self.combo_CustomTimespan_Month_From["values"] = (intCombo_Months)
        self.combo_CustomTimespan_Month_From.grid(column=1, row=1,
                                                  sticky=tkinter.E)

        # Label frame for the TO custom timespan comboboxes.
        self.comboLabelFrameCustomTimespan_To = ttk.LabelFrame(
        self.comboFrame_Custom_Timespan, text="To:", labelanchor=tkinter.N)
        self.comboLabelFrameCustomTimespan_To.grid(column=1, row=0, padx=5,
                                                    pady=5, sticky=tkinter.W)

        # Label for YEAR TO combobox.
        comboLabel_CustomTimespan_Year_To = ttk.Label(
            self.comboLabelFrameCustomTimespan_To,
            text="Year:")
        comboLabel_CustomTimespan_Year_To.grid(column=0, row=0,
                                               sticky=tkinter.W)

        # Label for MONTH TO combobox.
        comboLabel_CustomTimespan_Month_To = ttk.Label(
            self.comboLabelFrameCustomTimespan_To,
            text="Month:")
        comboLabel_CustomTimespan_Month_To.grid(column=1, row=0,
                                                  sticky=tkinter.E)

        # Combobox requirements for YEAR TO.
        self.intCustomTimespan_Year_To = tkinter.IntVar()
        self.combo_CustomTimespan_Year_To = ttk.Combobox(
            self.comboLabelFrameCustomTimespan_To, width=4,
            textvariable=self.intCustomTimespan_Year_To,
            state="readonly")
        self.combo_CustomTimespan_Year_To["values"] = (intList_Years)
        self.combo_CustomTimespan_Year_To.grid(column=0, row=1,
                                               sticky=tkinter.W)

        # Combobox requirements for MONTH TO.
        self.intCustomTimespan_Month_To = tkinter.IntVar()
        self.combo_CustomTimespan_Month_To = ttk.Combobox(
            self.comboLabelFrameCustomTimespan_To, width=2,
            textvariable=self.intCustomTimespan_Month_To, state="readonly")
        self.combo_CustomTimespan_Month_To["values"] = (intCombo_Months)
        self.combo_CustomTimespan_Month_To.grid(column=1, row=1,
                                                sticky=tkinter.E)

        # For all items in the custom comboFrame, configure their grids the
        # same way.
        for child in self.comboFrame_Custom_Timespan.winfo_children():
            child.grid_configure(padx=10, pady=1)

        # Display first index for MONTH FROM (01).
        self.combo_CustomTimespan_Month_From.current(0)

        # Display first index for YEAR FROM (current year).
        self.combo_CustomTimespan_Year_From.current(0)

        # Display first index for MONTH TO (01).
        self.combo_CustomTimespan_Month_To.current(0)

        # Display first index for YEAR TO (current year).
        self.combo_CustomTimespan_Year_To.current(0)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_CustomTimespan_Year_From.bind("<<ComboboxSelected>>",
                                                 self.func_Set_Custom_Timespan)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_CustomTimespan_Month_From.bind("<<ComboboxSelected>>",
                                                  self.func_Set_Custom_Timespan)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_CustomTimespan_Year_To.bind("<<ComboboxSelected>>",
                                               self.func_Set_Custom_Timespan)

        # Combobox selection binding that will be used to populate URL Field.
        self.combo_CustomTimespan_Month_To.bind("<<ComboboxSelected>>",
                                                self.func_Set_Custom_Timespan)

    def func_ComboCustomMagnitude(self):

        # This function controls the display of the custom combobox frame
        # controlling the custom Magnitude.

        # If the custom magnitude combobox frame already exists (is visible)...
        if self.comboFrame_Custom_Magnitude is not None:

            # Remove the frame.
            self.comboFrame_Custom_Magnitude.grid_remove()

        # Widget frame for custom magnitude.
        self.comboFrame_Custom_Magnitude = tkinter.Frame(self.initialFrame)
        self.comboFrame_Custom_Magnitude.grid(column=0, row=1, padx=60, pady=5,
                                              sticky=tkinter.E)

        # Label frame for the magnitude range comboboxes.
        self.comboLabelFrame_Custom_Magnitude = ttk.LabelFrame(
            self.comboFrame_Custom_Magnitude, text="Range:",
            labelanchor=tkinter.N)
        self.comboLabelFrame_Custom_Magnitude.grid(column=0, row=0, padx=5,
                                                   pady=5, sticky=tkinter.E)

        # Label for MINIMUM magnitude.
        comboLabel_Custom_Magnitude_Min = ttk.Label(
            self.comboLabelFrame_Custom_Magnitude, text="Min:        ")
        comboLabel_Custom_Magnitude_Min.grid(column=0, row=0, sticky=tkinter.W)

        # Label for MAXIMUM magnitude.
        comboLabel_Custom_Magnitude_Max = ttk.Label(
            self.comboLabelFrame_Custom_Magnitude, text="Max:")
        comboLabel_Custom_Magnitude_Max.grid(column=3, row=0, sticky=tkinter.W)

        # Combobox requirements for MINIMUM magnitude.
        self.doubleCustom_Magnitude_Min = tkinter.DoubleVar()
        self.combo_Custom_Magnitude_Min = ttk.Combobox(
            self.comboLabelFrame_Custom_Magnitude, width=4,
            textvariable=self.doubleCustom_Magnitude_Min, state="readonly")
        self.combo_Custom_Magnitude_Min["values"] = (dbl_Combo_Magnitudes)
        self.combo_Custom_Magnitude_Min.grid(column=0, row=1, sticky=tkinter.W)

        # Combobox requirements for MAXIMUM magnitude.
        self.doubleCustom_Magnitude_Max = tkinter.DoubleVar()
        self.combo_Custom_Magnitude_Max = ttk.Combobox(
            self.comboLabelFrame_Custom_Magnitude, width=4,
            textvariable=self.doubleCustom_Magnitude_Max, state="readonly")
        self.combo_Custom_Magnitude_Max["values"] = (dbl_Combo_Magnitudes)
        self.combo_Custom_Magnitude_Max.grid(column=3, row=1, sticky=tkinter.E)

        # For all items in the custom magnitude comboFrame, configure their
        # grids the same way.
        for child in self.comboFrame_Custom_Magnitude.winfo_children():
            child.grid_configure(padx=10, pady=1)

        # Display first index for MINIMUM magnitude (-1.0).
        self.combo_Custom_Magnitude_Min.current(0)

        # Display last index for MAXIMUM magnitude (10.0).
        self.combo_Custom_Magnitude_Max.current(22)

        # Combobox selection binding that will be used to populate URL field.
        self.combo_Custom_Magnitude_Min.bind("<<ComboboxSelected>>",
                                             self.func_Set_Custom_Magnitude)

        # Combobox selection binding that will be used to populate URL field.
        self.combo_Custom_Magnitude_Max.bind("<<ComboboxSelected>>",
                                             self.func_Set_Custom_Magnitude)

    def func_NonCustomHour_UTC_with_CustomMag(self):

        # This function calculates UTC timespan if timespan = HOUR and
        # magnitude = CUSTOM.

        # Current UTC time minus last hour achieves UTC time from an hour ago.
        self.lastHour_UTC_DateTime = \
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)

        # String format of URL parameter with previous UTC hour incorporated.
        self.stringLastHour_UTC_DateTime = \
            earthquake_Custom_siteURL_StartTime + \
            str(self.lastHour_UTC_DateTime.strftime("%Y-%m-%dT%H:%M"))

        # String format of URL parameter with current UTC time incorporated.
        self.stringCurrent_UTC_DateTime = \
            earthquake_Custom_siteURL_EndTime + \
            str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M"))

        # Combined LAST HOUR and CURRENT UTC time to create URL string.
        self.previous_UTC_Hour = self.stringLastHour_UTC_DateTime + \
                                 self.stringCurrent_UTC_DateTime

    def func_NonCustomDay_UTC_with_CustomMag(self):

        # This function calculates UTC timespan if timespan = DAY and
        # magnitude = CUSTOM.

        # Current UTC time minus last 24 hours achieves UTC time for last day.
        self.last24Hour_UTC_DateTime = \
            datetime.datetime.utcnow() - datetime.timedelta(hours=24)

        # String format of URL parameter with previous UTC day incorporated.
        self.stringLast24Hour_UTC_DateTime = \
            earthquake_Custom_siteURL_StartTime + \
            str(self.last24Hour_UTC_DateTime.strftime("%Y-%m-%dT%H:%M"))

        # String format of URL parameter with current UTC time incorporated.
        self.stringCurrent_UTC_DateTime = earthquake_Custom_siteURL_EndTime + \
                    str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M"))

        # Combined LAST 24 HOURS and CURRENT UTC time to create URL string.
        self.previous_UTC_24Hour = self.stringLast24Hour_UTC_DateTime + \
                                   self.stringCurrent_UTC_DateTime

    def func_NonCustomWeek_UTC_with_CustomMag(self):

        # This function calculates UTC timespan if timespan = WEEK and
        # magnitude = CUSTOM.

        # Current UTC time minute last 7 days achieves UTC time for last week.
        self.lastWeek_UTC_DateTime = datetime.datetime.utcnow() - \
                                     datetime.timedelta(days=7)

        # String format of URL parameter with previous UTC week incorporated.
        self.stringLastWeek_UTC_DateTime = \
            earthquake_Custom_siteURL_StartTime + \
            str(self.lastWeek_UTC_DateTime.strftime("%Y-%m-%dT%H:%M"))

        # String format of URL parameter with current UTC time incorporated.
        self.stringCurrent_UTC_DateTime = earthquake_Custom_siteURL_EndTime + \
                    str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M"))

        # Combined LAST WEEK and CURRENT UTC time to create URL string.
        self.previous_UTC_Week = self.stringLastWeek_UTC_DateTime + \
                                 self.stringCurrent_UTC_DateTime

    def func_NonCustom30Days_UTC_with_CustomMag(self):

        # This function calculates UTC timespan if timespan = MONTH and
        # magnitude = CUSTOM.

        # Current UTC time minus last 30 days achieves UTC time for last month.
        self.last30Days_UTC_DateTime = datetime.datetime.utcnow() - \
                                       datetime.timedelta(days=30)

        # String format of URL parameter with previous UTC month incorporated.
        self.stringLast30Days_UTC_DateTime = \
            earthquake_Custom_siteURL_StartTime + \
            str(self.last30Days_UTC_DateTime.strftime("%Y-%m-%dT%H:%M"))

        # String format of URL parameter with current UTC time incorporated.
        self.stringCurrent_UTC_DateTime = earthquake_Custom_siteURL_EndTime + \
                    str(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M"))

        # Combined LAST MONTH and CURRENT UTC time to create URL string.
        self.previous_UTC_30Days = self.stringLast30Days_UTC_DateTime + \
                                   self.stringCurrent_UTC_DateTime

    def func_Set_Custom_Timespan(self, event):

        # This function handles events related to the custom Timespan options
        # that a user selects. Based on those selections, this function will
        # assign values and trigger other actions if necessary.

        try:

            # If the FROM YEAR in custom timespan has a value...
            if self.intCustomTimespan_Year_From.get():

                # Convert/assign the integer value to string.
                self.textCustomYearFrom = \
                    str(self.intCustomTimespan_Year_From.get())

            # If the FROM MONTH in custom timespan has a value...
            if self.intCustomTimespan_Month_From.get():

                # Convert/assign the integer value to string.
                self.textCustomMonthFrom = \
                    str(self.intCustomTimespan_Month_From.get())

            # If the TO YEAR in custom timespan has a value...
            if self.intCustomTimespan_Year_To.get():

                # Convert/assign the integer value to string.
                self.textCustomYearTo = \
                    str(self.intCustomTimespan_Year_To.get())

            # If the TO MONTH in custom timespan has a value...
            if self.intCustomTimespan_Month_To.get():

                # Convert/assign the integer value to string.
                self.textCustomMonthTo = \
                str(self.intCustomTimespan_Month_To.get())

            # If all combobox parameters for custom timespan exist...
            if self.intCustomTimespan_Year_From is not None and \
                self.intCustomTimespan_Month_From is not None and \
                self.intCustomTimespan_Year_To is not None and \
                self.intCustomTimespan_Month_To is not None:

                # Set the custom timespan URL to active.
                self.custom_timespan_url = "Active"

                # Create the timespan file/folder naming convention with values.
                self.timespan_file_folder_naming = "_" + \
                                    self.textCustomYearFrom + \
                                    self.textCustomMonthFrom.zfill(2) + \
                                    "_to_" + self.textCustomYearTo + \
                                    self.textCustomMonthTo.zfill(2)

                # Create the custom URL text for accessing the data from web.
                self.text_eq_Custom_siteURL = earthquake_Custom_siteURL_CSV + \
                                        earthquake_Custom_siteURL_StartTime + \
                                        self.textCustomYearFrom + "-" + \
                                        self.textCustomMonthFrom + "-01" + \
                                        earthquake_Custom_siteURL_EndTime + \
                                        self.textCustomYearTo + "-" + \
                                        self.textCustomMonthTo + "-" + \
                                        str(calendar.monthrange(
                                        int(self.textCustomYearTo),
                                        int(self.textCustomMonthTo))[1])

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)


    def func_Set_Custom_Magnitude(self, event):

        # This function handles events related to the custom Magnitude options
        # that a user selects. Based on those selections, this function will
        # assign values and trigger other actions if necessary.

        try:

            # If the custom MINIMUM magnitude has a value...
            if str(self.doubleCustom_Magnitude_Min.get()):

                # Convert/assign the double value to string.
                # String conversion required for 0.0 to be accessible from
                # Combo list. "0.0" as double will not populate.
                self.textCustomMagFrom = str(
                    self.doubleCustom_Magnitude_Min.get())

            # If the custom MAXIMUM magnitude has a value...
            if self.doubleCustom_Magnitude_Max.get():

                # Convert/assign the double value to string.
                self.textCustomMagTo = str(
                    self.doubleCustom_Magnitude_Max.get())

            # If both combobox parameters for custom magnitude exist...
            if self.textCustomMagFrom is not None and \
                self.textCustomMagTo is not None:

                # Assign the URL formatted parameters for accessing the web.
                self.minMag = earthquake_Custom_siteURL_Min_Magnitude + \
                              self.textCustomMagFrom
                self.maxMag = earthquake_Custom_siteURL_Max_Magnitude + \
                              self.textCustomMagTo

                # Create the custom URL text used for accessing data from web.
                self.custom_magnitude_url = self.minMag + self.maxMag

            # If negative signs exist in the FROM magnitude value, change it
            # to an underscore. This will be used for file naming and analyses.
            if "-" in self.textCustomMagFrom:

                self.textCustomMagFrom = \
                    self.textCustomMagFrom.replace("-", "neg_")

            # If negative signs exist in the TO magnitude value, change it
            # to an underscore. This will be used for file naming and analyses.
            if "-" in self.textCustomMagTo:

                self.textCustomMagTo = self.textCustomMagTo.replace("-","neg_")

            # The combined string with adjustments used for file naming and
            # analyses later on in the script.
            self.custom_Mag_Naming = \
                self.textCustomMagFrom.replace(".", "_") + "_to_" + \
                self.textCustomMagTo.replace(".", "_")

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_URLFrame(self):

        # This function controls the display of the URL frame within the GUI.

        # Widget frame for displaying the URL hyperlink text.
        self.urlFrame = tkinter.Frame(self.initialFrame)
        self.urlFrame.grid(column=0, row=2, padx=0, pady=5, sticky=tkinter.W)

        # Label for the URL text box.
        urlLabel_EarthquakeURL = ttk.Label(self.urlFrame,
                            text="URL Download File Link:")
        urlLabel_EarthquakeURL.grid(column=0, row=0, padx=20, pady=1,
                                    sticky=tkinter.W)

        # Parameters for the URL textbox.
        self.textURLTextbox = tkinter.StringVar()
        self.textURLTextbox.set(urlDialog_Message)
        urlTextbox_EarthquakeURL = ttk.Entry(self.urlFrame,
                                             textvariable=self.textURLTextbox,
                                             width=70, state="readonly")
        urlTextbox_EarthquakeURL.grid(column=0, row=1, padx=20, pady=0)

    def func_PopulateURLField_Timespan(self, event):

        # This function handles the events where a user selects a timespan
        # option from the combobox. The selection will trigger various responses
        # as detailed below.

        try:

            # If the timespan combobox displays "Select..."...
            if self.stringEarthquakeTimespan.get() == "Select...":

                # Clear any variable assignments from the following items.
                self.timespan_url = None
                self.custom_timespan_url = None
                self.nonCustomTime_with_CustomMag = None

                # Display this generic message within the URL textbox.
                self.textURLTextbox.set(urlDialog_Message)

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # If the custom timespan comboboxes exist, remove them from GUI.
                if self.comboFrame_Custom_Timespan is not None:

                    self.comboFrame_Custom_Timespan.grid_remove()

            # If the user selects "Past Hour" from combobox...
            elif self.stringEarthquakeTimespan.get() == "Past Hour":

                # Run the function that calculates UTC parameters in case a
                # custom magnitude is selected.
                self.func_NonCustomHour_UTC_with_CustomMag()

                # Assign/clear variables as needed.
                self.timespan_url = "_hour"
                self.custom_timespan_url = None
                self.nonCustomTime_with_CustomMag = self.previous_UTC_Hour

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # Run the function that does a custom URL parameter check.
                self.func_Custom_Parameter_URL_Check()

                # If the custom timespan comboboxes exist, remove them from GUI.
                if self.comboFrame_Custom_Timespan is not None:

                    self.comboFrame_Custom_Timespan.grid_remove()

            # If the user selects "Past Day" from combobox...
            elif self.stringEarthquakeTimespan.get() == "Past Day":

                # Run the function that calculates UTC parameters in case a
                # custom magnitude is selected.
                self.func_NonCustomDay_UTC_with_CustomMag()

                # Assign/clear variables as needed.
                self.timespan_url = "_day"
                self.custom_timespan_url = None
                self.nonCustomTime_with_CustomMag = self.previous_UTC_24Hour

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # Run the function that does a custom URL parameter check.
                self.func_Custom_Parameter_URL_Check()

                # If the custom timespan comboboxes exist, remove them from GUI.
                if self.comboFrame_Custom_Timespan is not None:

                    self.comboFrame_Custom_Timespan.grid_remove()

            # If the user selects "Past 7 Days" from combobox...
            elif self.stringEarthquakeTimespan.get() == "Past 7 Days":

                # Run the function that calculates UTC parameters in case a
                # custom magnitude is selected.
                self.func_NonCustomWeek_UTC_with_CustomMag()

                # Assign/clear variables as needed.
                self.timespan_url = "_week"
                self.custom_timespan_url = None
                self.nonCustomTime_with_CustomMag = self.previous_UTC_Week

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # Run the function that does a custom URL parameter check.
                self.func_Custom_Parameter_URL_Check()

                # If the custom timespan comboboxes exist, remove them from GUI.
                if self.comboFrame_Custom_Timespan is not None:

                    self.comboFrame_Custom_Timespan.grid_remove()

            # If the user selects "Past 30 Days" from combobox...
            elif self.stringEarthquakeTimespan.get() == "Past 30 Days":

                # Run the function that calculates UTC parameters in case a
                # custom magnitude is selected.
                self.func_NonCustom30Days_UTC_with_CustomMag()

                # Assign/clear variables as needed.
                self.timespan_url = "_month"
                self.custom_timespan_url = None
                self.nonCustomTime_with_CustomMag = self.previous_UTC_30Days

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # Run the function that does a custom URL parameter check.
                self.func_Custom_Parameter_URL_Check()

                # If the custom timespan comboboxes exist, remove them from GUI.
                if self.comboFrame_Custom_Timespan is not None:

                    self.comboFrame_Custom_Timespan.grid_remove()

            # If the user selects "Custom..." from the combobox...
            elif self.stringEarthquakeTimespan.get() == "Custom...":

                # Set the non-custom time with custom mag variable to None.
                self.nonCustomTime_with_CustomMag = None

                # Run function that checks if GUI window needs to be resized.
                self.func_windowResize()

                # Display this generic message within the URL textbox.
                self.textURLTextbox.set(urlDialog_Message)

                # Assign timespan URL variable to "Custom".
                self.timespan_url = "Custom"

                # Run the function that controls the custom timespan combobox.
                self.func_ComboCustomTimespan()

                # Run the function that sets the custom timespan variables.
                self.func_Set_Custom_Timespan(event)

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_PopulateURLField_Magnitude(self, event):

        # This function handles the events where a user selects a magnitude
        # option from the combobox. The selection will trigger various responses
        # as detailed below.

        # If the magnitude combobox displays "Select..."...
        if self.stringEarthquakeMagnitude.get() == "Select...":

            # Clear any variable assignments from the following items.
            self.magnitude_url = None
            self.mag_naming = None

            # Display this generic message within the URL textbox.
            self.textURLTextbox.set(urlDialog_Message)

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # If the custom magnitude comboboxes exist, remove them from GUI.
            if self.comboFrame_Custom_Magnitude is not None:

                self.comboFrame_Custom_Magnitude.grid_remove()

        # If the user selects "All" from the combobox...
        elif self.stringEarthquakeMagnitude.get() == "All":

            # Assign/clear variables as needed.
            self.magnitude_url = "all"
            self.mag_naming = "all"
            self.custom_magnitude_url = None

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

            # If the custom magnitude comboboxes exist, remove them from GUI.
            if self.comboFrame_Custom_Magnitude is not None:

                self.comboFrame_Custom_Magnitude.grid_remove()

        # If the user selects "1.0+" from the combobox...
        elif self.stringEarthquakeMagnitude.get() == "1.0+":

            # Assign/clear variables as needed.
            self.magnitude_url = "1.0"
            self.mag_naming = "1_0"
            self.custom_magnitude_url = None

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

            # If the custom magnitude comboboxes exist, remove them from GUI.
            if self.comboFrame_Custom_Magnitude is not None:

                self.comboFrame_Custom_Magnitude.grid_remove()

        # If the user selects "2.5+" from the combobox...
        elif self.stringEarthquakeMagnitude.get() == "2.5+":

            # Assign/clear variables as needed.
            self.magnitude_url = "2.5"
            self.mag_naming = "2_5"
            self.custom_magnitude_url = None

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

            # If the custom magnitude comboboxes exist, remove them from GUI.
            if self.comboFrame_Custom_Magnitude is not None:

                self.comboFrame_Custom_Magnitude.grid_remove()

        # If the user selects "4.5+" from the combobox...
        elif self.stringEarthquakeMagnitude.get() == "4.5+":

            # Assign/clear variables as needed.
            self.magnitude_url = "4.5"
            self.mag_naming = "4_5"
            self.custom_magnitude_url = None

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Run the function that does a custom URL parameter check.
            self.func_Custom_Parameter_URL_Check()

            # If the custom magnitude comboboxes exist, remove them from GUI.
            if self.comboFrame_Custom_Magnitude is not None:

                self.comboFrame_Custom_Magnitude.grid_remove()

        # If the user selects "Custom..." from the combobox...
        elif self.stringEarthquakeMagnitude.get() == "Custom...":

            # Assign/clear variables as needed.
            self.magnitude_url = "Custom"
            self.mag_naming = None

            # Run the function that checks if GUI window needs to be resized.
            self.func_windowResize()

            # Display this generic message within the URL textbox.
            self.textURLTextbox.set(urlDialog_Message)

            # Run the function that controls the display of the custom
            # magnitude comboboxes.
            self.func_ComboCustomMagnitude()

            # Run the function that sets the custom magnitude variables.
            self.func_Set_Custom_Magnitude(event)

    def func_Custom_Parameter_URL_Check(self): #event

        # This function checks all website URL paramaters to ensure they are
        # correct and ready to display within the URL textbox.

        # If the user has selected both timespan and magnitude combobox values..
        if self.timespan_url is not None and self.magnitude_url is not None:

            # If neither the custom timespan or custom magnitude are
            # selected...
            if self.custom_timespan_url is None and \
                    self.custom_magnitude_url is None:

                # Set the URL text of non custom timespan/magnitude values.
                self.text_EQ_URL = earthquake_siteURL + self.magnitude_url + \
                                   self.timespan_url + fileExtCSV

                # Display the URL text within the URL textbox.
                self.textURLTextbox.set(self.text_EQ_URL)

            # Else if the custom timespan is selected and custom magnitude not
            # selected...
            elif self.custom_timespan_url is not None and \
                    self.custom_magnitude_url is None:

                # If the user selected "All" for magnitude...
                if self.stringEarthquakeMagnitude.get() == "All":

                    # Set the URL text for custom timespan and non-custom
                    # magnitude. The "All" selection requires unique
                    # URL parameters from the other options.
                    self.text_EQ_URL = self.text_eq_Custom_siteURL

                    # Display the URL text within the URL textbox.
                    self.textURLTextbox.set(self.text_EQ_URL)

                # Else if the user selection doesn't equal "Select..." or
                # "Custom..." from the magnitude combobox...
                elif self.stringEarthquakeMagnitude.get() != "Select..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

                    # Set the URL text for custom timespan and non-custom
                    # magnitude (different format from "All" selection above).
                    self.text_EQ_URL = self.text_eq_Custom_siteURL + \
                                    earthquake_Custom_siteURL_Min_Magnitude + \
                                    self.magnitude_url

                    # Display the URL text within the URL textbox.
                    self.textURLTextbox.set(self.text_EQ_URL)

            # Else if the custom timespan is not selected and custom magnitude
            # is selected...
            elif self.custom_timespan_url is None and \
                    self.custom_magnitude_url is not None:

                # Set the URL text for a non-custom timespan and custom
                # magnitude.
                self.text_EQ_URL = earthquake_Custom_siteURL_CSV + \
                                   self.nonCustomTime_with_CustomMag + \
                                   self.minMag + self.maxMag

                # Display the URL text within the URL textbox.
                self.textURLTextbox.set(self.text_EQ_URL)

            # Else if both the custom timespan and magnitude are selected...
            elif self.custom_timespan_url is not None and \
                    self.custom_magnitude_url is not None:

                # Set the URL text for a custom timespan and custom magnitude.
                self.text_EQ_URL = self.text_eq_Custom_siteURL + \
                                   self.custom_magnitude_url

                # Display the URL text within the URL textbox.
                self.textURLTextbox.set(self.text_EQ_URL)

            else:

                # Else, display the generic text message within the URL textbox.
                self.textURLTextbox.set(urlDialog_Message)

    def func_WorkspaceFolderFrame(self):

        # The following function controls the workspace folder frame within the
        # GUI.

        # Widget frame for the workspace folder assignment.
        self.workspaceFolderFrame = tkinter.Frame(self.initialFrame)
        self.workspaceFolderFrame.grid(column=0, row=3, padx=0, pady=5,
                                       sticky=tkinter.W)

        # Label for the assigned workspace.
        workspaceFolderLabel_FolderDialog = ttk.Label(self.workspaceFolderFrame,
                                             text="Set Workspace:")
        workspaceFolderLabel_FolderDialog.grid(column=0, row=0, padx=20, pady=1)

        # Browse button for the user to select an output folder location.
        self.workspaceFolderButton_FolderDialog = \
            ttk.Button(self.workspaceFolderFrame, text="Browse...",
                       command=self.func_FolderDialog)
        self.workspaceFolderButton_FolderDialog.grid(column=0, row=1, padx=20,
                                                     pady=0, sticky=tkinter.EW)

        # Variables for the folder location to display within a GUI textbox.
        self.textWorkspaceDialogPath = tkinter.StringVar()
        self.textWorkspaceDialogPath.set(folderDialog_Message)
        self.workspaceFolderTextbox_EarthquakeFolderDialog = \
            ttk.Entry(self.workspaceFolderFrame,
                      textvariable=self.textWorkspaceDialogPath, width=52,
                      state="readonly")
        self.workspaceFolderTextbox_EarthquakeFolderDialog.grid(column=1,
                                        row=1, padx=0, pady=0, sticky=tkinter.W)

    def func_FolderDialog(self):

        # This function controls the assignment of the output file directory
        # via the "Browse..." button.

        # First, the function checks to see if the window needs to be re-sized.
        # The re-size will occur if the Scrollbox and Progressbar are visible.
        self.func_windowResize()

        # Once the "Browse..." button is clicked, the user will be prompted to
        # select an output workspace.
        self.folderDialogPath = \
            filedialog.askdirectory(parent=self.workspaceFolderFrame)

        # If the user clicks Cancel, folderDialogPath becomes an empty string
        # and does not assign a valid workspace.
        if self.folderDialogPath == "":

            # This will cause the workspace text to automatically reset to the
            # original generic message.
            self.textWorkspaceDialogPath.set(folderDialog_Message)

        else:
            # Otherwise, the workspace will be set and display for the user.
            self.textWorkspaceDialogPath.set(self.folderDialogPath)

    def func_ButtonFrame(self):

        # This function controls the laytout of the Exit/Cancel, Back, and OK
        # buttons, as well as the "More Options" checkbox.

        # Button frame for housing all of the buttons.
        self.buttonFrame = tkinter.Frame(self.initialFrame)
        self.buttonFrame.grid(column=0, row=4, padx=0, pady=20,
                              sticky=tkinter.NSEW)

        # Exit button.
        self.buttonExitCancel = ttk.Button(self.buttonFrame, text="Exit",
                                command=self.func_Exit_Cancel_Click)
        # widgetButtonCancel.config(height = 20, width = 20)
        self.buttonExitCancel.grid(column=0, row=0, padx=40, pady=0,
                                   sticky=tkinter.W)

        # Back button.
        self.buttonBack = ttk.Button(self.buttonFrame, text="Back",
                                command=self.func_BackClick)
        self.buttonBack.grid(column=3, row=0, padx=5, pady=0, sticky=tkinter.E)

        # OK button.
        self.buttonOK = ttk.Button(self.buttonFrame, text="OK",
                                   command=self.func_OKClick_Thread)
        self.buttonOK.grid(column=4, row=0, padx=5, pady=0, sticky=tkinter.E)

        # Variables for the "More Options" checkbox.
        self.statusVar_Checkbutton_Options = tkinter.IntVar()
        self.checkboxOptions = tkinter.Checkbutton(self.buttonFrame,
                text="More Options", variable = self.statusVar_Checkbutton_Options,
                command=self.func_CheckboxOptions)
        self.checkboxOptions.grid(column=5, row=0, padx=15, pady=0,
                                  sticky=tkinter.E)
        self.checkboxOptions.deselect()

    def func_BackClick(self):

        # This function controls what happens when the Back button is clicked.

        # The previous screen (to select hazard type appears).
        from GUI_ApplicationDriver import AppDriver
        appDrive = AppDriver(self.winfo_toplevel())
        appDrive.place(in_=self.winfo_toplevel(), x=0, y=0, relwidth=1,
                       relheight=1)
        appDrive.lift()

    def func_Exit_Cancel_Click(self):

        # This function controls what happens when the Exit/Cancel button is
        # clicked.

        # If the user clicks the Exit button...
        if self.buttonExitCancel["text"] == "Exit":

            # Exit/Terminate the program.
            self.quit()
            self.destroy()
            sys.exit(0)

        # If the user clicks the Cancel button after clicking OK...
        if self.buttonExitCancel["text"] == "Cancel":

            # Yes/No Messagebox warning message, verifying the user's choice.
            userSelection = messagebox.askyesno("Are you sure?",
                            "Are you sure you want to cancel?\n" +
                            "This will terminate any unfinished processes and "
                            "exit the program.", icon=messagebox.WARNING)

            # If user selects Yes...
            if userSelection == True:

                # Immediately terminate all processes and exit the program.
                self.quit()
                self.destroy()
                sys.exit(0)

            else:

                # If the user selects No, then do nothing and return to the
                # active program.
                return

    def func_OKClick_Thread(self):

        # This function controls the OKClick function, by running it within a
        # threaded environment. This prevents the GUI from freezing, and allows
        # for the processing messages and progress bar to provide live updates.
        # The daemon setting allows for the application to properly terminate
        # when the user clicks the "Cancel" button.

        self.thread_func_OKClick = Thread(target=self.func_OKClick)
        self.thread_func_OKClick.daemon = True
        self.thread_func_OKClick.start()

        # Disable all GUI selectable items except the "Cancel" button after
        # starting.
        self.func_Disable_Buttons()

    def func_OKClick(self):

        # This function controls what occurs once the user clicks the OK button.

        try:

            # GUI height expansion if no Custom comboboxes have been selected.
            self.okClick_NonCustom_ExpansionHeight = \
                guiWindow_EarthquakeOptions_Height + 200

            # If a custom timespan or custom magnitude has been selected...
            if self.customSelection_Height is not None:

                # Expand the height of the GUI to accomodate the Custom
                # timespan/magnitude height, plus the processing messages and
                # progress bar.
                self.okClick_Custom_ExpansionHeight = \
                    self.customSelection_Height + 200

            # If the scroll box (for processing messages) already exists,
            # remove it.
            if self.scrollBoxFrame is not None:

                self.scrollBoxFrame.grid_remove()

            # If the progress bar already exists, remove it.
            if self.progressBarFrame is not None:

                self.progressBarFrame.grid_remove()

            # If the user has selected a valid timespan, magnitude, and assigned
            # an output workspace folder...
            if self.stringEarthquakeTimespan.get() != "Select..." and \
                self.stringEarthquakeMagnitude.get() != "Select..." and \
                self.workspaceFolderTextbox_EarthquakeFolderDialog.get() != \
                    folderDialog_Message:

                # Start a timer for the script.
                self.start_time = time.time()

                # If the "Options" checkbox is selected...
                if self.statusVar_Checkbutton_Options.get() == 1:

                    # If the user hasn't selected a clipping option...
                    if self.radioButton_Selection is None:

                        # Display error message.
                        messagebox.showerror(errorMessage_Header,
                                    message="Error in Clipping Options.\n" +
                                    "A clipping option must be selected.")

                        # Re-enable all selectable items in the GUI.
                        self.func_Enable_Buttons()

                        # Exit the function.
                        return

                    # If the timespan or magnitude combobox is "Custom..."...
                    if self.stringEarthquakeTimespan.get() == "Custom..." or \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # If all custom timespan comboboxes have values...
                        if self.intCustomTimespan_Year_From is not None and \
                                self.intCustomTimespan_Year_To is not None and \
                            self.intCustomTimespan_Month_From is not None and \
                            self.intCustomTimespan_Month_To is not None:

                            # If the YEAR FROM exceeds the YEAR TO value...
                            if self.intCustomTimespan_Year_From.get() > \
                                    self.intCustomTimespan_Year_To.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                        message="Invalid timespan entry.\n" +
                                                "From date exceeds To date.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                            # Else if the FROM MONTH exceeds the TO MONTH within
                            # the same YEAR...
                            elif self.intCustomTimespan_Year_From.get() == \
                                    self.intCustomTimespan_Year_To.get() and \
                                    self.intCustomTimespan_Month_From.get() > \
                                    self.intCustomTimespan_Month_To.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                        message="Invalid timespan entry.\n" +
                                                "From date exceeds To date.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                        # If the custom minimum magnitude and the custom
                        # maximum magnitude comboboxes have values...
                        if self.doubleCustom_Magnitude_Min is not None and\
                                self.doubleCustom_Magnitude_Max is not None:

                            # If the minimum magnitude exceeds the maximum
                            # magnitude...
                            if self.doubleCustom_Magnitude_Min.get() > \
                                    self.doubleCustom_Magnitude_Max.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                message="Invalid magnitude entry.\n" +
                                "Minimum magnitude exceeds Maximum magnitude.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                        # If no errors have occurred, adjust the GUI dimensions
                        # as assigned.
                        self.winfo_toplevel().geometry(
                            "%dx%d" % (self.checkboxExpansionWidth,
                                       self.okClick_Custom_ExpansionHeight))

                    else:

                        # If no "Custom..." comboboxes have been selected, and
                        # no errors thrown, adjust the GUI dimensions as
                        # assigned.
                        self.winfo_toplevel().geometry("%dx%d" % (
                            self.checkboxExpansionWidth,
                            self.okClick_NonCustom_ExpansionHeight))

                # Else if the "More Options" checkbox is not selected...
                elif self.statusVar_Checkbutton_Options.get() == 0:

                    # If the timespan or magnitude "Custom..." comboboxes are
                    # selected...
                    if self.stringEarthquakeTimespan.get() == "Custom..." or \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # If all custom timespan comboboxes have values...
                        if self.intCustomTimespan_Year_From is not None and \
                            self.intCustomTimespan_Year_To is not None and \
                            self.intCustomTimespan_Month_From is not None and \
                            self.intCustomTimespan_Month_To is not None:

                            # If the YEAR FROM exceeds the YEAR TO value...
                            if self.intCustomTimespan_Year_From.get() > \
                                    self.intCustomTimespan_Year_To.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                        message="Invalid timespan entry.\n" +
                                                "From date exceeds To date.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                            # Else if the FROM MONTH exceeds the TO MONTH within
                            # the same YEAR...
                            elif self.intCustomTimespan_Year_From.get() == \
                                    self.intCustomTimespan_Year_To.get() and \
                                    self.intCustomTimespan_Month_From.get() > \
                                    self.intCustomTimespan_Month_To.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                        message="Invalid timespan entry.\n" +
                                                "From date exceeds To date.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                        # If both the minimum and maximum magnitude comboboxes
                        # have values...
                        if self.doubleCustom_Magnitude_Min is not None and \
                            self.doubleCustom_Magnitude_Max is not None:

                            # If the MINIMUM magnitude exceeds the MAXIMUM
                            # magnitude...
                            if self.doubleCustom_Magnitude_Min.get() > \
                                    self.doubleCustom_Magnitude_Max.get():

                                # Display error message.
                                messagebox.showerror(errorMessage_Header,
                                message="Invalid magnitude entry.\n" +
                                "Minimum magnitude exceeds Maximum magnitude.")

                                # Re-enable all selectable items in the GUI.
                                self.func_Enable_Buttons()

                                # Exit the function.
                                return

                        # If no errors have occurred, adjust the GUI dimensions
                        # as assigned.
                        self.winfo_toplevel().geometry("%dx%d" % (
                                    guiWindow_EarthquakeOptions_Width,
                                    self.okClick_Custom_ExpansionHeight))

                    else:

                        # If no "Custom..." comboboxes have been selected, and
                        # no errors thrown, adjust the GUI dimensions as
                        # assigned.
                        self.winfo_toplevel().geometry("%dx%d" % (
                            guiWindow_EarthquakeOptions_Width,
                            self.okClick_NonCustom_ExpansionHeight))

                # If no errors encountered, continue executing the following
                # functions...

                # Run function to activate the scrolled text processing frame.
                self.func_ScrolledTextProcessingFrame()

                # Run function to activate the progress bar frame.
                self.func_ProgressBarFrame()

                # Disable all user-selectable items within the GUI.
                self.func_Disable_Buttons()

                # Run function to start the status bar.
                self.func_StartStatusBar()

                # Run function to create a folder in the user-specified output
                # workspace folder.
                # PLEASE NOTE:
                # Numerous subtasks are executed within this function.
                self.func_CreateFolder()

                # Once all tasks are completed, this function will calculate the
                # time it took for the script to run from start to finish.
                self.func_Calculate_Script_Time()

                # This function will attempt to take all of the text from the
                # scrolled text box and save it to a text file within the
                # user-defined output workspace folder.
                self.func_Scroll_saveOutputText()

                # Re-enable all user-selectable items within the GUI.
                self.func_Enable_Buttons()

                # Run function to stop the status bar.
                self.func_StopStatusBar()

                # Ensure progressbar displays 100%, as the script is now done.
                self.func_ProgressBar_setProgress(100)

            else:

                # If the timespan combobox shows "Select..."...
                if self.stringEarthquakeTimespan.get() == "Select...":

                    # Display error message.
                    messagebox.showerror(errorMessage_Header,
                                        message="Invalid timespan entry.\n" +
                                        "Please select an option from the "
                                        "drop-down list and try again.")

                    # Re-enable all selectable intems in the GUI.
                    self.func_Enable_Buttons()

                # Else if the magnitude combobox shows "Select..."...
                elif self.stringEarthquakeMagnitude.get() == "Select...":

                    # Display error message.
                    messagebox.showerror(errorMessage_Header,
                                         message="Invalid magnitude entry.\n" +
                                        "Please select an option from "
                                        "the drop-down list and try again.")

                    # Re-enable all selectable intems in the GUI.
                    self.func_Enable_Buttons()

                # Else if the output workspace text is the default message...
                elif \
                self.workspaceFolderTextbox_EarthquakeFolderDialog.get() == \
                        folderDialog_Message:

                    # Display error message.
                    messagebox.showerror(errorMessage_Header,
                                message="Output folder path not specified.\n" +
                                "Please try again.")

                    # Re-enable all selectable items in the GUI.
                    self.func_Enable_Buttons()

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Re-enable all user-selectable options.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Output scroll text to file.
            self.func_Scroll_saveOutputText()

            # Exit the application's task.
            exit()

    def func_ScrolledTextProcessingFrame(self):

        # This function controls the scrolled text processing frame properties
        # within the GUI.

        # Frame for the scrolled text.
        self.scrollBoxFrame = tkinter.Frame(self.processingFrame)

        # Set the scroll height at 8 lines.
        self.scrollHeight = 8

        # If the "More Options" checkbox is selected...
        if self.statusVar_Checkbutton_Options.get() == 1:

            # Set the scrolled text frame to 90 characters wide.
            self.scrollWidth = 90

            # Set the frame parameters to accommodate the width.
            self.scrollBoxFrame.grid(column=0, row=5, padx=10, pady=5,
                                     columnspan=2)

        # If the "More Options" checkbox is not selected...
        if self.statusVar_Checkbutton_Options.get() == 0:

            # Set the scrolled text frame to 52 characters wide.
            self.scrollWidth = 52

            # Set the frame parameters to accommodate the width.
            self.scrollBoxFrame.grid(column=0, row=5, padx=10, pady=5,
                                     columnspan=1)

        # Scrolledtext box for processing messages to display.
        self.scrollBox = scrolledtext.ScrolledText(self.scrollBoxFrame,
                        width=self.scrollWidth, height=self.scrollHeight,
                        wrap=tkinter.WORD, state=tkinter.DISABLED)
        self.scrollBox.grid(column=0, row=0)

        # Sets the text variable to the function for updating the scrolledtext
        # output.
        self.func_Scroll_setOutputText("Beginning assigned tasks...", None)

    def func_ProgressBarFrame(self):

        # This function controls the layout of the progress bar within the GUI.

        # Frame for displaying the progress bar.
        self.progressBarFrame = tkinter.Frame(self.processingFrame)

        # If the "More Options" checkbox is selected...
        if self.statusVar_Checkbutton_Options.get() == 1:

            # Set the pixel width of the progress bar.
            self.progressBar_Length = 740

            # Set the frame parameters to accommodate the width.
            self.progressBarFrame.grid(column=0, row=6, padx=10, pady=5,
                                       columnspan=2)

        # If the "More Options" checkbox is not selected...
        if self.statusVar_Checkbutton_Options.get() == 0:

            # Set the pixel width of the progress bar.
            self.progressBar_Length = 450

            # Set the frame parameters to accommodate the width.
            self.progressBarFrame.grid(column=0, row=6, padx=10, pady=5,
                                       columnspan=1)

        # Status bar showing that the application is running.
        self.statusBar = ttk.Progressbar(self.progressBarFrame,
                                               orient='horizontal',
                                               length=self.progressBar_Length,
                                               mode='determinate')
        self.statusBar.grid(column=0, row=0)

        # Progress bar.
        self.progressBar = ttk.Progressbar(self.progressBarFrame,
                                           orient='horizontal',
                                           length=self.progressBar_Length,
                                           mode='determinate')
        self.progressBar.grid(column=0, row=1)

        # Progress bar starting value.
        self.progressBar["value"] = 0

        # Progress bar maximum value.
        self.progressBar["maximum"] = 100

    def func_RunStatusBar(self):

        # This function controls the appearance of the status bar.

        for i in range(100):
            sleep(0.03)
            self.statusBar["value"] = i  # increment progressbar
            self.statusBar.update()  # have to call update() in loop
        self.statusBar["value"] = 0  # reset/clear progressbar

    def func_StartStatusBar(self):

        # This function starts the status bar.

        self.statusBar.start()

    def func_StopStatusBar(self):

        # This function stops the status bar.

        self.statusBar.stop()

    def func_CheckboxOptions(self):

        # This function controls what happens to the GUI when the "More Options"
        # checkbox is selected/deselected.

        # If the "More Options" checkbox is "checked"...
        if self.statusVar_Checkbutton_Options.get() == 1:

            # Run the window resize function to re-size GUI.
            self.func_windowResize()

            # Run the function to display the Analysis/Clipping Options.
            self.func_AnalysisOptionsFrame()

        else:

            # If the "More Options" checkbox is unchecked, clear the radio button
            # selection, re-size the window, and remove the Analysis/Clipping
            # Options.
            self.radioButton_Selection = None
            self.func_windowResize()
            self.analysisOptionsFrame.grid_remove()

    def func_AnalysisOptionsFrame(self):

        # This function controls the layout of the Analysis/Clipping Options
        # within the GUI.

        # Widget frame for the Analysis Options.
        self.analysisOptionsFrame = tkinter.Frame(self.optionsFrame)
        self.analysisOptionsFrame.grid(column=0, row=0, padx=0, pady=5,
                                       sticky=tkinter.NW)

        # Label frame for the Analysis Options.
        self.analysisOptionsLabelFrame = \
            ttk.LabelFrame(self.analysisOptionsFrame,
                           text="Analysis Options (with Esri defaults)",
                           labelanchor=tkinter.NW)
        self.analysisOptionsLabelFrame.grid(column=0, row=0, padx=0, pady = 2,
                                            sticky=tkinter.W, columnspan=3)

        # Label frame for the Clipping Options.
        self.clippingOptionsLabelFrame = \
            ttk.LabelFrame(self.analysisOptionsFrame, text="Clipping Options",
                           labelanchor=tkinter.NW)
        self.clippingOptionsLabelFrame.grid(column=0, row=1, padx=0, pady=0,
                                            sticky=tkinter.W, columnspan=2)

        # Frame for the US clipping option.
        self.clippingOptions_radiobuttonFrame_US = \
            ttk.Frame(self.clippingOptionsLabelFrame)
        self.clippingOptions_radiobuttonFrame_US.grid(column=0, row=0, padx=0,
                                                      pady=0, sticky=tkinter.W)

        # Radio button variables for the USA clipping option.
        self.statusClippingOption = tkinter.IntVar()
        self.radiobuttonClippingOption_US = \
            tkinter.Radiobutton(self.clippingOptions_radiobuttonFrame_US,
                    text="USA", value = 1, variable=self.statusClippingOption,
                    command = self.func_RadioButton_Clipping_Command)
        self.radiobuttonClippingOption_US.grid(column=0, row=0, padx=0, pady=0,
                                               sticky=tkinter.W)
        self.radiobuttonClippingOption_US.deselect()

        # Frame for the State clipping option.
        self.clippingOptions_radiobuttonFrame_State = \
            ttk.Frame(self.clippingOptionsLabelFrame)
        self.clippingOptions_radiobuttonFrame_State.grid(column=0, row=1,
                                                padx=0, pady=0,sticky=tkinter.W)

        # Radio button variables for the State clipping option.
        self.radiobuttonClippingOption_State = \
            tkinter.Radiobutton(self.clippingOptions_radiobuttonFrame_State,
                    text="State", value = 2, variable=self.statusClippingOption,
                    command = self.func_RadioButton_Clipping_Command)
        self.radiobuttonClippingOption_State.grid(column=0, row=0, padx=0,
                                                  pady=0, sticky=tkinter.W)
        self.radiobuttonClippingOption_State.deselect()

        # Frame for the County clipping option.
        self.clippingOptions_radiobuttonFrame_County = ttk.Frame(
            self.clippingOptionsLabelFrame)
        self.clippingOptions_radiobuttonFrame_County.grid(column=0, row=2,
                                                          padx=0,
                                                          pady=0,
                                                          sticky=tkinter.W)

        # Radio button variables for the County clipping option.
        self.radiobuttonClippingOption_County = \
            tkinter.Radiobutton(self.clippingOptions_radiobuttonFrame_County,
                text="County", value = 3, variable=self.statusClippingOption,
                                command=self.func_RadioButton_Clipping_Command)
        self.radiobuttonClippingOption_County.grid(column=0, row=0, padx=0,
                                                pady=0, sticky=tkinter.W)
        self.radiobuttonClippingOption_County.deselect()

        # Checkbox variables for the IDW option.
        self.statusAnalysis_IDW = tkinter.IntVar()
        self.checkbox_IDW = tkinter.Checkbutton(self.analysisOptionsLabelFrame,
                                text="IDW", variable=self.statusAnalysis_IDW)
        #, command=self.test_IDW_parameters)
        self.checkbox_IDW.grid(column=0, row=0, padx=0, pady=0,sticky=tkinter.W)
        self.checkbox_IDW.deselect()

        # Checkbox variables for the Kernel Density option.
        self.statusAnalysis_KernelDensity = tkinter.IntVar()
        self.checkbox_KernelDensity = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame,
            text="Kernel Dens.", variable=self.statusAnalysis_KernelDensity)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_KernelDensity.grid(column=1, row=0, padx=0, pady=0,
                                         sticky=tkinter.W)
        self.checkbox_KernelDensity.deselect()

        # Checkbox variables for the Kriging option.
        self.statusAnalysis_Kriging = tkinter.IntVar()
        self.checkbox_Kriging = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame, text="Kriging",
                                variable=self.statusAnalysis_Kriging)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_Kriging.grid(column=2, row=0, padx=0, pady=0,
                                   sticky=tkinter.W)
        self.checkbox_Kriging.deselect()

        # Checkbox variables for the Natural Neighbor option.
        self.statusAnalysis_NaturalNeighbor = tkinter.IntVar()
        self.checkbox_NaturalNeighbor = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame,
            text="Nat. Neigh.", variable=self.statusAnalysis_NaturalNeighbor)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_NaturalNeighbor.grid(column=0, row=1, padx=0, pady=0,
                                           sticky=tkinter.W)
        self.checkbox_NaturalNeighbor.deselect()

        # Checkbox variables for the Optimized Hot Spot option.
        self.statusAnalysis_OptHotSpot = tkinter.IntVar()
        self.checkbox_OptHotSpot = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame,
                text="Opt. Hot Spot", variable=self.statusAnalysis_OptHotSpot)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_OptHotSpot.grid(column=1, row=1, padx=0, pady=0,
                                      sticky=tkinter.W)
        self.checkbox_OptHotSpot.deselect()

        # Checkbox variables for the Point Density option.
        self.statusAnalysis_PointDensity = tkinter.IntVar()
        self.checkbox_PointDensity = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame,
                text="Point Dens.", variable=self.statusAnalysis_PointDensity)
        #, command=self.func_Window_Parameters_PointDensity)
        self.checkbox_PointDensity.grid(column=2, row=1, padx=0, pady=0,
                                        sticky=tkinter.W)
        self.checkbox_PointDensity.deselect()

        # Checkbox variables for the Spline option.
        self.statusAnalysis_Spline = tkinter.IntVar()
        self.checkbox_Spline = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame, text="Spline",
            variable=self.statusAnalysis_Spline)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_Spline.grid(column=0, row=2, padx=0, pady=0,
                                  sticky=tkinter.W)
        self.checkbox_Spline.deselect()

        # Checkbox variables for the Thiessen option.
        self.statusAnalysis_Thiessen = tkinter.IntVar()
        self.checkbox_Thiessen = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame, text="Thiessen",
            variable=self.statusAnalysis_Thiessen)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_Thiessen.grid(column=1, row=2, padx=0, pady=0,
                                    sticky=tkinter.W)
        self.checkbox_Thiessen.deselect()

        # Checkbox variables for the Trend option.
        self.statusAnalysis_Trend = tkinter.IntVar()
        self.checkbox_Trend = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame, text="Trend",
            variable=self.statusAnalysis_Trend)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_Trend.grid(column=2, row=2, padx=0, pady=0,
                                   sticky=tkinter.W)
        self.checkbox_Trend.deselect()

        # Checkbox variables for the Output Count Details to CSV File option.
        self.statusAnalysis_OutputToCSVFile = tkinter.IntVar()
        self.checkbox_OutputToCSVFile = \
            tkinter.Checkbutton(self.analysisOptionsLabelFrame,
            text="Output Count Details to CSV File",
            variable=self.statusAnalysis_OutputToCSVFile)
        # command=self.func_Controls_For_Analysis_Options)
        self.checkbox_OutputToCSVFile.grid(column=0, row=3, padx=0, pady=0,
                                            columnspan=3, sticky=tkinter.W)
        self.checkbox_OutputToCSVFile.deselect()

    def func_RadioButton_State_Frame_Options(self):

        # This function controls what occurs when the user selects STATE as the
        # clipping option. If the user selects STATE, a combobox appears with
        # all states (and DC) populated.

        # Frame for State combobox.
        self.comboFrame_State = ttk.Frame(self.clippingOptionsLabelFrame)
        self.comboFrame_State.grid(column=1, row=1, padx=1, pady=1,
                             sticky=tkinter.W)

        # Combobox variables to display combobox with appropriate values.
        self.stringState_Name = tkinter.StringVar()
        self.combo_State_Name = ttk.Combobox(self.comboFrame_State, width=4,
            textvariable=self.stringState_Name, state="readonly")  # font =
        self.combo_State_Name["values"] = (dictKeys_StateNames)
        self.combo_State_Name.grid(column=0, row=0, padx = 5,
                                            sticky=tkinter.W)

        # Display the state at the first index based on state abbreviation (AK).
        self.combo_State_Name.current(0)

        # Bind the user's selection to a function that checks for GUI re-sizing.
        self.combo_State_Name.bind("<<ComboboxSelected>>",
                                   self.func_Check_If_Combobox_Text_Changes)

    def func_RadioButton_County_Frame_Options(self):

        # This function controls what occurs when the user selects COUNTY as the
        # clipping option. If the user selects COUNTY, a combobox appars with
        # all county names affiliated with whatever state is displayed within
        # the STATE combobox.

        # Import all county names associated with each state from a separate
        # dictionary module.
        from GUI_CountiesPerState import dict_state_counties

        # Frame for the county combobox.
        self.comboFrame_Counties = ttk.Frame(self.clippingOptionsLabelFrame)
        self.comboFrame_Counties.grid(column=1, row=2, padx=1, pady=1,
                             sticky=tkinter.W)

        # Combobox variables for displaying the counties.
        self.stringCounty_Name = tkinter.StringVar()
        self.combo_County_Name = ttk.Combobox(self.comboFrame_Counties,width=28,
                                    textvariable=self.stringCounty_Name,
                                    state="readonly")  # font =
        self.combo_County_Name["values"] = \
            (dict_state_counties[self.stringState_Name.get()])
        self.combo_County_Name.grid(column=0, row=0, padx = 5, sticky=tkinter.W)

        # Display the first county name for the selected state (alphabetical).
        self.combo_County_Name.current(0)

        # Bind the user's selection to a function that checks for GUI re-sizing.
        self.combo_County_Name.bind("<<ComboboxSelected>>",
                                    self.func_Check_If_Combobox_Text_Changes)

        # Bind the user's input to a function that determines which counties to
        # display, depending on which state the user selects.
        self.combo_State_Name.bind("<<ComboboxSelected>>",
                                self.func_Autopopulate_County_Combobox_Choices)

    def func_Check_If_Combobox_Text_Changes(self, event):

        # This function exists to check if the State or County Combobox text
        # field changes after the OK function has iterated. If something does
        # change after an iteration, the Window Resize function will check and
        # see if the scroll box and progress bar should be removed.

        self.func_windowResize()

    def func_Autopopulate_County_Combobox_Choices(self, event):

        # This function exists to auto-populate the County Combobox depending on
        # state choice. If the user changes the state, the counties will update.

        try:

            # Import all county names associated with each state from a separate
            # dictionary module.
            from GUI_CountiesPerState import dict_state_counties

            # Check to see if the GUI window should be re-sized.
            self.func_windowResize()

            # If the user selects the COUNTY radiobutton...
            if self.radioButton_Selection == 3:

                # If the STATE combobox has a value...
                if self.stringState_Name.get():

                    # Populate the counties from the dictionary affiliated with
                    # that state selection.
                    self.combo_County_Name["values"] = (
                    dict_state_counties[self.stringState_Name.get()])

                    # Display county at first index (alphabetical).
                    self.combo_County_Name.current(0)

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_CreateFolder(self):

        # This function controls the creation of the folder where all future
        # processing will be accomplished. This will be saved in the
        # user-specified output folder.
        # PLEASE NOTE:
        # Many sub-functions are attached to this function.

        try:

            # If the "More Options" checkbox is selected...
            if self.statusVar_Checkbutton_Options.get() == 1:

                # If the USA clipping option is selected...
                if self.radioButton_Selection == 1:

                    # Create variable for adding USA and DC Only to folder
                    # naming convention.
                    self.folderNamingAddition = \
                        "_" + featureClass_50States_and_DC_only

                # If the STATE clipping option is selected...
                if self.radioButton_Selection == 2:

                    # Create variable for adding State to folder
                    # naming convention.
                    self.featureClass_State_Selection_Only = \
                        "state_only_" + self.stringState_Name.get()
                    self.folderNamingAddition = \
                        "_" + self.featureClass_State_Selection_Only

                # If the COUNTY clipping option is selected...
                if self.radioButton_Selection == 3:

                    # Create modified variable for County name, removing all
                    # instances of special characters or spacing.
                    self.modified_stringCountyName = \
                        self.stringCounty_Name.get().\
                        replace("'", "").replace("-", "").\
                        replace(".", "").replace(" ", "")

                    # Full string used for feature class naming purposes.
                    self.featureClass_County_State_Naming = "county_only_" + \
                                        self.modified_stringCountyName + "_" + \
                                        self.stringState_Name.get()

                    # Full string used for folder naming purposes.
                    self.folderNamingAddition = \
                        "_" + self.featureClass_County_State_Naming

                # If both timespan/magnitude comboboxes are not "Custom..."...
                if self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

                    # Assign naming conventions.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.mag_naming + \
                                                     self.timespan_url + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate + \
                                        self.folderNamingAddition

                # If timespan combobox is "Custom..." and magnitude combobox is
                # not "Custom..."...
                if self.stringEarthquakeTimespan.get() == "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

                    # Assign naming conventions.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.mag_naming + \
                                    self.timespan_file_folder_naming + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate + \
                                        self.folderNamingAddition

                # If timespan is "Custom..." and magnitude is "Custom..."...
                if self.stringEarthquakeTimespan.get() == "Custom..." and \
                        self.stringEarthquakeMagnitude.get() == "Custom...":

                    # Assign naming conventions.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.custom_Mag_Naming + \
                                    self.timespan_file_folder_naming + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate + \
                                        self.folderNamingAddition

                # If timespan is not "Custom..." and magnitude is "Custom..."...
                if self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() == "Custom...":

                    # Assign naming conventions.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.custom_Mag_Naming + \
                                                     self.timespan_url + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate + \
                                        self.folderNamingAddition

            # If "More Options" checkbox is unchecked...
            if self.statusVar_Checkbutton_Options.get() == 0:

                # If both timespan/magnitude comboboxes are not "Custom"...
                if self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

                    # Assign naming conventions for output data and folders.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.mag_naming + \
                                                     self.timespan_url + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate

                # If timespan combobox is "Custom..." and magnitude combobox is
                # not "Custom..."...
                if self.stringEarthquakeTimespan.get() == "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

                    # Assign naming conventions for output data and folders.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.mag_naming + \
                                    self.timespan_file_folder_naming + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate

                # If timespan combobox is "Custom..." and magnitude combobox is
                # "Custom..."...
                if self.stringEarthquakeTimespan.get() == "Custom..." and \
                        self.stringEarthquakeMagnitude.get() == "Custom...":

                    # Assign naming conventions for output data and folders.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.custom_Mag_Naming + \
                                    self.timespan_file_folder_naming + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate

                # If timespan combobox is not "Custom..." and magnitude combobox
                # is "Custom..."...
                if self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() == "Custom...":

                    # Assign naming conventions for output data and folders.
                    # (Mag/Timespan/Current Date broken out seperately to be
                    # used later on for CSV files, XY Event Layers, and
                    # Feature Class).
                    self.only_Mag_Timespan_CurDate = self.custom_Mag_Naming + \
                                                     self.timespan_url + curDate

                    # Full Path Name to be used for output files
                    self.fullPathName = self.folderDialogPath + "/" + usgs + \
                                        "_" + quake + "_" + \
                                        self.only_Mag_Timespan_CurDate

            # If the folder path already exists...
            if os.path.isdir(self.fullPathName) == True:

                try:

                    self.func_Scroll_setOutputText(
                        "Folder path already exists.", None)

                    self.func_Scroll_setOutputText(
                        "Deleting pre-existing folder.", None)

                    # Pause script for 0.5 seconds.
                    sleep(0.5)

                    # Delete the folder.
                    shutil.rmtree(self.fullPathName)

                    self.func_Scroll_setOutputText(
                        "Pre-existing folder deleted.", None)

                    # Increment progress bar.
                    self.func_ProgressBar_setProgress(3)

                except Exception as e:

                    # Show error message.
                    self.func_Scroll_setOutputText(str(e) + "\n" +
                                                   traceback.format_exc(),
                                                   color_Red)

                    # Re-enable all user-selectable options.
                    self.func_Enable_Buttons()

                    # Stop the status bar.
                    self.func_StopStatusBar()

                    # Increment progress bar to 100 percent.
                    self.func_ProgressBar_setProgress(100)

                    # Calculate total script processing time.
                    self.func_Calculate_Script_Time()

                    # Output scroll text to file.
                    self.func_Scroll_saveOutputText()

                    # Exit the application's task.
                    exit()

            # Pause script for 2.0 seconds.
            sleep(2.0)

            self.func_Scroll_setOutputText("Creating folder path:\n" +
                                           self.fullPathName, None)

            # If the folder doesn't already exist, create it.
            if not os.path.exists(self.fullPathName):

                os.makedirs(self.fullPathName)

                self.func_Scroll_setOutputText("Folder path created.", None)

                # Increment progress bar.
                self.func_ProgressBar_setProgress(6)

            # Once the folder has been created, the function to download the
            # CSV files will start.
            self.func_DownloadCSV()

        except Exception as e:

            # Show error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Re-enable all selectable buttons and drop-down lists.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Save all scroll box text to file.
            self.func_Scroll_saveOutputText()

            # Exit the process.
            exit()

    def func_Create_CSV_subFolder(self):

        # This function controls the creation of a CSV subfolder where all
        # downloaded/created CSVs will be stored.

        try:

            # Name and location for the CSV subfolder.
            self.csvDirectory = self.fullPathName + "/CSV_Folder/"

            self.func_Scroll_setOutputText(
                "Creating CSV subfolder...", None)

            # Pause script for 0.5 seconds.
            sleep(0.5)

            # If subfolder doesn't exist, create it.
            if not os.path.exists(self.csvDirectory):

                os.makedirs(self.csvDirectory)

                self.func_Scroll_setOutputText(
                    "CSV subfolder created.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(9)

        except Exception as e:

            # Show error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_DownloadCSV(self):

        # This function controls the downloading of the CSV files from the web.
        # This refers to CSVs obtained from non-Custom timespans.
        # Custom timespan CSVs are handled with another function detailed below.

        try:

            # If timespan is not "Custom..." and magnitude isn't "Custom..."...
            if self.stringEarthquakeTimespan.get() != "Custom..." and \
                    self.stringEarthquakeMagnitude.get() != "Custom...":

                # Run function to create CSV subfolder.
                self.func_Create_CSV_subFolder()

                try:

                    self.func_Scroll_setOutputText(
                        "Downloading:\n" + usgs + "_" + quake + "_" +
                        self.mag_naming + self.timespan_url + curDate +
                        fileExtCSV, None)

                    # Retrieve CSV from URL.
                    request.urlretrieve(self.textURLTextbox.get(),
                                        self.csvDirectory + "/" + usgs + "_" +
                                        quake + "_" + self.mag_naming +
                                        self.timespan_url + curDate +
                                        fileExtCSV)

                    self.func_Scroll_setOutputText(
                        "Download Complete.", None)

                # If download fails, try one more time (it could have been
                # a small, temporary network glitch).
                except:

                    self.func_Scroll_setOutputText(
                        "Download failed, trying again:\n" + usgs + "_" +
                        quake + "_" + self.mag_naming +
                        self.timespan_url + curDate +
                        fileExtCSV, color_Orange)

                    sleep(5)

                    # Retrieve CSV from URL.
                    request.urlretrieve(self.textURLTextbox.get(),
                                        self.csvDirectory + "/" + usgs + "_" +
                                        quake + "_" + self.mag_naming +
                                        self.timespan_url + curDate +
                                        fileExtCSV)

                    self.func_Scroll_setOutputText(
                        "Download Complete.", None)

                # Increment progress bar.
                self.func_ProgressBar_setProgress(20)

                # Run function to do non-custom data checks on the CSV file.
                self.func_NonCustomTimespan_CSV_HeaderCheck_ValueCheck()

            # If timespan is "Custom..." and magnitude is not "Custom..."...
            if self.stringEarthquakeTimespan.get() == "Custom..." and \
                    self.stringEarthquakeMagnitude.get() != "Custom...":

                # Run function to create CSV subfolder.
                self.func_Create_CSV_subFolder()

                # Run function to do custom CSV downloads and data checks.
                self.func_CustomTimespan_Download_CSV_and_HeaderCheck()

            # If timespan is "Custom..." and magnitude is "Custom..."...
            if self.stringEarthquakeTimespan.get() == "Custom..." and \
                    self.stringEarthquakeMagnitude.get() == "Custom...":

                # Run function to create CSV subfolder.
                self.func_Create_CSV_subFolder()

                # Run function to do custom CSV downloads and data checks.
                self.func_CustomTimespan_Download_CSV_and_HeaderCheck()

            # If timespan is not "Custom..." and magnitude is "Custom..."...
            if self.stringEarthquakeTimespan.get() != "Custom..." and \
                    self.stringEarthquakeMagnitude.get() == "Custom...":

                # Run function to create CSV subfolder.
                self.func_Create_CSV_subFolder()

                try:

                    self.func_Scroll_setOutputText(
                        "Downloading:\n" + usgs + "_" +
                        quake + "_" + self.custom_Mag_Naming +
                        self.timespan_url + curDate +
                        fileExtCSV, None)

                    # Retrieve CSV from URL.
                    request.urlretrieve(self.textURLTextbox.get(),
                                        self.csvDirectory + "/" + usgs + "_" +
                                        quake + "_" + self.custom_Mag_Naming +
                                        self.timespan_url + curDate +
                                        fileExtCSV)

                    self.func_Scroll_setOutputText(
                        "Download Complete.", None)

                # If download fails, try one more time (it could have been
                # a small, temporary network glitch).
                except:

                    self.func_Scroll_setOutputText(
                        "Download failed, trying again:\n" + usgs + "_" +
                        quake + "_" + self.custom_Mag_Naming +
                        self.timespan_url + curDate + fileExtCSV, color_Orange)

                    sleep(5)

                    # Retrieve CSV from URL.
                    request.urlretrieve(self.textURLTextbox.get(),
                                self.csvDirectory + "/" + usgs + "_" + quake +
                                "_" +
                                self.custom_Mag_Naming + self.timespan_url +
                                curDate + fileExtCSV)

                    self.func_Scroll_setOutputText(
                        "Download Complete.", None)

                # Increment progress bar.
                self.func_ProgressBar_setProgress(20)

                # Run the function for doing non-custom data checks.
                self.func_NonCustomTimespan_CSV_HeaderCheck_ValueCheck()

            # Pause script for 0.5 seconds.
            sleep(0.5)

        except HTTPError as httpError:

            # Display error message for URL-specific problems.
            self.func_Scroll_setOutputText(str(httpError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access web URL.\n"
                                 "Perhaps the website's URL is missing, "
                                 "offline, or down for maintenance?\n"
                                 "Please check URL connection and try again.")

        except URLError as urlError:

            # Display error message for internet connectivity-specific problems.
            self.func_Scroll_setOutputText(str(urlError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access internet connectivity.\n"
                                 "Possibly temporary internet issues?\n"
                                 "Please check connection and try again.")

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_NonCustomTimespan_CSV_HeaderCheck_ValueCheck(self):

        # This function will take the downloaded CSV (with non-custom timespan)
        # and assigned differing naming conventions, while also doing header
        # checks and analyzing data for unneeded values or discrepancies.

        try:

            # If the magnitude combobox displays "Custom..."...
            if self.stringEarthquakeMagnitude.get() == "Custom...":

                # Open the CSV file.
                self.csv_InputFile = open(self.csvDirectory + "/" + usgs +
                                    "_" + quake + "_" + self.custom_Mag_Naming +
                                    self.timespan_url + curDate + fileExtCSV)

                # Read the CSV file.
                self.csv_Reader = csv.reader(self.csv_InputFile)

                # Create/open a new CSV file for output modifications to be
                # written to.
                self.csv_OutputFile = open(self.csvDirectory + "/" + usgs +
                                    "_" + quake + "_" +
                                    self.custom_Mag_Naming + self.timespan_url +
                                    curDate + "_checked" + fileExtCSV,"w")

                # Write to the output CSV file.
                self.csv_Writer = csv.writer(self.csv_OutputFile, quotechar='"',
                                    delimiter=',', quoting=csv.QUOTE_ALL,
                                    skipinitialspace=True, lineterminator='\n')

                # This will be the output naming convention of the CSV file once
                # it has gone through all of its checks.
                self.csv_Check_If_Empty_CSV_Input = self.csvDirectory + "/" + \
                                            usgs + "_" + quake + "_" + \
                                            self.custom_Mag_Naming + \
                                            self.timespan_url + curDate + \
                                                    "_checked" + fileExtCSV

                # This will be the naming convention of the output feature class
                # once converted from CSV.
                self.nameFeatureClass_FromCSV = usgs + "_" + quake + "_" + \
                                                self.custom_Mag_Naming + \
                                                self.timespan_url + curDate

            # If the magnitude combobox does not display "Custom..."...
            elif self.stringEarthquakeMagnitude.get() != "Custom...":

                # Open the CSV file.
                self.csv_InputFile = open(self.csvDirectory + "/" + usgs +
                                        "_" + quake + "_" +
                                        self.mag_naming + self.timespan_url +
                                        curDate + fileExtCSV)

                # Read the CSV file.
                self.csv_Reader = csv.reader(self.csv_InputFile)

                # Create/open a new CSV file for output modifications to be
                # written to.
                self.csv_OutputFile = open(self.csvDirectory + "/" + usgs +
                                        "_" + quake + "_" +
                                        self.mag_naming + self.timespan_url +
                                        curDate + "_checked" + fileExtCSV,"w")

                # Write to the output CSV file.
                self.csv_Writer = csv.writer(self.csv_OutputFile, quotechar='"',
                                    delimiter=',', quoting=csv.QUOTE_ALL,
                                    skipinitialspace=True, lineterminator='\n')

                # This will be the output naming convention of the CSV file once
                # it has gone through all of its checks.
                self.csv_Check_If_Empty_CSV_Input = self.csvDirectory + "/" + \
                                usgs + "_" + quake + "_" + self.mag_naming + \
                                self.timespan_url + \
                                curDate + "_checked" + fileExtCSV

                # This will be the naming convention of the output feature class
                # once converted from CSV.
                self.nameFeatureClass_FromCSV = usgs + "_" + quake + "_" + \
                                                self.mag_naming + \
                                                self.timespan_url + curDate

            self.func_Scroll_setOutputText("Checking CSV file for missing "
                                    "headers, erroneous lat/long values, and "
                                    "removing all non-earthquake events.", None)

            # Remove single quotes and spaces from the CSV's first row.
            firstLine = \
                str(next(self.csv_Reader)).replace("'", "").replace(" ", "")

            # If the earthquake headers exist in that CSV's first row...
            if quake_headers in firstLine:

                # Write the earthquake headers to the output CSV file, splitting
                # at the comma. The firstLine row will be skipped for the next
                # step.
                self.csv_Writer.writerow(quake_headers.split(","))

            else:

                # Else, if the earthquake headers are not present in the CSV's
                # first row, add the earthquake headers.
                self.csv_Writer.writerow(quake_headers.split(","))

                # Return to first row of input CSV file, since this row does not
                # represent a header.
                self.csv_InputFile.seek(0)

            # For each row in the input CSV...
            for row in self.csv_Reader:

                # If entire row is not empty and lat/long columns and magnitude
                # column are not blank...
                if row and row[1] != "" and row[2] != "" and row[4] != "":

                    # If lat/long columns are not showing 0,0 coordinates...
                    if (row[1] != "0" or row[1] != "0.0") and \
                            (row[2] != "0" or row[2] != "0.0"):

                        # If lat/long columns are within appropriate range...
                        if float(row[1]) >= -90.0 and float(row[1]) <= 90.0 \
                                and float(row[2]) >= -180.0 and \
                                float(row[2]) <= 180.0:

                            # If the earthquake type column shows "earthquake"..
                            if str(row[14]).lower() == csv_Parameter_Earthquake:

                                # Write the row to the output CSV.
                                self.csv_Writer.writerow(row)

            # Close the input CSV (otherwise there may be a file lock).
            self.csv_InputFile.close()

            # Close the output CSV (otherwise there may be a file lock).
            self.csv_OutputFile.close()

            self.func_Scroll_setOutputText("CSV file checked.", None)

            # Increment progres bar.
            self.func_ProgressBar_setProgress(25)

            # Run function to check if output CSV file contains 0 earthquakes.
            self.func_Check_If_Empty_CSV(self.csv_Check_If_Empty_CSV_Input)

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Close the input CSV (otherwise there may be a file lock).
            self.csv_InputFile.close()

            # Close the output CSV (otherwise there may be a file lock).
            self.csv_OutputFile.close()

    def func_CustomTimespan_Download_CSV_and_HeaderCheck(self):

        # This function will take the downloaded CSV (with custom timespan)
        # and assigned differing naming conventions, while also doing header
        # checks and analyzing data for unneeded values or discrepancies.

        try:

            # Take the Custom Year From and Custom Month From and combine them
            # into a start date string. The first day of the month is added to
            # the start date.
            startDate = self.textCustomYearFrom + "-" + \
                                    self.textCustomMonthFrom + "-1"

            # Take the Custom Year To and Custom Month To and combine them
            # into an end date string. Python calculates the proper end date
            # for whichever month/year combination is used.
            endDate = self.textCustomYearTo + "-" + \
                      self.textCustomMonthTo + "-" + \
                      str(calendar.monthrange(int(self.textCustomYearTo),
                                                int(self.textCustomMonthTo))[1])

            # Formats the start date as YYYY-M-DD.
            start = datetime.datetime.strptime(startDate, '%Y-%m-%d').date()

            # Formats the end date as YYYY-M-DD.
            end = datetime.datetime.strptime(endDate, '%Y-%m-%d').date()

            # Replace start with cur_date in the while loop below if errors.
            # Otherwise, leave it alone. Might delete this soon.
            # cur_date = start

            # Counter for number of monthlyCSV downloads.
            counter_MonthlyCSV = 0

            # Create an ordered dictionary for storing names of CSV files per
            # month.
            dict = collections.OrderedDict()
            dict.clear()

            # While the start date is before the end date...
            while start < end:

                # Convert the start date to string.
                date_YMD = str(start)

                # Divide the string date into year, month, and day parameters by
                # using the "-" symbol as the delimiter.
                y, m, d = date_YMD.split("-")

                # Add the date timeframe for the monthly CSV to the dictionary,
                # assigning the proper number of days to each year/month
                # combination.
                dict[str(start)] = y + "-" + m + "-" + str(
                    calendar.monthrange(int(y), int(m))[1])

                # Increment the previous month by one month.
                start += relativedelta(months=1)

            # For each key/value combination within the dictionary...
            for key, value in dict.items():

                # Apply this naming convention to that monthly CSV file.
                downloadedURL_fileName = "monthlyCSV_" + str(
                    counter_MonthlyCSV + 1) + "_" + str(
                    key).replace("-", "_") + "_to_" + str(value).replace(
                    "-", "_") + fileExtCSV

                # If the magnitude drop-down list shows "All"...
                if self.stringEarthquakeMagnitude.get() == "All":

                    try:

                        self.func_Scroll_setOutputText("Downloading:\n" +
                                                       downloadedURL_fileName,
                                                       None)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                                    earthquake_Custom_siteURL_StartTime + key +
                                    earthquake_Custom_siteURL_EndTime + value,
                                    self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                    # If download fails, try one more time (it could have been
                    # a small, temporary network glitch).
                    except:

                        self.func_Scroll_setOutputText(
                            "Download failed, trying again:\n" +
                            downloadedURL_fileName, color_Orange)

                        sleep(5)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                            earthquake_Custom_siteURL_StartTime + key +
                            earthquake_Custom_siteURL_EndTime + value,
                            self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                # If the magnitude drop-down list shows "1.0+"...
                elif self.stringEarthquakeMagnitude.get() == "1.0+":

                    try:

                        self.func_Scroll_setOutputText("Downloading:\n" +
                                                       downloadedURL_fileName,
                                                       None)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                                    earthquake_Custom_siteURL_StartTime + key +
                                    earthquake_Custom_siteURL_EndTime + value +
                                    earthquake_Custom_siteURL_Min_Magnitude +
                                    str(1.0), self.csvDirectory +
                                    downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                    # If download fails, try one more time (it could have been
                    # a small, temporary network glitch).
                    except:

                        self.func_Scroll_setOutputText(
                            "Download failed, trying again:\n" +
                            downloadedURL_fileName, color_Orange)

                        sleep(5)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                            earthquake_Custom_siteURL_StartTime + key +
                            earthquake_Custom_siteURL_EndTime + value +
                            earthquake_Custom_siteURL_Min_Magnitude + str(1.0),
                            self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                # If the magnitude drop-down list shows "2.5+"...
                elif self.stringEarthquakeMagnitude.get() == "2.5+":

                    try:

                        self.func_Scroll_setOutputText("Downloading:\n" +
                                                       downloadedURL_fileName,
                                                       None)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                                    earthquake_Custom_siteURL_StartTime + key +
                                    earthquake_Custom_siteURL_EndTime + value +
                                    earthquake_Custom_siteURL_Min_Magnitude +
                                    str(2.5), self.csvDirectory +
                                    downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                    # If download fails, try one more time (it could have been
                    # a small, temporary network glitch).
                    except:

                        self.func_Scroll_setOutputText(
                            "Download failed, trying again:\n" +
                            downloadedURL_fileName, color_Orange)

                        sleep(5)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                            earthquake_Custom_siteURL_StartTime + key +
                            earthquake_Custom_siteURL_EndTime + value +
                            earthquake_Custom_siteURL_Min_Magnitude + str(2.5),
                            self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                # If the magnitude drop-down list shows "4.5+"...
                elif self.stringEarthquakeMagnitude.get() == "4.5+":

                    try:

                        self.func_Scroll_setOutputText("Downloading:\n" +
                                                       downloadedURL_fileName,
                                                       None)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                                    earthquake_Custom_siteURL_StartTime + key +
                                    earthquake_Custom_siteURL_EndTime + value +
                                    earthquake_Custom_siteURL_Min_Magnitude +
                                    str(4.5), self.csvDirectory +
                                    downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                    # If download fails, try one more time (it could have been
                    # a small, temporary network glitch).
                    except:

                        self.func_Scroll_setOutputText(
                            "Download failed, trying again:\n" +
                            downloadedURL_fileName, color_Orange)

                        sleep(5)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                            earthquake_Custom_siteURL_StartTime + key +
                            earthquake_Custom_siteURL_EndTime + value +
                            earthquake_Custom_siteURL_Min_Magnitude + str(4.5),
                            self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                # If the magnitude drop-down list shows "Custom..."...
                elif self.stringEarthquakeMagnitude.get() == "Custom...":

                    try:

                        self.func_Scroll_setOutputText("Downloading:\n" +
                                                       downloadedURL_fileName,
                                                       None)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                                    earthquake_Custom_siteURL_StartTime + key +
                                    earthquake_Custom_siteURL_EndTime + value +
                                    earthquake_Custom_siteURL_Min_Magnitude +
                                    self.minMag + self.maxMag,
                                    self.csvDirectory + downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                    # If download fails, try one more time (it could have been
                    # a small, temporary network glitch).
                    except:

                        self.func_Scroll_setOutputText(
                            "Download failed, trying again:\n" +
                            downloadedURL_fileName, color_Orange)

                        sleep(5)

                        # Retrieve the CSV for the next month with this
                        # magnitude's specific naming convention.
                        request.urlretrieve(earthquake_Custom_siteURL_CSV +
                            earthquake_Custom_siteURL_StartTime + key +
                            earthquake_Custom_siteURL_EndTime + value +
                            earthquake_Custom_siteURL_Min_Magnitude +
                            self.minMag + self.maxMag, self.csvDirectory +
                            downloadedURL_fileName)

                        self.func_Scroll_setOutputText("Download Complete.",
                                                       None)

                # Increment CSV counter.
                counter_MonthlyCSV = counter_MonthlyCSV + 1

            # Increment progress bar.
            self.func_ProgressBar_setProgress(22)

            # Create new counter for counting the monthly CSV files during the
            # append process.
            counter_MonthlyCSV_ForAppend = 0

            # Set Key and Value within dictionary to next Key/Value set.
            key, value = next(iter(dict.items()))

            self.func_Scroll_setOutputText("Appending CSV files while checking "
                "for missing headers, erroneous lat/long values, and removing "
                "all non-earthquake events.", None)

            # Naming convention of output CSV file for appending.
            self.csv_Check_If_Empty_CSV_Input = self.csvDirectory + usgs + \
                        "_" + quake + "_" + "monthlyCSV_appended_" + \
                        self.only_Mag_Timespan_CurDate + "_checked" + fileExtCSV

            # Create/Open output CSV file for the the append process.
            csv_OutputFile = open(self.csv_Check_If_Empty_CSV_Input, "a")

            # Naming convention for the feature class from CSV naming convention
            # to be used later when the feature class is created.
            self.nameFeatureClass_FromCSV = \
                usgs + "_" + quake + "_" + self.only_Mag_Timespan_CurDate

            # Create CSV writer to begin writing data to the appended CSV file.
            csvWriter = csv.writer(csv_OutputFile, quotechar='"', delimiter=',',
                                   quoting=csv.QUOTE_ALL, skipinitialspace=True,
                                   lineterminator='\n')

            # Open the first monthly CSV file to be appended to output CSV.
            csv_InputFile = open(self.csvDirectory + "monthlyCSV_" +
                        str(counter_MonthlyCSV_ForAppend + 1) + "_" +
                        str(key).replace("-", "_") + "_to_" +
                        str(value).replace("-", "_") + fileExtCSV)

            # Read the first monthly CSV file to be appended to output CSV.
            csv_Reader = csv.reader(csv_InputFile)

            # Properly format first line of CSV to match header formatting.
            firstLine = str(next(csv_Reader)).replace("'", "").replace(" ", "")

            # If the headers exist within the first line of the CSV...
            if quake_headers in firstLine:

                # Write the first header row to the CSV file.
                csvWriter.writerow(quake_headers.split(","))

            else:

                # Headers are missing in first CSV, so write them anyways.
                csvWriter.writerow(quake_headers.split(","))

                # Return the input CSV back to first row. This is necessary if
                # headers did not already exist within the input CSV.
                csv_InputFile.seek(0)

            # For each row within the first monthly CSV...
            for row in csv_Reader:

                # If entire row is not empty and lat/long columns and magnitude
                # column are not blank...
                if row and row[1] != "" and row[2] != "" and row[4] != "":

                    # If lat/long columns aren't showing 0,0 coordinates...
                    if (row[1] != "0" or row[1] != "0.0") and \
                            (row[2] != "0" or row[2] != "0.0"):

                        # If lat/long columns are within appropriate range...
                        if float(row[1]) >= -90.0 and float(row[1]) <= 90.0 and\
                            float(row[2]) >= -180.0 and float(row[2]) <= 180.0:

                            # If the earthquake type is an actual earthquake...
                            if str(row[14]).lower() == csv_Parameter_Earthquake:

                                # Write the row to the appended CSV file.
                                csvWriter.writerow(row)

            # Increment counter for monthly CSV file.
            counter_MonthlyCSV_ForAppend = counter_MonthlyCSV_ForAppend + 1

            # Close the first monthly CSV file.
            csv_InputFile.close()

            # For each monthly CSV file to be appended...
            for num in range(1, counter_MonthlyCSV):

                # Open the next monthly CSV file.
                csv_NextFile = open(self.csvDirectory + "monthlyCSV_" +
                    str(counter_MonthlyCSV_ForAppend + 1) + "_" +
                    str(list(dict.keys())[num]).replace("-","_") + "_to_" +
                    str(list(dict.values())[num]).replace("-", "_") +
                    fileExtCSV)

                # Read the next monthly CSV file.
                csv_Next_Reader = csv.reader(csv_NextFile)

                # Properly format first line of next CSV to match header
                # formatting.
                firstLine_nextCSV = \
                    str(next(csv_Next_Reader)).replace("'", "").replace(" ", "")

                # If the headers exist within the first line of the next CSV...
                if quake_headers in firstLine_nextCSV:

                    # Skip the row and don't add to appended CSV.
                    pass

                else:

                    # If headers are missing, return the next CSV back to first
                    # row so that the first row doesn't get skipped in the next
                    # step.
                    csv_NextFile.seek(0)

                # For each row within the next monthly CSV...
                for row in csv_Next_Reader:

                    # If entire row is not empty and lat/long columns and
                    # magnitude column are not blank...
                    if row and row[1] != "" and row[2] != "" and row[4] != "":

                        # If lat/long columns aren't showing 0,0 coordinates...
                        if (row[1] != "0" or row[1] != "0.0") and \
                                (row[2] != "0" or row[2] != "0.0"):

                            # If lat/long columns are within appropriate range..
                            if float(row[1]) >= -90.0 and \
                                float(row[1]) <= 90.0 and \
                                float(row[2]) >= -180.0 and \
                                float(row[2]) <= 180.0:

                                # If the earthquake type is an actual
                                # earthquake...
                                if str(row[14]).lower() == \
                                        csv_Parameter_Earthquake:

                                    # Append the row to the output appended CSV.
                                    csvWriter.writerow(row)

                # Close that next CSV file.
                csv_NextFile.close()

                # Increment the counter for the next monthly CSV file to be
                # appended.
                counter_MonthlyCSV_ForAppend = counter_MonthlyCSV_ForAppend + 1

            # Close the output CSV file for appending once all monthly CSV files
            # have been appended.
            csv_OutputFile.close()

            self.func_Scroll_setOutputText(str(counter_MonthlyCSV) +
                                " CSV files were appended and checked.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(25)

            # Execute function to check if appended CSV file is empty.
            self.func_Check_If_Empty_CSV(self.csv_Check_If_Empty_CSV_Input)


        except HTTPError as httpError:

            # Display error message for URL-specific problems.
            self.func_Scroll_setOutputText(str(httpError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access web URL.\n"
                                 "Perhaps the website's URL is missing, "
                                 "offline, or down for maintenance?\n"
                                 "Please check URL connection and try again.")


        except URLError as urlError:

            # Display error message for internet connectivity-specific problems.

            self.func_Scroll_setOutputText(str(urlError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access internet connectivity.\n"
                                 "Possibly temporary internet issues?\n"
                                 "Please check connection and try again.")

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Check_If_Empty_CSV(self, csvName):

        # This function checks to see the output, checked CSV file contains any
        # earthquake records.

        try:

            # Open the output, checked CSV file...
            with open(csvName) as csvFile:

                # Count all records within the CSV file. Assign the count total
                # to a worldwide earthquake count variable.
                self.worldwide_earthquake_count = sum(1 for row in csvFile)

                # If the earthquake count is less than 1...
                if self.worldwide_earthquake_count <= 1:

                    # Display error message explaining that no earthquake
                    # records exist within the CSV file. The function will exit
                    # from here.
                    messagebox.showerror(errorMessage_Header,
                                    message="CSV file contains no data!\n" + \
                                    "Unable to create GIS data.")

                    # Re-enable all selectable buttons and drop-down lists.
                    self.func_Enable_Buttons()

                    # Stop the status bar.
                    self.func_StopStatusBar()

                    # Increment progress bar to 100 percent.
                    self.func_ProgressBar_setProgress(100)

                    # Calculate total script processing time.
                    self.func_Calculate_Script_Time()

                    # Save all scroll box text to file.
                    self.func_Scroll_saveOutputText()

                    # Exit the process.
                    exit()

                else:

                    # Else if earthquake records exist, but are in excess of
                    # 500,000 records...
                    if self.worldwide_earthquake_count >= 500000:

                        # Inform the user that the next geoprocessing tasks may
                        # take considerable time to execute.
                        self.func_Scroll_setOutputText("BE ADVISED:\n" +
                            "The CSV contains " + '{:,}'.format(
                            self.worldwide_earthquake_count) + " features.\n" +
                            "All additional processes may take considerable "
                            "time to complete.", color_Orange)

                        # Pause the script for five seconds to allow the user
                        # ample time to read the message.
                        sleep(5)

                    # Increment progress bar.
                    self.func_ProgressBar_setProgress(28)

                    # Execute function to create feature class from CSV file.
                    self.func_CreateFeatureClass_from_CSV(
                        self.csv_Check_If_Empty_CSV_Input,
                        self.nameFeatureClass_FromCSV)

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Re-enable all selectable buttons and drop-down lists.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Save all scroll box text to file.
            self.func_Scroll_saveOutputText()

            # Exit the process.
            exit()

    def func_CreateFeatureClass_from_CSV(
            self, csvName, nameFeatureClass_FromCSV):

        # This function controls the process of creating a GIS subfolder where
        # an output File GDB will be stored with a feature class created from
        # the checked CSV file. During this process, the CSV file is converted
        # into a feature class. This feature class is used to create a new,
        # re-projected feature class of the same data. The original feature
        # class is deleted, and the re-projected feature class naming convention
        # is changed to match the original feature class that was deleted.

        try:

            # Set input CSV argument as name of unclipped, unprojected feature
            # class.
            self.featureClass_Earthquakes_Unclipped_Unprojected = \
                nameFeatureClass_FromCSV

            # Set name for GIS Subfolder creation.
            self.subFolder_GIS = self.fullPathName + "/GIS_Folder/"

            self.func_Scroll_setOutputText("Creating GIS subfolder...", None)

            # If the GIS subfolder doesn't already exist, create it.
            if not os.path.exists(self.subFolder_GIS):

                os.makedirs(self.subFolder_GIS)

                self.func_Scroll_setOutputText("GIS subfolder created.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(31)

            # Pause script for half a second.
            sleep(0.5)

            self.func_Scroll_setOutputText("Creating File GDB...", None)

            # Create File GDB within the GIS subfolder.
            arcpy.CreateFileGDB_management(self.subFolder_GIS, nameFileGDB)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("File GDB created.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(34)

            self.func_Scroll_setOutputText(
                "Creating temporary XY Event Layer from CSV...", None)

            # XY Event Layer input parameters.
            inputFile = csvName
            input_X_Field = "longitude"
            input_Y_Field = "latitude"
            outputFile = "in_memory/csv_XY_EventLayer"
            spatialReferenceType = None
            input_Z_Field = None

            # Process: Make temporary XY Event Layer (Geographic Coordinate
            # system defaults to WGS84 when spatial reference set to None).
            arcpy.MakeXYEventLayer_management(inputFile, input_X_Field,
                                              input_Y_Field, outputFile,
                                              spatialReferenceType,
                                              input_Z_Field)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Temporary XY Event Layer from CSV created.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(37)

            self.func_Scroll_setOutputText(
                "Creating Feature Class from XY Event Layer...", None)

            # Convert temporary XY Event Layer into a feature class stored
            # within the File GDB.
            arcpy.FeatureClassToFeatureClass_conversion(outputFile,
                            self.subFolder_GIS + nameFileGDB,
                            self.featureClass_Earthquakes_Unclipped_Unprojected)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature Class from XY Event Layer created.", None)

            # Set workspace to the File GDB for following tasks.
            arcpy.env.workspace = self.subFolder_GIS + nameFileGDB

            # Create new variable for unclipped, projected feature class name.
            # This will be a temporary naming convention.
            self.featureClass_Earthquakes_Unclipped_Projected = \
                    self.featureClass_Earthquakes_Unclipped_Unprojected + \
                    "_Projected"

            self.func_Scroll_setOutputText("Projecting feature class to PCS " +
                            pcsReferenceString +
                            " with Central Meridian Offset (-30.0 degrees)...",
                            None)

            # Set projected coordinate system of feature class to the designated
            # PCS reference with -30.0 Central Meridian offset.
            arcpy.Project_management(
                self.featureClass_Earthquakes_Unclipped_Unprojected,
                self.featureClass_Earthquakes_Unclipped_Projected, pcsReference)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("PCS Projection to " +
                    pcsReferenceString +
                    " with Central Meridian Offset (-30.0 degrees) completed.",
                    None)

            self.func_Scroll_setOutputText(
                "Recalculating extent for feature class...",
                None)

            # Recalculate extent of newly projected feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                self.featureClass_Earthquakes_Unclipped_Projected)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class extent recalculated.",
                                           None)

            self.func_Scroll_setOutputText("Deleting feature class " +
                        self.featureClass_Earthquakes_Unclipped_Unprojected +
                        " from File GDB...", None)

            # Delete original feature class conversion from CSV.
            arcpy.Delete_management(
                self.featureClass_Earthquakes_Unclipped_Unprojected)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature class deleted from File GDB.", None)

            self.func_Scroll_setOutputText("Renaming feature class " +
                self.featureClass_Earthquakes_Unclipped_Projected + " to " +
                self.featureClass_Earthquakes_Unclipped_Unprojected + "...",
                None)

            # Rename the projected feature class to the unprojected feature
            # class name that was just deleted.
            arcpy.Rename_management(
                self.featureClass_Earthquakes_Unclipped_Projected,
                self.featureClass_Earthquakes_Unclipped_Unprojected)

            # Display ArcPy geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature class has been renamed.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(40)

            # Execute function that clears any "in_memory" storage used during
            # ArcPy geoprocessing tasks.
            self.func_Clear_InMemory()

            # Execute function to evaluate which clipping option is selected.
            self.func_RadioButton_Clipping_Rules()

        except arcpy.ExecuteError:

            # Display ArcPy-specific error messages. If any geoprocessing tasks
            # fails, no further functions are attempted.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            # Re-enable all selectable buttons and drop-down lists.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Save all scroll box text to file.
            self.func_Scroll_saveOutputText()

            # Exit the process.
            exit()

        except Exception as e:

            # Display all other error messages.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Re-enable all selectable buttons and drop-down lists.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Save all scroll box text to file.
            self.func_Scroll_saveOutputText()

            # Exit the process.
            exit()

    def func_RadioButton_Clipping_Command(self):

        # This function controls how the clipping options should operate with
        # regard to the radio buttons. Depending on the clipping selection,
        # the appearance of state or county drop-down lists will change.

        try:

            # Get the value of the clipping option selected by the user.
            self.radioButton_Selection = self.statusClippingOption.get()

            # If the clipping option represents "USA"...
            if self.radioButton_Selection == 1:

                # If the user selects USA after already selecting State, remove
                # the state drop-down list and set state variables to None.
                if self.comboFrame_State is not None:

                    self.comboFrame_State.grid_remove()

                    self.comboFrame_State = None

                    self.stringState_Name = None

                # If the user selects USA after already selecting county option,
                #  remove the county/state drop-down lists and set county
                # variables to None.
                if self.comboFrame_Counties is not None:

                    self.comboFrame_Counties.grid_remove()

                    self.comboFrame_Counties = None

                    self.stringCounty_Name = None

                # Execute function to resize window accordingly.
                self.func_windowResize()

            # If the clipping option represents "State"...
            if self.radioButton_Selection == 2:

                # If the user selects State after already selecting State,
                # remove the previously created state drop-down list and reset
                # state variables to None. This prevents duplicate drop-down
                # lists from stacking on top of each other with each radio
                # button click.
                if self.comboFrame_State is not None:

                    self.comboFrame_State.grid_remove()

                    self.comboFrame_State = None

                # If the user selects State after already selecting County,
                # remove the previously created county/state drop-down lists and
                # reset county variables to None. This prevents duplicate
                # drop-down lists from stacking on top of each other with
                # each radio button click.
                if self.comboFrame_Counties is not None:

                    self.comboFrame_Counties.grid_remove()

                    self.comboFrame_Counties = None

                    self.stringCounty_Name = None

                # Execute function that handles the functionality of the state
                # drop-down list.
                self.func_RadioButton_State_Frame_Options()

                # Excecute function to resize window accordingly.
                self.func_windowResize()

            # If the clipping option represents "County" while the state
            # drop-down list is already visible (User selects state option
            # immediately before switching to county option)...
            if self.radioButton_Selection == 3 and \
                    self.comboFrame_State is not None:

                # Do nothing, leave the state drop-down list visible.
                pass

                # If the user selects County after already selecting County,
                # remove the previously created county drop-down list and
                # reset county variables to None. This prevents duplicate
                # drop-down lists from stacking on top of each other with
                # each radio button click.
                if self.comboFrame_Counties is not None:

                    self.comboFrame_Counties.grid_remove()

                    self.comboFrame_Counties = None

                    self.stringCounty_Name = None

                # Execute function that handles the functionality of the county
                # drop-down list.
                self.func_RadioButton_County_Frame_Options()

                # Execute function to resize window accordingly.
                self.func_windowResize()

            # If the clipping option represents "County" while the state
            # drop-down list isn't already visible (User does not select state
            # option immediately before switching to county option)...
            if self.radioButton_Selection == 3 and \
                    self.comboFrame_State is None:

                # If County options already exists, remove the drop-down list
                # and clear county variablesto prevent duplicate drop-down lists
                # from stacking on top of each other.
                if self.comboFrame_Counties is not None:

                    self.comboFrame_Counties.grid_remove()

                    self.comboFrame_Counties = None

                    self.stringCounty_Name = None

                # Execute function that handles the functionality of the state
                # drop-down list.
                self.func_RadioButton_State_Frame_Options()

                # Execute function that handles the functionality of the county
                # drop-down list.
                self.func_RadioButton_County_Frame_Options()

                # Execute function to resize window accordingly.
                self.func_windowResize()

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_RadioButton_Clipping_Rules(self):

        # This function controls how the Census Bureau's Shapefile is clipped,
        # depending on user preference assigned within the clipping options
        # radio button/drop-down list selection.
        try:
            # If the radio button is USA...
            if self.radioButton_Selection == 1:

                # Execute function that downloads/unzips the Census Bureau's
                # Shapefile.
                self.func_Download_Unzip_Census_Shapefile()

                # Once Census Shapefile has been downloaded, execute function
                # to extract the 50 states and Washington DC only.
                self.func_Extract_50_States_and_DC_Only(
                    self.subFolder_CensusShapefile + "/" +
                    census_URL_CountyShapefile_FileName + fileExtShp,
                    self.subFolder_GIS + "/" + nameFileGDB)

                # Then execute function to clip earthquake features to the
                # polygon boundary for US states and DC.
                self.func_FeatureClass_Clip(self.nameFeatureClass_FromCSV,
                                featureClass_50States_and_DC_only,
                                "clipped_" + self.nameFeatureClass_FromCSV)

                # Execute function to verify if clipped earthquake feature class
                # still contains any features.
                self.func_Check_If_Empty_Output_FeatureClass(
                    self.clipped_Output_FeatureClass)

                # Execute function that controls analysis options.
                self.func_Controls_For_Analysis_Options(
                    featureClass_50States_and_DC_only)

            # If the radio button is State...
            elif self.radioButton_Selection == 2:

                # Execute function that downloads/unzips the Census Bureau's
                # Shapefile.
                self.func_Download_Unzip_Census_Shapefile()

                # Once Census Shapefile has been downloaded, execute function
                # to extract state selection only.
                self.func_Extract_State_Selection_Only(
                    self.subFolder_CensusShapefile + "/" +
                    census_URL_CountyShapefile_FileName + fileExtShp,
                    self.subFolder_GIS + "/" + nameFileGDB)

                # Then execute function to clip earthquake features to the
                # polygon state boundary.
                self.func_FeatureClass_Clip(self.nameFeatureClass_FromCSV,
                                    self.featureClass_State_Selection_Only,
                                    "clipped_" + self.nameFeatureClass_FromCSV)

                # Execute function to verify if clipped earthquake feature class
                # still contains any features.
                self.func_Check_If_Empty_Output_FeatureClass(
                    self.clipped_Output_FeatureClass)

                # Execute function that controls analysis options.
                self.func_Controls_For_Analysis_Options(
                    self.featureClass_State_Selection_Only)

            # If the radio button is County...
            elif self.radioButton_Selection == 3:

                # Execute function that downloads/unzips the Census Bureau's
                # Shapefile.
                self.func_Download_Unzip_Census_Shapefile()

                # Once Census Shapefile has been downloaded, execute function
                # to extract the county selection only.
                self.func_Extract_County_Selection_Only(
                    self.subFolder_CensusShapefile + "/" +
                    census_URL_CountyShapefile_FileName + fileExtShp,
                    self.subFolder_GIS + "/" + nameFileGDB)

                # Then execute function to clip earthquake features to the
                # polygon county boundary.
                self.func_FeatureClass_Clip(self.nameFeatureClass_FromCSV,
                                    self.featureClass_County_State_Naming,
                                    "clipped_" + self.nameFeatureClass_FromCSV)

                # Execute function to verify if clipped earthquake feature class
                # still contains any features.
                self.func_Check_If_Empty_Output_FeatureClass(
                    self.clipped_Output_FeatureClass)

                # Execute function that controls analysis options.
                self.func_Controls_For_Analysis_Options(
                    self.featureClass_County_State_Naming)

        except Exception as e:

            # Display error message.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Download_Unzip_Census_Shapefile(self):

        # This function controls the download and and unzipping of the Shapefile
        # obtained from the US Census Bureau.

        try:

            # Create subfolder naming variable for location to save Shapefile.
            self.subFolder_CensusShapefile = self.subFolder_GIS + \
                                             "/Census_Shapefile/"

            self.func_Scroll_setOutputText(
                "Creating Census Shapefile subfolder...", None)

            # If subfolder does not already exist, create it.
            if not os.path.exists(self.subFolder_CensusShapefile):
                os.makedirs(self.subFolder_CensusShapefile)

                self.func_Scroll_setOutputText(
                    "Census Shapefile subfolder created.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(43)

            # Pause script for half a second.
            sleep(0.5)

            try:

                self.func_Scroll_setOutputText(
                    "Downloading US Census Shapefile...", None)

                # Attempt to download the Shapefile.
                request.urlretrieve(census_URL_CountyShapefile,
                                    self.subFolder_CensusShapefile + "/" +
                                    census_URL_CountyShapefile_FileName +
                                    fileExtZip)

                self.func_Scroll_setOutputText(
                    "US Census Shapefile Downloaded.", None)

            # If download fails, try one more time (it could have been
            # a small, temporary network glitch).
            except:

                self.func_Scroll_setOutputText(
                    "Download failed, trying again.", color_Orange)

                sleep(5)

                # Attempt to download the Shapefile.
                request.urlretrieve(census_URL_CountyShapefile,
                                    self.subFolder_CensusShapefile + "/" +
                                    census_URL_CountyShapefile_FileName +
                                    fileExtZip)

                self.func_Scroll_setOutputText(
                    "US Census Shapefile Downloaded.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(49)

            # Pause script for half a second.
            sleep(0.5)

            self.func_Scroll_setOutputText(
                "Unzipping US Census Shapefile...", None)

            # Unzip the Shapefile within the same shapefile subfolder.
            unZipThisFile = zipfile.ZipFile(self.subFolder_CensusShapefile +
                                    "/" + census_URL_CountyShapefile_FileName +
                                    fileExtZip, 'r')
            unZipThisFile.extractall(self.subFolder_CensusShapefile)

            # Close file to prevent locks.
            unZipThisFile.close()

            self.func_Scroll_setOutputText(
                "US Census Shapefile unzipped.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(52)

        except HTTPError as httpError:

            # Display error message for URL-specific problems.
            self.func_Scroll_setOutputText(str(httpError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access web URL.\n"
                                 "Perhaps the website's URL is missing, "
                                 "offline, or down for maintenance?\n"
                                 "Please check URL connection and try again.")


        except URLError as urlError:

            # Display error message for internet connectivity-specific problems.
            self.func_Scroll_setOutputText(str(urlError), color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "Unable to access internet connectivity.\n"
                                 "Possibly temporary internet issues?\n"
                                 "Please check connection and try again.")

        except Exception as e:

            # Display error messages for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Extract_50_States_and_DC_Only(self, censusShapefile, fileGDB_Path):

        # This function controls the process of extracting the 50 states and
        # Washington DC from the Census Bureau's Shapefile and performing
        # various modifications to that data.

        try:

            self.func_Scroll_setOutputText(
                "Copying Census Shapefile to File GDB...", None)

            # Copy the Census Shapefile to a feature class within the File GDB.
            arcpy.CopyFeatures_management(censusShapefile,
                        fileGDB_Path + "/" + featureClass_50States_and_DC_only)

            # Display geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Census Shapefile copied to File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(55)

            # Pause script for one second.
            sleep(1)

            self.func_Scroll_setOutputText(
                "Extracting 50 States and DC from Feature Class...", None)

            # Open the Census feature class with an Update Cursor.
            # Attribute field set to the state's FIPS code.
            with arcpy.da.UpdateCursor(fileGDB_Path + "/" +
                                    featureClass_50States_and_DC_only,
                                    census_Shapefile_Field_StateFIPS) as cursor:

                # For each feature in the Census feature class.
                for row in cursor:

                    # This If statement removes non-50 state (and DC) FIPS codes
                    # from the Census feature class. The original data includes
                    # all US territories, and those FIPS codes must be removed.
                    if row[0] == "60" or row[0] == "66" or row[0] == "69" or \
                                    row[0] == "72" or row[0] == "78":

                        # Delete polygon feature.
                        cursor.deleteRow()

            # Display geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "50 States and DC extracted from Feature Class.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(56)

            # Set the workspace within the File GDB for the following tasks.
            arcpy.env.workspace = fileGDB_Path

            # Set naming convention variable for projecting Census feature
            # class.
            self.featureClass_Polygons_Projected = \
                featureClass_50States_and_DC_only + "_Projected"

            self.func_Scroll_setOutputText("Projecting feature class to PCS " +
                            pcsReferenceString +
                            " with Central Meridian Offset (-30.0 degrees)...",
                            None)

            # Project the Census feature class to the designated PCS as a new
            # feature class within the File GDB.
            arcpy.Project_management(featureClass_50States_and_DC_only,
                                     self.featureClass_Polygons_Projected,
                                     pcsReference)

            # Display geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("PCS Projection to " +
                                           pcsReferenceString + " completed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(57)

            self.func_Scroll_setOutputText(
                "Recalculating extent for feature class...", None)

            # Recalculate extent of the projected Census feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                self.featureClass_Polygons_Projected)

            # Display geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class extent recalculated.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(58)

            self.func_Scroll_setOutputText("Deleting feature class " +
                                           featureClass_50States_and_DC_only +
                                           " from File GDB...", None)

            # Delete the original, pre-projected Census feature class from the
            # File GDB. It is no longer needed.
            arcpy.Delete_management(featureClass_50States_and_DC_only)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature class deleted from File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(59)

            self.func_Scroll_setOutputText("Renaming feature class " +
                                    self.featureClass_Polygons_Projected +
                                    " back to " +
                                    featureClass_50States_and_DC_only + "...",
                                    None)

            # Rename the projected Census feature class to the original naming
            # convention of the feature class that was just deleted.
            arcpy.Rename_management(self.featureClass_Polygons_Projected,
                                    featureClass_50States_and_DC_only)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class has been renamed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(60)

        except arcpy.ExecuteError:

            # Display geoprocessing error messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

        except Exception as e:

            # Display error messages for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Extract_State_Selection_Only(self, censusShapefile, fileGDB_Path):

        # This function controls the process of extracting the user-selected
        # state from the Census Bureau's Shapefile and performing various
        # modifications to that data.

        try:

            self.func_Scroll_setOutputText(
                "Copying Census Shapefile to File GDB...", None)

            # Copy the Census Shapefile to a feature class within the File GDB.
            arcpy.CopyFeatures_management(censusShapefile, fileGDB_Path + "/" +
                                        self.featureClass_State_Selection_Only)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Census Shapefile copied to File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(55)

            # Pause script for one second.
            sleep(1)

            self.func_Scroll_setOutputText("Extracting state selection(" +
                                           self.stringState_Name.get() +
                                           ") from Feature Class...", None)

            # Open the Census feature class with an Update Cursor.
            # Attribute field set to the state's FIPS code.
            with arcpy.da.UpdateCursor(fileGDB_Path + "/" +
                                    self.featureClass_State_Selection_Only,
                                    census_Shapefile_Field_StateFIPS) as cursor:

                # For each feature in the Census feature class...
                for row in cursor:

                    # This If statement removes all polygons not affiliated with
                    # the user-selected state's FIPS code. This is accessed
                    # from the state name/state FIPS dictionary.
                    if row[0] != \
                    dict_StateName_StateFIPs.get(self.stringState_Name.get()):

                        # Delete polygon feature.
                        cursor.deleteRow()

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("State selection(" +
                                        self.stringState_Name.get() +
                                        ") extracted from Feature Class.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(56)

            # Set workspace for the following tasks.
            arcpy.env.workspace = fileGDB_Path

            # Set naming convention variable for projecting Census feature
            # class.
            self.featureClass_Polygons_Projected = \
                self.featureClass_State_Selection_Only + "_Projected"

            self.func_Scroll_setOutputText("Projecting feature class to PCS " +
                            pcsReferenceString +
                            " with Central Meridian Offset (-30.0 degrees)...",
                            None)

            # Project the Census feature class to the designated PCS as a new
            # feature class within the File GDB.
            arcpy.Project_management(self.featureClass_State_Selection_Only,
                                     self.featureClass_Polygons_Projected,
                                     pcsReference)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("PCS Projection to " +
                                           pcsReferenceString + " completed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(57)

            self.func_Scroll_setOutputText(
                                    "Recalculating extent for feature class...",
                                    None)

            # Recalculate extent of the projected Census feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                                        self.featureClass_Polygons_Projected)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class extent recalculated.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(58)

            self.func_Scroll_setOutputText("Deleting feature class " +
                                    self.featureClass_State_Selection_Only  +
                                    " from File GDB...", None)

            # Delete the original, pre-projected Census feature class from the
            # File GDB. It is no longer needed.
            arcpy.Delete_management(self.featureClass_State_Selection_Only )

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature class deleted from File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(59)

            self.func_Scroll_setOutputText("Renaming feature class " +
                                self.featureClass_Polygons_Projected +
                                " back to " +
                                self.featureClass_State_Selection_Only + "...",
                                None)

            # Rename the projected Census feature class to the original naming
            # convention of the feature class that was just deleted.
            arcpy.Rename_management(self.featureClass_Polygons_Projected,
                                    self.featureClass_State_Selection_Only)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class has been renamed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(60)

        except arcpy.ExecuteError:

            # Display geoprocessing error messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

        except Exception as e:

            # Display error messages for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Extract_County_Selection_Only(self, censusShapefile, fileGDB_Path):

        # This function controls the process of extracting the user-selected
        # county from the Census Bureau's Shapefile and performing various
        # modifications to that data.

        try:

            self.func_Scroll_setOutputText(
                "Copying Census Shapefile to File GDB...", None)

            # Copy the Census Shapefile to a feature class within the File GDB.
            arcpy.CopyFeatures_management(censusShapefile, fileGDB_Path + "/" +
                                          self.featureClass_County_State_Naming)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Census Shapefile copied to File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(55)

            # Pause script for one second.
            sleep(1)

            self.func_Scroll_setOutputText("Extracting (" +
                                           self.stringCounty_Name.get() +
                                           ", " + self.stringState_Name.get() +
                                           ") from Feature Class...", None)

            # Open the Census feature class with an Update Cursor.
            # Field names set to the state's FIPS code and county names.
            with arcpy.da.UpdateCursor(fileGDB_Path + "/" +
                                self.featureClass_County_State_Naming,
                                field_names=[census_Shapefile_Field_StateFIPS,
                                census_Shapefile_Field_CountyName]) as cursor:

                # For each feature in the Census feature class...
                for row in cursor:

                    # If the feature's state FIPS code matches the user-selected
                    # state's FIPS code...
                    if row[0] == dict_StateName_StateFIPs.get(
                            self.stringState_Name.get()):

                        # If the feature's county name matches the user-selected
                        # county name within the matching state FIPS code...
                        if row[1] == self.stringCounty_Name.get():

                            # Do nothing, leave that record within the feature
                            # class.
                            pass

                        else:

                            # Delete the feature from the feature class, as it
                            # is not a match.
                            cursor.deleteRow()

                    else:

                        # Else, delete the feature as the state FIPS code does
                        # not match the user-selected state.
                        cursor.deleteRow()

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(self.stringCounty_Name.get() + ", " +
                                        self.stringState_Name.get() +
                                        " extracted from Feature Class.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(56)

            # Set workspace for the following tasks.
            arcpy.env.workspace = fileGDB_Path

            # Set naming convention variable for projecting Census feature
            # class.
            self.featureClass_Polygons_Projected = \
                self.featureClass_County_State_Naming + "_Projected"

            self.func_Scroll_setOutputText("Projecting feature class to PCS " +
                    pcsReferenceString +
                    " with Central Meridian Offset (-30.0 degrees)...", None)

            # Project the Census feature class to the designated PCS as a new
            # feature class within the File GDB.
            arcpy.Project_management(self.featureClass_County_State_Naming,
                                     self.featureClass_Polygons_Projected,
                                     pcsReference)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("PCS Projection to " +
                                           pcsReferenceString + " completed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(57)

            self.func_Scroll_setOutputText(
                "Recalculating extent for feature class...", None)

            # Recalculate extent of the projected Census feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                self.featureClass_Polygons_Projected)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class extent recalculated.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(58)

            self.func_Scroll_setOutputText("Deleting feature class " +
                                        self.featureClass_County_State_Naming  +
                                        " from File GDB...", None)

            # Delete the original, pre-projected Census feature class from the
            # File GDB. It is no longer needed.
            arcpy.Delete_management(self.featureClass_County_State_Naming )

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Feature class deleted from File GDB.", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(59)

            self.func_Scroll_setOutputText("Renaming feature class " +
                                self.featureClass_Polygons_Projected +
                                " back to " +
                                self.featureClass_County_State_Naming + "...",
                                None)

            # Rename the projected Census feature class to the original naming
            # convention of the feature class that was just deleted.
            arcpy.Rename_management(self.featureClass_Polygons_Projected,
                                    self.featureClass_County_State_Naming)

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText("Feature class has been renamed.",
                                           None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(60)

        except arcpy.ExecuteError:

            # Display geoprocessing error messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

        except Exception as e:

            # Display error messages for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_FeatureClass_Clip(self, inputFC, clipFC, outputFC_Name):

        # This function controls the processes involved with clipping the
        # earthquake point feature class to the user-selected Census polygon
        # boundary feature class.

        try:

            # Set the workspace to the File GDB for the following tasks.
            arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

            # Set a new variable name for clipping based on this argument.
            self.clipped_Output_FeatureClass = outputFC_Name

            # If the user selects USA...
            if self.radioButton_Selection == 1:

                # Display this particular message before executing the clip.
                self.func_Scroll_setOutputText(
                    "Clipping earthquake features to 50 states and DC...", None)

            # If the user selects State...
            elif self.radioButton_Selection == 2:

                # Display this particular message before executing the clip.
                self.func_Scroll_setOutputText(
                    "Clipping earthquake features to state selection(" +
                    self.stringState_Name.get() + ")...", None)

            # If the user selects County...
            elif self.radioButton_Selection == 3:

                # Display this particular message before executing the clip.
                self.func_Scroll_setOutputText(
                    "Clipping earthquake features to " +
                    self.stringCounty_Name.get() + ", " +
                    self.stringState_Name.get() + "...", None)

            # Perform a clip of the earthquake point features to the specified
            # polygon boundary.
            arcpy.Clip_analysis(inputFC, clipFC,
                                self.clipped_Output_FeatureClass)

            # Display geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            # If the user selects USA...
            if self.radioButton_Selection == 1:

                # Display this particular message after executing the clip.
                self.func_Scroll_setOutputText("Earthquake features have been "
                                        "clipped to 50 states and DC.", None)

            # If the user selects State...
            if self.radioButton_Selection == 2:

                # Display this particular message after executing the clip.
                self.func_Scroll_setOutputText("Earthquake features have been "
                                               "clipped to state selection(" +
                                               self.stringState_Name.get() +
                                               ").", None)

            # If the user selects County...
            if self.radioButton_Selection == 3:

                # Display this particular message after executing the clip.
                self.func_Scroll_setOutputText("Earthquake features have been "
                                "clipped to " + self.stringCounty_Name.get() +
                                ", " + self.stringState_Name.get() + ".", None)

            # Increment progress bar.
            self.func_ProgressBar_setProgress(64)

        except arcpy.ExecuteError:

            # Display geoprocessing-specific errors.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

        except Exception as e:

            # Display all other types of errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Check_If_Empty_Output_FeatureClass(self,
                                                clipped_FeatureClass_Points):

        # This function controls the processes that check to ensure the clipped
        # earthquake point feature class have features once clipped.

        # Set workspace to File GDB.
        arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

        # Get the feature count of the input argument and assign to count
        # variable.
        self.earthquakeCountResult = \
            arcpy.GetCount_management(clipped_FeatureClass_Points)

        # Store the integer version of the earthquake count to variable.
        self.clipped_earthquakeCount = \
            int(self.earthquakeCountResult.getOutput(0))

        # If user selects USA...
        if self.radioButton_Selection == 1:

            # Display this particular message with earthquake count value.
            self.func_Scroll_setOutputText(str(self.clipped_earthquakeCount) +
            " earthquake features observed within the 50 states and DC.", None)

        # If user selects State...
        if self.radioButton_Selection == 2:

            # Display this particular message with earthquake count value.
            self.func_Scroll_setOutputText(str(self.clipped_earthquakeCount) +
                                    " earthquake features observed within " +
                                    self.stringState_Name.get() + ".", None)

        # If user selects County...
        if self.radioButton_Selection == 3:

            # Display this particular message with earthquake count value.
            self.func_Scroll_setOutputText(str(self.clipped_earthquakeCount) +
                                    " earthquake features observed within " +
                                    self.stringCounty_Name.get() + ", " +
                                    self.stringState_Name.get() + ".", None)

        # Increment progress bar.
        self.func_ProgressBar_setProgress(67)

        # Pause script for one second.
        sleep(1)

        # If zero earthquake features present within the feature class...
        if self.clipped_earthquakeCount < 1:

            # Display this message and error message to the user, since the
            # script can't proceed any farther.
            self.func_Scroll_setOutputText("1 or fewer earthquake features "
                        "present within the timespan/magnitude/location.\n" +
                        "Unable to continue with analysis.", color_Red)

            messagebox.showerror(errorMessage_Header,
                                 "No earthquake features present within the "
                                 "timespan/magnitude/location.\n" +
                                 "Unable to continue with analysis.")

            # Re-enable all selectable buttons and drop-down lists.
            self.func_Enable_Buttons()

            # Stop the status bar.
            self.func_StopStatusBar()

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

            # Calculate total script processing time.
            self.func_Calculate_Script_Time()

            # Save all scroll box text to file.
            self.func_Scroll_saveOutputText()

            # Exit the process.
            exit()

    def func_Controls_For_Analysis_Options(self, featureClass_Mask):

        # This function controls the analysis geoprocessing options, if selected
        # by the user.

        # Set the initial progress bar value for all analyses to the following
        # value. As each analysis completes, the value will be incremented by
        # three percent.
        self.analysis_Percentage_Counter = 67

        try:

            # If the user chooses to output the count results to CSV file...
            if self.statusAnalysis_OutputToCSVFile.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                self.func_Scroll_setOutputText(
                    "Compiling count results to CSV file...", None)

                # If the user selects USA clipping option...
                if self.radioButton_Selection == 1:

                    # Perform spatial join of clipped earthquake feature class
                    # and the USA polygon feature class. Store output in_memory.
                    arcpy.SpatialJoin_analysis(self.clipped_Output_FeatureClass,
                                            featureClass_50States_and_DC_only,
                                            "in_memory/SpatialJoin")

                    # Create/Open a new CSV file within the CSV subfolder for
                    # data counts to be written into.
                    csvFile = open(self.csvDirectory + "DataCounts_" +
                                   self.nameFeatureClass_FromCSV +
                                   self.folderNamingAddition + fileExtCSV, "w")

                    # If timespan and magnitude drop-downs don't show Custom...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # If timespan drop-down shows Custom and magnitude doesn't..
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # WRite the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                        self.textCustomMonthFrom.zfill(2) +
                                        "-" + self.textCustomYearTo +
                                        self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # If timespan and magnitude drop-downs both show Custom...
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                      self.textCustomMonthFrom.zfill(2) +
                                      "-" + self.textCustomYearTo +
                                      self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # If timespan drop-down doesn't show Custom and Magnitude
                    # does...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() == "Custom...":

                        #Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                    self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # Now write the following lines, regardless of
                    # timespan/magnitude selection.
                    csvFile.write("\n")
                    csvFile.write("Worldwide Earthquakes:," +
                                  str(self.worldwide_earthquake_count) + ",\n")
                    csvFile.write("USA (and DC) Earthquakes:," +
                                  str(self.clipped_earthquakeCount) + ",\n")
                    csvFile.write("\n")
                    csvFile.write("Nationwide Earthquake Data,\n")
                    csvFile.write("V,V,V,V,V,\n")
                    csvFile.write("Minimum Magnitude,Maximum Magnitude,"
                                  "Mean Magnitude,Median Magnitude,"
                                  "Mode Magnitude,\n")

                    # Create empty list to store all US magnitude values.
                    magList_US = []

                    # Open the in_memory spatial join as a Search Cursor,
                    # with analysis fields set to FIPS code and magnitude.
                    with arcpy.da.SearchCursor("in_memory/SpatialJoin",
                                            [census_Shapefile_Field_StateFIPS,
                                             analysis_Mag_Field]) as cursor:

                        # For each feature within the spatial join...
                        for row in cursor:

                            # Add the magnitude to the US list.
                            magList_US.append(row[1])

                    try:

                        # Calculate mode of all magnitudes within US list.
                        modeValue_US = mode(magList_US)

                        # Convert mode information to float and then to
                        # string with two decimal places.
                        modeString_US = \
                            str("{0:.2f}".format(float(modeValue_US)))

                    except StatisticsError:

                        # This catches any lists containing no mode.
                        # This will occur if all values within list are
                        # unique values.

                        # Assign mode to the following phrase.
                        modeString_US = "No Unique Mode"

                        pass

                    # Write the following data to the data counts CSV.
                    # Min mag, max mag, mean mag, median mag, and mode mag.
                    csvFile.write(str(min(magList_US)) + "," +
                            str(max(magList_US)) + "," +
                            str("{0:.2f}".format(numpy.mean(magList_US)) + "," +
                            str("{0:.2f}".format(numpy.median(magList_US))) +
                            "," + modeString_US + "," + ",\n"))

                    csvFile.write("\n")
                    csvFile.write("Earthquake Data per State,\n")
                    csvFile.write("V,V,V,V,V,V,V,V,\n")
                    csvFile.write("States with Earthquakes,Earthquake Count,"
                                  "Minimum Magnitude,Maximum Magnitude,"
                                  "Mean Magnitude,Median Magnitude,"
                                  "Mode Magnitude,State FIPS Code,\n")

                    # Create empty list for storing earthquake/magnitude values.
                    magList_State = []

                    # For each state value in the ordered dictionary...
                    for key in dictKeys_OrderedDict_StateNames:

                        # Set counter to zero, for counting earthquakes within
                        # each state during loop.
                        counter = 0

                        # Clears magList_State after each state count has
                        # concluded.
                        magList_State.clear()

                        # Open the in_memory spatial join as a Search Cursor,
                        # with analysis fields set to FIPS code and magnitude.
                        with arcpy.da.SearchCursor("in_memory/SpatialJoin",
                                            [census_Shapefile_Field_StateFIPS,
                                             analysis_Mag_Field]) as cursor:

                            # For each feature within the spatial join...
                            for row in cursor:

                                # If FIPS code matches a state in the ordered
                                # dictionary...
                                if row[0] == \
                                        dictKeys_OrderedDict_StateNames[key]:

                                    # Append row information to magList_State.
                                    magList_State.append(row[1])

                                    # Increment counter by one.
                                    counter = counter + 1

                        # If counter is greater than zero...
                        if counter > 0:

                            try:

                                # Calculate mode of all magnitudes within list.
                                modeValue_State = mode(magList_State)

                                # Convert mode information to float and then to
                                # string with two decimal places.
                                modeString_State = \
                                    str("{0:.2f}".format(
                                        float(modeValue_State)))

                            except StatisticsError:

                                # This catches any lists containing no mode.
                                # This will occur if all values within list are
                                # unique values.

                                # Assign mode  to the following phrase.
                                modeString_State = "No Unique Mode"

                                pass

                            # Write the following data to the data counts CSV.
                            # State name, how many earthquakes, min mag, max
                            # mag, mean mag, median mag, mode mag, and FIPs.
                            csvFile.write(str(key) + "," + str(counter) +
                                "," + str(min(magList_State)) + "," +
                                str(max(magList_State)) + "," +
                                str("{0:.2f}".format(
                                    numpy.mean(magList_State)) + "," +
                                str("{0:.2f}".format(
                                    numpy.median(magList_State))) + "," +
                                modeString_State + "," +
                                str(dictKeys_OrderedDict_StateNames[key]) +
                                ",\n"))

                    # Close the data counts CSV file.
                    csvFile.close()

                # If the user selects State clipping option...
                if self.radioButton_Selection == 2:

                    # Import the tuples and dictionaries affiliated with states
                    # and counties.
                    import GUI_CountiesPerState

                    # Execute function to obtain total earthquake count within
                    # the US.
                    self.func_CSV_DataCount_Nationwide_Count()

                    # Perform spatial join of clipped earthquake feature class
                    # and State polygon feature class. Store output in_memory.
                    arcpy.SpatialJoin_analysis(self.clipped_Output_FeatureClass,
                                        self.featureClass_State_Selection_Only,
                                        "in_memory/SpatialJoin")

                    # Create/Open a new CSV file within the CSV subfolder for
                    # data counts to be written into.
                    csvFile = open(self.csvDirectory + "DataCounts_" +
                                   self.nameFeatureClass_FromCSV +
                                   self.folderNamingAddition + fileExtCSV, "w")

                    # If timespan and magnitude drop-downs don't show Custom...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # If timespan drop-down shows Custom and magnitude drop-down
                    # doesn't show Custom...
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                      self.textCustomMonthFrom.zfill(2) +
                                      "-" + self.textCustomYearTo +
                                      self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # If timespan drop-down shows Custom and magnitude drop-down
                    # shows Custom...
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                      self.textCustomMonthFrom.zfill(2) +
                                      "-" + self.textCustomYearTo +
                                      self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # If timespan drop-down doesn't show Custom and magnitude
                    # drop-down shows Custom...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                    self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # Now write the following lines, regardless of
                    # timespan/magnitude selection.
                    csvFile.write("\n")
                    csvFile.write("Worldwide Earthquakes:," +
                                  str(self.worldwide_earthquake_count) + ",\n")
                    csvFile.write("USA (and DC) Earthquakes:," +
                                  str(self.usa_earthquake_count) + ",\n")
                    csvFile.write("\n")
                    csvFile.write("State Earthquakes - " +
                                  str(self.stringState_Name.get()) +
                                  " (FIPS: " +
                                  str(dictKeys_OrderedDict_StateNames[
                                          self.stringState_Name.get()]) +
                                  "):," + str(self.clipped_earthquakeCount) +
                                  ",\n")
                    csvFile.write("\n")
                    csvFile.write("Statewide Earthquake Data,\n")
                    csvFile.write("V,V,V,V,V,\n")
                    csvFile.write("Minimum Magnitude,Maximum Magnitude,"
                                  "Mean Magnitude,Median Magnitude,"
                                  "Mode Magnitude,\n")

                    # Create empty list to store all state magnitude values.
                    magList_State = []

                    # Open the in_memory spatial join as a Search Cursor,
                    # with analysis fields set to FIPS code and magnitude.
                    with arcpy.da.SearchCursor("in_memory/SpatialJoin",
                                            [census_Shapefile_Field_CountyName,
                                                analysis_Mag_Field]) as cursor:

                        # For each feature within the spatial join...
                        for row in cursor:

                            # Add the magnitude to the state list.
                            magList_State.append(row[1])

                    try:

                        # Calculate mode of all magnitudes within state list.
                        modeValue_State = mode(magList_State)

                        # Convert mode information to float and then to
                        # string with two decimal places.
                        modeString_State = \
                            str("{0:.2f}".format(float(modeValue_State)))

                    except StatisticsError:

                        # This catches any lists containing no mode.
                        # This will occur if all values within list are
                        # unique values.

                        # Assign mode to the following phrase.
                        modeString_State = "No Unique Mode"

                        pass

                    # Write the following data to the data counts CSV.
                    # Min mag, max mag, mean mag, median mag, and mode mag.
                    csvFile.write(str(min(magList_State)) + "," +
                            str(max(magList_State)) + "," +
                            str("{0:.2f}".format(numpy.mean(magList_State)) +
                            "," +
                            str("{0:.2f}".format(numpy.median(magList_State))) +
                            "," + modeString_State + "," + ",\n"))

                    csvFile.write("\n")
                    csvFile.write("Earthquake Data per County\n")
                    csvFile.write("V,V,V,V,V,V,V,\n")
                    csvFile.write("Counties with Earthquakes,Earthquake Count,"
                                  "Minimum Magnitude,Maximum Magnitude,"
                                  "Mean Magnitude,Median Magnitude,"
                                  "Mode Magnitude,\n")

                    # Create empty list for storing earthquake/magnitude values.
                    magList_County = []

                    # For each county list within state/county dictionary
                    # matching the state drop-down selection...
                    for key in GUI_CountiesPerState.dict_state_counties[
                        self.stringState_Name.get()]:

                        # Set counter to zero, for counting earthquakes within
                        # each state during loop.
                        counter = 0

                        # Clears magList after each state count has concluded.
                        magList_County.clear()

                        # Open the in_memory spatial join as a Search Cursor,
                        # with analysis fields set to county name and magnitude.
                        with arcpy.da.SearchCursor("in_memory/SpatialJoin",
                                            [census_Shapefile_Field_CountyName,
                                                analysis_Mag_Field]) as cursor:

                            # For each feature within the spatial join...
                            for row in cursor:

                                # If the county name matches a county name
                                # within the state/county dictionary....
                                if row[0] == key:

                                    # Append row information to magList.
                                    magList_County.append(row[1])

                                    # Increment counter by one.
                                    counter = counter + 1

                        # If row counter is greater than zero...
                        if counter > 0:

                            try:

                                # Calculate mode of all magnitudes within list.
                                modeValue_County = mode(magList_County)

                                # Convert mode information to float and then to
                                # string with two decimal places.
                                modeString_County = \
                                    str("{0:.2f}".format(
                                        float(modeValue_County)))

                            except StatisticsError:

                                # This catches any lists containing no mode.
                                # This will occur if all values within list are
                                # unique values.

                                # Assign modeString to the following phrase.
                                modeString_County = "No Unique Mode"

                                pass

                            # Write the following data to the data counts CSV.
                            # County name, how many earthquakes, min mag, max
                            # mag, mean mag, median mag, and mode mag.
                            csvFile.write(str(key) + ", " + str(counter) +
                                "," + str("{0:.2f}".format(
                                min(magList_County))) +
                                "," + str("{0:.2f}".format(
                                max(magList_County))) +
                                "," +
                                str("{0:.2f}".format(
                                numpy.mean(magList_County))) +
                                "," +
                                str("{0:.2f}".format(
                                numpy.median(magList_County))) +
                                "," + modeString_County +",\n")

                    # Close the data counts CSV file.
                    csvFile.close()

                # If the user selects County clipping option...
                if self.radioButton_Selection == 3:

                    # Import the tuples and dictionaries affiliated with states
                    # and counties.
                    import GUI_CountiesPerState

                    # Execute function to obtain total earthquake count within
                    # the US.
                    self.func_CSV_DataCount_Nationwide_Count()

                    # Execute function to obtain total earthquake count within
                    # the state.
                    self.func_CSV_DataCount_Statewide_Count()

                    # Create/Open a new CSV file within the CSV subfolder for
                    # data counts to be written into.
                    csvFile = open(self.csvDirectory + "DataCounts_" +
                                   self.nameFeatureClass_FromCSV +
                                   self.folderNamingAddition + fileExtCSV, "w")

                    # If timespan and magnitude drop-downs don't show Custom...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                    self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # If timespan drop-down shows Custom and magnitude drop-down
                    # doesn't show Custom...
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() != "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                      self.textCustomMonthFrom.zfill(2) +
                                      "-" + self.textCustomYearTo +
                                      self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                self.stringEarthquakeMagnitude.get() + ",\n")

                    # timespan drop-down shows Custom and magnitude drop-down
                    # shows Custom...
                    if self.stringEarthquakeTimespan.get() == "Custom..." and \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," + self.textCustomYearFrom +
                                      self.textCustomMonthFrom.zfill(2) +
                                      "-" + self.textCustomYearTo +
                                      self.textCustomMonthTo.zfill(2) + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # If timespan drop-down doesn't show Custom and magnitude
                    # drop-down shows Custom...
                    if self.stringEarthquakeTimespan.get() != "Custom..." and \
                            self.stringEarthquakeMagnitude.get() == "Custom...":

                        # Write the following lines into the data counts CSV.
                        csvFile.write("Timespan:," +
                                    self.stringEarthquakeTimespan.get() + ",\n")
                        csvFile.write("Magnitude Range:," +
                                      self.textCustomMagFrom + "-" +
                                      self.textCustomMagTo + ",\n")

                    # Now write the following lines, regardless of
                    # timespan/magnitude selection.
                    csvFile.write("\n")
                    csvFile.write("Worldwide Earthquakes:," +
                                  str(self.worldwide_earthquake_count) + ",\n")
                    csvFile.write("USA (and DC) Earthquakes:," +
                                  str(self.usa_earthquake_count) + ",\n")
                    csvFile.write("State Earthquakes - " +
                        str(self.stringState_Name.get()) + " (FIPS: " +
                        str(dictKeys_OrderedDict_StateNames[
                                self.stringState_Name.get()]) + "):," +
                                  str(self.state_earthquake_count) + ",\n")
                    csvFile.write("\n")
                    csvFile.write("County Earthquakes - " +
                                  self.stringCounty_Name.get() + ":," +
                                  str(self.clipped_earthquakeCount) + ",\n")
                    csvFile.write("\n")
                    csvFile.write("County Earthquake Data\n")
                    csvFile.write("V,V,V,V,V,\n")
                    csvFile.write("Minimum Magnitude,Maximum Magnitude,"
                                  "Mean Magnitude,Median Magnitude,"
                                  "Mode Magnitude,\n")

                    # Create empty list for storing earthquake/magnitude values.
                    magList = []

                    # For each county list within state/county dictionary
                    # matching the state drop-down selection...
                    for key in GUI_CountiesPerState.dict_state_counties[
                                                self.stringState_Name.get()]:

                        # Set counter to zero, for counting earthquakes within
                        # each county during loop.
                        counter = 0

                        # Clears magList after each county count has concluded.
                        magList.clear()

                        # Open the in_memory spatial join as a Search Cursor,
                        # with analysis fields set to county name and magnitude.
                        with arcpy.da.SearchCursor("in_memory/SpatialJoin",
                                        [census_Shapefile_Field_CountyName,
                                        analysis_Mag_Field]) as cursor:

                            # For each feature within the spatial join...
                            for row in cursor:

                                # If the county name matches a county name
                                # within the state/county dictionary...
                                if row[0] == key:

                                    # Append row information to magList.
                                    magList.append(row[1])

                                    # Increment counter by one.
                                    counter = counter + 1

                        # If row counter is greater than zero...
                        if counter > 0:

                            try:

                                # Calculate mode of all magnitudes within list.
                                modeValue = mode(magList)

                                # Convert mode information to float and then to
                                # string with two decimal places.
                                modeString = \
                                    str("{0:.2f}".format(float(modeValue)))

                            except StatisticsError:

                                # This catches any lists containing no mode.
                                # This will occur if all values within list are
                                # unique.

                                #Assign modeString to the following phrase.
                                modeString = "No Unique Mode"

                                pass

                            # Write the following data to the data counts CSV.
                            # Min mag, max mag, mean mag, median mag, and
                            # mode mag.
                            csvFile.write(str("{0:.2f}".format(min(magList))) +
                                "," + str("{0:.2f}".format(max(magList))) +
                                "," +
                                str("{0:.2f}".format(numpy.mean(magList))) +
                                "," +
                                str("{0:.2f}".format(numpy.median(magList))) +
                                "," + modeString + ",\n")

                    # Close the data counts CSV file.
                    csvFile.close()

                # Clear any intermediate output from memory.
                self.func_Clear_InMemory()

                self.func_Scroll_setOutputText("Count results successfully "
                                               "written to CSV file.", None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(
                "Output CSV was not written successfully.", color_Red)

            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

        try:

            # If the user selects the IDW analysis...
            if self.statusAnalysis_IDW.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing IDW Analysis on all "
                                    "points, then clipping/masking output to " +
                                    featureClass_Mask + " extent...", None)

                # Point Density parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                required_ZField = analysis_Mag_Field
                optional_CellSize = None
                optional_Power = None
                optional_SearchRadius = None

                # Perform the IDW analysis.
                output_IDW = arcpy.sa.Idw(required_InputFile, required_ZField,
                                            optional_CellSize, optional_Power,
                                            optional_SearchRadius)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                self.func_Scroll_setOutputText("Masking IDW results...", None)

                # Mask the IDW results.
                output_IDW_with_Mask = arcpy.sa.ExtractByMask(
                    output_IDW, featureClass_Mask)

                # Save the masked IDW feature class results to File GDB.
                output_IDW_with_Mask.save(
                    "idw_" + self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText("IDW Analysis completed.", None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self. analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script by one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

        try:

            # If the user selects the Kernel Density analysis...
            if self.statusAnalysis_KernelDensity.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Kernel Density "
                    "Analysis on all points, then clipping/masking output to " +
                    featureClass_Mask + " extent...", None)

                # Kernel Density parameters, with optional parameters set to
                # None for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                optional_PopField = None
                optional_CellSize = None
                optional_SearchRadius = None
                optional_AreaUnitScaleFactor = None
                optional_OutputCellValues = None
                optional_Method = None

                # Perform the Kernel Density analysis.
                output_KernelDensity = arcpy.sa.KernelDensity(
                    required_InputFile, optional_PopField, optional_CellSize,
                    optional_SearchRadius, optional_AreaUnitScaleFactor,
                    optional_OutputCellValues, optional_Method)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                # Mask the Kernel Density results.
                output_KernelDensity_with_Mask = arcpy.sa.ExtractByMask(
                    output_KernelDensity, featureClass_Mask)

                self.func_Scroll_setOutputText(
                    "Masking Kernel Density results...", None)

                # Save the masked Kernel Density feature class results to
                # File GDB.
                output_KernelDensity_with_Mask.save("kerneldensity_" +
                                            self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText(
                    "Kernel Density Analysis completed.", None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

        try:

            # If the user selects the Kriging analysis...
            if self.statusAnalysis_Kriging.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Kriging Analysis on "
                                "all points, then clipping/masking output to " +
                                featureClass_Mask + " extent...", None)

                # Kriging parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                required_ZField = analysis_Mag_Field
                optional_KrigingModel = None
                optional_CellSize = None
                optional_SearchRadius = None
                optional_OutputVariancePredictionRaster = None

                # Perform the Kriging analysis.
                output_Kriging = arcpy.sa.Kriging(required_InputFile,
                                    required_ZField, optional_KrigingModel,
                                    optional_CellSize, optional_SearchRadius,
                                    optional_OutputVariancePredictionRaster)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                # Mask the Kriging results.
                output_Kriging_with_Mask = arcpy.sa.ExtractByMask(
                    output_Kriging, featureClass_Mask)

                self.func_Scroll_setOutputText("Masking Kriging results...",
                                               None)

                # Save the masked Kriging results to File GDB.
                output_Kriging_with_Mask.save(
                    "kriging_" + self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText("Kriging Analysis completed.",
                                               None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

        try:

            # If the user selects the Natural Neighbor analysis...
            if self.statusAnalysis_NaturalNeighbor.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                # If the total number of earthquake features reach 14,750,000...
                if self.worldwide_earthquake_count >= 14750000:

                    # Display this message, as the geoprocessing tool will fail
                    # if the total number approaches 15 million records (Esri).
                    self.func_Scroll_setOutputText(
                        "UNABLE TO EXECUTE NATURAL NEIGHBOR ANALYSIS:\n" +
                        "According to Esri, this analysis will fail if the "
                        "input earthquake count nears 15,000,000.\n" +
                        "Skipping this analysis...", color_Red)

                else:
                    # Else, perform the analysis.
                    self.func_Scroll_setOutputText("Performing Natural "
                                        "Neighbor Analysis on all points, "
                                        "then clipping/masking output to " +
                                        featureClass_Mask + " extent...", None)

                    # Natural Neighbor parameters, with optional parameters set
                    # to None for Esri defaults.
                    required_InputFile = self.clipped_Output_FeatureClass
                    required_ZField = analysis_Mag_Field
                    optional_CellSize = None

                    # Perform the Natural Neighbor analysis.
                    output_NaturalNeighbor = arcpy.sa.NaturalNeighbor(
                        required_InputFile, required_ZField, optional_CellSize)

                    # Get geoprocessing messages.
                    self.func_Scroll_setOutputText(arcpy.GetMessages(0),
                                                   color_Blue)

                    # Pause script for one second.
                    sleep(1)

                    # Mask the Natural Neighbor results.
                    output_NaturalNeighbor_with_Mask = arcpy.sa.ExtractByMask(
                        output_NaturalNeighbor, featureClass_Mask)

                    self.func_Scroll_setOutputText(
                        "Masking Natural Neighbor results...", None)

                    # Save masked results to the File GDB.
                    output_NaturalNeighbor_with_Mask.save(
                        "naturalneighbor_" + self.clipped_Output_FeatureClass)

                    # Get geoprocessing messages.
                    self.func_Scroll_setOutputText(arcpy.GetMessages(0),
                                                   color_Blue)

                    self.func_Scroll_setOutputText(
                        "Natural Neighbor Analysis completed.", None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

        try:

            # If the user selects the Optimized Hot Spot analysis...
            if self.statusAnalysis_OptHotSpot.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                # Static Optimized Hot Spot Analysis parameters, with optional
                # parameters set to None for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                optional_IncidentDataAggregationMethod = None
                optional_BoundingPolygons = None
                optional_PolygonsForAggregatingIncidents = None
                optional_DensitySurface = None

                # If the clipped earthquake count is less than 30 features...
                if self.clipped_earthquakeCount < 30:

                    # Display the following message and skip, as a minimum of
                    # 30 samples is required (per Esri) when the analysis field
                    # option is set with a value.
                    self.func_Scroll_setOutputText(
                        "UNABLE TO EXECUTE OPTIMIZED HOT SPOT ANALYSIS (WITH"
                        " ANALYSIS FIELD OPTION):\n" +
                        "According to Esri, this analysis requires a minimum of"
                        " 30 earthquakes within the sampling area.\n" +
                        "Skipping this analysis...", color_Red)

                else:

                    # Else, perform the analysis.
                    self.func_Scroll_setOutputText(
                        "Performing Optimized Hot Spot Analysis on all points "
                        "(analysis field = 'mag'), with output clipped to " +
                        featureClass_Mask + " extent...", None)

                    # Output file name with Analysis Field option.
                    # A temporary workspace is assigned for intermediate output.
                    required_InputFile = self.clipped_Output_FeatureClass
                    required_OutputFile_WithMagField = "in_memory/tempInput_Mag"

                    # Analysis Field option reset to analysis_Mag_Field.
                    optional_AnalysisField = analysis_Mag_Field

                    # Please note: Some sort of "bug" occurs when the Optimized
                    # Hot Spot Analysis is conducted here with an Analysis Field
                    # utilized. A feature class lock will persist on the input
                    # file, even when the geoprocessing script has concluded.
                    # This will not occur when the Analysis Field option is left
                    # blank, however. The lock was causing issues with later
                    # tasks within the script. Numerous attempts were made to
                    # find the root cause of the issue, but the solution
                    # presented is discussed farther down within this function
                    # block.
                    arcpy.OptimizedHotSpotAnalysis_stats(required_InputFile,
                                required_OutputFile_WithMagField,
                                optional_AnalysisField,
                                optional_IncidentDataAggregationMethod,
                                optional_BoundingPolygons,
                                optional_PolygonsForAggregatingIncidents,
                                optional_DensitySurface)

                    # Display geoprocessing output messages.
                    self.func_Scroll_setOutputText(arcpy.GetMessages(0),
                                                   color_Blue)

                    self.func_Scroll_setOutputText("Optimized Hot Spot Analysis"
                                    " on all points (analysis field = '" +
                                    analysis_Mag_Field + "') completed.", None)

                    self.func_Scroll_setOutputText("Clipping Optimized Hot Spot"
                                    " Analysis (analysis field = '" +
                                    analysis_Mag_Field + "') results...", None)

                    # The intermediate output feature class is clipped to the
                    # predetermined feature class mask and saved as a new
                    # feature class.
                    arcpy.Clip_analysis(required_OutputFile_WithMagField,
                                        featureClass_Mask,
                                        "opthotspot_" + analysis_Mag_Field +
                                        "AnalysisField_" + \
                                        self.clipped_Output_FeatureClass)

                    # Get geoprocessing messages.
                    self.func_Scroll_setOutputText(arcpy.GetMessages(0),
                                                   color_Blue)

                    self.func_Scroll_setOutputText("Clipping for Optimized Hot "
                                "Spot Analysis (analysis field = '" +
                                analysis_Mag_Field + "') completed.", None)

                    # Pause script for one second.
                    sleep(1)

                # Begin the second iteration of the same analysis WITHOUT an
                # analysis field set as an input parameter.

                # If the clipped earthquake count is less than 60 features...
                if self.clipped_earthquakeCount < 60:

                    # Display the following message and skip, as a minimum of
                    # 60 samples is required (per Esri) when the analysis field
                    # option is not used.
                    self.func_Scroll_setOutputText(
                        "UNABLE TO EXECUTE OPTIMIZED HOT SPOT ANALYSIS (WITHOUT"
                        " ANALYSIS FIELD OPTION):\n" +
                        "According to Esri, this analysis requires a minimum of"
                        " 60 earthquakes within the sampling area.\n" +
                        "Skipping this analysis...", color_Red)

                else:

                    # As previously discussed, the Analysis Field option was
                    # causing a feature class lock on the input feature class.
                    # The most suitable way to fix this issue was to re-run
                    # the Optimized Hot Spot Analysis tool WITHOUT an Analysis
                    # Field option set. The following geoprocessing tool causes
                    # the lock to disappear from the feature class, which allows
                    # the rest of the script to function properly. As a result,
                    # the user will have two outputs for the Optimized Hot Spot
                    # Analysis.
                    self.func_Scroll_setOutputText("Performing Optimized Hot "
                            "Spot Analysis on all points (no analysis field), "
                            "with output clipped to " + featureClass_Mask +
                            " extent...", None)

                    # Changed output file name without Analysis Field option.
                    # A temporary workspace is assigned for intermediate output.
                    required_OutputFile_WithoutMagField = \
                        "in_memory/tempInput_noMag"

                    # Analysis Field option reset to None.
                    optional_AnalysisField = None

                    # ArcPy runs the amended Optimized Hot Spot Analysis
                    arcpy.OptimizedHotSpotAnalysis_stats(required_InputFile,
                                    required_OutputFile_WithoutMagField,
                                    optional_AnalysisField,
                                    optional_IncidentDataAggregationMethod,
                                    optional_BoundingPolygons,
                                    optional_PolygonsForAggregatingIncidents,
                                    optional_DensitySurface)

                    # Display geoprocessing output messages.
                    self.func_Scroll_setOutputText(
                        arcpy.GetMessages(0), color_Blue)

                    self.func_Scroll_setOutputText("Optimized Hot Spot Analysis"
                        " on all points (no analysis field) completed.", None)

                    self.func_Scroll_setOutputText("Clipping Optimized Hot Spot"
                            " Analysis (no analysis field) results...", None)

                    # The intermediate output feature class is clipped to the
                    # predetermined feature class mask and saved as a new
                    # feature class.
                    arcpy.Clip_analysis(required_OutputFile_WithoutMagField,
                                        featureClass_Mask,
                                            "opthotspot_noAnalysisField_" + \
                                            self.clipped_Output_FeatureClass)

                    # Get geoprocessing messages.
                    self.func_Scroll_setOutputText(
                        arcpy.GetMessages(0), color_Blue)

                    self.func_Scroll_setOutputText("Clipping for Optimized Hot "
                        "Spot Analysis (no analysis field) completed.", None)

                # Clear any intermediate output from memory.
                self.func_Clear_InMemory()

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                                        self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        try:

            # If the user selects the Point Density analysis...
            if self.statusAnalysis_PointDensity.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Point Density "
                                "Analysis on all points, then clipping/masking "
                                "output to " + featureClass_Mask + " extent...",
                                None)

                # Point Density parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                optional_PopField = None
                optional_CellSize = None
                optional_NeighborhoodType = None
                optional_AreaUnitScalFactor = None

                # Execute Point Density analysis with default Esri values.
                output_PointDensity = arcpy.sa.PointDensity(required_InputFile,
                                        optional_PopField, optional_CellSize,
                                        optional_NeighborhoodType,
                                        optional_AreaUnitScalFactor)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                # Mask the Point Density results.
                output_PointDensity_with_Mask = \
                    arcpy.sa.ExtractByMask(output_PointDensity,
                                           featureClass_Mask)

                self.func_Scroll_setOutputText(
                    "Masking Point Density results...", None)

                # Save the masked results to the File GDB.
                output_PointDensity_with_Mask.save("pointdensity_" +
                                            self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText(
                    "Point Density Analysis completed.", None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

        try:

            # If the user selects the Spline analysis...
            if self.statusAnalysis_Spline.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Spline Analysis on "
                                "all points, then clipping/masking output to " +
                                featureClass_Mask + " extent...", None)

                # Spline parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                required_ZField = analysis_Mag_Field
                optional_CellSize = None
                optional_SplineType = None
                optional_Weight = None
                optional_PointNumber = None

                # Execute Spline Analysis with default Esri values.
                output_Spline = arcpy.sa.Spline(required_InputFile,
                                required_ZField, optional_CellSize,
                                optional_SplineType, optional_Weight,
                                optional_PointNumber)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                # Mask the Spline results.
                output_Spline_with_Mask = arcpy.sa.ExtractByMask(output_Spline,
                                                          featureClass_Mask)

                self.func_Scroll_setOutputText("Masking Spline results...",
                                               None)

                # Save the masked results to File GDB.
                output_Spline_with_Mask.save("spline_" +
                                             self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText("Spline Analysis completed.",
                                               None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Clear any intermediate output from memory.
                self.func_Clear_InMemory()

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        try:

            # If the user selects the Thiessen analysis...
            if self.statusAnalysis_Thiessen.get() == 1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Thiessen Polygon "
                            "Analysis on all points, with output clipped to " +
                            featureClass_Mask + " extent...", None)

                # Thiessen parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                required_OutputFile = "in_memory/Thiessen"

                # This is not the Esri default. Parameter set to ALL so all
                # fields would be included with output (for visual reference).
                optional_OutputFields = "ALL"

                # Perform the Thiessen Polygon analysis.
                arcpy.CreateThiessenPolygons_analysis(required_InputFile,
                                    required_OutputFile, optional_OutputFields)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                self.func_Scroll_setOutputText(
                    "Clipping Thiessen Polygon Analysis results...", None)

                # Perform a clip of the Thiessen polygon output and save to the
                # File GDB.
                arcpy.Clip_analysis(required_OutputFile, featureClass_Mask,
                                "thiessen_" + self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText(
                    "Thiessen Polygon Analysis completed.", None)

                # Clear any intermediate output from memory.
                self.func_Clear_InMemory()

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            # Clear any intermediate output from memory.
            self.func_Clear_InMemory()

            pass

        try:

            # If the user selects the Trend analysis...
            if self.statusAnalysis_Trend.get() ==1:

                # Set the workspace for the following analysis.
                arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

                # Set the extent to the input argument feature class mask.
                arcpy.env.extent = featureClass_Mask

                self.func_Scroll_setOutputText("Performing Trend Analysis on "
                            "all points, then clipping/masking output to " +
                            featureClass_Mask + " extent...", None)

                # Trend parameters, with optional parameters set to None
                # for Esri defaults.
                required_InputFile = self.clipped_Output_FeatureClass
                required_ZField = analysis_Mag_Field
                optional_CellSize = None
                optional_Order = None
                optional_RegressionType = None
                optional_OutputRMSFile = None

                # Execute Trend Analysis with default Esri values
                output_Trend = arcpy.sa.Trend(required_InputFile,
                            required_ZField, optional_CellSize, optional_Order,
                            optional_RegressionType, optional_OutputRMSFile)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                # Pause script for one second.
                sleep(1)

                # Mask the Trend results.
                output_Trend_with_Mask = arcpy.sa.ExtractByMask(output_Trend,
                                                            featureClass_Mask)

                self.func_Scroll_setOutputText("Masking Trend results...", None)

                # Save the masked results to the File GDB.
                output_Trend_with_Mask.save("trend_" +
                                            self.clipped_Output_FeatureClass)

                # Get geoprocessing messages.
                self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

                self.func_Scroll_setOutputText("Trend Analysis completed.",
                                               None)

                # Increase current progress bar percentage by three percent.
                self.analysis_Percentage_Counter = \
                    self.analysis_Percentage_Counter + 3

                # Increment progress bar by adjusted value.
                self.func_ProgressBar_setProgress(
                    self.analysis_Percentage_Counter)

                # Pause script for one second.
                sleep(1)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error messages for all other errors and skip failed
            # analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

    def func_CSV_DataCount_Nationwide_Count(self):

        # This function controls the counting of all earthquakes within the US.
        # Used only if state or county clipping option is selected. It will be
        # used within the output data counts CSV file.

        try:

            # Set workspace to File GDB for the following analysis.
            arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

            # Assign Census Shapefile within Shapefile subfolder to variable.
            censusShapefile = self.subFolder_CensusShapefile + "/" + \
                              census_URL_CountyShapefile_FileName + fileExtShp

            # Create Census polygon feature class variable stored within memory.
            memoryFeatureClass_US = "in_memory/" + \
                                    featureClass_50States_and_DC_only

            # Copy Census Shapefile to feature class stored in memory.
            arcpy.CopyFeatures_management(censusShapefile,
                                          memoryFeatureClass_US)

            # Pause script for one second.
            sleep(1)

            # Open the Census in_memory feature class with an Update Cursor.
            with arcpy.da.UpdateCursor(memoryFeatureClass_US,
                                    census_Shapefile_Field_StateFIPS) as cursor:

                # For each feature in the Census in_memory feature class...
                for row in cursor:

                    # This If statement removes non-50 state (and DC) FIPS codes
                    # from the Census feature class. The original polygons
                    # include all US territories.
                    if row[0] == "60" or row[0] == "66" or row[0] == "69" or \
                                    row[0] == "72" or row[0] == "78":

                        # Delete feature from in_memory feature class.
                        cursor.deleteRow()

            # Recalculate the extent of the in_memory feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                memoryFeatureClass_US)

            # Create new feature class variable in_memory for clipped earthquake
            # points.
            clipped_Output_FeatureClass = "in_memory/ClippedOutputFC_US"

            # Perform a clip of raw earthquake points to the 50 US states and DC
            # polygons and store within the clipped feature class in_memory.
            arcpy.Clip_analysis(self.nameFeatureClass_FromCSV,
                                memoryFeatureClass_US,
                                clipped_Output_FeatureClass)

            # Perform a count on the clipped earthquake features found within
            # the in_memory clipped feature class.
            earthquakeCountResult_US = arcpy.GetCount_management(
                clipped_Output_FeatureClass)

            # Store the integer earthquake count as a variable for use within
            # other functions.
            self.usa_earthquake_count = \
                int(earthquakeCountResult_US.getOutput(0))

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(
                "Failure to count for output US CSV values.", color_Red)

            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_CSV_DataCount_Statewide_Count(self):

        # This function controls the counting of all earthquakes within the
        # user-selected state.
        # Used only if county clipping option is selected. It will be
        # used within the output data counts CSV file.

        try:

            # Set workspace to File GDB for the following analysis.
            arcpy.env.workspace = self.subFolder_GIS + "/" + nameFileGDB

            # Assign Census Shapefile within Shapefile subfolder to variable.
            censusShapefile = self.subFolder_CensusShapefile + "/" + \
                                census_URL_CountyShapefile_FileName + fileExtShp

            # Create Census polygon feature class variable stored in memory.
            memoryFeatureClass_State = "in_memory/" + \
                                       self.stringState_Name.get()

            # Copy Census Shapefile to feature class stored in memory.
            arcpy.CopyFeatures_management(censusShapefile,
                                          memoryFeatureClass_State)

            # Pause script for one second.
            sleep(1)

            # Open the Census in_memory feature class with an Update Cursor.
            with arcpy.da.UpdateCursor(memoryFeatureClass_State,
                                    census_Shapefile_Field_StateFIPS) as cursor:

                # For each feature in the Census in_memory feature class...
                for row in cursor:

                    # This If statement removes all state polygon features not
                    # matching the user-selected state FIPS code.
                    if row[0] != \
                    dict_StateName_StateFIPs.get(self.stringState_Name.get()):

                        # Delete feature from in_memory feature class.
                        cursor.deleteRow()

            # Recalculate the extent of the in_memory feature class.
            arcpy.RecalculateFeatureClassExtent_management(
                memoryFeatureClass_State)

            # Create new feature class variable in_memory for clipped earthquake
            # points.
            clipped_Output_FeatureClass = "in_memory/ClippedOutputFC_State"

            # Perform a clip of raw earthquake points to the user-selected state
            # and store output as the clipped in_memory feature class.
            arcpy.Clip_analysis(self.nameFeatureClass_FromCSV,
                                memoryFeatureClass_State,
                                clipped_Output_FeatureClass)

            # Perform a count on the clipped earthquake features found within
            # the in_memory clipped feature class.
            earthquakeCountResult_State = arcpy.GetCount_management(
                clipped_Output_FeatureClass)

            # Store the integer earthquake count as a variable for use within
            # the in_memory clipped feature class.
            self.state_earthquake_count = \
                int(earthquakeCountResult_State.getOutput(0))

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(
                "Failure to count for output state CSV values.", color_Red)

            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Clear_InMemory(self):

        # This function is responsible for clearing any intermediate data output
        # that has been stored in memory as "in_memory".

        try:

            self.func_Scroll_setOutputText(
                "Deleting any intermediary data (in memory)...", None)

            # Delete the in_memory data.
            arcpy.Delete_management("in_memory")

            # Get geoprocessing messages.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Blue)

            self.func_Scroll_setOutputText(
                "Intermediary data (in memory) deleted.", None)

        except arcpy.ExecuteError:

            # Display geoprocessing errors and skip the failed analysis.
            self.func_Scroll_setOutputText(arcpy.GetMessages(0), color_Red)

            pass

        except Exception as e:

            # Display error message for all other errors.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def func_Scroll_saveOutputText(self):

        # This function writes all of the output text found within the
        # ScrolledText widget to a text file located within the user-defined
        # workspace. This is done at the conclusion of every application
        # iteration.

        try:

            # If the output text file's naming convention has been set...
            if self.nameFeatureClass_FromCSV is not None:

                # Create/Open a new text file for all output messages to be
                # written to.
                textFile_ProcessingHistory = open(self.fullPathName + "/" +
                        "ProcessingHistory_" + self.nameFeatureClass_FromCSV +
                                              fileExtText,"w")
            else:

                # If the application throws errors and fails within the early
                # stages, the naming convention for the output text file will
                # not be established. If that is the case, the naming convention
                # will be saved with FAILED in the name.
                textFile_ProcessingHistory = open(self.fullPathName + "/" +
                        "ProcessingHistory_FAILED" + fileExtText, "w")

            # Once the application processes have finished, take all output
            # messages within the scroll box and write to the output text file.
            textFile_ProcessingHistory.write(
                self.scrollBox.get(1.0, tkinter.END))

            # Close the text file.
            textFile_ProcessingHistory.close()

            self.func_Scroll_setOutputText(
                "The processing history (what you see here) "
                "has been logged to a text file "
                "within the user-defined workspace.", None)

            # Increment progress bar to 100 percent.
            self.func_ProgressBar_setProgress(100)

        except Exception as e:

            # Display error message and skip the failed analysis.
            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

            pass

    def func_windowResize(self):

        # This function controls the actions that occur when determining if
        # the GUI window needs to be resized.

        # If the scroll box already exists...
        if self.scrollBoxFrame is not None:

            # Remove the scroll box.
            self.scrollBoxFrame.grid_remove()

        # If the progress bar already exists...
        if self.progressBarFrame is not None:

            # Remove the progress bar.
            self.progressBarFrame.grid_remove()

        # Set the GUI expansion width if the More Options checkbox is selected.
        self.checkboxExpansionWidth = guiWindow_EarthquakeOptions_Width + 300

        # Set the GUI expansion height if timespan/magnitude drop-downs show
        # "Custom...".
        self.customSelection_Height = guiWindow_EarthquakeOptions_Height + 75

        # If the More Options checkbox is not selected and "Custom..." is not
        # selected for both timespan and magnitude...
        if self.statusVar_Checkbutton_Options.get() == 0 and \
                        self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

            # Set the GUI window dimensions accordingly.
            self.winfo_toplevel().geometry("%dx%d" % (
                guiWindow_EarthquakeOptions_Width,
                guiWindow_EarthquakeOptions_Height))

            # If the Custom Magnitude Min/Max drop-down lists are visible...
            if self.comboFrame_Custom_Magnitude is not None:

                # Remove the Custom Magnitude Min/Max drop-down lists.
                self.comboFrame_Custom_Magnitude.grid_remove()

            # If the Custom Timespan From/To drop-down lists are visible...
            if self.comboFrame_Custom_Timespan is not None:

                # Remove the Custom Timespan From/To drop-down lists.
                self.comboFrame_Custom_Timespan.grid_remove()

            # Clear the variable assignment for the State combobox drop-down.
            if self.comboFrame_State is not None:

                self.comboFrame_State = None

            # Clear the variable assignment for the County combobox drop-down.
            if self.comboFrame_Counties is not None:

                self.comboFrame_Counties = None

        # Else if the More Options checkbox is not selected and custom timespan
        # or custom magnitude are selected...
        elif self.statusVar_Checkbutton_Options.get() == 0 and \
                (self.stringEarthquakeTimespan.get() == "Custom..." or
                        self.stringEarthquakeMagnitude.get() == "Custom..."):

            # Set the GUI window dimensions accordingly.
            self.winfo_toplevel().geometry("%dx%d" % (
                guiWindow_EarthquakeOptions_Width,
                self.customSelection_Height))

            # Clear the variable assignment for the State combobox drop-down.
            if self.comboFrame_State is not None:

                self.comboFrame_State = None

            # Clear the variable assignment for the County combobox drop-down.
            if self.comboFrame_Counties is not None:

                self.comboFrame_Counties = None

        # Else if the More Options checkbox is selected and both the custom
        # timespan and custom magnitude are not selected...
        elif self.statusVar_Checkbutton_Options.get() == 1 and \
                        self.stringEarthquakeTimespan.get() != "Custom..." and \
                        self.stringEarthquakeMagnitude.get() != "Custom...":

            # Set the GUI window dimensions accordingly.
            self.winfo_toplevel().geometry("%dx%d" % (
                self.checkboxExpansionWidth,
                guiWindow_EarthquakeOptions_Height))

            # If the Custom Magnitude Min/Max drop-down lists are visible...
            if self.comboFrame_Custom_Magnitude is not None:

                # Remove the Custom Magnitude Min/Max drop-down lists.
                self.comboFrame_Custom_Magnitude.grid_remove()

            # If the Custom Timespan From/To drop-down lists are visible...
            if self.comboFrame_Custom_Timespan is not None:

                # Remove the Custom Timespan From/To drop-down lists.
                self.comboFrame_Custom_Timespan.grid_remove()

        # Else if the More Options checkbox is checked and the custom timespan
        # or custom magnitude are selected...
        elif self.statusVar_Checkbutton_Options.get() == 1 and \
                (self.stringEarthquakeTimespan.get() == "Custom..." or
                         self.stringEarthquakeMagnitude.get() == "Custom..."):

            # Set the GUI window dimensions accordingly.
            self.winfo_toplevel().geometry("%dx%d" % (
                self.checkboxExpansionWidth,
                self.customSelection_Height))

    def func_Enable_Buttons(self):

        # This function controls the enabling of all user-selectable buttons,
        # checkboxes, radio buttons, and drop-down lists. This is used when the
        # application has finished performing all tasks.

        # Enable Magnitude drop-down list.
        self.combo_EarthquakeMagnitude.config(state="readonly")
        self.combo_EarthquakeMagnitude.update()

        # Enable Timespan drop-down list.
        self.combo_EarthquakeTimespan.config(state="readonly")
        self.combo_EarthquakeTimespan.update()

        # Enable the "Browse" button for setting the output workspace.
        self.workspaceFolderButton_FolderDialog.config(state=tkinter.NORMAL)
        self.workspaceFolderButton_FolderDialog.update()

        # Enable the Back button.
        self.buttonBack.config(state=tkinter.NORMAL)
        self.buttonBack.update()

        # Enable the OK button.
        self.buttonOK.config(state=tkinter.NORMAL)
        self.buttonOK.update()

        # Enable the More Options checkbox.
        self.checkboxOptions.config(state=tkinter.NORMAL)
        self.checkboxOptions.update()

        # Rename the Cancel button text back to Exit, leave enabled.
        self.buttonExitCancel.config(text="Exit")
        self.buttonExitCancel.update()

        # If the Custom Magnitude Min/Max drop-down lists are visible...
        if self.comboFrame_Custom_Magnitude is not None:

            # Enable the Custom Magnitude Min drop-down list.
            self.combo_Custom_Magnitude_Min.config(state="readonly")
            self.combo_Custom_Magnitude_Min.update()

            # Enable the Custom Magnitude Max drop-down list.
            self.combo_Custom_Magnitude_Max.config(state="readonly")
            self.combo_Custom_Magnitude_Max.update()

        # If the Custom Timespan From/To drop-down lists are visible...
        if self.comboFrame_Custom_Timespan is not None:

            # Enable the Custom Timespan From Year drop-down list.
            self.combo_CustomTimespan_Year_From.config(state="readonly")
            self.combo_CustomTimespan_Year_From.update()

            # Enable the Custom Timespan To Year drop-down list.
            self.combo_CustomTimespan_Year_To.config(state="readonly")
            self.combo_CustomTimespan_Year_To.update()

            # Enable the Custom Timespan From Month drop-down list.
            self.combo_CustomTimespan_Month_From.config(state="readonly")
            self.combo_CustomTimespan_Month_From.update()

            # Enable the Custom Timespan To Month drop-down list.
            self.combo_CustomTimespan_Month_To.config(state="readonly")
            self.combo_CustomTimespan_Month_To.update()

        # If the Analysis Options and Clipping Options are visible...
        if self.analysisOptionsFrame is not None:

            # Enable the US Clipping Option.
            self.radiobuttonClippingOption_US.config(state=tkinter.NORMAL)
            self.radiobuttonClippingOption_US.update()

            # Enable the State Clipping Option.
            self.radiobuttonClippingOption_State.config(state=tkinter.NORMAL)
            self.radiobuttonClippingOption_State.update()

            # Enable the County Clipping Option.
            self.radiobuttonClippingOption_County.config(state=tkinter.NORMAL)
            self.radiobuttonClippingOption_County.update()

            #if arcpy.CheckExtension("Spatial") == "Available":
            #arcpy.CheckOutExtension("3D")

            # Enable the IDW checkbox.
            self.checkbox_IDW.config(state=tkinter.NORMAL)
            self.checkbox_IDW.update()

            # Enable the Kernel Density checkbox.
            self.checkbox_KernelDensity.config(state=tkinter.NORMAL)
            self.checkbox_KernelDensity.update()

            #if arcpy.CheckExtension("GeoStats") == "Available":

            # Enable the Kriging checkbox.
            self.checkbox_Kriging.config(state=tkinter.NORMAL)
            self.checkbox_Kriging.update()

            #if arcpy.CheckExtension("Spatial") == "Available":

            # Enable the Natural Neighbor checkbox.
            self.checkbox_NaturalNeighbor.config(state=tkinter.NORMAL)
            self.checkbox_NaturalNeighbor.update()

            # Enable the Optimized Hot Spot checkbox.
            self.checkbox_OptHotSpot.config(state=tkinter.NORMAL)
            self.checkbox_OptHotSpot.update()

            # Enable the Point Density checkbox.
            self.checkbox_PointDensity.config(state=tkinter.NORMAL)
            self.checkbox_PointDensity.update()

            # Enable the Spline checkbox.
            self.checkbox_Spline.config(state=tkinter.NORMAL)
            self.checkbox_Spline.update()

            # Enable the Thiessen checkbox.
            self.checkbox_Thiessen.config(state=tkinter.NORMAL)
            self.checkbox_Thiessen.update()

            # Enable the Trend checkbox.
            self.checkbox_Trend.config(state=tkinter.NORMAL)
            self.checkbox_Trend.update()

            # Enable the Output Data Counts to CSV checkbox.
            self.checkbox_OutputToCSVFile.config(state=tkinter.NORMAL)
            self.checkbox_OutputToCSVFile.update()

        # If the State drop-down list in the State Clipping Options is visible..
        if self.combo_State_Name is not None:

            # Enable the drop-down list for the State Clipping Option.
            self.combo_State_Name.config(state="readonly")
            self.combo_State_Name.update()

        # If the County drop-down list in the County Clipping Options is
        # visible...
        if self.combo_County_Name is not None:

            # Enable the drop-down list for the County Clipping Option.
            self.combo_County_Name.config(state="readonly")
            self.combo_County_Name.update()

    def func_Disable_Buttons(self):

        # This function controls the disabling of all user-selectable buttons,
        # checkboxes, radio buttons, and drop-down lists. This is used when the
        # application begins performing all tasks after the user clicks the OK
        # button.

        # Disable the Magnitude drop-down list.
        self.combo_EarthquakeMagnitude.config(state=tkinter.DISABLED)
        self.combo_EarthquakeMagnitude.update()

        # Disable the Timespan drop-down list.
        self.combo_EarthquakeTimespan.config(state=tkinter.DISABLED)
        self.combo_EarthquakeTimespan.update()

        # Disable the "Browse" button for the output workspace.
        self.workspaceFolderButton_FolderDialog.config(state=tkinter.DISABLED)
        self.workspaceFolderButton_FolderDialog.update()

        # Disable the Back button.
        self.buttonBack.config(state=tkinter.DISABLED)
        self.buttonBack.update()

        # Disable the OK button.
        self.buttonOK.config(state=tkinter.DISABLED)
        self.buttonOK.update()

        # Disable the More Options checkbox.
        self.checkboxOptions.config(state=tkinter.DISABLED)
        self.checkboxOptions.update()

        # Change the text on the Exit button to "Cancel", leave enabled.
        self.buttonExitCancel.config(text="Cancel")
        self.buttonExitCancel.update()

        # If the Custom Timespan From/To drop-down boxes are visible...
        if self.comboFrame_Custom_Timespan is not None:

            # Disable the Year From drop-down list.
            self.combo_CustomTimespan_Year_From.config(state=tkinter.DISABLED)
            self.combo_CustomTimespan_Year_From.update()

            # Disable the Year To drop-down list.
            self.combo_CustomTimespan_Year_To.config(state=tkinter.DISABLED)
            self.combo_CustomTimespan_Year_To.update()

            # Disable the Month From drop-down list.
            self.combo_CustomTimespan_Month_From.config(state=tkinter.DISABLED)
            self.combo_CustomTimespan_Month_From.update()

            # Disable the Month To drop-down list.
            self.combo_CustomTimespan_Month_To.config(state=tkinter.DISABLED)
            self.combo_CustomTimespan_Month_To.update()

        # If the Custom Magnitude Min/Max drop-down lists are visible...
        if self.comboFrame_Custom_Magnitude is not None:

            # Disable the Min Magnitude drop-down list.
            self.combo_Custom_Magnitude_Min.config(state=tkinter.DISABLED)
            self.combo_Custom_Magnitude_Min.update()

            # Disable the Max Magnitude drop-down list.
            self.combo_Custom_Magnitude_Max.config(state=tkinter.DISABLED)
            self.combo_Custom_Magnitude_Max.update()

        # If the Analysis Options and Clipping Options are visible...
        if self.analysisOptionsFrame is not None:

            # Disable the US Clipping Option checkbox.
            self.radiobuttonClippingOption_US.config(state=tkinter.DISABLED)
            self.radiobuttonClippingOption_US.update()

            # Disable the State Clipping Option checkbox.
            self.radiobuttonClippingOption_State.config(state=tkinter.DISABLED)
            self.radiobuttonClippingOption_State.update()

            # Disable the County Clipping Option checkbox.
            self.radiobuttonClippingOption_County.config(state=tkinter.DISABLED)
            self.radiobuttonClippingOption_County.update()

            # Disable the IDW checkbox.
            self.checkbox_IDW.config(state=tkinter.DISABLED)
            self.checkbox_IDW.update()

            # Disable the Kernel Density checkbox.
            self.checkbox_KernelDensity.config(state=tkinter.DISABLED)
            self.checkbox_KernelDensity.update()

            # Disable the Kriging checkbox.
            self.checkbox_Kriging.config(state=tkinter.DISABLED)
            self.checkbox_Kriging.update()

            # Disable the Natural Neighbor checkbox.
            self.checkbox_NaturalNeighbor.config(state=tkinter.DISABLED)
            self.checkbox_NaturalNeighbor.update()

            # Disable the Optimized Hot Spot checkbox.
            self.checkbox_OptHotSpot.config(state=tkinter.DISABLED)
            self.checkbox_OptHotSpot.update()

            # Disable the Point Density checkbox.
            self.checkbox_PointDensity.config(state=tkinter.DISABLED)
            self.checkbox_PointDensity.update()

            # Disable the Spline checkbox.
            self.checkbox_Spline.config(state=tkinter.DISABLED)
            self.checkbox_Spline.update()

            # Disable the Thiessen checkbox.
            self.checkbox_Thiessen.config(state=tkinter.DISABLED)
            self.checkbox_Thiessen.update()

            # Disable the Trend checkbox.
            self.checkbox_Trend.config(state=tkinter.DISABLED)
            self.checkbox_Trend.update()

            # Disable the Output Data Counts to CSV File checkbox.
            self.checkbox_OutputToCSVFile.config(state=tkinter.DISABLED)
            self.checkbox_OutputToCSVFile.update()

        # If the State drop-down list in the State Clipping Option is visible..
        if self.combo_State_Name is not None:

            # Disable the drop-down list for the State Clipping Option.
            self.combo_State_Name.config(state=tkinter.DISABLED)
            self.combo_State_Name.update()

        # If the County drop-down list in the County Clipping Option is
        # visible...
        if self.combo_County_Name is not None:

            # Disable the drop-down list for the County Clipping Option.
            self.combo_County_Name.config(state=tkinter.DISABLED)
            self.combo_County_Name.update()

    def func_Calculate_Script_Time(self):

        # This function determines the total time of script processing and
        # formats that time to display within the scroll box.

        # Current time minus start time.
        self.elapsed_time = time.time() - self.start_time

        # If total time is greater than or equal to 3600 seconds, execute
        # conversion formula for hour, minute, second.
        if self.elapsed_time >= 3600:

            self.hours = int(self.elapsed_time / 3600)
            self.remainingSeconds = self.elapsed_time%3600

            if self.remainingSeconds >= 60:

                self.minutes = int(self.remainingSeconds / 60)
                self.remainingSeconds = self.remainingSeconds%60

            elif self.remainingSeconds < 60:

                self.minutes = 0

            self.func_Scroll_setOutputText(
                "This Python script completed in:\n" +
                "{0:.0f}".format(self.hours) + " h, " +
                "{0:.0f}".format(self.minutes) + " m", None)

        # Else if total time is greater than or equal to 60 seconds, execute
        # conversion formula for minutes and seconds.
        elif self.elapsed_time >= 60:

            self.minutes = int(self.elapsed_time / 60)
            self.remainingSeconds = self.elapsed_time%60

            self.func_Scroll_setOutputText(
                "This Python script completed in:\n" +
                "{0:.0f}".format(self.minutes) + " m, " +
                "{0:.0f}".format(self.remainingSeconds) + " s", None)

        # Else if total time is greater than or equal to zero seconds, display
        # the seconds.
        elif self.elapsed_time >= 0:

            self.remainingSeconds = self.elapsed_time

            self.func_Scroll_setOutputText(
                "This Python script completed in:\n" +
                "{0:.0f}".format(self.remainingSeconds) + " s", None)

    def func_Scroll_setOutputText(self, word, tag):

        # This function controls what and how the output texts are displayed
        # within the scroll box for users to read. It takes an input argument
        # from the user as well as a text color tag.

        # These tags set the color used for specific text.
        self.scrollBox.tag_config(color_Red, foreground = color_Red)
        self.scrollBox.tag_config(color_Orange, foreground = color_Orange)
        self.scrollBox.tag_config(color_Blue, foreground = color_Blue)

        # This section inputs the user-defined wording and displays the message
        # within the scroll box. The focus of the scroll box shifts to the
        # last (bottom) entered text message.
        self.scrollBox.config(state=tkinter.NORMAL)
        self.scrollBox.insert(tkinter.END, word, (tag))
        self.scrollBox.insert(tkinter.END, "\n--------------------\n")
        self.scrollBox.see(tkinter.END)
        self.scrollBox.config(state=tkinter.DISABLED)

    def func_ProgressBar_setProgress(self, value):

        # This function controls the progress bar increment by taking a
        # user-defined input argument (integer).

        self.progressBar["value"] = value
        self.progressBar.update()



################################################################################
# TESTING SECTION #
################################################################################

    # TO BE USED IF INPUT PARAMETERS ARE NEEDED FOR EACH ANALYSIS!
    def func_Window_Parameters_PointDensity(self):

        try:

            if self.statusAnalysis_PointDensity.get() == 1:

                def setParameters():
                    print("hello.")

                    window.destroy()

                window = tkinter.Toplevel()
                window.geometry("400x200")
                window.title("Optional Parameters")

                window.geometry(
                    '+{}+{}'.format(self.winfo_toplevel().winfo_x(),
                                    self.winfo_toplevel().winfo_y()))

                window_Label_CellSize = ttk.Label(window,
                                                text="Cell Size (Optional):")
                window_Label_CellSize.grid(column=0, row=0, padx=20, pady=20,
                                           sticky=tkinter.W)

                self.window_StringParameter_CellSize = tkinter.StringVar()
                window_ParameterEntry_CellSize = ttk.Entry(window,
                            textvariable=self.window_StringParameter_CellSize,
                                                           width=20)
                window_ParameterEntry_CellSize.grid(column=1, row=0, padx=5,
                                                    pady=20)

                window_Label_Neighborhood_Type = ttk.Label(window,
                                        text="Neighborhood Type (Optional):")
                window_Label_Neighborhood_Type.grid(column=0, row=1, padx=10,
                                                    pady=10, sticky=tkinter.W)

                self.window_ParameterEntry_Neighborhood_Type_Text = \
                    tkinter.StringVar()
                window_ParameterEntry_Neighborhood_Type_ComboBox = \
                    ttk.Combobox(window, width=12,
                    textvariable = \
                    self.window_ParameterEntry_Neighborhood_Type_Text,
                                 state="readonly")
                window_ParameterEntry_Neighborhood_Type_ComboBox["values"] = \
                    ("NbrAnnulus","NbrCircle", "NbrRectangle", "NbrWedge")
                window_ParameterEntry_Neighborhood_Type_ComboBox.grid(column=1,
                                row=1, padx=10, pady=10, sticky=tkinter.W)
                window_ParameterEntry_Neighborhood_Type_ComboBox.current(1)

                window_Button_OK = tkinter.Button(window, text="OK",
                                                  command=setParameters)
                window_Button_OK.grid(column=0, row=3, padx=20, pady=1)

                window.lift()
                window.attributes("-topmost", True)
                window.grab_set()

                window.protocol("WM_DELETE_WINDOW", self.disable_event)

                window.mainloop()

        except Exception as e:

            self.func_Scroll_setOutputText("Error Message: " + str(e) + "\n" +
                                           "Traceback: " +
                                           traceback.format_exc(), color_Red)

    def disable_event(self):

        pass

    def test_IDW_parameters(self):

        import tkinter.simpledialog

        if self.statusAnalysis_IDW.get() == 1:

            result = tkinter.simpledialog.askstring("test title", "test prompt")
            print(result)