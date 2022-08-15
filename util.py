import errno
import subprocess
import os.path
import platform
import collections
import shutil
import requests
import urllib.request
import urllib.parse

GUIString = collections.namedtuple('GUIString', 'id label help order')

confDir = r"conf"
confFilename = r"conf-{setKey}"
guiStringsFilename = r'gui-en-{setKey}.csv'

theEyeUrl = 'http://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'

def getKeySetString(string, setKey):
    return string.replace('{setKey}', setKey)


def getConfFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.conf'


def getConfBakFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.bak'


def getGuiStringsFilename(setKey):
    return getKeySetString(guiStringsFilename, setKey)


def lines_that_contain(string, fp):
    return [line for line in fp if string in line]


def callProcess(subProcessArgs,logger):
    process = subprocess.Popen(subProcessArgs, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    logger.logProcess(process)
    return process.wait()


def downloadZip(gameZipPath, logger):
    response = requests.get('https://github.com/eried/ArduboyCollection/archive/refs/heads/master.zip', stream=True,
                            headers={'User-agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        totalSize = 52 * 1024 * 1024 #int(response.headers.get('content-length'))
        rightSize = totalSize
        typeSize = ['b', 'kb', 'mb', 'gb']
        typeIndex = 0
        printableSize = ''
        while rightSize > 0 and typeIndex < len(typeSize):
            printableSize = str(rightSize) + ' ' + typeSize[typeIndex]
            rightSize = int(rightSize / 1024)
            typeIndex = typeIndex + 1
        logger.log('  Downloading ArduboyCollection.zip of size %s' % printableSize)
        with open(gameZipPath, 'wb') as f:
            if totalSize is None:
                f.write(response.content)
            else:
                downloaded = 0
                totalSize = int(totalSize)
                for data in response.iter_content(chunk_size=max(int(totalSize / 1000), 1024 * 1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / totalSize)
                    logger.log('\r    [{}{}]'.format(
                        '█' * done, '.' * (50 - done)), logger.INFO, True)
        return True
    else:
        logger.log(
            '  <ERROR> error %s while downloading from web %s: %s' % (
                response.status_code, gameZipPath, response.reason),
            logger.ERROR)
        return False
    

# Loads UI Strings
def loadUIStrings(scriptDir, guiStringsFile):
    guiStrings = dict()
    file = open(os.path.join(scriptDir, 'gui', guiStringsFile), 'r', encoding="utf-8")
    order = 0
    for line in file.readlines()[1:]:
        confLine = line.split(";")
        if len(confLine) == 3:
            guiStrings[confLine[0]] = GUIString(confLine[0], confLine[1], confLine[2].rstrip('\n\r ').replace("#n","\n"), order)
            order = order + 1
    file.close()
    return guiStrings


# Handle os escaping of path in local output dir
def localOSPath(path):
    if platform.system() == 'Windows':
        return path
    else:
        return path.replace('\\', '/')
