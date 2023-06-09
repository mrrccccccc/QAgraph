# 交互程序
from question_classifier import *
from question_parser import *
from answer_search import *

# 交互类
class Chat:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = "很抱歉，没有理解您的问题，我的词汇量有限"
        res_classify = self.classifier.classify(sent)   # 将用户输入的sent进行分类
        #print(res_classify)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        #print(res_sql)
        final_answers = self.searcher.search_main(res_sql)
        #print(final_answers)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = Chat()         #创建图
    while(1):
        sent = input()
        print(handler.chat_main(sent))