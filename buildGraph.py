# 构建图谱
import os
import json
from py2neo import Graph,Node

class MdGraph:
    def __init__(self):
        # 获取绝对路径的上一层目录
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 获取json文件路径
        self.data_path = os.path.join(cur_dir,'data/md.json')
        # 连接neo4j（初始账号密码都是neo4j,我改了密码）
        self.g = Graph("http://localhost:7474",user="neo4j",password="wodeshengri5031",name="neo4j")

    # 读取文件
    def readNode(self):
        # 共5类节点，进行追问时所问的内容和建议（先想了这些，后续再修改）
        symptoms = []   #有什么症状
        causes = []     #什么病因
        diseases=[]     #初步诊断的病情
        departments=[]  #建议去哪个科室检查
        drugs=[]        #建议服用什么药

        # 构建节点实体关系（就只写了4个，有些病理不太懂，后续修改）
        rels_causes=[]       #原因——疾病的关系
        rels_symptom=[]      #症状——疾病的关系
        rels_departments=[]  #疾病——科室的关系
        rels_drugs=[]        #疾病——药物的关系

        count = 0
        datas = json.load(open(self.data_path, 'r', encoding='utf-8'))
        for data in datas:
            count += 1
            #print(count)
            disease = data['name']
            diseases.append(disease)
            if 'symptoms' in data:
                symptoms += data['symptoms']
                # 同一疾病有多个症状
                for symptom in data['symptoms']:
                    rels_symptom.append([disease, symptom])
            if 'causes' in data:
                causes += data['causes']
                for cause in data['causes']:
                    rels_causes.append([disease,cause])
            if 'departments' in data:
                departments += data['departments']
                for department in data['departments']:
                    rels_departments.append([disease,department])
            if 'drugs' in data:
                drugs += data['drugs']
                for drug in data['drugs']:
                    rels_drugs.append([disease, drug])
        return set(diseases),set(drugs),set(causes),set(symptoms),departments,rels_symptom,rels_causes,rels_departments,rels_drugs

    # 建立节点
    def createNode(self,label,nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count,len(nodes))
        return

    # 创建知识图谱实体节点类型schema
    def createGraghNodes(self):
        Diseases, Drugs, Causes, Symptoms, Departments,rels_symptom,rels_causes,rels_departments,rels_drugs = self.readNode()
        self.createNode('Disease',Diseases)
        self.createNode('Drug',Drugs)
        self.createNode('Symptom',Symptoms)
        self.createNode('Cause',Causes)
        self.createNode('Department',Departments)
        return

    # 创建实体关系边
    def createGraphRels(self):
        Diseases, Drugs, Causes, Symptoms, Departments,rels_symptom,rels_causes,rels_departments,rels_drugs = self.readNode()
        self.createRela('Disease','Cause',rels_causes,'caused_by','诱因')
        self.createRela('Disease','Symptom',rels_symptom,'has_symptom','症状')
        self.createRela('Disease','Department',rels_departments,'belongs_to','科室')
        self.createRela('Disease','Drug',rels_drugs,'cured_by','药物')


    # 创建实体关联边
    # 起止节点，边，关系类型，关系名
    def createRela(self, startNode, endNode, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        setEdges = []
        for edge in edges:
            setEdges.append('#####'.join(edge))
        #print(setEdges)
        all = len(set(setEdges))
        for edge in set(setEdges):
            edge = edge.split('#####')
            p = edge[0]
            q = edge[1]
            # match语法，p,q为标签，rel_type为关系类别，rel_name为关系名
            query = "match(p:%s),(q:%s) where p.name='%s' and q.name='%s' create(p)-[rel:%s{name:'%s'}]->(q)" %(
                startNode, endNode, p, q, rel_type, rel_name
            )
            try:
                self.g.run(query)
                count += 1
                print(startNode, endNode, p, q, rel_type)
            except Exception as e:
                print(e)
        return

    # 导出数据
    def exportData(self):
        Diseases, Drugs, Causes, Symptoms, Departments,rels_symptom,rels_causes,rels_departments,rels_drugs = self.readNode()
        f_drug = open('dict/drug.txt', 'w+',encoding="utf-8")
        f_cause = open('dict/cause.txt', 'w+',encoding="utf-8")
        f_department = open('dict/department.txt', 'w+',encoding="utf-8")
        f_symptom = open('dict/symptoms.txt', 'w+',encoding="utf-8")
        f_disease = open('dict/disease.txt', 'w+',encoding="utf-8")

        f_drug.write('\n'.join(list(Drugs)))
        f_cause.write('\n'.join(list(Causes)))
        f_department.write('\n'.join(list(Departments)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_cause.close()
        f_department.close()
        f_symptom.close()
        f_disease.close()
        return


if __name__ == '__main__':
    handler = MdGraph()         #创建图
    handler.createGraghNodes()  #创建节点
    handler.createGraphRels()   #创建关系
    handler.exportData()