import numpy as np
import json
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn import metrics
from transformers import BertTokenizer, BertConfig
from transformers import BertModel
import time
import os
# import matplotlib.pyplot as plt
import random

# # 导入分词器，模型配置，向量化后的训练集
# def bert_config():
start_time = time.time()

# 定义两个路径
BERT_PATH = 'D:/办公/自动出题/Bert_Base/bert-base-chinese'
ALTERNATIVE_PATH = 'C:/myApplication/bert-base-chinese/bert-base-chinese'

# 检查BERT_PATH是否存在
if os.path.exists(BERT_PATH):
    # 如果存在，使用BERT_PATH
    print(f"使用路径：{BERT_PATH}")
elif os.path.exists(ALTERNATIVE_PATH):
    # 如果不存在，使用ALTERNATIVE_PATH
    print(f"使用备用路径：{ALTERNATIVE_PATH}")
    BERT_PATH = ALTERNATIVE_PATH
else:
    print("路径不存在")


# a. 通过词典导入分词器
tokenizer = BertTokenizer.from_pretrained(BERT_PATH)
# b. 导入配置文件
model_config = BertConfig.from_pretrained(BERT_PATH)
# 修改配置
model_config.output_hidden_states = True
model_config.output_attentions = True
# 通过配置和路径导入模型
bert_model = BertModel.from_pretrained(BERT_PATH, config=model_config)


# 读取jsonl文件
with open('新版本训练集/新版训练集4.1.jsonl', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

# 将文本向量化
if not os.path.exists('text_embeddings_5.0.npy'):
    text_embeddings = []
    for item in data:
        text = item['题目'] + ' ' + item['解析']
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        outputs = bert_model(**inputs)
        text_embeddings.append(outputs.last_hidden_state.mean(dim=1).detach().numpy())
    text_embeddings = np.concatenate(text_embeddings)
    np.save('text_embeddings_5.0.npy', text_embeddings)
else:
    text_embeddings = np.load('text_embeddings_5.0.npy')


embedding_time = time.time() - start_time
# print(f"向量化所需时间：{embedding_time}")

def knn_title(title, knn_nums):
    # 将输入的题目向量化
    inputs = tokenizer(title, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = bert_model(**inputs)
    title_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()

    # 使用knn找到最相近的41个题目
    knn = NearestNeighbors(n_neighbors=knn_nums, metric='cosine')
    knn.fit(text_embeddings)
    distances, indices = knn.kneighbors(title_embedding)

    # 返回最相近的knn_nums个题目和解析
    return [str(data[i]) for i in indices[0]]

def knn_title_threshold(title, knn_nums, threshold):
    # 将输入的题目向量化
    inputs = tokenizer(title, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = bert_model(**inputs)
    title_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()

    # 找到最相近的题目knn_nums个题目
    knn = NearestNeighbors(n_neighbors=knn_nums, metric='cosine')
    knn.fit(text_embeddings)
    distances, indices = knn.kneighbors(title_embedding)

    # 根据阈值筛选结果
    indices_threshold = indices[distances > threshold]
    distances_threshold = distances[distances > threshold]

    print(indices_threshold.shape[0])
    # 如果筛选后的题目数量少于3个，就从原始的knn结果中取前3个，至少要保留3个题目
    if indices_threshold.shape[0] < 3:
        indices_threshold = indices.flatten()[:3]
        distances_threshold = distances.flatten()[:3]

    indices_threshold = indices_threshold.flatten()

    if indices_threshold.shape[0] == 3:
        print(indices_threshold.shape[0])
    # print(indices_threshold.shape)
    # 返回最相近的knn_nums个题目和解析
    return [str(data[i]) for i in indices_threshold]

    # 根据阈值筛选结果
    # num_threshold = int(len(distances[0]) * threshold)
    # sorted_indices = [x for _, x in sorted(zip(distances[0], indices[0]))]
    # indices = sorted_indices[:num_threshold]
    #
    # # print(len(indices))
    # # 返回最相近的knn_nums个题目和解析
    # return [str(data[i]) for i in indices]

def random_title(random_nums):
    random_titles = random.sample(data, random_nums)
    return str(random_titles)

import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from transformers import BertTokenizer, BertModel
import random

# 使用模拟退火算法选择阈值
def choose_threshold(input_file, knn_nums, max_iterations=100, initial_temp=100.0, cooling_rate=0.99):
    with open(input_file, "r", encoding="utf-8") as file:
        data = [json.loads(line) for line in file]

    # 计算所有题目的嵌入
    embeddings = []
    for item in data:
        question = item['题目']
        question = str(question)
        inputs = tokenizer(question, return_tensors='pt', padding=True, truncation=True, max_length=512)
        outputs = bert_model(**inputs)
        title_embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        embeddings.append(title_embedding)

    embeddings = np.vstack(embeddings)

    # 计算所有题目的最近邻距离
    knn = NearestNeighbors(n_neighbors=knn_nums, metric='cosine')
    knn.fit(embeddings)
    distances, indices = knn.kneighbors(embeddings)

    # 预先存储所有题目的距离
    distances_dict = {i: distances[i] for i in range(len(data))}
    print("距离计算完成")

    # 计算每道题最近邻题目的距离范围的中间值
    median_distances = [np.median(distances_dict[i]) for i in distances_dict]
    initial_threshold = np.median(median_distances)

    def get_knn_list(threshold):
        knn_list = []
        for i in range(len(data)):
            count = np.sum(distances_dict[i] > threshold)
            knn_list.append(count)
        return knn_list

    def cost_function(knn_list):
        std_knn = np.std(knn_list)
        mean_knn = np.mean(knn_list)
        if mean_knn >= (knn_nums * 4 / 5) or mean_knn <= (knn_nums * 2 / 5):
            return float('inf')
        return std_knn

    # 模拟退火参数
    temperature = initial_temp
    current_threshold = initial_threshold
    current_knn_list = get_knn_list(current_threshold)
    current_cost = cost_function(current_knn_list)
    best_threshold = current_threshold
    best_knn_list = current_knn_list
    best_cost = current_cost

    for iteration in range(max_iterations):
        # 随机选择新的阈值
        new_threshold = current_threshold + random.uniform(-0.01, 0.01)
        new_knn_list = get_knn_list(new_threshold)
        new_cost = cost_function(new_knn_list)

        # 判断是否接受新的阈值
        if new_cost < current_cost or random.uniform(0, 1) < np.exp((current_cost - new_cost) / temperature):
            current_threshold = new_threshold
            current_knn_list = new_knn_list
            current_cost = new_cost

        # 更新最佳解
        if new_cost < best_cost:
            best_threshold = new_threshold
            best_knn_list = new_knn_list
            best_cost = new_cost

        # 降低温度
        temperature *= cooling_rate

        # 打印进度
        if iteration % 5 == 0:
            print(f"Iteration {iteration}: Best Cost = {best_cost}, Best Threshold = {best_threshold}")

    # 获取最佳阈值下的最近邻题目列表
    def get_knn_titles(threshold):
        knn_titles = []
        for i in range(len(data)):
            indices_threshold = indices[i][distances[i] > threshold]
            distances_threshold = distances[i][distances[i] > threshold]
            if len(indices_threshold) < 3:
                indices_threshold = indices[i][:3]
                distances_threshold = distances[i][:3]
            knn_titles.append([str(data[j]) for j in indices_threshold])
        return knn_titles

    best_knn_titles = get_knn_titles(best_threshold)

    print(f"最佳knn题目数量列表{best_knn_list}")
    print(f"最佳阈值{best_threshold}")
    print(f"均值为{np.mean(best_knn_list)}")
    print(f"标准差为{best_cost}")
    # print(best_knn_titles)
    return best_knn_titles
    # return best_knn_list, best_threshold

# # 示例调用
# input_file = "新版本训练集/新版测试集4.1.jsonl"
# knn_nums = 50
# best_knn_titles = choose_threshold(input_file, knn_nums)
#
# print(f"Best Threshold: {best_threshold}")
# print(f"Best KNN List: {best_knn_list}")

# random_title(40)
# # 测试函数
# title = "如图，在矩形$$ABCD$$中,点$$E$$是$$AD$$的中点,过$$A$$,$$E$$,$$C$$三点的圆交直线$$CD$$于另一点$$F$$.求证:$$AF \\bot BE$$."
# similar_titles = knn_title(title,5)
# print(similar_titles)

# # 测试函数
# title = "在Rt$$\triangle ABC$$中，$$\angle ACB = 90^\circ$$，$$F$$是边$$AB$$上一点，且$$CB=CF$$，过点$$A$$作$$CF$$的垂线，交$$CF$$的延长线于点$$D$$，求证：$$\triangle ADF \sim \triangle ACB$$."
# similar_titles = knn_title_threshold(title, 30, 0.08)
# print(similar_titles)
