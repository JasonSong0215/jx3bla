import csv

d={
'2021-04-23-23-22-40_赵八嫂_1258.fstt.jx3dat': ['十七年蝉', '轻安', '许仙敢玩蛇', '牡丹鱼片', '烟团团', '山河逆流舞', '残魂影', '唐郁', '就是辣个秀秀', '八岁想吃糖', '空尘羽', '蝉息', '莫莫莫玄雨', '椋然然', '溯未未未', '我变卦怎么了', '唐欣心', '鹤知州@唯我独尊', '是樱桃吖', '花秋裳', '半壶西凤酒', '左渭雨@飞鸢泛月', '陆溟焱', '园子', '不吃橘子皮'], 
'2021-04-24-22-55-44_海荼_420.fstt.jx3dat': ['半壶西凤酒', '鹤知州@唯我独尊', '轻安', '左渭雨@飞鸢泛月', '沧歌歌', '残魂影', '莫莫莫玄雨', '烟团团', '许仙敢玩蛇', '大桔', '是樱桃吖', '空尘羽', '柒酱酱', '不吃橘子皮', '我变卦怎么了', '塔罗占卜小人', '唐欣心', '陆溟焱', '八岁想吃糖', '落星惊鸿', '十七年蝉', '风过无音', '椋然然', '就是辣个秀秀', '花秋裳'], 
'2021-04-25-22-31-42_姜集苦_369.fstt.jx3dat': ['谢山河', '十七年蝉', '烟团团', '风过无音', '唐郁', '就是辣个秀秀', '空尘羽', '左渭雨@飞鸢泛月', '蝉息', '椋然然', '我变卦怎么了', '唐欣心', '柒酱酱', '鹤知州@唯我独尊', '是樱桃吖', '花秋裳', '半壶西凤酒', '八岁大魔王', '陆溟焱', '轻安', '狗宝宝', '沧歌歌', '莫莫莫玄雨', '不吃橘子皮', '许仙敢玩蛇'], 
'2021-04-30-23-14-24_宇文灭_146.fstt.jx3dat': ['鹤知州@唯我独尊', '枫竹竹', '轻安', '花秋裳', '左渭雨@飞鸢泛月', '狗宝宝', '沧歌歌', '沉星夜', '残魂影', '莫莫莫玄雨', '唐郁', '许仙敢玩蛇', '空尘羽', '柒酱酱', '陆太清', '谢山河', '酷发发小清羽', '陆溟焱', '不吃橘子皮', '山河逆流舞', '凌落九天', '解战袍', '椋然然', '溯未未未', '人工模拟智能'], 
'2021-05-01-21-52-59_宇文灭_497.fstt.jx3dat': ['鹤知州@唯我独尊', '轻安', '花秋裳', '左渭雨@飞鸢泛月', '狗宝宝', '沉星夜', '残魂影', '莫莫莫玄雨', '一糯', '唐郁', '许仙敢玩蛇', '谁于吾欢颜', '空尘羽', '凌落九天', '谢山河', '八岁大魔王', '酷发发小清羽', '羡渔@幽月轮', '蝉息', '陆溟焱', '您配玩霸刀么', '解战袍', '歆羡羡', '溯未未未', '不吃橘子皮'], 
'2021-05-08-22-17-07_宫威_120.fstt.jx3dat': ['裴玄煜', '鹤知州@唯我独尊', '轻安', '玉漱倾城', '太傻了', '沉星夜', '太酷了', '唐郁', '许仙敢玩蛇', '小相遇', '葡萄酸奶', '寒月妖梦@破阵子', '谢山河', '我变卦怎么了', '羡渔@幽月轮', '陆溟焱', '凌落九天', '阿白和你拼了', '左渭雨@飞鸢泛月', '淼渺喵', '您配玩霸刀么', '橙头焚影@绝代天骄', '橙头冰心@绝代天骄', '溯未未未', '息曲'], 
'2021-05-10-22-56-25_宫威_117.fstt.jx3dat': ['寒翻蛱蝶翎', '轻安', '左渭雨@飞鸢泛月', '沉星夜', '残魂影', '一糯', '唐郁', '烟团团', '许仙敢玩蛇', '空尘羽', '不吃橘子皮', '寒月妖梦@破阵子', '谢山河', '溯未未未', '羡渔@幽月轮', '蝉息', '陆溟焱', '凌落九天', '明屿', '孤竹寒潭', '您配玩霸刀么', '椋然然', '千面红尘', '璃衣', '莫莫莫玄雨'], 
'2021-05-12-22-55-13_宫威_203.fstt.jx3dat': ['寒翻蛱蝶翎', '鹤知州@唯我独尊', '轻安', '左渭雨@飞鸢泛月', '狗宝宝', '沉星夜', '残魂影', '未书', '莫莫莫玄雨', '一糯', '唐郁', '陆荼', '不吃橘子皮', '凌落九天', '璃衣', '寒月妖梦@破阵子', '羡渔@幽月轮', '蝉息', '陆溟焱', '水龙头', '明屿', '您配玩霸刀么', '烟团团', '千面红尘'], 
'2021-05-13-22-46-31_宫威_181.fstt.jx3dat': ['鹤知州@唯我独尊', '与山举杯', '相望', '左渭雨@飞鸢泛月', '沧歌歌', '沉星夜', '未书', '莫莫莫玄雨', '一糯', '唐郁', '烟团团', '糖炮', '不吃橘子皮', '璃衣', '离墨墨', '陆溟焱', '寒月妖梦@破阵子', '紫授朱衣', '您配玩霸刀么', '凌落九天', '旧友', '花渐开', '许仙敢玩蛇'], 
'2021-05-17-22-58-29_宫威_128.fstt.jx3dat': ['寒翻蛱蝶翎', '酒间行@幽月轮', '鹤知州@唯我独尊', '轻安', '花秋裳', '左渭雨@飞鸢泛月', '沉星夜', '残魂影', '未书', '莫莫莫玄雨', '唐郁', '烟团团', '空尘羽', '不吃橘子皮', '璃衣', '羡渔@幽月轮', '凌落九天', '寒月妖梦@破阵子', '健心心', '您配玩霸刀么', '一糯', '饮酒疏狂', '溯未未未', '雪爹@剑胆琴心', '陆溟焱'], 
'2021-05-19-22-38-10_宫威_235.fstt.jx3dat': ['寒翻蛱蝶翎', '涯角', '轻安', '花秋裳', '左渭雨@飞鸢泛月', '残魂影', '未书', '一糯', '唐郁', '烟团团', '许仙敢玩蛇', '陆溟焱', '顾飞卿', '健心心', '不吃橘子皮', '璃衣', '沉星夜小时候', '萧雨落', '羡渔@幽月轮', '凌落九天', '寒月妖梦@破阵子', '水龙头', '溯未未未', '流血的尾巴', '鹤知州@唯我独尊'], 
'2021-05-20-22-48-18_宫威_670.fstt.jx3dat': ['水龙头', '狗宝宝', '健心心', '烟团团', '沉星夜小时候', '涯角', '残魂影', '璃衣', '左渭雨@飞鸢泛月', '蝉息', '萧雨落', '不吃橘子皮', '寒月妖梦@破阵子', '溯未未未', '鹤知州@唯我独尊', '花秋裳', '寒翻蛱蝶翎', '凌落九天', '陆溟焱', '顾飞卿', '一糯', '羡渔@幽月轮', '清风欲弄弦', '唐郁', '未书'], 
'2021-05-22-21-26-59_宫威_630.fstt.jx3dat': ['水龙头', '顾飞卿', '许仙敢玩蛇', '烟团团', '涯角', '唐郁', '残魂影', '璃衣', '左渭雨@飞鸢泛月', '蝉息', '萧雨落', '寒月妖梦@破阵子', '溯未未未', '您配玩霸刀么', '鹤知州@唯我独尊', '寒翻蛱蝶翎', '花秋裳', '照顾男大学生', '凌落九天', '陆溟焱', '一糯', '清风欲弄弦', '羡渔@幽月轮', '沉星夜小时候', '不吃橘子皮'], 
'2021-05-25-21-19-20_宫傲_178.fstt.jx3dat': ['水龙头', '沉星夜', '许仙敢玩蛇', '烟团团', '涯角', '唐郁', '残魂影', '左渭雨@飞鸢泛月', '蝉息', '萧雨落', '寒月妖梦@破阵子', '溯未未未', '徽岚', '神父王喇嘛', '贪七刀就会死', '花秋裳', '狗宝宝', '照顾男大学生', '凌落九天', '陆溟焱', '一糯', '羡渔@幽月轮', '不吃橘子皮', '沧歌歌'], 
'2021-05-31-22-57-40_宫傲_195.fstt.jx3dat': ['顾飞卿', '烟团团', '不用诉离觞', '涯角', '唐郁', '锤宝', '残魂影', '璃衣', '左渭雨@飞鸢泛月', '蝉息', '秋月小时候@梦江南', '萧雨落', '寒月妖梦@破阵子', '溯未未未', '一龙襄一@天鹅坪', '健心', '亦荣亦初', '照顾男大学生', '沉星夜', '一糯', '羡渔@幽月轮', '莫莫莫玄雨', '神父王喇嘛', '不吃橘子皮', '沧歌歌'], 
'2021-06-01-22-55-04_宫傲_255.fstt.jx3dat': ['真澄哀', '打咩', '不用诉离觞', '忱耳', '涯角', '潺音', '唐郁', '锤宝', '璃衣', '左渭雨@飞鸢泛月', '萧雨落', '寒月妖梦@破阵子', '一龙襄一@天鹅坪', '健心', '神父王喇嘛', '亦荣亦初', '沉星夜', '照顾男大学生', '残魂影', '一糯', '羡渔@幽月轮', '莫莫莫玄雨', '不吃橘子皮', '清风欲弄弦', '蝉息'], 
'2021-06-02-22-50-04_宫傲_262.fstt.jx3dat': ['沉星夜', '不用诉离觞', '村支书@乾坤一掷', '笙漫漫', '唐郁', '锤宝', '残魂影', '璃衣', '左渭雨@飞鸢泛月', '蝉息', '萧雨落', '寒月妖梦@破阵子', '一龙襄一@天鹅坪', '健心', '神父王喇嘛', '亦荣亦初', '照顾男大学生', '涯角', '一糯', '羡渔@幽月轮', '清风欲弄弦', '莫莫莫玄雨', '不吃橘子皮', '玩蛇靓妹', '凌落九天'], 
'2021-06-03-22-49-58_宫傲_373.fstt.jx3dat': ['不用诉离觞', '涯角', '笙漫漫', '唐郁', '锤宝', '残魂影', '璃衣', '空尘羽', '安子琪', '寒月妖梦@破阵子', '左渭雨@飞鸢泛月', '我变卦怎么了', '一龙襄一@天鹅坪', '贪七刀就会死', '鹤知州@唯我独尊', '亦荣亦初', '断潺', '照顾男大学生', '凌落九天', '沉星夜', '一糯', '羡渔@幽月轮', '清风欲弄弦', '不吃橘子皮', '玩蛇靓妹'], 
'2021-06-05-22-57-13_宫傲_371.fstt.jx3dat': ['沉星夜', '不用诉离觞', '涯角', '笙漫漫', '锤宝', '沈阿哭', '残魂影', '璃衣', '寒月妖梦@破阵子', '溯未未未', '我变卦怎么了', '一龙襄一@天鹅坪', '酒间行@幽月轮', '流火火@龙争虎斗', '贪七刀就会死', '断潺', '照顾男大学生', '凌落九天', '亦荣亦初', '左渭雨@飞鸢泛月', '空尘羽', '唐郁', '不吃橘子皮', '沧歌歌', '甜甜烟']}
p = {}

header = ['']
rows = []

num = 0
for line in d:
    l = d[line]
    for name in l:
        p[name] = 0
    num += 1
    header.append(line)
    
for line in p:
    p[line] = [0] * num

num = 0
for line in d:
    l = d[line]
    for name in l:
        p[name][num] = 1
    num += 1
        
for line in p:
    row = [line] + p[line]
    rows.append(row)
    
with open('tmp.csv','w', encoding='utf-8', newline='')as f:
    f_csv = csv.writer(f)
    f_csv.writerow(header)
    f_csv.writerows(rows)
