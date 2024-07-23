# 首先把测试得到的txt文件转为jsonl文件
import re
import json


# 看两个jsonl中有哪些行不一样
def find_difference(file_path1, file_path2):
    # 读取jsonl文件
    with open(file_path1, 'r', encoding="utf-8") as f:
        lines1 = f.readlines()

    # 读取jsonl文件
    with open(file_path2, 'r', encoding="utf-8") as f:
        lines2 = f.readlines()

    # 将lines1中的每一行都转换为json对象，然后提取出题目
    titles1 = [json.loads(line)['题目'] for line in lines1]

    # 将lines2中的每一行都转换为json对象，然后提取出题目
    titles2 = [json.loads(line)['题目'] for line in lines2]

    # 只保留不在title2但在lines1中的行
    new_lines1 = []
    for line in lines1:
        json_line = json.loads(line)
        if json_line['题目'] not in titles2:
            new_lines1.append(line)

    # 只保留不在title1但在lines2中的行
    new_lines2 = []
    for line in lines2:
        json_line = json.loads(line)
        if json_line['题目'] not in titles1:
            new_lines2.append(line)

    # 将结果写回jsonl文件
    with open("test1.jsonl", 'w', encoding="utf-8") as f:
        for line in new_lines1:
            f.write(line)

    # 将结果写回jsonl文件
    with open("test2.jsonl", 'w', encoding="utf-8") as f:
        for line in new_lines2:
            f.write(line)


# 把提示工程中用到的训练题目从原始数据中剔除，得到测试集
def create_test(file_path1, file_path2, output_file):
    # 读取jsonl文件
    with open(file_path1, 'r', encoding="utf-8") as f:
        lines1 = f.readlines()

    # 读取jsonl文件
    with open(file_path2, 'r', encoding="utf-8") as f:
        lines2 = f.readlines()

    # 将lines1中的每一行都转换为json对象，然后提取出题目
    titles1 = [json.loads(line)['题目'] for line in lines1]

    # 只保留不在title1但在lines2中的行
    new_lines2 = []
    for line in lines2:
        json_line = json.loads(line)
        if json_line['题目'] not in titles1:
            new_lines2.append(line)

    # 将结果写回jsonl文件
    with open(output_file, 'w', encoding="utf-8") as f:
        for line in new_lines2:
            f.write(line)


# 去除jsonl中重复的行
def remove_duplicates(file_name, output_file):
    data = []
    unique_titles = set()

    # 读取jsonl文件
    with open(file_name, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    lines1 = [json.loads(line) for line in lines]

    for line in lines1:
        # 去除题目中的空格
        line['题目'] = line['题目'].replace(' ', '')

        # 去除题目最后一个字符的标点符号
        line['题目'] = re.sub(r'[^\w\s]$', '', line['题目'])

        # 去除题目开头的已知或已知后带有标点符号的部分
        line['题目'] = re.sub(r'^已知[^\w\s]*', '', line['题目'])
        line['题目'] = re.sub(r'^如图所示[^\w\s]*', '', line['题目'])
        line['题目'] = re.sub(r'^如图[^\w\s]*', '', line['题目'])


        # 如果题目不在unique_titles中，则添加到data和unique_titles中
        if line['题目'] not in unique_titles:
            unique_titles.add(line['题目'])
            data.append(line)

    with open(output_file, 'w', encoding="utf-8") as f:
        for line in data:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')


# 把解析删掉，生成只有题目的测试集
def remain_title(file_path1, file_path2):
    # 读取jsonl文件
    with open(file_path1, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    # 删除其他字段，只保留题目和解析
    for item in data:
        if 'parse' in item:
            del item['parse']

    # 将修改后的数据写回jsonl文件
    with open(file_path2, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


# 能找到独立的INT，通过正则表达式区分开POINT等其他谓词
def find_alone_predicate():
    jsonl_list = []
    with open('训练集与测试集/新训练集.jsonl', 'r', encoding='utf-8') as f:
        for item in f:
            jsonl_list.append(json.loads(item))

    for item in jsonl_list:
        hypo = item["解析"]
        if re.search(r'\bINT\b', hypo):
            print(item)


import random


# 随机选取nums个题做测试集
def random_select_test(input_file, output_file, nums):
    jsonl_list = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for item in f:
            jsonl_list.append(json.loads(item))
    random_samples = random.sample(jsonl_list, nums)
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in random_samples:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

# 把英文txt文件转为标准jsonl格式,但是存在一部分前双引号后单引号的内容
def en_txt_title_to_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 创建一个空的列表来存储修改后的行
    new_lines = []

    # 遍历文件的每一行
    for line in lines:
        # 使用正则表达式匹配双引号中的内容
        match = re.search(r'"(.*?)"', line)
        if match:
            # 如果找到匹配，将其替换为新的格式
            new_line = "{'Problem': '" + match.group(1) + "'}" + "\n"
            new_lines.append(new_line)
        else:
            # 如果没有找到匹配，保留原始的行
            new_line = line
            new_lines.append(new_line)

    # 将修改后的行写回文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in new_lines:
            f.write(line)


# en_txt_title_to_jsonl('训练集与测试集/新训练集_英文题目.txt', '训练集与测试集/新训练集_英文题目2.txt')

# 继续把非标准txt转为标准jsonl格式，其中有部分缺失后单引号为手工添加
def txt_title_to_jsonl():
    # 读取txt文件
    with open('训练集与测试集/新训练集_英文题目1.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # 将所有单引号转为双引号
    content = content.replace('\'', '\"')

    # 将所有的双反斜杠转为AAA
    content = content.replace('\\\\', 'AAA')
    content = content.replace('\\', '\\\\')
    content = content.replace('AAA', '\\\\')

    content = content.replace('$$', 'BBB')
    content = content.replace('$', '$$')
    content = content.replace('BBB', '$$')

    # 将所有的"题目"变为"Problem"
    content = content.replace('题目', 'Problem')

    # 将字符串转为字典列表
    dict_list = [json.loads(line) for line in content.split('\n') if line]

    # 写入到jsonl文件
    with open('训练集与测试集/新训练集_仅英文题目.jsonl', 'w', encoding='utf-8') as f:
        for d in dict_list:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')

# txt_title_to_jsonl()

# 把完全处理好的jsonl英文题目，与解析合并为新训练集英文版
def merge_en_title():
    with open('训练集与测试集/新训练集_仅英文题目.jsonl', 'r', encoding='utf-8') as f1:
        data1 = [json.loads(line) for line in f1]
    with open('训练集与测试集/新训练集.jsonl', 'r', encoding='utf-8') as f2:
        data2 = [json.loads(line) for line in f2]
    for i in range(len(data2)):
        data1[i]['parse'] = data2[i]['解析']
    with open('训练集与测试集/新训练集_en.jsonl', 'w', encoding='utf-8') as f:
        for line in data1:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')


def find_duplicates(file_name):
    data = []
    titles = {}
    with open(file_name, 'r', encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if item['题目'] not in titles:
                titles[item['题目']] = line
                data.append(line)
            else:
                print("以下是重复的题目：")
                print("第一次出现：", titles[item['题目']])
                print("第二次出现：", line)

# 把生成结果的解析放入测试集，用于测试新的微调模型
def add_title_to_jsonl(input_file1, input_file2, output_file):
    with open(input_file1, 'r', encoding='utf-8') as file_in1:
        data1 = [json.loads(line) for line in file_in1]
    with open(input_file2, 'r', encoding='utf-8') as file_in2:
        data2 = [json.loads(line) for line in file_in2]
    for i in range(len(data1)):
        data2[i]['解析'] = data1[i]['解析']
    with open(output_file, 'w', encoding='utf-8') as file_output:
        for item in data2:
            file_output.write(json.dumps(item, ensure_ascii=False) + '\n')


def divide_train(input_file, output_file1, output_file2, output_file3):
    with open(input_file, 'r', encoding='utf-8') as file_in:
        data = [json.loads(line) for line in file_in]
    data1 = data[:247]
    data2 = data[247:494]
    data3 = data[494:]

    # 拆分字典并保存
    for i, data in enumerate([data1, data2, data3]):
        output_file = [output_file1, output_file2, output_file3][i]
        with open(output_file, 'w', encoding='utf-8') as file_out:
            for d in data:
                file_out.write(json.dumps({"题目": d["题目"]}, ensure_ascii=False) + '\n')
                file_out.write(json.dumps({"解析": d["解析"]}, ensure_ascii=False) + '\n')


# 合成单个文件
def merge_file(input_file, output_file):
    data = []
    with open(input_file, 'r', encoding='utf-8') as file_in:
        lines = file_in.readlines()
        for i in range(0, len(lines), 2):
            question = json.loads(lines[i])
            answer = json.loads(lines[i+1])
            data.append({**question, **answer})

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for d in data:
            file_out.write(json.dumps(d, ensure_ascii=False) + '\n')
# # 找到题目重复的行
# find_duplicates('test1.jsonl')
# merge_en_title()
# find_alone_predicate()


# find_difference("训练集与测试集/新训练集.jsonl", "提示工程测试集与训练集/训练集1.6（提示工程）.jsonl")
remove_duplicates('新版本训练集/新版数据集.jsonl', '新版本训练集/新版数据集3.0.jsonl')
random_select_test('新版本训练集/新版数据集3.0.jsonl', '新版本训练集/新版测试集4.2.jsonl', 100) # 从所有数据集中随机选择100个作为测试集
create_test("新版本训练集/新版测试集4.2.jsonl", '新版本训练集/新版数据集3.0.jsonl', '新版本训练集/新版训练集4.2.jsonl') # 把提示工程中用到的训练题目从原始数据中剔除，得到测试集
# remain_title("qwen微调数据/测试集4.1.jsonl", 'qwen微调数据/测试集4.1仅答案.jsonl')
# add_title_to_jsonl("chatglm3微调数据集/37_delete_output.jsonl", "提示工程测试集与训练集/测试集1.5_delete.jsonl", "chatglm3微调数据集/37_test.jsonl")
# divide_train('训练集与测试集/新训练集.jsonl', '新版本训练集/训练集1.jsonl', '新版本训练集/训练集2.jsonl', '新版本训练集/训练集3.jsonl')
# merge_file('新版本训练集/所有问题集.jsonl', '新版本训练集/所有问题集_merged.jsonl')