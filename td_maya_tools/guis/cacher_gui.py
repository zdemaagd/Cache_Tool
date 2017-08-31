#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    zdd130030

:synopsis:
    This module writes export and reads import alembic caches for maya animations from a GUI

:description:
    The module allows the user to save out alembic caches to a file destination from Maya. The object name and file
    destination may be given. The module also allows for the importing of alembic caches into Maya. The file path  must
    be given to import a cache. All of these functions are done through user input on a GUI.

:applications:
    Autodesk Maya

:see_also:
    N/A

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import tempfile
# Third party
import maya.cmds as cmds
import maya.mel as mel
# Internal

# External
import td_maya_tools.cacher as cacher
try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui

from maya import OpenMayaUI as omui
from shiboken import wrapInstance
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#
"""
This function allows the GUI to be created
"""
def get_maya_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow    = wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget)
    return mayaMainWindow
#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

# set up GUI interface
class CacherGUI(QtGui.QDialog):
    """
     This class is the GUI for the maya_tools.cacher.py file
    """
    def __init__(self):
        QtGui.QDialog.__init__(self, parent=get_maya_window())
        self.le_frame_start = None
        self.le_frame_end = None
        self.text_write_directory = None
        self.dir_name = None

    # build gui layout
    def init_gui(self):
        """
        Sets up all objects present in the GUI
        """
        # create main layout box
        main_hb = QtGui.QHBoxLayout(self)

        # set up buttons
        btn_write_directory = QtGui.QPushButton('Directory', self)
        btn_read_directory = QtGui.QPushButton('Directory')
        btn_read_file = QtGui.QPushButton('File', self)
        btn_write_cache = QtGui.QPushButton('Write Cache', self)
        btn_cancel = QtGui.QPushButton('Cancel', self)

        # set up line edits

        self.le_frame_start = QtGui.QLineEdit()
        self.le_frame_end = QtGui.QLineEdit()

        # set up text
        text_write_title = QtGui.QLabel('Write Cache')
        text_read_title = QtGui.QLabel('Read Cache')
        text_frange = QtGui.QLabel('Frame Range')
        text_frange_to = QtGui.QLabel('to')
        text_read_or = QtGui.QLabel('or')
        text_blank = QtGui.QLabel('')
        self.text_write_directory = QtGui.QLabel('')

        # button logic
        btn_write_cache.clicked.connect(self.validate_export)
        btn_write_directory.clicked.connect(self.select_dir)
        btn_read_directory.clicked.connect(self.select_dir_read)
        btn_read_file.clicked.connect(self.select_file_read)
        btn_cancel.clicked.connect(self.close)

        # set up gui layout
        # write title
        row_write_title = QtGui.QHBoxLayout()
        row_write_title.addWidget(text_write_title)

        # read title
        row_read_title = QtGui.QHBoxLayout()
        row_read_title.addWidget(text_read_title)

        # frame range
        row_frange = QtGui.QHBoxLayout()
        row_frange.addWidget(text_frange)
        row_frange.addWidget(self.le_frame_start)
        row_frange.addWidget(text_frange_to)
        row_frange.addWidget(self.le_frame_end)

        # write directory
        row_write_directory = QtGui.QHBoxLayout()
        row_write_directory.addWidget(btn_write_directory)
        row_write_directory.addWidget(self.text_write_directory)

        # read directory
        row_read_directory = QtGui.QHBoxLayout()
        row_read_directory.addWidget(btn_read_directory)

        # read file
        row_read_file = QtGui.QHBoxLayout()
        row_read_file.addWidget(btn_read_file)

        # write accept
        row_waccept = QtGui.QHBoxLayout()
        row_waccept.addWidget(btn_write_cache)

        # read or line
        row_or = QtGui.QHBoxLayout()
        row_or.addWidget(text_blank)
        row_or.addWidget(text_read_or)
        row_or.addWidget(text_blank)

        # write column
        column_write = QtGui.QVBoxLayout()
        column_write.addLayout(row_write_title)
        column_write.addLayout(row_frange)
        column_write.addLayout(row_write_directory)
        column_write.addLayout(row_waccept)
        column_write.addWidget(text_blank)

        # read column
        column_read = QtGui.QVBoxLayout()
        column_read.addLayout(row_read_title)
        column_read.addLayout(row_read_directory)
        column_read.addLayout(row_or)
        column_read.addLayout(row_read_file)
        column_read.addWidget(btn_cancel)

        # place boxes onto main
        main_hb.addLayout(column_write)
        main_hb.addLayout(column_read)

        # create area and window title
        column_write.addStretch(1)
        column_read.addStretch(1)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Maya Cacher')
        self.show()

    # check if frame range was input
    def get_frange(self):
        """
        Runs commands to retrieve frame values
        """
        self.ex_min = self.le_frame_start.text()
        self.ex_max = self.le_frame_end.text()
        """
        #if no start input
        if not self.le_frame_start.text():
            ex_min= long(cmds.playbackOptions(minTime=True, query=True))

        #if no end input
        if not self.le_frame_end.text():
            ex_max = long(cmds.playbackOptions(maxTime=True, query=True))
        """
        # selects the directory to write

    def select_dir(self):
        """
        Runs commands and methods to select export directory
        """
        # opens the file dialog
        write_directory_name = cmds.fileDialog2(dialogStyle=2, caption='Load Directory',
        fileMode=2, okCaption='Select')
        self.dir_name = ''.join(str(letter) for letter in write_directory_name)
        # sets a value to be set into the line edit
        self.file_location = self.dir_name
        self.update_export()

    # selects the directory to read
    def select_dir_read(self):
        """
        Runs commands and methods to select import directory
        """
        # opens the file dialog
        read_directory_name = cmds.fileDialog2(dialogStyle=2, caption='Load Directory',
        fileMode=3, okCaption='Select')
        read_dir_name = ''.join(str(letter) for letter in read_directory_name)

        # runs the loading cache for each file in directory
        file_list = cmds.getFileList(folder=read_dir_name, filespec='*.abc')
        for name in file_list:
            file_name = ''.join(str(letter) for letter in name)
            # sets a value for cacher
            self.read_file = read_dir_name + '/' + file_name

            # runs the import operation
            self.read_cache()
        self.display_import_result()
        # selects the file to read

    def select_file_read(self):
        """
        Runs commands and methods to open a dialog to import a file
        """
        # opens the file dialog
        read_file_name = cmds.fileDialog(directoryMask='*.abc')
        # sets a value for cacher
        self.read_file = read_file_name

        # runs the loading cache
        self.read_cache()

    # vailidates export
    def validate_export(self):
        """
        Runs commands to make sure something is selected before caching
        """
        valid = cmds.ls(selection=True)
        if not valid:
            self.display_warning()
        else:
            self.write_cache()

    # displays warning box
    def display_warning(self):
        """
         Runs commands to display if nothing is selected
        """
        reply = QtGui.QMessageBox.question(self, 'Error', "No Object Selected")

        # updates text representing write directory

    def update_export(self):
        self.text_write_directory.setText(self.file_location)

    # export result
    def display_export_result(self):
        """
        Runs all the necessary commands and methods to display export results
        """
        reply = QtGui.QMessageBox.question(self, 'Export Result',
        "Files saved to Directory: %s" % self.file_location)

    # import result
    def display_import_result(self):
        """
        Runs all the necessary commands and methods to display import results
        """
        reply = QtGui.QMessageBox.question(self, 'Import Result',
        "Imported Cache successfully")

    # writes cache useing cacher.py
    def write_cache(self):
        """
         Runs all the necessary commands and methods to export alembic cache from Maya.
        """
        self.get_frange()
        selected_obj = cmds.ls(selection=True)
        # converts list to strings and checks if there is a directory
        for geo in selected_obj:
            name = ''.join(str(geo) for geo in selected_obj)
            if self.dir_name:
                w_file_name = self.dir_name + '/' + name + '.abc'
            else:
                w_file_name = None
            ex_cacher = cacher.ExportCache(self.ex_min, self.ex_max, name, w_file_name)
            ex_cacher.process_args()
            ex_cacher.export_cache()
            self.display_export_result()

    # reads cache using cacher.py
    def read_cache(self):
        """
        Runs all the necessary commands and methods to import alembic cache to Maya.
        """
        imp_cacher = cacher.ImportCache(self.read_file)
        imp_cacher.import_cache()
        self.display_import_result()

