import os.path
import sys
from arduboygui import ArduboyGUI
from logger import Logger

if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    title = 'ArduboyConverter 0.1-beta'
    logger = Logger()
    logger.log(title)
    logger.log('Script path : ' + scriptDir)

    gui = ArduboyGUI(scriptDir, logger, title)
    gui.draw()
