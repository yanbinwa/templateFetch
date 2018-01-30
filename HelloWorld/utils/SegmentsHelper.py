# -*- coding: utf-8 -*-  
import jieba

def segment(sentence):
    try:
        ret = [];
        for word in jieba.cut(sentence, cut_all=False, HMM=True):
            if word.strip() != '':
                ret.append(word);
        return ret;
    except:
        return None;

if __name__ == "__main__":
    sentence = '我想看[Person]XXX[Season]';
    ret = segment(sentence);
    print(ret);