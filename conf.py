
def cleanString(string):
    return string.rstrip('\n\r ').lstrip()


def loadConf(confFile, encoding="utf-8"):
    conf = dict()
    
    file = open(confFile, 'r', encoding=encoding)
    for line in file.readlines():
        if not line.startswith('#'):
            confLine = line.split("=")
            if len(confLine) == 2:
                conf[cleanString(confLine[0])] = cleanString(confLine[1])
    
    file.close()        
    return conf
