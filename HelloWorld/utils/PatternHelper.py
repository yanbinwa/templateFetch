# -*- coding: utf-8 -*-  
import re;

PATTERN = '((第)?(((\\d+))|([一,二,三,四,五,六,七,八,九,十]+))集)|(第(((\\d+))|([一,二,三,四,五,六,七,八,九,十]+))(部|期|季))'

def seasonPattern(sentence):
    searchObj = re.search(PATTERN, sentence, flags = 0);
    if searchObj != None:
        return searchObj.group(0);
    return None

if __name__ == "__main__":
    sentence = '我想看大话西游11集';
    print(seasonPattern(sentence));