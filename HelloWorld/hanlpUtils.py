# -*- coding: utf-8 -*-  
from jpype import *

startJVM(getDefaultJVMPath(), "-Djava.class.path=/Users/emotibot/Documents/workspace/other/HelloWorld/lib/hanlp-portable-1.3.4.jar", "-Xms1g", "-Xmx1g")
StandardTokenizer = JClass('com.hankcs.hanlp.tokenizer.StandardTokenizer')

def segment(sentence):
    segments = StandardTokenizer.segment(sentence);
    ret = [];
    for i in range(segments.size()):
        ret.append(str(segments.get(i).word));
    return ret;

def segmentSentences(sentences):
    rets = [];
    for sentence in sentences:
        ret = segment(sentence)
        if ret != None:
            rets.append(ret);
    return rets;

if __name__ == "__main__":
    strTmp = "我想看电影";
    print(segment(strTmp));
