import xlrd
import xlwt
import json
import requests
from HelloWorld.service import TemplateFetchServiceSingleton
import HelloWorld.constants as Constants
from HelloWorld.config import Config

config = Config();
TEMPLATE_FILE_DIR = config.getProperties(Constants.TEMPLATE_FILE_DIR_KEY) + '/'; 
TEMPLATE_OUTPUT_FILE = TEMPLATE_FILE_DIR + config.getProperties(Constants.TEMPLATE_OUTPUT_FILE_KEY);


class Test:
    
    def __init__(self):
        self.templateService = TemplateFetchServiceSingleton();
        self.templateService.trainModelFromFile(TEMPLATE_OUTPUT_FILE);
    
    def testLog(self, fileName):
        data = xlrd.open_workbook(fileName);
        table = data.sheet_by_index(0);
        names = [];
        sentences = [];
        for i in range(1, table.nrows):
            domain = table.cell(i, 2).value;
            intent = table.cell(i, 3).value;
            if domain != 'VIDEO' or intent != 'QUERY':
                continue;
            result = table.cell(i, 4).value;
            name = self.getName(result);
            if name is None:
                continue;
            sentence = table.cell(i, 5).value;
            names.append(name);
            sentences.append(sentence);
        
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
        workbook.save('/Users/emotibot/Documents/workspace/other/HelloWorld/file/output.xls');
    
    #需要调用nlu，确保name是在词库中的    
    def createTestLog(self, fileName):
        data = xlrd.open_workbook(fileName);
        table = data.sheet_by_index(0);
        names = [];
        sentences = [];
        for i in range(1, table.nrows):
            domain = table.cell(i, 2).value;
            intent = table.cell(i, 3).value;
            if domain != 'VIDEO' or intent != 'QUERY':
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
            synonymSegments = jsonObj[0].get('synonymSegment') if 'synonymSegment' in jsonObj[0] else '';
            if synonymSegments == '':
                continue;
            tag = False;
            for segment in synonymSegments:
                if segment['orgWord'] == name and segment['pos'] == 'nud':
                    tag = True;
                    break;
            
            if tag:
                names.append(name);
                sentences.append(sentence);
        
        workbook = xlwt.Workbook(encoding = 'utf-8');
        worksheet = workbook.add_sheet('template', cell_overwrite_ok = True);
        for i in range(len(names)):
            sentence = sentences[i];
            name = names[i];
            
            worksheet.write(i, 0, name);   
            worksheet.write(i, 1, sentence);
        workbook.save('/Users/emotibot/Documents/workspace/other/HelloWorld/file/output.xls');
                
    def getName(self, result):
        if result is None or result == '':
            return None;
        jsonObj = json.loads(result);
        return jsonObj.get('name');
    
    def callNlu(self, sentence):
        params = {
            'f' : 'synonymSegment',
            'q' : sentence,
            'appid' : '5a200ce8e6ec3a6506030e54ac3b970e'
        }
        jsonStr = requests.get('http://172.16.101.61:13901/parse', params).text;
        jsonObj = json.loads(jsonStr);
        return jsonObj
        
if __name__ == "__main__":
    test = Test();
    test.createTestLog("/Users/emotibot/Documents/workspace/other/HelloWorld/file/log.xlsx");