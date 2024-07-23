import re
import json

class Accuracy_Count():
    result_num = 0
    test_num = 0
    total_num = 0
    right_num = 0
    wrong_len_num = 0
    wrong_char_num = 0
    redundancy_num = 0
    correct_title = 0
    correct_title_75 = 0
    test_predicates = set()
    all_predicates = set()
    wrong_titles = []
    predicates = ['R_TRAPEZOID', 'QUADRILATERAL', 'RATIO', 'HYPOTHESES', 'POINT', 'TRIANGLE', 'EQ_TRIANGLE',
                      'SQUARE', 'CYCLIC', 'PRATIO', 'TRATIO', 'NRATIO',
                      'ON_LINE', 'ON_CIRCLE', 'MIDPOINT', 'R_TRIANGLE', 'ISO_TRIANGLE', 'ON_PLINE',
                      'ON_RCIRCLE', 'ON_TLINE', 'PARALLEL', 'LRATIO', 'EQUAL', 'EQANGLE', 'CON_TRIANGLE',
                      'SIM_TRIANGLE', 'EQ_PRODUCT', 'PERPENDICULAR', 'EQDISTANCE', 'ANGLE_BISECTOR', 'S_ANGLE',
                      'PARALLELOGRAM', 'RECTANGLE', 'LC_TANGENT', 'TRAPEZOID', 'CIRCLE', 'INTERSECTION_CC',
                      'INTERSECTION_LL', 'INTERSECTION_LC', 'CENTROID', 'ORTHOCENTER', 'CIRCUMCENTER', 'INCENTER']
    # 把所有行的谓词和字母提取出来变成一个字典，字典里的键是谓词，字典里的键值是包含了字母列表的列表，除了HYPOTHESES
    def extract_info(self, text, flag):
        info = {}
        for line in text.split('\n'):
            match = re.findall(r'\b([A-Z_]{2,})\b', line)  # 匹配大写单词，2表示至少两个字母
            if "SHOW" in info:
                break
            if match:
                predicate = match[0]
                letters = re.findall(r'\b([A-Z]|\d+)\b', line)  # 匹配单独出现的大写字母或数字
                if predicate == "SHOW":
                    if len(match) < 2:  # 检查match的长度,如果SHOW后面没有谓词就跳过
                        continue
                    else:
                        predicate = match[1]  # 如果出现show，则把后面一个谓词作为键，字母作为键值
                if predicate == "HYPOTHESES":
                    info[predicate] = []
                    continue
                if predicate == "EQUAL":  # EQUAL的添加都需要单独处理，因为添加的是字符串不是字母
                    equal_parts = line.split(' ')[1:]  # 使用空格分割字符串，并且去掉第一个元素（即"EQUAL"）
                    if predicate in info:
                        info[predicate].append(equal_parts)
                    else:
                        info[predicate] = [equal_parts]
                    if flag == 'result':  # 当解析的是预测结果时，result+1，解析的是测试集时，test+1
                        self.result_num += 1
                    else:
                        self.test_num += 1
                    self.total_num += 1
                    continue
                # 给谓词添加对应的字母
                if predicate in info:
                    info[predicate].append(letters)
                    if flag == 'result':
                        self.result_num += 1
                    else:
                        self.test_num += 1
                    self.total_num += 1
                else:
                    info[predicate] = [letters]
                    if flag == 'result':
                        self.result_num += 1
                    else:
                        self.test_num += 1
                    self.total_num += 1
                # 如果出现了show，直接break，防止有多个show的情况拉低准确率
                if match[0] == "SHOW":
                    break
        return info

    # 接收所有data，按行添加谓词
    def data_predicates_collection(self, data):
        self.test_predicates = set()
        self.all_predicates = set()
        for i in range(len(data)):
            self.predicates_collection(data[i])
        return self.test_predicates

    # 查看谓词列表
    def predicates_collection(self, text):
        # 提取信息
        if '解析' in text:
            info1 = self.extract_info(text['解析'], 'result')
        else:
            info1 = self.extract_info(text['response'], 'result')

        # 把测试集所有谓词加入集合输出，查看有多少谓词
        for key in info1.keys():
            if key in self.predicates:
                self.test_predicates.add(key)
            self.all_predicates.add(key)

    # 接收所有data，调用compare_texts按行比较
    def compare_data(self, data1, data2):
        for i in range(len(data2)):
            ac.compare_texts(data1[i], data2[i])

    # 封装每一次对谓词和后面字母整体的检查函数
    def check_all_predicateAndChar(self, predicate, wrong_predicates, info1, info2, check_method):
        if predicate in info1 and predicate in info2:
            for list1 in info1[predicate]:
                right_predicate_flag = False   # 设置一个标志位，如果正确就设置为True，每一个谓词结果只添加一次错误，而不是边比较边添加，导致一个谓词结果出现多次错误
                wrong_len_flag = False   # 设置一个标志位，如果是len错误，就变True
                predicate_str = predicate + " " + " ".join(list1)
                for list2 in info2[predicate]:
                    if len(list1) != len(list2):
                        wrong_len_flag = True
                        continue
                    if check_method(list1, list2):
                        right_predicate_flag = True
                if not right_predicate_flag:
                    wrong_predicates.append(predicate_str)  # 如果有错误的，就添加
                    self.wrong_char_num += 1
                else:
                    self.right_num += 1
                if wrong_len_flag and not right_predicate_flag:
                    self.wrong_len_num += 1

    # 把只在测试结果，不在测试集中的谓词都添加进去
    def redundancy_predicates_add(self, info1, info2, predicate, redundancy_predicates):
        if predicate in info1 and predicate not in info2:
            if predicate in ['PARALLELOGRAM', 'RECTANGLE', 'TRAPEZOID', 'CIRCLE', 'QUADRILATERAL', 'R_TRAPEZOID', 'TRIANGLE', 'EQ_TRIANGLE', 'SQUARE', 'R_TRIANGLE', 'ISO_TRIANGLE', 'PARALLEL', 'INTERSECTION_LL']:
                self.right_num += 1
            else:
                for i in info1[predicate]:
                    redundancy_predicates.append(predicate + " " + " ".join(i))
                    self.redundancy_num += 1


    def compare_texts(self, text1, text2):
        # 提取信息
        if '解析' in text1:
            info1 = self.extract_info(text1['解析'], 'result')
        else:
            info1 = self.extract_info(text1['response'], 'result')
        if '解析' in text2:
            info2 = self.extract_info(text2['解析'], 'test')
        else:
            info2 = self.extract_info(text2['response'], 'test')

        temp_right_num = self.right_num

        wrong_predicates = []
        redundancy_predicates = []
        # 不考虑顺序谓词列表
        predicates = ['POINT', 'TRIANGLE', 'EQ_TRIANGLE', 'SQUARE', 'CYCLIC']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.no_sequence)


        # 1考虑，23不考虑
        predicates = ['ON_LINE', 'ON_CIRCLE', 'MIDPOINT', 'R_TRIANGLE', 'ISO_TRIANGLE']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_1)


        # 1考虑，23不考虑，45考虑
        predicates = ['LRATIO']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_145)

        # 12，34分别不考虑，PCn的相对位置与ABm相对位置一致
        predicates = ['RATIO', 'PRATIO', 'TRATIO', 'NRATIO']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_56)

        # 1考虑，234不考虑
        predicates = ['CENTROID', 'ORTHOCENTER', 'CIRCUMCENTER', 'INCENTER']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.no_sequence234)

        # 1考虑，23，45不考虑，23，45组间考虑
        predicates = ['INTERSECTION_LC']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence2345)

        # 1考虑，23，45不考虑，23，45组间不考虑
        predicates = ['INTERSECTION_CC', 'INTERSECTION_LL']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.no_sequence2345)

        # 都考虑
        predicates = ['PARALLELOGRAM', 'RECTANGLE', 'LC_TANGENT', 'TRAPEZOID', 'CIRCLE', 'QUADRILATERAL', 'R_TRAPEZOID']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.all_sequence)

        # 13不考虑，2考虑，x考虑
        predicates = ['S_ANGLE']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_x)

        # 13考虑，24不考虑
        predicates = ['ANGLE_BISECTOR']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_13)

        # 12，34分别不考虑，组内不考虑，如果有5则考虑5
        predicates = ['PERPENDICULAR', 'EQDISTANCE', 'ON_PLINE', 'PARALLEL']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_5)

        # 12，34，56，78分别不考虑，1234组间不考虑，5678组间不考虑
        predicates = ['EQ_PRODUCT']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.no_sequence_12345678)

        # 14，25，36分别做set，然后与训练集做判断
        predicates = ['CON_TRIANGLE', 'SIM_TRIANGLE']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_vertical)

        # 13,46不考虑，2,5考虑
        predicates = ['EQANGLE']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_25)

        # 字符串判断，前一半和后一半是否分别相等,或交叉相等
        predicates = ['EQUAL']
        # 比较信息
        for predicate in predicates:
            # 把只在测试结果，不在测试集中的谓词都添加进去
            self.redundancy_predicates_add(info1, info2, predicate, redundancy_predicates)
            self.check_all_predicateAndChar(predicate, wrong_predicates, info1, info2, self.sequence_string)


        # 计算正确的题目数量有多少
        if self.right_num - temp_right_num == len(info2):
            self.correct_title += 1
        # 计算75%正确的题目有多少
        if (self.right_num - temp_right_num) / len(info2) >= 0.75:
            self.correct_title_75 += 1

        # 把多余的谓词和错误的谓词添加成一个列表中的两个列表元素
        title_wrong = []
        title_wrong.append(redundancy_predicates)
        title_wrong.append(wrong_predicates)
        # 每一个列表都是一道题的两种错误谓词
        self.wrong_titles.append(title_wrong)


    # 不考虑顺序的谓词
    def no_sequence(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        if set1 == set2:
            return True
        else:
            return False

    # 1考虑，23不考虑
    def sequence_1(self, list1, list2):
        set1 = set(list1[1:])
        set2 = set(list2[1:])
        if set1 == set2 and list1[0] == list2[0]:
            return True
        else:
            return False


    # 1考虑，23不考虑，45考虑
    def sequence_145(self, list1, list2):
        set1 = set(list1[1:3])
        set2 = set(list2[1:3])
        if set1 == set2 and list1[0] == list2[0] and list1[3:] == list2[3:]:
            return True
        else:
            return False

    # 12，34分别不考虑，PCn的相对位置与ABm相对位置一致
    def sequence_56(self, list1, list2):
        set1 = set(list1[0:2])
        set2 = set(list2[0:2])
        set3 = set(list1[2:4])
        set4 = set(list2[2:4])
        if set1 == set2 and set3 == set4 and list1[4:] == list2[4:]:
            return True
        # 如果list1 P C A B n m list2 A B P C m n 要求字母组对位相等，且数字也对位相等n == n， m == m
        if set1 == set4 and set2 == set3 and list1[4] == list2[5] and list1[5] == list2[4]:
            return True
        else:
            return False

    # 1考虑，234不考虑
    def no_sequence234(self, list1, list2):
        set1 = set(list1[1:])
        set2 = set(list2[1:])
        if set1 == set2 and list1[0] == list2[0]:
            return True
        else:
            return False

    # 1考虑，23，45不考虑，23，45组间不考虑
    def no_sequence2345(self, list1, list2):
        set1 = set(list1[1:3])
        set2 = set(list2[1:3])
        set3 = set(list1[3:])
        set4 = set(list2[3:])
        if (set1 == set2 and set3 == set4) or (set1 == set4 and set2 == set3) and list1[0] == list2[0]:
            return True
        else:
            return False

    # 1考虑，23，45不考虑，23，45组间考虑
    def sequence2345(self, list1, list2):
        set1 = set(list1[1:3])
        set2 = set(list2[1:3])
        set3 = set(list1[3:])
        set4 = set(list2[3:])
        if set1 == set2 and set3 == set4 and list1[0] == list2[0]:
            return True
        else:
            return False

    # 都考虑
    def all_sequence(self, list1, list2):
        n1 = len(list1)
        n2 = len(list2)
        for i in range(n1):
            if list1[i] != list2[i]:
                return False
        self.right_num += 1
        return True

    # 13不考虑，2考虑，x考虑
    def sequence_x(self, list1, list2):
        set1 = set(list1[0] + list1[2])
        set2 = set(list2[0] + list2[2])
        if set1 == set2 and list1[1] == list2[1] and list1[3] == list2[3]:
            return True
        else:
            return False

    # 13考虑，24不考虑
    def sequence_13(self, list1, list2):
        set1 = set(list1[1] + list1[3])
        set2 = set(list2[1] + list2[3])
        set3 = set(list1[1:3])
        set4 = set(list2[1:3])
        if set1 == set2 and list1[0] == list2[0] and list1[2] == list2[2]:
            return True
        else:
            return False

    # 12，34分别不考虑，组内不考虑，如果有5则考虑5
    def sequence_5(self, list1, list2):
        n1 = len(list1)
        set1 = set(list1[:2])
        set2 = set(list2[:2])
        set3 = set(list1[2:4])
        set4 = set(list2[2:4])
        if n1 == 4:
            if (set1 == set2 and set3 == set4) or (set1 == set4 and set2 == set3):
                return True
        elif n1 == 5:
            if (set1 == set2 and set3 == set4 and list1[4] == list2[4]) or (
                    set1 == set4 and set2 == set3 and list1[4] == list2[4]):
                return True
        else:
            return False

    # 12，34，56，78分别不考虑，1234组间不考虑，5678组间不考虑
    def no_sequence_12345678(self, list1, list2):
        set1 = set(list1[0:2])
        set2 = set(list2[0:2])
        set3 = set(list1[2:4])
        set4 = set(list2[2:4])
        set5 = set(list1[4:6])
        set6 = set(list2[4:6])
        set7 = set(list1[6:])
        set8 = set(list2[6:])
        if set1 == set2 and set3 == set4 and set5 == set6 and set7 == set8:  # list1前四个与list2前四个相等，list1后四个与list2后四个相等
            return True
        elif set1 == set4 and set2 == set3 and set5 == set6 and set7 == set8:  # 前两组交换
            return True
        elif set1 == set2 and set3 == set4 and set5 == set8 and set6 == set7:  # 后两组交换
            return True
        elif set1 == set4 and set2 == set3 and set5 == set8 and set6 == set7:  # 前后两组都交换
            return True
        elif set1 == set6 and set3 == set8 and set5 == set2 and set7 == set4:   # list1前四个与list2后四个相等，list1后四个与list2前四个相等
            return True
        elif set1 == set8 and set3 == set6 and set5 == set2 and set7 == set4:   # 前两个对调
            return True
        elif set1 == set6 and set3 == set8 and set5 == set4 and set7 == set2:   # 后两个对调
            return True
        elif set1 == set8 and set3 == set6 and set5 == set4 and set7 == set2:   # 前后两组都对调
            return True
        else:
            return False

    # 14，25，36分别做set，然后与训练集做判断
    def sequence_vertical(self, list1, list2):
        set1 = set(list1[:3])
        set2 = set(list2[:3])
        set3 = set(list1[3:])
        set4 = set(list2[3:])
        if not (set1 == set2 and set3 == set4 or set1 == set4 and set2 == set3):  # 当三个字母都对不上的时候直接返回False
            return False
        # 前三个和都三个字母都一样时，如ABC与BAC，DEF与EDF
        set1 = set(list1[0] + list1[3])
        set2 = set(list1[1] + list1[4])
        set3 = set(list1[2] + list1[5])
        set4 = set(list2[0] + list2[3])
        set5 = set(list2[1] + list2[4])
        set6 = set(list2[2] + list2[5])
        if not (set1 == set4 or set1 == set5 or set1 == set6):
            return False
        elif not (set2 == set4 or set2 == set5 or set2 == set6):
            return False
        elif not (set3 == set4 or set3 == set5 or set3 == set6):
            return False
        else:
            return True

    # 13,46不考虑，2,5考虑,1346组间顺序也不能变
    def sequence_25(self, list1, list2):
        set1 = set(list1[0] + list1[2])
        set2 = set(list1[3] + list1[5])
        set3 = set(list2[0] + list2[2])
        set4 = set(list2[3] + list2[5])
        # 考虑的是一种顺序 ABC DEF   CBA FED，要在下面加一种前后交换，交叉相等的判定
        # if (list1[1] != list2[1] and list1[4] != list2[4] or list1[1] != list2[4] and list1[4] != list1[1]) is not True:
        #     return False
        if set1 == set3 and set2 == set4:
            if list1[1] == list2[1] and list1[4] == list2[4]:
                return True
            else:
                return False
        if set1 == set4 and set2 == set3:
            if list1[1] == list2[4] and list1[4] == list2[1]:
                return True
            else:
                return False


        return False

    # 字符串判断，前一半和后一半是否分别相等,或交叉相等
    def sequence_string(self, list1, list2):
        if list1[0] == list2[0] and list2[1] == list2[1] or list1[0] == list2[1] and list1[1] == list2[0]:
            return True
        else:
            return False


# 比较两个数据中的谓词
def compare_two_predicate(data1, data2):
    print("data1中在已整理的谓词列表中的谓词有")
    predicates1 = ac.data_predicates_collection(data1)
    print(predicates1)
    print(len(predicates1))
    print("data1中所有谓词")
    all_predicates1 = ac.all_predicates
    print(all_predicates1)
    print(len(all_predicates1))
    print("data2中在已整理的谓词列表中的谓词有")
    predicates2 = ac.data_predicates_collection(data2)
    print(predicates2)
    print(len(predicates2))
    print("data2中所有谓词")
    all_predicates2 = ac.all_predicates
    print(all_predicates2)
    print(len(all_predicates2))

    predicates = set()
    for i in all_predicates1:
        if i not in all_predicates2:
            predicates.add(i)
    print("在1不在2中的谓词有：")
    print(predicates)

    predicates = set()
    for i in all_predicates2:
        if i not in all_predicates1:
            predicates.add(i)
    print("在2不在1中的谓词有：")
    print(predicates)

# 准确率计算
def accuracy(data1, data2, wrongwords_file = None):
    ac.compare_data(data1, data2)

    # # 测试
    # ac.compare_texts(text1, text2)
    # ac.compare_texts(text3, text4)
    accuracy = ac.right_num / ac.result_num
    recall = ac.right_num / ac.test_num
    print(f"所有谓词数量有：{ac.total_num}")
    print(f"正确的谓词数量有：{ac.right_num}")
    print(f"测试结果中有谓词个数：{ac.result_num}")
    print(f"测试集答案中有谓词个数：{ac.test_num}")
    print(f"字母长度错误的谓词个数：{ac.wrong_len_num}")
    print(f"字母错误(包括长度错误)的谓词个数：{ac.wrong_char_num}")
    print(f"多余谓词的个数：{ac.redundancy_num}")
    print(f"正确的题目数量：{ac.correct_title}")
    print(f"75%以上谓词正确的题目数量：{ac.correct_title_75}")
    print(f"准确率：{accuracy}")
    print(f"召回率：{recall}")
    # print(ac.wrong_titles)
    # 把每个题意多余谓词和错误谓词按行放入文件查看
    if not wrongwords_file:
        print("不生成错误谓词文件")
        return
    with open(wrongwords_file, 'w', encoding='utf-8') as f:
        for line in ac.wrong_titles:
            f.write(str(line[0]) + ' ' + str(line[1]) + '\n')
    print("错误谓词文件：" + wrongwords_file)


# 把测试结果的txt转为jsonl
def txt_to_jsonl(input_path, output_path):
    # 读取txt文件的内容
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 先把frac,overarc，Rt带{}的都替换为()
    pattern = re.compile(r'frac\{([^{}]+)\}\{([^{}]+)\}')
    content = pattern.sub(r'frac(\1)(\2)', content)
    pattern = re.compile(r'overarc\{([^{}]+)\}')
    content = pattern.sub(r'overarc(\1)', content)
    content = content.replace("text{Rt}", "text(Rt)")

    # 把单\换成双\\，要避免把\n的单反斜杠换成双
    content = content.replace("\\\\", "WW")
    content = content.replace('\\n', 'QQ')
    content = content.replace('\\', '\\\\')
    content = content.replace('WW', '\\\\')
    content = content.replace('QQ', '\\n')

    # 使用正则表达式提取花括号中的内容,re.DOTALL 标志，使正则表达式匹配跨行的文本re.MULTILINE 标志，以支持多行模式。
    pattern = re.compile(r'\{(.*?)\}', re.DOTALL | re.MULTILINE)
    matches = pattern.findall(content)

    # 转化为jsonl格式
    jsonl_data = []

    # 将匹配的字典修改格式后放入列表
    for match in matches:
        match = "{" + match + "}"  # 加上大括号

        # 替换解析一栏中的所有换行符
        raw_data = match
        # 找到解析那一栏的开始和结束位置
        start_pos = raw_data.find('"解析": "') + len('"解析": "')
        # 提取解析那一栏的内容
        parse_section = raw_data[start_pos:]
        # 替换解析内容中的换行符
        parse_section = parse_section.replace("\n", "\\n")
        # 将替换后的内容放回原始数据中
        match = raw_data[:start_pos] + parse_section

        # 把frac()重新换为frac{},overarc,text
        pattern = re.compile(r'frac\(([^()]+)\)\(([^()]+)\)')
        match = pattern.sub(r'frac{\1}{\2}', match)
        pattern = re.compile(r'overarc\(([^()]+)\)')
        match = pattern.sub(r'overarc{\1}', match)
        match = match.replace("text(Rt)", "text{Rt}text(Rt)")

        match = match.replace("'", '"')

        # print(match)
        jsonl_data.append(json.loads(json.dumps(match, ensure_ascii=False)))

    # 将jsonl数据写入文件
    with open(output_path, 'w', encoding='utf-8') as file:
        for line in jsonl_data:
            file.write(line + '\n')

# chatglm3生成的原始结果转化为能计算准确率的结果
def raw_jsonl_to_jsonl(input_file, output_file):
    # 打开原始jsonl文件
    with open(input_file, 'r', encoding='utf-8') as file_in:
        data = [json.loads(line) for line in file_in]

    # 提取response字段中的特定部分
    responses = []
    for item in data:
        response = item['response']
        if 'HYPOTHESES' not in response:
            responses.append(" ")
            continue
        if 'SHOW' not in response:
            match = re.search(r'HYPOTHESES.*', response, re.DOTALL)    # re.DOTALL代表让'.'匹配包括换行在内的所有字符。
            responses.append(match.group(0))
            continue
        match = re.search(r'HYPOTHESES.*SHOW.*\n?', response, re.DOTALL)
        if match:
            responses.append(match.group(0))

    # 将response字段写入新的jsonl文件
    with open(output_file, 'w', encoding='utf-8') as file_out:
        for response in responses:
            file_out.write(json.dumps({'解析': response}, ensure_ascii=False) + '\n')

# 删除输出中解析为一个空格的行
def delete_space_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file_in:
        data = [json.loads(line) for line in file_in]
    delete_data = []
    for item in data:
        if item['解析'] != ' ':
            delete_data.append(item)
    with open(output_file, 'w', encoding='utf-8') as file_output:
        for item in delete_data:
            file_output.write(json.dumps(item, ensure_ascii=False) + '\n')

# swift框架微调结果转为可用结果
def raw_jsonl_to_jsonl1(input_file, output_file):
    # 打开原始jsonl文件
    with open(input_file, 'r', encoding='utf-8') as file_in:
        data = [json.loads(line) for line in file_in]

    # 提取response字段中的特定部分
    responses = []
    for item in data:
        response = item['response'][0]
        if 'HYPOTHESES' not in response:
            responses.append(" ")
            continue
        if 'SHOW' not in response:
            match = re.search(r'HYPOTHESES.*', response, re.DOTALL)    # re.DOTALL代表让'.'匹配包括换行在内的所有字符。
            responses.append(match.group(0))
            continue
        match = re.search(r'HYPOTHESES.*SHOW.*\n?', response, re.DOTALL)
        if match:
            responses.append(match.group(0))

    # 将response字段写入新的jsonl文件
    with open(output_file, 'w', encoding='utf-8') as file_out:
        for response in responses:
            file_out.write(json.dumps({'解析': response}, ensure_ascii=False) + '\n')


# swift框架vllm微调结果转为可用结果
def raw_jsonl_to_jsonl_vllm(input_file, output_file):
    # 打开原始jsonl文件
    with open(input_file, 'r', encoding='utf-8') as file_in:
        data = [json.loads(line) for line in file_in]

    # 提取response字段中的特定部分
    responses = []
    for item in data:
        response = item['response']['response']
        if 'HYPOTHESES' not in response:
            responses.append(" ")
            continue
        if 'SHOW' not in response:
            match = re.search(r'HYPOTHESES.*', response, re.DOTALL)    # re.DOTALL代表让'.'匹配包括换行在内的所有字符。
            responses.append(match.group(0))
            continue
        match = re.search(r'HYPOTHESES.*SHOW.*\n?', response, re.DOTALL)
        if match:
            responses.append(match.group(0))

    # 将response字段写入新的jsonl文件
    with open(output_file, 'w', encoding='utf-8') as file_out:
        for response in responses:
            file_out.write(json.dumps({'解析': response}, ensure_ascii=False) + '\n')



# # 提示工程测试结果转为jsonl格式
# txt_to_jsonl('提示工程测试结果保存/8.17测试结果.txt', '提示工程测试结果保存/8.17测试结果.jsonl')
# 原始jsonl测试结果转为标准jsonl格式
# raw_jsonl_to_jsonl('chatglm3微调数据集/3_7_final_output.jsonl', 'chatglm3微调数据集/37_final_output.jsonl')
# raw_jsonl_to_jsonl1('qwen微调数据/qwen1half_72b_chat_1.jsonl', 'qwen微调数据/qwen1half_72b_chat_1_final.jsonl')

# # # 将vllm推理结果转为标准jsonl格式
# raw_jsonl_to_jsonl_vllm('新qwen1.5微调数据/qwen1half_new_9.jsonl', '新qwen1.5微调数据/qwen1half_new_9_final.jsonl')

# # 将vllm_revise推理结果转为标准jsonl格式
# raw_jsonl_to_jsonl_vllm('qwen微调数据/qwen1half_72b_chat_revise_6.jsonl', 'qwen微调数据/qwen1half_72b_chat_revise_6_final.jsonl')

# # 删除输出中解析为一个空格的行
# delete_space_jsonl("chatglm3微调数据集/37_output.jsonl", "chatglm3微调数据集/37_delete_output.jsonl")

ac = Accuracy_Count()
# 读取jsonl文件,第一个是测试结果，第二个是测试集
with open('提示工程测试结果保存/8.0测试结果.jsonl', 'r', encoding='utf-8') as f:
    data1 = [json.loads(line) for line in f]

with open('新版本训练集/新版测试集4.1.jsonl', 'r', encoding='utf-8') as f:
    data2 = [json.loads(line) for line in f]

# 比较两个数据的谓词，下面这两个功能不能同时运行，会给ac对象的属性加和两次
compare_two_predicate(data1, data2)

# # 计算两个数据的准确率等
# accuracy(data1, data2, '提示工程测试结果保存/8.17测试结果_wrongwords.jsonl')