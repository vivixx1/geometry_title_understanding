import requests
import json
from Bert_KNN import knn_title, random_title, knn_title_threshold, choose_threshold

def call_gpt4_api(messages, temperature=0.1):
    # API接口的URL
    url = "your end point url"
    api_key = "your azure api key"

    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # 请求的数据
    data = {
        "messages": messages,
        "temperature": temperature
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)

    # 检查响应状态
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def send_message(question, file_path, knn_titles=''):
    print("query: " + question + "\n")
    messages = [{"role": "system", "content": get_system_prompt(question, knn_titles)}, {"role": "user", "content": question}]
    assistant_reply = call_gpt4_api(messages)
    if assistant_reply:
        print("\nresponse: \n" + assistant_reply + "\n")
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(assistant_reply + "\n")

def get_system_prompt(title, knn_titles):
    system_prompt = """请你作为一名平面几何数学专家来协助我解析几何题目，首先找出题目中包含如点、线段、圆、多边形等几何实体，然后找出题目中平行，垂直，点在线上，点在多边形上等几何关系，并且都转化为构造语句
请按照我给你的例子中的格式，将题目填写在题目一栏，归纳出的几何关系填写在解析一栏中。
需要注意的是每道题只有一个待证结论，请写在解析一栏的SHOW中。
例子:
输入题目：{"题目": "如图，在矩形$$ABCD$$中,点$$E$$是$$AD$$的中点,过$$A$$,$$E$$,$$C$$三点的圆交直线$$CD$$于另一点$$F$$.求证:$$AF \\bot BE$$."}
输出：
{"题目": "如图，在矩形$$ABCD$$中,点$$E$$是$$AD$$的中点,过$$A$$,$$E$$,$$C$$三点的圆交直线$$CD$$于另一点$$F$$.求证:$$AF \\bot BE$$.", "解析": " HYPOTHESES: \nPOINT A B C D E F\nRECTANGLE A B C D\nMIDPOINT E A D\nCIRCUMCENTER O A E C\nON_LINE F C D\nON_CIRCLE F O A\nSHOW: PERPENDICULAR A F B E"}
我将给你一组构造语句以及对应几何关系的含义供你学习
构造语句 | 几何关系
POINT A	| 构造一个自由点A
ON_LINE C A B | C在直线AB上
ON_CIRCLE C A B	| C在圆AB上
PERPENDICULAR A B C D | AB垂直CD
MIDPOINT O A B | O是线段AB的中点
INTERSECTION_LC E A B C D | E是直线AB和圆CD的交点
INTERSECTION_LL E A B C D | E是直线AB和直线CD的交点
EQANGLE F E B E B C	| 约束∠FEB与∠EBC相等，其中E，B为角的顶点
CIRCLE A B | 以A为圆心，B为圆上一点做一个圆
TRIANGLE A B C | A,B,C组成了一个三角形
R_TRIANGLE A B C | 直线AB与AC交于点A，角CAB为直角的直角三角形
ISO_TRIANGLE A B C | 等腰三角形ABC，AB=AC
EQ_TRIANGLE A B C | AB=BC=CA,∠ABC=∠CAB=∠BCA=60°
PARALLELOGRAM A B C D | ABCD是平行四边形
RECTANGLE A B C D | ABCD是长方形
SQUARE A B C D | ABCD是正方形
S_ANGLE A B C x	| ∠ABC的度数为x度
ANGLE_BISECTOR D A B C | 角ABC的角平分线为DB
LC_TANGENT A B O | AB是以O为圆心、OB为半径的圆的切线
PARALLEL A B C D | AB∥CD
RATIO A F C F 1 2 | AF：FC=1：2
EQDISTANCE A B C D | AB与CD长度相等
EQ_PRODUCT A B A B B C B D | 两条边相乘与另两条边相乘相等AB*AB = BC*BD只能用于待证结论
CON_TRIANGLE A B C D E F | △ABC≌△DEF
SIM_TRIANGLE A B C D E F | △ABC∽△DEF
接下来我会给你一组题目和几何关系供你学习参考\n"""
    # system_prompt = system_prompt + '\n'.join(knn_title_threshold(title, 40, 0.037))  # 旧版阈值选择
    # system_prompt = system_prompt + '\n'.join(knn_title(title, 40))   # knn题目
    system_prompt = system_prompt + '\n'.join(random_title(40))    # 随机最近邻题目
    # system_prompt = system_prompt + knn_titles  # 模拟退火版prompt
    system_prompt = system_prompt + '\n'
    system_prompt += """下面我将给出一道几何数学题，请你模仿上面给出的例子得到结果。
注意事项:请使用上面提供的所有构造语句，不要使用没有提供的构造语句"""
    return system_prompt

# 模拟退火阈值版knn
# if __name__ == "__main__":
#     with open("新版本训练集/新版测试集4.1.jsonl", "r", encoding="utf-8") as file:
#         data = [json.loads(line) for line in file]
#     best_knn_titles = choose_threshold("新版本训练集/新版测试集4.1.jsonl", 40)
#     for i in range(len(data)):
#         question = data[i]['题目']
#         question = str(question)
#         knn_title = '\n'.join(best_knn_titles[i])
#         send_message(question, "提示工程测试结果保存/8.1测试结果.txt", knn_title)

# 随机和普通knn版
if __name__ == "__main__":
    with open("新版本训练集/新版测试集4.1.jsonl", "r", encoding="utf-8") as file:
        data = [json.loads(line) for line in file]
    for item in data:
        question = item['题目']
        question = str(question)
        send_message(question, "提示工程测试结果保存/8.17测试结果.txt")




