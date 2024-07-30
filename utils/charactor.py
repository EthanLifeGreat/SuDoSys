import json


def genCharactor(charactorid):
    #读json
    with open('seeds.json', 'r', encoding='utf-8') as file:
        seeds = json.load(file)
    try:
        charactor = next((seed for seed in seeds if seed["id"] == charactorid))
        # 拼接字符串
        charactorInfo = "当前情绪：" + str(charactor['当前情绪']) + "，当前症状表现：" + str(charactor['当前症状表现']) + "，困扰和压力来源：" + str(charactor['困扰和压力来源'])
        charactorInfo += "推测年龄：" + str(charactor['推测年龄']) + "，性别：" + str(charactor['推测性别']) + "，既往心理健康史：" + str(charactor['既往心理健康史'])
        charactorInfo += "生活习惯：" + str(charactor['生活习惯']) + "，职业：" + str(charactor['职业']) + "，个人爱好和兴趣：" + str(charactor['个人爱好和兴趣'])
    except StopIteration:
        return ""

    return charactorInfo