import xlrd
import xlwt
import json
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
                
    def getName(self, result):
        if result is None or result == '':
            return None;
        jsonObj = json.loads(result);
        return jsonObj.get('name');
        
if __name__ == "__main__":
    test = Test();
    test.testLog("/Users/emotibot/Documents/workspace/other/HelloWorld/file/log.xlsx");