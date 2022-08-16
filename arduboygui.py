import tkinter as Tk
from tkinter import ttk, messagebox, filedialog
from operator import attrgetter
import tkinter.font as Font
import wckToolTips
import conf
import util
import os
import shutil
import platform
from datetime import datetime
from arduboyconverter import ArduboyConverter
from functools import partial
import _thread


# Main GUI
class ArduboyGUI:
    DEFAULT_FONT_SIZE = 9

    def __init__(self, scriptDir, logger, title):
        self.scriptDir = scriptDir
        self.setKey = 'arduboy'
        self.cache = None
        self.loading = True
        # TODO create conf file from guiStrings if it doesn't exist and do not ship it with tool anymore
        self.configuration = conf.loadConf(
            os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)))
        self.guiVars = dict()
        self.guiStrings = util.loadUIStrings(self.scriptDir, util.getGuiStringsFilename(self.setKey))

        self.window = Tk.Tk()
        self.window.resizable(False, False)
        self.window.geometry('+50+50')
        self.startFontSize = self.DEFAULT_FONT_SIZE

        if platform.system() == 'Windows':
            #TODO change icon
            self.window.iconbitmap('arduboyicon.ico')

        self.window.title(title)
        self.logger = logger

        # Init all components
        self.root = None
        self.mainFrame = None
        self.pathsFrame = None
        self.outputEntry = None
        self.selectOutputDirButton = None
        self.configurationFrame = None
        self.useGenreSubFolderCheckButton = None
        self.autoUpdateCheckButton = None
        self.buttonsFrame = None
        self.verifyButton = None
        self.saveButton = None
        self.proceedButton = None
        self.consoleFrame = None
        self.logTest = None
        self.scrollbar = None

    def draw(self):
        self.root = Tk.Frame(self.window, padx=10, pady=5)
        self.root.grid(column=0, row=0)
        self.__drawMainframe__()
        self.window.mainloop()

    # Main mama Frame
    def __drawMainframe__(self):
        self.mainFrame = Tk.Frame(self.root, padx=10, pady=0)
        self.mainFrame.grid(column=0, row=1, sticky="EW", pady=5)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.__drawPathsFrame__()
        self.__drawConfigurationFrame__()
        self.__drawButtonsFrame__()
        self.__drawConsole__()

    # Paths frame
    def __drawPathsFrame__(self):
        self.pathsFrame = Tk.LabelFrame(self.mainFrame, text="Your Paths", padx=10, pady=5)
        self.pathsFrame.grid(column=0, row=0, sticky="EW", pady=5)
        self.pathsFrame.grid_columnconfigure(1, weight=1)
        setRow = 0

        outputDirLabel = Tk.Label(self.pathsFrame, text=self.guiStrings['outputDir'].label)
        wckToolTips.register(outputDirLabel, self.guiStrings['outputDir'].help)
        outputDirLabel.grid(column=0, row=setRow, padx=5, sticky=Tk.W)
        self.guiVars['outputDir'] = Tk.StringVar()
        self.guiVars['outputDir'].set(self.configuration['outputDir'])
        self.outputEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['outputDir'])
        self.outputEntry.grid(column=1, row=setRow, padx=5, sticky="WE")
        self.selectOutputDirButton = Tk.Button(self.pathsFrame, text=self.guiStrings['selectOutputDir'].label,
                                               command=lambda: self.__openFileExplorer__('outputDir'))
        self.selectOutputDirButton.grid(column=2, row=setRow, padx=5, sticky="WE")
        wckToolTips.register(self.selectOutputDirButton, self.guiStrings['selectOutputDir'].help)

    # Configuration Frame
    def __drawConfigurationFrame__(self):
        self.configurationFrame = Tk.LabelFrame(self.mainFrame, text="Configuration", padx=10, pady=5)
        self.configurationFrame.grid(column=0, row=1, sticky="EW", pady=5)
        # self.configurationFrame.columnconfigure(0, weight=1)

        self.guiVars['autoUpdate'] = Tk.IntVar()
        self.guiVars['autoUpdate'].set(self.configuration['autoUpdate'])
        self.autoUpdateCheckButton = Tk.Checkbutton(self.configurationFrame,
                                                           text=self.guiStrings['autoUpdate'].label,
                                                           variable=self.guiVars['autoUpdate'], onvalue=1,
                                                           offvalue=0)
        wckToolTips.register(self.autoUpdateCheckButton, self.guiStrings['autoUpdate'].help)
        self.autoUpdateCheckButton.grid(column=0, row=0, sticky="W", pady=5, padx=5)

        self.guiVars['genreSubFolders'] = Tk.IntVar()
        self.guiVars['genreSubFolders'].set(self.configuration['genreSubFolders'])
        self.useGenreSubFolderCheckButton = Tk.Checkbutton(self.configurationFrame,
                                                           text=self.guiStrings['genreSubFolders'].label,
                                                           variable=self.guiVars['genreSubFolders'], onvalue=1,
                                                           offvalue=0)
        wckToolTips.register(self.useGenreSubFolderCheckButton, self.guiStrings['genreSubFolders'].help)
        self.useGenreSubFolderCheckButton.grid(column=1, row=0, sticky="W", pady=5, padx=5)

    # Action buttons frame
    def __drawButtonsFrame__(self):
        self.buttonsFrame = Tk.Frame(self.mainFrame, padx=10)
        self.buttonsFrame.grid(column=0, row=3, sticky="EW", pady=5)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=400)
        emptyFrame.grid(column=0, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(0, weight=3)
        self.verifyButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['verify'].label,
                                      command=self.__clickVerify__)
        wckToolTips.register(self.verifyButton, self.guiStrings['verify'].help)
        self.verifyButton.grid(column=1, row=0, sticky="EW", padx=3)
        self.saveButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['save'].label, command=self.__clickSave__)
        wckToolTips.register(self.saveButton, self.guiStrings['save'].help)
        self.saveButton.grid(column=2, row=0, sticky="EW", padx=3)
        self.proceedButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['proceed'].label,
                                       command=self.__clickProceed__)
        wckToolTips.register(self.proceedButton, self.guiStrings['proceed'].help)
        self.proceedButton.grid(column=3, row=0, sticky="EW", padx=3)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=350)
        emptyFrame.grid(column=4, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(4, weight=3)

    # Listener for Save button
    def __clickSave__(self):
        self.logger.log('\n<--------- Saving configuration --------->')
        self.__saveConfFile__()
        self.__saveConfInMem__()

    # Saves to conf file
    def __saveConfFile__(self):
        confBackupFilePath = os.path.join(self.scriptDir, util.confDir, util.getConfBakFilename(self.setKey))
        if os.path.exists(confBackupFilePath):
            os.remove(confBackupFilePath)
        shutil.copy2(os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)),
                     os.path.join(self.scriptDir, util.confDir, util.getConfBakFilename(self.setKey)))
        confFile = open(os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)), "w",
                        encoding="utf-8")
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys:
            if key.id not in ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList',
                              'filter', 'selectall', 'unselectall', 'loadCustom', 'saveCustom', 'selectOutputDir',
                              'selectCollectionDir', 'selectSelectionPath']:
                if key.help:
                    confFile.write('# ' + key.help.replace('\n', '\n# ') + '\n')
                if key.id == 'images':
                    imagesValue = self.guiVars[self.guiStrings['images'].label + ' #1'].get()
                    if self.guiStrings['images'].label + ' #2' in self.guiVars:
                        imagesValue = imagesValue + '|' + self.guiVars[
                            self.guiStrings['images'].label + ' #2'].get()
                    confFile.write(key.id + ' = ' + imagesValue + '\n')
                else:
                    if key.id in self.guiVars:
                        confFile.write(key.id + ' = ' + str(self.guiVars[key.id].get()) + '\n')
        confFile.close()
        self.logger.log('    Configuration saved in ' + util.getConfFilename(self.setKey) + ' file')

    # Saves in memory
    def __saveConfInMem__(self):
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys:
            if key.id not in ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList',
                              'selectall', 'unselectall', 'loadCustom', 'saveCustom', 'selectOutputDir',
                              'selectCollectionDir', 'selectSelectionPath']:
                if key.id == 'images':
                    imagesValue = self.guiVars[self.guiStrings['images'].label + ' #1'].get()
                    if self.guiStrings['images'].label + ' #2' in self.guiVars:
                        imagesValue = imagesValue + '|' + self.guiVars[
                            self.guiStrings['images'].label + ' #2'].get()
                    self.configuration['images'] = imagesValue
                else:
                    if key.id in self.guiVars:
                        self.configuration[key.id] = str(self.guiVars[key.id].get())
        self.logger.log('    Configuration saved in memory')

    # Listener for Verify button
    def __clickVerify__(self):
        self.logger.log('\n<--------- Verify ' + self.setKey + ' Parameters --------->')
        error = False
        for key in ['outputDir']:
            if not os.path.exists(self.guiVars[key].get()):
                error = True
                self.logger.log(key + ' folder does not exist')

        if not error:
            self.logger.log('All Good!')
        return error

    # Set enabled/disabled state for a component
    @staticmethod
    def __setComponentState__(component, state):
        if component is not None:
            component['state'] = state

    # Handles state of all the components based on UI status
    def __handleComponentsState__(self, clickedProcess):
        mainButtons = [self.verifyButton, self.saveButton, self.proceedButton]
        entryComponents = [self.outputEntry, self.selectOutputDirButton]
        otherComponents = [self.useGenreSubFolderCheckButton, self.autoUpdateCheckButton]

        if clickedProcess:
            [self.__setComponentState__(c, 'disabled') for c in mainButtons + otherComponents + entryComponents]
        else:
            [self.__setComponentState__(c, 'normal') for c in mainButtons + otherComponents + entryComponents]

    def postProcess(self):
        self.__handleComponentsState__(False)
        self.logger.log("All done. You can quit now.")

    # Listener for Proceed Button
    def __clickProceed__(self):
        self.logger.log('\n<--------- Saving ' + self.setKey + ' configuration --------->')
        self.__saveConfInMem__()

        message = self.guiStrings['confirm'].help.replace('{outputDir}', self.guiVars['outputDir'].get()).replace('#n',
                                                                                                                  '\n')
        result = messagebox.askokcancel(self.guiStrings['confirm'].label, message)

        if result and not self.__clickVerify__():
            self.__handleComponentsState__(True)

            self.logger.log('\n<--------- Starting ' + self.setKey + ' Process --------->')
            useGenreSubFolders = True if self.guiVars['genreSubFolders'].get() == 1 else False
            autoUpdate = True if self.guiVars['autoUpdate'].get() ==1 else False
            outputDir = self.guiVars['outputDir'].get()
            arduboyConverter = ArduboyConverter(self.scriptDir, outputDir, autoUpdate, useGenreSubFolders,
                                            partial(self.postProcess), self.logger)
            _thread.start_new(arduboyConverter.convertGames, ())

    # File Explorer for various vars
    def __openFileExplorer__(self, var):
        result = filedialog.askdirectory(initialdir=self.guiVars[var].get(),
                                         title="Select your " + self.guiStrings[var].label)

        if result != '':
            if platform.system() == 'Windows':
                result = result.replace('/', '\\')
            self.__updateConsoleFromQueue__()
            self.guiVars[var].set(result)

    # Grabs messages from logger queue
    def __updateConsoleFromQueue__(self):
        while not self.logger.log_queue.empty():
            line = self.logger.log_queue.get()
            self.__writeToConsole__(line)
            self.root.update_idletasks()
        self.logTest.after(10, self.__updateConsoleFromQueue__)

    # Console Frame
    def __drawConsole__(self):
        self.consoleFrame = Tk.Frame(self.root, padx=10)
        self.consoleFrame.grid(column=0, row=5, sticky="EW", pady=5)
        self.consoleFrame.grid_columnconfigure(0, weight=1)
        self.logTest = Tk.Text(self.consoleFrame, height=22, state='disabled', wrap='word', background='black',
                               foreground='yellow')
        self.logTest.grid(column=0, row=0, sticky="EW")
        self.logTest.tag_config('ERROR', background='black', foreground='red')
        self.logTest.tag_config('WARNING', background='black', foreground='orange')
        self.logTest.tag_config('INFO', background='black', foreground='yellow')
        self.scrollbar = Tk.Scrollbar(self.consoleFrame, orient=Tk.VERTICAL, command=self.logTest.yview)
        self.scrollbar.grid(column=1, row=0, sticky=(Tk.N, Tk.S))
        self.logTest['yscrollcommand'] = self.scrollbar.set
        self.logTest.after(10, self.__updateConsoleFromQueue__)

    # Write message to console
    def __writeToConsole__(self, msg):
        numlines = self.logTest.index('end - 1 line').split('.')[0]
        self.logTest['state'] = 'normal'
        if numlines == 24:
            self.logTest.delete(1.0, 2.0)
        previousLine = self.logTest.get('end-1c linestart', 'end-1c')
        # handle progress bar
        if msg[1] and previousLine.startswith('    [') and previousLine.endswith(']'):
            self.logTest.delete('end-1c linestart', 'end')

        if self.logTest.index('end-1c') != '1.0':
            self.logTest.insert('end', '\n')
        self.logTest.insert('end', msg[2], msg[0])
        self.logTest.see(Tk.END)
        self.logTest['state'] = 'disabled'


