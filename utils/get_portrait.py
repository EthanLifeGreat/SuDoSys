import json


def get_portrait(portrait_id):
    # read json
    with open('seeds.json', 'r', encoding='utf-8') as file:
        seeds = json.load(file)
    try:
        portrait = next((seed for seed in seeds if seed["id"] == portrait_id))
        # 拼接字符串
        portrait_str = "当前情绪：" + str(portrait['当前情绪']) + "，当前症状表现：" + str(portrait['当前症状表现']) + "，困扰和压力来源：" + str(portrait['困扰和压力来源'])
        portrait_str += "推测年龄：" + str(portrait['推测年龄']) + "，性别：" + str(portrait['推测性别']) + "，既往心理健康史：" + str(portrait['既往心理健康史'])
        portrait_str += "生活习惯：" + str(portrait['生活习惯']) + "，职业：" + str(portrait['职业']) + "，个人爱好和兴趣：" + str(portrait['个人爱好和兴趣'])
    except StopIteration:
        return ""

    return portrait_str
