# -*- coding: utf-8 -*-   

import xlrd
import xlwt
import requests
import json
import os
import HelloWorld.constants as Constants
from HelloWorld.config import Config

config = Config();
TEMPLATE_FILE_DIR = config.getProperties(Constants.TEMPLATE_FILE_DIR_KEY) + '/'; 
VIDEO_SENTENCE_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.VIDEO_SENTENCE_FILE_KEY);
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);
VIDEO_NAME_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.VIDEO_NAME_FILE_KEY);

VIDEO_LEVEL_INFO = '专有词库>长虹>影视>电影';
TV_LEVEL_INFO = '专有词库>长虹>影视>电视剧';
TEMPLATE_TAG = 'XXX';

'''
读取xlsx文件，调用nlu接口，
当levelInfo为专有词库>长虹>影视>电影 或 专有词库>长虹>影视>电视剧，
同时只拥有一个，将其替换成XXX作为模板
将原句和模板句一同输出到xlsx文件中作为训练的语料
'''
def buildTemplateDataFile(sentenceFile):
    data = xlrd.open_workbook(sentenceFile);
    table = data.sheet_by_index(0);
    sentences = [];
    for i in range(table.nrows):
        sentence = table.cell(i, 0).value;
        if sentence != None:
            sentences.append(sentence);
              
    sentenceCandidates = [];
    targetTemplates = [];
    for sentence in sentences:
        jsonObj = callNlu(sentence);
        try:
            count = 0;
            template = sentence;
            synonymSegments = jsonObj[0].get('synonymSegment');
            for segment in synonymSegments:
                levelInfo = segment.get('levelInfo');
                if levelInfo == VIDEO_LEVEL_INFO or levelInfo == TV_LEVEL_INFO:
                    template = template.replace(segment.get('orgWord'), TEMPLATE_TAG);
                    count = count + 1;
            if count == 1:
                sentenceCandidates.append(sentence);
                targetTemplates.append(template);
                print('sentence: ' + sentence + '; template: ' + targetTemplates);
        except:
            continue;
    
    (sentenceCandidates, targetTemplates) = createTemplateData(targetTemplates);
    workbook = xlwt.Workbook(encoding = 'utf-8');
    worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
    
    for i in range(len(sentenceCandidates)):
        worksheet.write(i, 0, sentenceCandidates[i]);
        worksheet.write(i, 1, targetTemplates[i]);
    if os.path.isfile(TEMPLATE_OUTPUT_FILE):
        os.remove(TEMPLATE_OUTPUT_FILE)
        
    workbook.save(TEMPLATE_OUTPUT_FILE);
    return;

def callNlu(sentence):
    params = {
        'f' : 'synonymSegment',
        'q' : sentence,
        'appid' : '5a200ce8e6ec3a6506030e54ac3b970e'
    }
    jsonStr = requests.get('http://172.16.101.61:13901/parse', params).text;
    jsonObj = json.loads(jsonStr);
    return jsonObj

def createTemplateData(targetTemplates):
    targetTemplates = list(set(targetTemplates));
    newSentenceCandidates = [];
    newTargetTemplates = [];
    videoNameList = readFile();
    for targetTemplate in targetTemplates:
        for videoName in videoNameList:
            newTargetTemplates.append(targetTemplate);
            newSentenceCandidates.append(targetTemplate.replace(TEMPLATE_TAG, videoName));
    return (newSentenceCandidates, newTargetTemplates);
    
def readFile():
    file = open(VIDEO_NAME_FILE, encoding='utf-8');
    videoNameList = [];
    for line in file:
        videoNameList.append(line);
    return videoNameList;
    
if __name__ == "__main__":
    buildTemplateDataFile(VIDEO_SENTENCE_FILE);
