# 通过对问题中的关键词进行提取和分析，对问题进行分类

import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        # 获取绝对路径的上一层目录
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])

        # 特征词路径
        self.diseasePath = os.path.join(cur_dir, 'dict/disease.txt')
        self.causePath = os.path.join(cur_dir, 'dict/cause.txt')
        self.drugPath = os.path.join(cur_dir, 'dict/drug.txt')
        self.symptomPath = os.path.join(cur_dir, 'dict/symptoms.txt')
        self.departmentPath = os.path.join(cur_dir, 'dict/department.txt')

        # 加载特征词
        self.diseaseWds = [i.strip() for i in open(self.diseasePath,encoding="utf-8") if i.strip()]
        self.foodWds = [i.strip() for i in open(self.causePath,encoding="utf-8") if i.strip()]
        self.drugWds = [i.strip() for i in open(self.drugPath,encoding="utf-8") if i.strip()]
        self.symptomWds = [i.strip() for i in open(self.symptomPath,encoding="utf-8") if i.strip()]
        self.departmentWds = [i.strip() for i in open(self.departmentPath,encoding="utf-8") if i.strip()]
        self.regionWords = set(self.diseaseWds+self.foodWds+self.drugWds+self.symptomWds+self.departmentWds)

        # 构建领域actree，基于”树“机构进行匹配
        self.regionTree = self.buildActree(list(self.regionWords))
        # 构建字典
        self.wdtype_dict = self.buildWdtypeDict()
        # 问句疑问词
        self.symptomQs = ['症状','表征','现象','表现']
        self.causeQs = ['原因','为什么','为啥','为何','怎么会','咋样才','怎么才会','导致']
        self.drugQs = ['药','药品','口服液','胶囊','颗粒','药片','含片']
        self.belongQs = ['属于','什么科','啥科','哪个科','科室']

    # 分类主函数
    def classify(self, question):
        data={}
        medical_dict = self.checkQs(question)
        #print(medical_dict)
        if not medical_dict:
            return {}
        data['args'] = medical_dict

        # 收集问句中所涉及到的实体类型
        Obtypes = []
        for Obtype in medical_dict.values():
            Obtypes += Obtype
        #print(Obtypes)
        # 问题类型
        Qstypes = []
        if self.checkWords(self.symptomQs, question) and ('disease' in Obtypes):
            Qstype = 'disease_symptom'
            Qstypes.append(Qstype)

        if self.checkWords(self.symptomQs, question) and ('symptom' in Obtypes):
            #print(1)
            Qstype = 'symptom_disease'
            Qstypes.append(Qstype)

        if self.checkWords(self.belongQs, question) and ('disease' in Obtypes):
            Qstype = 'disease_department'
            Qstypes.append(Qstype)

        if self.checkWords(self.causeQs, question) and ('disease' in Obtypes):
            Qstype = 'cause_disease'
            Qstypes.append(Qstype)

        if self.checkWords(self.drugQs, question) and ('disease' in Obtypes):

            Qstype = 'disease_drug'
            Qstypes.append(Qstype)

        # 如果没有查到，就返回对应疾病
        if Qstypes == [] and 'symptom' in Obtypes:
            Obtypes = ['symptom_disease']

        # 最后返回字典
        data['question_types'] = Qstypes
        return data

    # 构建actree，加速过滤
    def buildActree(self, wordlist):
        actree = ahocorasick.Automaton()            #ahocorasick库 ac自动化 自动过滤
        for index, word in enumerate(wordlist):
            actree.add_word(word,(index,word))
        actree.make_automaton()                     #将树转化为AC自动机
        return actree

    # 构建词对应的类型
    def buildWdtypeDict(self):
        wd_dict = dict()
        for wd in self.regionWords:
            wd_dict[wd] = []
            if wd in self.diseaseWds:
                wd_dict[wd].append('disease')
            if wd in self.departmentWds:
                wd_dict[wd].append('department')
            if wd in self.foodWds:
                wd_dict[wd].append('cause')
            if wd in self.drugWds:
                wd_dict[wd].append('drug')
            if wd in self.symptomWds:
                wd_dict[wd].append('symptom')
        return wd_dict

    # 问句过滤
    def checkQs(self, question):
        regionWds = []
        for i in self.regionTree.iter(question):
            wd = i[1][1]            #匹配到的词
            regionWds.append(wd)

        # 取重复的短词，比如说如果regionWds=['流行感冒']，stopWds=['感冒']
        stopWds = []
        for wd1 in regionWds:
            for wd2 in regionWds:
                if wd1 in wd2 and wd1 != wd2:
                    stopWds.append(wd1)

        # 最后只取较长的词，'流行感冒'
        finalWds = [i for i in regionWds if i not in stopWds]
        final_dict = {i:self.wdtype_dict.get(i) for i in finalWds}
        #print(regionWds)
        return final_dict

    # 基于特征词进行分类
    def checkWords(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False
