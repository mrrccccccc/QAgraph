from py2neo import Graph


class AnswerSearcher:
    def __init__(self):
        self.g = Graph("http://localhost:7474",user="neo4j",password="wodeshengri5031",name="neo4j")
        self.numLimit = 30  #最多显示30个字符

    # 执行sql查询
    def search_main(self, sqls):
        final_answers = []
        for sql_dict in sqls:
            Qstype = sql_dict['question_types']
            queries = sql_dict['sql']
            answers = []
            for query in queries:
                res = self.g.run(query).data()
                answers += res
            #print(answers)
            final_answer = self.answerPrettify(Qstype, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    # 根据对应的question type，调用回复模板
    def answerPrettify(self, Qstype, answers):
        final_answer = []
        if not answers:
            return ''
        elif Qstype == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括：{1}'.format(subject, ': '.join(list(set(desc))[:self.numLimit]))

        elif Qstype == 'symptom_disease':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '如果您有{1}的症状，可能患有{0}'.format(subject, ': '.join(list(set(desc))[:self.numLimit]))

        elif Qstype == 'disease_department':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}病症需要去往{1}就医'.format(subject, ': '.join(list(set(desc))[:self.numLimit]))

        elif Qstype == 'cause_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}等原因可能会导致{1}'.format(subject, ': '.join(list(set(desc))[:self.numLimit]))

        elif Qstype == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}病症推荐药物为：{1}'.format(subject, ': '.join(list(set(desc))[:self.numLimit]))
        return final_answer
