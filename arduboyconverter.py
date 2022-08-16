import os
import conf
import shutil
import util
import xml.etree.ElementTree as etree
from xml.dom import minidom
from logger import Logger
from zipfile import ZipFile

class ArduboyConverter:

    def __init__(self, scriptDir, outputDir, autoUpdate, useGenreSubFolders, postProcess, logger):
        self.scriptDir = scriptDir
        self.logger = logger
        self.outputDir = outputDir
        self.useGenreSubFolders = useGenreSubFolders
        self.autoUpdate = autoUpdate
        self.postProcess = postProcess

    # Loops on all games to convert them
    def convertGames(self):
        if not os.path.exists(os.path.join(self.scriptDir, 'collection')):
            os.makedirs(os.path.join(self.scriptDir, 'collection'))
        collectionDir = os.path.join(self.scriptDir, 'collection', 'ArduboyCollection-master')
        if self.autoUpdate or not os.path.exists(collectionDir):
            self.logger.log('Updating collection')
            gameZipPath = os.path.join(self.scriptDir, 'collection', 'collection.zip')
            downloadSuccess = util.downloadZip(gameZipPath, self.logger)
            if downloadSuccess:
                self.__unzip(gameZipPath)
            else:
                return
        self.logger.log('Cleaning output dir')
        for file in os.listdir(os.path.join(self.outputDir)):
            fullPath = os.path.join(self.outputDir, file)
            shutil.rmtree(fullPath) if os.path.isdir(fullPath) else os.remove(fullPath)
        os.makedirs(os.path.join(self.outputDir, 'downloaded_images'))

        gamelist = self.initXml(self.outputDir)
        genreFolders = [f for f in os.listdir(collectionDir) if os.path.isdir(os.path.join(collectionDir, f))
                        and f not in ['.git', '.github', 'docs']]
        for genreFolder in genreFolders:
            if self.useGenreSubFolders:
                os.makedirs(os.path.join(self.outputDir, genreFolder))
            self.logger.log("  Handling %s genre" % genreFolder)
            gameFolders = [f for f in os.listdir(os.path.join(collectionDir, genreFolder))
                           if os.path.isdir(os.path.join(collectionDir, genreFolder, f))]
            for gameFolder in gameFolders:
                self.logger.log("    Handling %s game" % gameFolder)
                gameFiles = os.listdir(os.path.join(collectionDir, genreFolder, gameFolder))

                gameIni = list(filter(lambda f: f.lower().endswith('.ini'), gameFiles))
                if len(gameIni) == 1:
                    self.logger.log("      Parsing game.ini metadata")
                    try:
                        metadata = conf.loadConf(os.path.join(collectionDir, genreFolder, gameFolder, gameIni[0]), encoding="ANSI")
                    except:
                        metadata = conf.loadConf(os.path.join(collectionDir, genreFolder, gameFolder, gameIni[0]), encoding="cp1252")
                    title = metadata['title'] if 'title' in metadata else None
                    date = metadata['date'] if 'date' in metadata else None
                    developer = metadata['author'] if 'author' in metadata else None
                    description = metadata['description'] if 'description' in metadata else None
                else:
                    self.logger.log("      No game.ini metadata found", Logger.WARNING)
                    title = None
                    date = None
                    developer = None
                    description = None

                gameName = title if title is not None else gameFolder

                hexFile = list(filter(lambda f: f.lower().endswith('.hex'), gameFiles))
                if len(hexFile) > 0:
                    hexDestination = os.path.join(self.outputDir, genreFolder, gameFolder + '.hex') \
                        if self.useGenreSubFolders else os.path.join(self.outputDir, gameFolder + '.hex')
                    shutil.copy(os.path.join(collectionDir, genreFolder, gameFolder, hexFile[0]), hexDestination)

                    images = list(filter(lambda f: f.lower().endswith('.png'), gameFiles))
                    if len(images) > 0:
                        shutil.copy(os.path.join(collectionDir, genreFolder, gameFolder, images[0]),
                                    os.path.join(self.outputDir, 'downloaded_images', gameFolder + '.png'))
                    else:
                        self.logger.log("      No image found", Logger.WARNING)

                    self.__writeGamelistEntry__(gamelist, gameFolder, gameName, description, date, developer, genreFolder)
                else:
                    self.logger.log("      No hex file found in %d folder" % gameFolder, Logger.ERROR)

        self.writeXml(self.outputDir, gamelist)
        # TODO add process end message
        self.postProcess()

    # Inits in-memory gamelist xml either by opening the file or creating it
    @staticmethod
    def initXml(outputDir):
        if os.path.exists(os.path.join(outputDir, "gamelist.xml")):
            parser = etree.XMLParser(encoding="utf-8")
            return etree.parse(os.path.join(outputDir, "gamelist.xml"), parser=parser)
        else:
            tree = etree.ElementTree()
            tree._setroot(etree.Element('gameList'))
            return tree

    # Write full in-memory gamelist xml to outputDir
    @staticmethod
    def writeXml(outputDir, gamelist):
        xmlstr = minidom.parseString(etree.tostring(gamelist.getroot())).toprettyxml(indent="   ", newl="\r")
        xmlstr = '\n'.join([s for s in xmlstr.splitlines() if s.strip()])
        with open(os.path.join(outputDir, "gamelist.xml"), "wb") as f:
            f.write(xmlstr.encode('utf-8'))

    # Write metada for a given game to in-memory gamelist xml
    def __writeGamelistEntry__(self, gamelist, gameFolder, gameName, description, date, developer, genre):
        root = gamelist.getroot()

        year = date.replace('-', '').replace(':', '').replace('Z', '') if date is not None else ''
        path = './' + genre + '/' + gameFolder + '.hex' if self.useGenreSubFolders else "./" + gameFolder + '.hex'
        frontPic = './downloaded_images/' + gameFolder + '.png'

        gameElt = etree.SubElement(root, 'game')
        etree.SubElement(gameElt, 'path').text = path
        etree.SubElement(gameElt, 'name').text = gameName
        etree.SubElement(gameElt, 'desc').text = description if description is not None else ''
        etree.SubElement(gameElt, 'image').text = frontPic
        etree.SubElement(gameElt, 'releasedate').text = year
        etree.SubElement(gameElt, 'developer').text = developer if developer is not None else ''
        etree.SubElement(gameElt, 'genre').text = genre

    # Unzip game zip
    def __unzip(self, gameZipPath):
        collectionDir = os.path.join(self.scriptDir, 'collection')
        self.logger.log('Cleaning collection dir')
        for file in os.listdir(os.path.join(collectionDir)):
            fullPath = os.path.join(collectionDir, file)
            if file != 'collection.zip':
                shutil.rmtree(fullPath) if os.path.isdir(fullPath) else os.remove(fullPath)

        with ZipFile(gameZipPath, 'r') as zipFile:
            # Extract all the contents of zip file in current directory
            self.logger.log("Unzipping " + gameZipPath)
            zipFile.extractall(collectionDir)

        os.remove(os.path.join(collectionDir, 'collection.zip'))
