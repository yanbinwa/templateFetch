# -*- coding: utf-8 -*-   

import xlrd
import xlwt
import requests
import json
import os
import HelloWorld.constants as Constants
import random
from HelloWorld.config import Config
from HelloWorld.utils.PatternHelper import seasonPattern

config = Config();
TEMPLATE_FILE_DIR = config.getProperties(Constants.TEMPLATE_FILE_DIR_KEY) + '/'; 

VIDEO_SENTENCE_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.VIDEO_SENTENCE_FILE_KEY);
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);
VIDEO_NAME_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.VIDEO_NAME_FILE_KEY);

MUSIC_SENTENCE_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.MUSIC_SENTENCE_FILE_KEY);
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);
MUSIC_NAME_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.MUSIC_NAME_FILE_KEY);

VIDEO_LEVEL_INFO = '专有词库>长虹>影视>电影';
TV_LEVEL_INFO = '专有词库>长虹>影视>电视剧';
TEMPLATE_TAG = 'XXX';
PERSON_TAG = '[Person]';
SEASON_TAG = '[Season]';
VIDEO_TAG = '[Video]';
MUSIC_TAG = '[Music]';

NAME_ENTITY_PERSON_TAG = '<START:PER>'
NAME_ENTITY_MOVIE_TAG = '<START:MOVIE>'
NAME_ENTITY_MUSIC_TAG = '<START:MUSIC>'
NAME_ENTITY_END_TAG = '<END>'

TAG_MAP = {
#    PERSON_TAG : NAME_ENTITY_PERSON_TAG,
#    SEASON_TAG : SEASON_TAG,
    VIDEO_TAG : NAME_ENTITY_MOVIE_TAG,
#    MUSIC_TAG : NAME_ENTITY_MUSIC_TAG
};

APPID = config.getProperties(Constants.APPID_KEY);
NLU_URL = config.getProperties(Constants.NLU_ULR_KEY);

NER_TRAIN_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.NER_TRAIN_FILE_KEY);

'''
读取xlsx文件，调用nlu接口，
当levelInfo为专有词库>长虹>影视>电影 或 专有词库>长虹>影视>电视剧，
同时只拥有一个，将其替换成XXX作为模板
将原句和模板句一同输出到xlsx文件中作为训练的语料


新的思路，通过nameEntity来提取模板，同时考虑“第几集，第几期”作为模板

例如：我想看周星驰大话西游第一部  -> 我想看 Person XXX Season

'''
def buildTemplateDataFile(sentenceFile, targetTag, nameFile):
    nameEntityTag = TAG_MAP[targetTag];
    if nameEntityTag is None:
        return;
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
            namedEntities = jsonObj[0].get('namedEntities');
            entityNames = fetchNameEntitiesByTag(namedEntities, nameEntityTag);
            if entityNames is None or len(entityNames) != 1:
                continue;
            sentence = adjustSentence(targetTag, sentence, namedEntities);
            template = sentence.replace(entityNames[0], TEMPLATE_TAG);
            sentenceCandidates.append(sentence);
            targetTemplates.append(template);
            print('sentence: ' + sentence + '; template: ' + template);
        except Exception as e:
            print(e);
            continue;
    
    (sentenceCandidates, targetTemplates) = createTemplateData(targetTemplates, nameFile);
    workbook = xlwt.Workbook(encoding = 'utf-8');
    worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
    
    for i in range(len(sentenceCandidates)):
        worksheet.write(i, 0, sentenceCandidates[i]);
        worksheet.write(i, 1, targetTemplates[i]);
    if os.path.isfile(TEMPLATE_OUTPUT_FILE):
        os.remove(TEMPLATE_OUTPUT_FILE)
        
    workbook.save(TEMPLATE_OUTPUT_FILE);
    return;

def adjustSentence(targetTag, sentence, namedEntities):
    for tag, nameEntity in TAG_MAP.items():
        if tag == targetTag:
            continue;
        if tag == SEASON_TAG:
            sentence = replaceSeason(sentence);
        else:
            sentence = replaceByTag(sentence, namedEntities, nameEntity, tag);
    return sentence;

def replaceSeason(sentence):
    seasonStr = seasonPattern(sentence);
    if seasonStr != None:
        sentence = sentence.replace(seasonStr, SEASON_TAG);
    return sentence;

def replaceByTag(sentence, namedEntities, nameEntityTag, tag):
    entities = fetchNameEntitiesByTag(namedEntities, nameEntityTag);
    if entities is None or len(entities) == 0:
        return sentence;
    for entity in entities:
        sentence = sentence.replace(entity, tag);
    return sentence;

def fetchNameEntitiesByTag(sentence, tag):
    ret = [];
    cursor = 0;
    index = sentence.find(tag, cursor, len(sentence));
    while index >= 0:
        endIndex = sentence.find(NAME_ENTITY_END_TAG, index, len(sentence));
        if endIndex < 0:
            return None;
        ret.append(sentence[index + len(tag):endIndex]);
        cursor = endIndex + len(NAME_ENTITY_END_TAG);
        if cursor >= len(sentence):
            break;
        index = sentence.find(tag, cursor, len(sentence));
    return ret;

def callNlu(sentence):
    params = {
        'f' : 'synonymSegment,namedEntities',
        'q' : sentence,
        'appid' : APPID
    }
    jsonStr = requests.get(NLU_URL, params).text;
    jsonObj = json.loads(jsonStr);
    return jsonObj

def createTemplateData(targetTemplates, nameFile):
    targetTemplates = list(set(targetTemplates));
    newSentenceCandidates = [];
    newTargetTemplates = [];
    nameList = readFile(nameFile);
    for targetTemplate in targetTemplates:
        nameListTmp = nameList.copy();
        random.shuffle(nameListTmp);
        nameListTmp = nameListTmp[0:20];
        for name in nameListTmp:
            newTargetTemplates.append(targetTemplate);
            newSentenceCandidates.append(targetTemplate.replace(TEMPLATE_TAG, name));
    return (newSentenceCandidates, newTargetTemplates);

#去掉回车符
def readFile(nameFile):
    file = open(nameFile, encoding='utf-8');
    nameList = [];
    for line in file:
        nameList.append(line.replace('\n', ''));
    return nameList;

def buildTrainDataFileForNer(sentenceFile, targetTag, nameFile):
    nameEntityTag = TAG_MAP[targetTag];
    if nameEntityTag is None:
        return;
    data = xlrd.open_workbook(sentenceFile);
    table = data.sheet_by_index(0);
    sentences = [];
    for i in range(table.nrows):
        sentence = table.cell(i, 0).value;
        if sentence != None:
            sentences.append(sentence);
              
    trainTemplateDatas = [];
    for sentence in sentences:
        jsonObj = callNlu(sentence);
        try:
            namedEntities = jsonObj[0].get('namedEntities');
            entityNames = fetchNameEntitiesByTag(namedEntities, nameEntityTag);
            if entityNames is None or len(entityNames) != 1:
                continue;
            #这里仅保留<START:MOVIE><END>的标签，其余的标签去除，写入到txt文件中
            template1 = sentence.replace(entityNames[0], TEMPLATE_TAG);
            template2 = sentence.replace(entityNames[0], nameEntityTag + TEMPLATE_TAG + NAME_ENTITY_END_TAG);
            trainTemplateData = template1 + '\t' +  template2;
            trainTemplateDatas.append(trainTemplateData);
            print('sentence: ' + sentence + '; template: ' + trainTemplateData);
        except Exception as e:
            print(e);
            continue;
    
    trainTemplateDatas = list(set(trainTemplateDatas));
    trainDatas = [];
    nameList = readFile(nameFile);
    for trainTemplateData in trainTemplateDatas:
        nameListTmp = nameList.copy();
        random.shuffle(nameListTmp);
        nameListTmp = nameListTmp[0:20];
        for name in nameListTmp:
            trainDatas.append(trainTemplateData.replace(TEMPLATE_TAG, name));
    writeFile(NER_TRAIN_FILE, trainDatas);
    return;

def writeFile(nameFile, lines):
    with open(nameFile,'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n');
    
if __name__ == "__main__":
    #buildTemplateDataFile(VIDEO_SENTENCE_FILE, VIDEO_TAG, VIDEO_NAME_FILE);
    #buildTemplateDataFile(MUSIC_SENTENCE_FILE, MUSIC_TAG, MUSIC_NAME_FILE);
    buildTrainDataFileForNer(VIDEO_SENTENCE_FILE, VIDEO_TAG, VIDEO_NAME_FILE);