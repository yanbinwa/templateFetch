import xlrd
import xlwt
import json
import requests
from HelloWorld.service import TemplateFetchServiceSingleton
import HelloWorld.constants as Constants
from HelloWorld.config import Config
from HelloWorld.utils import TemplateHelper

config = Config();
TEMPLATE_FILE_DIR = config.getProperties(Constants.TEMPLATE_FILE_DIR_KEY) + '/'; 
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);
APPID = config.getProperties(Constants.APPID_KEY);
NLU_URL = config.getProperties(Constants.NLU_ULR_KEY);
TEST_INPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEST_INPUT_FILE_KEY);
TEST_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEST_OUTPUT_FILE_KEY);
TEST_CASE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEST_CASE_OUTPUT_FILE_KEY);

class Test:
    
    def __init__(self):
        self.templateService = TemplateFetchServiceSingleton();
        self.templateService.trainModelFromFile(TEMPLATE_OUTPUT_FILE);
    
    def testLog(self, fileName):
        data = xlrd.open_workbook(fileName);
        table = data.sheet_by_index(0);
        names = [];
        sentences = [];
        for i in range(0, table.nrows):
            names = table.cell(i, 0).value;
            sentences = table.cell(i, 1).value;
        
        workbook = xlwt.Workbook(encoding = 'utf-8');
        worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
        for i in range(len(names)):
            sentence = sentences[i];
            name = names[i];
            template = self.templateService.fetchTemplate(sentences[i]);
            if template is None or template == '':
                continue
            num1 = template.find('XXX');
            num2 = len(template) - template.find('XXX') - 3;
            if (num1 + num2) >= len(sentence):
                newName = '';
            else:
                newName = sentence;
                if (num1 > 0):
                    newName = newName[num1:];
                if (num2 > 0):
                    newName = newName[:len(newName) - num2];
            if (newName == name):
                tag = 'true';
            else:
                tag = 'false';
                
            worksheet.write(i, 0, sentence);
            worksheet.write(i, 1, template);
            worksheet.write(i, 2, name);
            worksheet.write(i, 3, newName);
            worksheet.write(i, 4, tag);
        workbook.save(TEST_CASE_OUTPUT_FILE);
    
    #需要调用nlu，确保name是在词库中的    
#     def createTestLog(self, fileName):
#         data = xlrd.open_workbook(fileName);
#         table = data.sheet_by_index(0);
#         names = [];
#         sentences = [];
#         for i in range(1, table.nrows):
#             domain = table.cell(i, 2).value;
#             intent = table.cell(i, 3).value;
#             if domain != 'VIDEO' or intent != 'QUERY':
#                 continue;
#             result = table.cell(i, 4).value;
#             name = self.getName(result);
#             if name is None:
#                 continue;
#             sentence = table.cell(i, 5).value;
#             #对sentence调用nlu，判断name是属于nud的
#             jsonObj = self.callNlu(sentence);
#             if jsonObj is None or len(jsonObj) == 0:
#                 continue;
#             synonymSegments = jsonObj[0].get('synonymSegment') if 'synonymSegment' in jsonObj[0] else '';
#             if synonymSegments == '':
#                 continue;
#             tag = False;
#             for segment in synonymSegments:
#                 if segment['orgWord'] == name and segment['pos'] == 'nud':
#                     tag = True;
#                     break;
#             
#             if tag:
#                 names.append(name);
#                 sentences.append(sentence);
#         
#         workbook = xlwt.Workbook(encoding = 'utf-8');
#         worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
#         for i in range(len(names)):
#             sentence = sentences[i];
#             name = names[i];
#             
#             worksheet.write(i, 0, name);   
#             worksheet.write(i, 1, sentence);
#         workbook.save(TEST_OUTPUT_FILE);
        
    #需要调用nlu，确保name是在词库中的    
    def createTestLog(self, fileName, domainTag, intentTag, nameEntityTag):
        data = xlrd.open_workbook(fileName);
        table = data.sheet_by_index(0);
        names = [];
        sentences = [];
        for i in range(1, table.nrows):
            domain = table.cell(i, 2).value;
            intent = table.cell(i, 3).value;
            if domain != domainTag or intent != intentTag:
                continue;
            result = table.cell(i, 4).value;
            name = self.getName(result);
            if name is None:
                continue;
            sentence = table.cell(i, 5).value;
            #对sentence调用nlu，判断name是属于nud的
            jsonObj = self.callNlu(sentence);
            if jsonObj is None or len(jsonObj) == 0:
                continue;
            nameEntities = jsonObj[0].get('namedEntities') if 'namedEntities' in jsonObj[0] else '';
            if nameEntities == '':
                continue;
            startIndex = nameEntities.index(nameEntityTag) if nameEntityTag in nameEntities else -1;
            if (startIndex < 0):
                continue;
            endIndex = nameEntities.index('<END>');
            if (endIndex < 0):
                continue;
            nameTmp = nameEntities[startIndex + len(nameEntityTag): endIndex];
            if nameTmp == name:
                names.append(name);
                sentences.append(sentence);
        
        workbook = xlwt.Workbook(encoding = 'utf-8');
        worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
        for i in range(len(names)):
            sentence = sentences[i];
            name = names[i];
            
            worksheet.write(i, 0, name);   
            worksheet.write(i, 1, sentence);
        workbook.save(TEST_OUTPUT_FILE);
                
    def getName(self, result):
        if result is None or result == '':
            return None;
        jsonObj = json.loads(result);
        return jsonObj.get('name');
    
    def callNlu(self, sentence):
        params = {
            'f' : 'synonymSegment,namedEntities',
            'q' : sentence,
            'appid' : APPID
        }
        jsonStr = requests.get(NLU_URL, params).text;
        jsonObj = json.loads(jsonStr);
        return jsonObj
        
if __name__ == "__main__":
    test = Test();
    #test.createTestLog(TEST_INPUT_FILE, 'VIDEO', 'QUERY', TemplateHelper.NAME_ENTITY_MOVIE_TAG);
    test.createTestLog(TEST_INPUT_FILE, 'MUSIC', 'QUERY', TemplateHelper.NAME_ENTITY_MUSIC_TAG);