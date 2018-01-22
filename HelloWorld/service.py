# -*- coding: utf-8 -*-  

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
#from sklearn.externals import joblib
#import jpype
import os
import xlrd
#import json
import HelloWorld.constants as Constants
import pickle
from HelloWorld.config import Config
import requests
import json
import jieba

config = Config();
JAVA_LIB_PATH = config.getProperties(Constants.JAVA_JAR_LIB_DIR_KEY);
HANLP_LIB = config.getProperties(Constants.HANLP_JAR_KEY);

#StandardTokenizer = JClass('com.hankcs.hanlp.tokenizer.StandardTokenizer')
# Start of the python invocation, the argv is manifest file

TEMPLATE_FILE_DIR = config.getProperties(Constants.TEMPLATE_FILE_DIR_KEY) + '/'; 
MODEL_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TRAIN_MODEL_FILE_KEY);
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);

class TemplateFetchServiceSingleton:
    
    __instance = None
    
    def __init__(self):
        return;
        
    def __new__(cls, *args, **kwd):
        if TemplateFetchServiceSingleton.__instance is None:
            TemplateFetchServiceSingleton.__instance = object.__new__(cls, *args, **kwd)
        return TemplateFetchServiceSingleton.__instance;
    
    def trainModel(self, sentences, targetTemplates):
        self.indexToTemplate = {};
        templateToIndex = {};
        index = 0;
        for targetTemplate in targetTemplates:
            if targetTemplate not in templateToIndex:
                templateToIndex[targetTemplate] = index;
                self.indexToTemplate[index] = targetTemplate;
                index += 1;
        
        targetTemplateIndexs = [];
        for targetTemplate in targetTemplates:
            targetTemplateIndexs.append(templateToIndex.get(targetTemplate));
            
        segments = self.segmentSentences(sentences);            
        data = self.prepareDatas(segments);
        #开始训练
        self.count_vect = CountVectorizer();
        X_train_counts = self.count_vect.fit_transform(data);
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts);
        self.tf_transformer.transform(X_train_counts);
        self.tfidf_transformer = TfidfTransformer();
        X_train_tfidf = self.tfidf_transformer.fit_transform(X_train_counts);
        self.model = MultinomialNB().fit(X_train_tfidf, targetTemplateIndexs);
        return;
    
    #读取excel文件    
    def trainModelFromFile(self, excelFile):
        sentences = [];
        targetTemplates = [];
        data = xlrd.open_workbook(excelFile);
        table = data.sheet_by_index(0);
        for i in range(table.nrows):
            sentence = table.cell(i, 0).value;
            targetTemplate = table.cell(i, 1).value;
            if sentence == None or targetTemplates == None:
                break;
            sentences.append(sentence);
            targetTemplates.append(targetTemplate);
            
        self.trainModel(sentences, targetTemplates)
        return;
    
#     def fetchTemplate(self, sentence):
#         if self.model == None:
#             return None;
#         data = [];
#         segment = self.segment(sentence);
#         if segment is None:
#             return '';
#         data.append(self.prepareData(segment));
#         
#         X_new_counts = self.count_vect.transform(data);
#         X_new_tfidf = self.tfidf_transformer.transform(X_new_counts);
#         retIndex = self.model.predict(X_new_tfidf);
#         if retIndex is not None and len(retIndex) > 0:
#             return self.indexToTemplate[retIndex[0]];
#         return '';
    
    def fetchTemplate(self, sentence):
        if self.model == None:
            return None;
        data = [];
        segment = self.segment(sentence);
        if segment is None:
            return '';
        data.append(self.prepareData(segment));
        
        X_new_counts = self.count_vect.transform(data);
        X_new_tfidf = self.tfidf_transformer.transform(X_new_counts);
        retIndexRate = self.model.predict_proba(X_new_tfidf)[0];
        indexToRateMap = {};
        for i in range(len(retIndexRate)):
            indexToRateMap[i] = retIndexRate[i];
        
        #取前五个
        count = 0;
        candidateItem = [];
        for (index, rate) in sorted(indexToRateMap.items(), key = lambda x : x[1], reverse = True):
            candidateItem.append((self.indexToTemplate[index], rate))
            count += 1;
            if count >= 10:
                break;
        
        ret = {};
        for (key, value) in candidateItem:
            ret[key] = value;  
        return ret;
    
    #这里要将self.indexToTemplate, self.count_vect和self.tfidf_transformer，self.model存放起来
#     def storeTrainModel(self):
#         if self.model == None:
#             return;
#         self.deleteFile(MODEL_FILE);
#         self.deleteFile(INDEX_TO_TEMPLATE_FILE);
#         joblib.dump(self.model, MODEL_FILE);
#         outfile = open(INDEX_TO_TEMPLATE_FILE, 'a', encoding='utf-8');
#         json.dump(self.indexToTemplate, outfile)  #ensure_ascii = False
#         outfile.write('\n');
#         return;
    
    def storeTrainModel(self):
        if self.model == None:
            return;
        self.deleteFile(MODEL_FILE);
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump((self.model, self.count_vect, self.tfidf_transformer, self.indexToTemplate), f);
        return;
    
    def uploadTrainModel(self):
        print('uploadTrainModel');
        with open(MODEL_FILE, 'rb') as f:
            (self.model, self.count_vect, self.tfidf_transformer, self.indexToTemplate) = pickle.load(f);
        return;
    
#     def segment(self, sentence):
#         try:
#             if jpype.isJVMStarted():
#                 jpype.shutdownJVM();
#             jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=" + JAVA_LIB_PATH  + "/" + HANLP_LIB, "-Xms1g", "-Xmx1g");
#             StandardTokenizer = jpype.JClass('com.hankcs.hanlp.tokenizer.StandardTokenizer');
#             segments = StandardTokenizer.segment(sentence);
#             print('segment finshed');
#             ret = [];
#             for i in range(segments.size()):
#                 ret.append(str(segments.get(i).word));
#             return ret;
#         except Exception as e:
#             print(e)
#             return None;
#         finally:
#             jpype.shutdownJVM();
    
#     def segment(self, sentence):
#         try:
#             segmentObj = self.callNlu(sentence);
#             ret = [];
#             synonymSegments = segmentObj[0].get('synonymSegment');
#             for segment in synonymSegments:
#                 ret.append(segment.get('orgWord'));
#         except:
#             return None;

    def callNlu(self, sentence):
        params = {
            'f' : 'synonymSegment',
            'q' : sentence,
            'appid' : '5a200ce8e6ec3a6506030e54ac3b970e'
        }
        jsonStr = requests.get('http://172.16.101.61:13901/parse', params).text;
        jsonObj = json.loads(jsonStr);
        return jsonObj
    
    def segment(self, sentence):
        try:
            ret = [];
            for word in jieba.cut(sentence, cut_all=False, HMM=True):
                ret.append(word);
            return ret;
        except:
            return None;

    def segmentSentences(self, sentences):
        rets = [];
        for sentence in sentences:
            ret = self.segment(sentence)
            if ret != None:
                rets.append(ret);
        return rets;
    
    def prepareDatas(self, segments):
        rets = []
        for segment in segments:
            rets.append(self.prepareData(segment));
        return rets;
    
    def prepareData(self, segment):
        strTmp = '';
        for i in range(len(segment)):
            if i > 0:
                strTmp += ' ';
            unicodeStr = repr(segment[i].encode('unicode_escape'));
            unicodeStr = unicodeStr[2:]
            unicodeStr = unicodeStr[:len(unicodeStr) - 1]
            strTmp += unicodeStr;
        return strTmp;
    
    def deleteFile(self, fileName):
        if os.path.isfile(fileName):
            os.remove(fileName);

if __name__ == "__main__":
    #test = TemplateFetchServiceSingleton();
    #test.trainModelFromFile(TEMPLATE_OUTPUT_FILE);
    #test.storeTrainModel();
    
    test = TemplateFetchServiceSingleton();
    test.uploadTrainModel();
    ret = test.fetchTemplate('大话西游帮我放');
    print(ret);