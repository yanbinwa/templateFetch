'''
从环境变量中读取config file的路径，之后加载config file
'''
import HelloWorld.constants as Constants
import os

class Config:
    
    __instance = None
    
    def __new__(cls, *args, **kwd):
        if Config.__instance is None:
            Config.__instance = object.__new__(cls, *args, **kwd)
        return Config.__instance;
    
    def __init__(self):
        configFile = os.environ.get(Constants.CONFIG_PATH_KEY);
        print(configFile);
        self.properties = {}
        try:
            fopen = open(configFile, 'r')
            for line in fopen:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        finally:
            fopen.close()
            
    def getProperties(self, key):
        return self.properties.get(key);
    
if __name__ == "__main__":
    config = Config();
    print(config.getProperties(Constants.INDEX_TO_TEMPLATE_FILE_KEY));