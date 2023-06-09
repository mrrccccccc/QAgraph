# 根据问题类型和关系边，从数据库中查询到对应的节点

class QuestionPaser:
    # 构建实体节点
    def buildEntityDict(self, args):
        entity_dict = {}
        for arg, Obtypes in args.items():
            for Obtype in Obtypes:
                if Obtype not in entity_dict:
                    entity_dict[Obtype] = [arg]
                else:
                    entity_dict[Obtype].append(arg)
        return entity_dict

    # 解析主函数
    def parser_main(self, resClassify):
        args = resClassify['args']
        entity_dict = self.buildEntityDict(args)
        Qstypes = resClassify['question_types']
        sqls = []
        for Qstype in Qstypes:
            sql_dict = {}
            sql_dict['question_types'] = Qstype
            sql = []
            if Qstype == 'disease_symptom':
                sql = self.sqlTransfer(Qstype, entity_dict.get('disease'))
            elif Qstype == 'symptom_disease':
                sql = self.sqlTransfer(Qstype, entity_dict.get('symptom'))
            elif Qstype == 'disease_department':
                sql = self.sqlTransfer(Qstype, entity_dict.get('disease'))
            elif Qstype == 'cause_disease':
                sql = self.sqlTransfer(Qstype, entity_dict.get('disease'))
            elif Qstype == 'disease_drug':
                sql = self.sqlTransfer(Qstype, entity_dict.get('disease'))

            if sql:
                sql_dict['sql'] = sql
                sqls.append(sql_dict)

        return sqls


    # 针对不同问题，分开进行处理
    def sqlTransfer(self, Qstype, entities):
        if not entities:
            return []
        # 查询语句
        sql = []
        if Qstype == 'disease_symptom':
            # 已知疾病查症状
            sql = ["MATCH(m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '{0}' return n.name，m.name".format(i) for i in entities]
        elif Qstype == 'symptom_disease':
            # 已知症状查疾病
            sql = ["MATCH(m:Disease)-[r:has_symptom]->(n:Symptom) where n.name = '{0}' return m.name,n.name".format(i) for i in entities]
        elif Qstype == 'cause_disease':
            # 已知食物查疾病
            sql = ["MATCH(m:Disease)-[r:caused_by]->(n:Cause) where m.name = '{0}' return m.name, n.name".format(i) for i in entities]
        elif Qstype == 'disease_department':
            # 已知疾病查部门
            sql = ["MATCH(m:Disease)-[r:belongs_to]->(n:Department) where m.name = '{0}' return n.name, m.name".format(i) for i in entities]
        elif Qstype == 'disease_drug':
            # 已知疾病查药品
            sql = ["MATCH(m:Disease)-[r:cured_by]->(n:Drug) where m.name = '{0}' return n.name, m.name".format(i) for i in entities]
        return sql
