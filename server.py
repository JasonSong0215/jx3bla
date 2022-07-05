# coding:utf-8
from flask import Flask, render_template, url_for, request, redirect, session, make_response, jsonify, abort
from flask import request    
from flask import make_response,Response
import urllib
import json
import re
import pymysql
import random
import time
import urllib.request
import hashlib
import configparser
import os
import traceback
from Constants import *

from tools.Functions import *
from equip.AttributeDisplay import AttributeDisplay
from tools.painter import XiangZhiPainter
from replayer.ReplayerBase import RankCalculator

version = EDITION
ip = "139.199.102.41"
announcement = "全新的DPS统计已出炉，大家可以关注一下，看一下各门派的表现~"
app = Flask(__name__) 
app.config['JSON_AS_ASCII'] = False
app.ad = AttributeDisplay()

def Response_headers(content):    
    resp = Response(content)    
    resp.headers['Access-Control-Allow-Origin'] = '*'    
    return resp
    
@app.route('/getAnnouncement', methods=['GET'])
def getAnnouncement():
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    sql = '''SELECT * FROM PreloadInfo;'''
    cursor.execute(sql)
    result = cursor.fetchall()
    version = result[0][0]
    announcement = result[0][1]
    updateurl = result[0][2]
    
    db.close()
    return jsonify({'version': version, 'announcement': announcement, 'url': updateurl})

@app.route('/setAnnouncement', methods=['POST'])
def setAnnouncement():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    version = jdata["version"]
    announcement = jdata["announcement"]
    updateurl = jdata["updateurl"]
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''DELETE FROM PreloadInfo;'''
    cursor.execute(sql)
    sql = '''INSERT INTO PreloadInfo VALUES ("%s", "%s", "%s");'''%(version, announcement, updateurl)
    cursor.execute(sql)
    
    db.commit()
    db.close()
    
    return jsonify({'result': 'success'})

@app.route('/getAttribute', methods=['POST'])
def getAttribute():
    '''
    远程获取属性，通过传入配装来获取属性.
    '''
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    equipStr = jdata["equipStr"]
    occ = jdata["occ"]
    res = app.ad.Display(equipStr, occ)
    return jsonify(res)
    
@app.route('/getUuid', methods=['POST'])
def getUuid():
    mac = request.form.get('mac')
    userip = request.remote_addr
    intTime = int(time.time())
    
    hashStr = mac + ip + str(intTime)
    uuid = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''INSERT INTO UserInfo VALUES ("%s", "%s", "%s", "%s", %d, %d, %d, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);'''%(uuid, "", mac, userip, intTime, 0, 0)
    cursor.execute(sql)
    
    db.commit()
    db.close()
    
    return jsonify({'uuid': uuid})
    
@app.route('/setUserId', methods=['POST'])
def setUserId():
    uuid = request.form.get('uuid')
    id = request.form.get('id')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT * from UserInfo WHERE uuid = "%s"'''%(uuid)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    sql = '''SELECT * from UserInfo WHERE id = "%s"'''%(id)
    cursor.execute(sql)
    result2 = cursor.fetchall()
    
    if result:
    
        if result[0][1] != "":
            db.close()
            return jsonify({'result': 'hasuuid'})
        elif result2:
            db.close()
            return jsonify({'result': 'dupid'})
        else:
            sql = """UPDATE UserInfo SET id="%s" WHERE uuid="%s";"""%(id, uuid)
            cursor.execute(sql)
            db.commit()
            db.close()
            return jsonify({'result': 'success'})
    else:
        db.close()
        return jsonify({'result': 'nouuid'})
        

@app.route('/getUserInfo', methods=['POST'])
def getUserInfo():
    uuid = request.form.get('uuid')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    sql = '''SELECT * from UserInfo WHERE uuid = "%s"'''%(uuid)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    response = {'exist': 0}
    
    if result:
        response["exist"] = 1
        response["item1"] = result[0][7]
        response["item2"] = result[0][8]
        response["item3"] = result[0][9]
        response["item4"] = result[0][10]
        response["exp"] = result[0][6]
        response["score"] = result[0][5]
        response["lvl"] = result[0][17]
        
    db.close()
    return jsonify(response)
    
    
@app.route('/userLvlup', methods=['POST'])
def userLvlup():
    uuid = request.form.get('uuid')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    sql = '''SELECT * from UserInfo WHERE uuid = "%s"'''%(uuid)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    response = {'result': "fail"}
    
    if result:
        lvl = result[0][17]
        exp = result[0][6]
        if exp >= LVLTABLE[lvl+1]:
            response["result"] = "success"
            item = [0, 0, 0, 0]
            for i in range(4):
                item[i] = result[0][7+i]
            rewardTable = []
            if lvl == 0:
                rewardTable = [2,0,2,0]
            elif lvl <= 3:
                rewardTable = [4,2,4,2]
            elif lvl <= 6:
                rewardTable = [10,4,10,4]
            elif lvl <= 9:
                rewardTable = [15,6,15,6]
            else:
                rewardTable = [0,10,0,10]
            
            rewardTxt = "你获得了升级奖励："
            rewardItem = ["中级点赞卡", "中级吐槽卡", "高级点赞卡", "高级吐槽卡"]
            rewardContent = []
            for i in range(4):
                if rewardTable[i] > 0:
                    rewardContent.append("[%s]*%d"%(rewardItem[i], rewardTable[i]))
                    item[i] += rewardTable[i]
            rewardTxt += ','.join(rewardContent)
            
            if lvl == 1:
                rewardTxt += '\n你解锁了功能：使用高级能量'
            
            if lvl == 4:
                rewardTxt += '\n你解锁了功能：使用超级避雷'
                
            response["info"] = rewardTxt
            
            sql = """UPDATE UserInfo SET item1=%d, item2=%d, item3=%d, item4=%d, lvl=%d WHERE uuid="%s";"""%(item[0], item[1], item[2], item[3], lvl+1, uuid)
            cursor.execute(sql)
    
    db.commit()
    db.close()
    return jsonify(response)
    
@app.route('/getDpsStat', methods=['POST'])
def getDpsStat():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    mapDetail = jdata["mapdetail"]
    boss = jdata["boss"]
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT statistics from DpsStat WHERE mapdetail = "%s" and boss = "%s"'''%(mapDetail, boss)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        J = result[0][0]
        db.close()
        return jsonify({'result': 'success', 'statistics': J})
    else:
        db.close()
        return jsonify({'result': 'norecord'})
        
@app.route('/Tianwang.html', methods=['GET'])
def Tianwang():
 
    server = request.args.get('server')
    ids = request.args.get('ids')
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()

    playerDps = {}
    playerPot = {}
    playerNum = {}
    playerComment = {}
    
    allInfo = {}
    
    stdMap = ["25人普通达摩洞", "25人英雄达摩洞", "25人普通白帝江关", "25人英雄白帝江关", "25人普通雷域大泽", "25人英雄雷域大泽"]
    mapToBoss = {"25人普通达摩洞": 6, "25人英雄达摩洞": 6, "25人普通白帝江关": 7, "25人英雄白帝江关": 7, "25人普通雷域大泽": 6, "25人英雄雷域大泽": 6}
    creditThreshold = [[0, 100], [6, 0.5], [12, 0.4], [18, 0.3], [24, 0.2], [30, 0.1]]

    ids_split = ids.split(' ')
    for id in ids_split:
        sql = '''SELECT occ, map, boss, dps, num from HighestDps WHERE server = "%s" and player = "%s"'''%(server, id)
        cursor.execute(sql)
        result = cursor.fetchall()
        playerDps[id] = {}
        playerNum[id] = {}
        playerPot[id] = {}
        playerComment[id] = []
        
        credit = 75
        
        for map in stdMap:
            playerDps[id][map] = [0] * mapToBoss[map]
            playerNum[id][map] = 0
            playerPot[id][map] = []
            if "occ" not in playerDps[id]:
                playerDps[id]["occ"] = 0
        
        for line in result:
            playerDps[id]["occ"] = line[0]

            if line[2] in ["余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅", 
                           "胡汤&罗芬", "赵八嫂", "海荼", "姜集苦", "宇文灭", "宫威", "宫傲",
                           "巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]:
                bossNum = {"余晖": 0, "宓桃": 1, "武雪散": 2, "猿飞": 3, "哑头陀": 4, "岳琳&岳琅": 5, 
                           "胡汤&罗芬": 0, "赵八嫂": 1, "海荼": 2, "姜集苦": 3, "宇文灭": 4, "宫威": 5, "宫傲": 6,
                           "巨型尖吻凤": 0, "桑乔": 1, "悉达罗摩": 2, "尤珈罗摩": 3, "月泉淮": 4, "乌蒙贵": 5}[line[2]]
                playerDps[id][line[1]][bossNum] = line[3]
                playerNum[id][line[1]] += line[4]
                
        sql = '''SELECT occ, map, boss, battledate, severe, pot from PotHistory WHERE server = "%s" and player = "%s"'''%(server, id)
        cursor.execute(sql)
        result = cursor.fetchall()   
        for line in result:
            if line[2] in ["余晖", "宓桃", "武雪散", "猿飞", "哑头陀", "岳琳&岳琅",
                           "胡汤&罗芬", "赵八嫂", "海荼", "姜集苦", "宇文灭", "宫威", "宫傲",
                           "巨型尖吻凤", "桑乔", "悉达罗摩", "尤珈罗摩", "月泉淮", "乌蒙贵"]:
                playerPot[id][line[1]].append([line[2], line[3], line[4], line[5]])
                
        for map in playerPot[id]:
            playerPot[id][map].sort(key=lambda x:x[1])
            
        #print(playerPot)
                
        sql = '''SELECT mapdetail, type, power, content, id FROM CommentInfo WHERE server = "%s" and player = "%s"'''%(server, id)
        cursor.execute(sql)
        result = cursor.fetchall()   
        for line in result:
            if line[0] in stdMap:
                powerDes = ""
                creditChange = 0
                if line[2] == 1:
                    powerDes = "初级"
                    creditChange = 2
                elif line[2] == 2:
                    powerDes = "中级"
                    creditChange = 8
                else:
                    powerDes = "高级"
                    creditChange = 20
                typeDes = ""
                if line[1] == 1:
                    typeDes = "点赞"
                elif line[1] == 2:
                    typeDes = "吐槽"
                    creditChange *= -1
                playerComment[id].append([line[0], typeDes, powerDes, line[3], line[4]])
                credit += creditChange
        
        for line in stdMap:
            d = {}
            if line not in allInfo:
                allInfo[line] = {}
            allInfo[line][id] = d
            d["numBoss"] = mapToBoss[line]
            d["dps"] = playerDps[id][line]
            d["occ"] = playerDps[id]["occ"]
            d["pot"] = playerPot[id][line]
            d["potSevere"] = 0
            d["potSum"] = 0
            for pot in d["pot"]:
                if pot[2] == 1:
                    d["potSevere"] += 1
                    d["potSum"] += 1
                elif pot[2] == 0:
                    d["potSum"] += 1
            d["numRecord"] = playerNum[id][line]
            d["potRate"] = d["potSevere"] / (d["numRecord"] + 1e-10)
            d["comments"] = playerComment[id]
            d["numComments"] = len(d["comments"])
            
            creditChange = 0
            for i in range(len(creditThreshold)):
                std = creditThreshold[i]
                if d["numRecord"] >= std[0] and d["potRate"] <= std[1]:
                    creditChange = i
            
            credit += creditChange
            
        if credit > 100:
            credit = 100
        if credit < 0:
            credit = 0
            
        for line in stdMap:
            allInfo[line][id]["credit"] = credit

    db.close()

    return render_template("Tianwang.html", allInfo=allInfo, edition=EDITION)
    
@app.route('/TianwangSearch.html', methods=['GET'])
def TianwangSearch():

    return render_template("TianwangSearch.html", edition=EDITION)
        
@app.route('/XiangZhiTable.html', methods=['GET'])
def XiangZhiTable():
    map = request.args.get('map')
    page = request.args.get('page')
    order = request.args.get('order')
    
    if map is None:
        map = '25人普通达摩洞'
    if page is None:
        page = 1
    if order is None:
        order = "score"
        
    page = int(page)
    
    if map not in ['25人普通达摩洞', '25人英雄达摩洞']:
        return jsonify({'result': '地图不正确'})
    if order not in ['score', 'battledate']:
        return jsonify({'result': '排序方式不正确'})
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    edition = "5.1.0"
    mapdetail = map

    sql = """SELECT server, id, score, battledate, mapdetail, edition, hash FROM XiangZhiStat WHERE edition>='%s' AND mapdetail='%s' AND public=1"""%(edition, mapdetail)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    db.close()
    
    result = list(result)
    
    pageNum = int((len(result) + 29) / 30)
    
    if order == "score":
        result.sort(key=lambda x:-x[2])
    elif order == "battledate":
        result.sort(key=lambda x:x[3])
        result = result[::-1]
        
        
    start = (page-1)*30
    end = page*30
    if start >= len(result):
        start = len(result)-1
    if end >= len(result):
        end = len(result)
    result = result[start:end]


    return render_template("XiangZhiTable.html", result=result, edition=EDITION, 
                           order=order, map=map, page=page, pagenum=pageNum)
    
@app.route('/XiangZhiData/png', methods=['GET'])
def XiangZhiDataPng():
    key = request.args.get('key')
    
    if key != None:
        db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
        cursor = db.cursor()
        
        sql = '''SELECT * FROM XiangZhiStat WHERE hash = "%s"'''%key
        cursor.execute(sql)
        result = cursor.fetchall()
        
        db.close()
        
        if result:
            line = result[0]
            stat = json.loads(line[7].replace("'", '"'))
            info = {"server": line[0],
                    "id": line[1],
                    "score": line[2],
                    "battledate": line[3],
                    "mapdetail": line[4],
                    "edition": line[5],
                    "hash": line[6],
                    "statistics": stat}
            fileList = os.listdir("static/png")
            print(stat)
            if "%s.png"%key not in fileList:
                printint = 1
                if len(key) < 16:
                    printint = 0
                painter = XiangZhiPainter(printint = printint)
                painter.paint(info, "static/png/%s.png"%key)
            return render_template("XiangZhiPng.html", key = key)
        
    return jsonify({'result': '记录不存在'})
    
@app.route('/uploadComment', methods=['POST'])
def uploadComment():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata) 

    dtype = jdata["type"]
    power = jdata["power"]
    content = jdata["content"]
    pot = jdata["pot"]
    server = jdata["server"]
    userid = jdata["userid"]
    mapdetail = jdata["mapdetail"]
    beginTime = jdata["time"]
    player = jdata["player"]
    hash = jdata["hash"]
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT time from CommentInfo WHERE server = "%s" AND player = "%s" and userid = "%s" and mapdetail = "%s"'''%(server, player, userid, mapdetail)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        date1 = time.strftime("%Y-%m-%d", time.localtime(beginTime))
        for line in result:
            date2 = time.strftime("%Y-%m-%d", time.localtime(line[0]))
            if date1 == date2:
                db.close()
                return jsonify({'result': 'duplicate'})
                
    # 检查能量是否合法
    sql = '''SELECT item1, item2, item3, item4, score, lvl from UserInfo WHERE uuid = "%s"'''%(userid)
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if not result:
        db.close()
        return jsonify({'result': 'lack'})
        
    if power == 3 and result[0][5] < 2:
        db.close()
        return jsonify({'result': 'denied'})
        
    deductItem = 0
    deductScore = 0
    if power == 2:
        if dtype == 1:
            if result[0][0] > 0:
                deductItem = 1
            else:
                deductScore = 8
        else:
            if result[0][2] > 0:
                deductItem = 3
            else:
                deductScore = 8
    if power == 3:
        if dtype == 1:
            if result[0][1] > 0:
                deductItem = 2
            else:
                deductScore = 20
        else:
            if result[0][3] > 0:
                deductItem = 4
            else:
                deductScore = 20
    
    if deductScore > 0 and result[0][4] < deductScore:
        db.close()
        return jsonify({'result': 'lack'})

    if deductScore > 0:
        sql = """INSERT INTO ScoreInfo VALUES ("", "%s", %d, "%s", %d)"""%(
            userid, int(time.time()), "进行评价：%s"%hash, -deductScore)
        cursor.execute(sql)
        
        sql = """UPDATE UserInfo SET score=%d WHERE uuid="%s";"""%(result[0][4]-deductScore, userid)
        cursor.execute(sql)
        
    elif deductItem > 0:
        sql = """UPDATE UserInfo SET item%d=%d WHERE uuid="%s";"""%(deductItem, result[0][deductItem-1]-1, userid)
        cursor.execute(sql)
        
    sql = """INSERT INTO CommentInfo VALUES("%s", "%s", "%s", "%s", "%s", "%s", %d, %d, %d, "%s", "%s")"""%(
        hash, server, player, userid, mapdetail, "", beginTime, dtype, power, content, pot)
    cursor.execute(sql)
        
    db.commit()
    db.close()
    return jsonify({'result': 'success'})


@app.route('/uploadActorData', methods=['POST'])
def uploadActorData():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    server = jdata["server"]
    boss = jdata["boss"]
    battleDate = jdata["battledate"]
    mapName = jdata["mapdetail"]
    #mapDetail = jdata["mapdetail"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    
    response = {}
    
    if "win" not in jdata:
        jdata["win"] = 1
        
    win = int(jdata["win"])
    
    if "time" not in jdata:
        jdata["time"] = 0
    if "begintime" not in jdata:
        jdata["begintime"] = 0
    if "userid" not in jdata:
        jdata["userid"] = "unknown"
        
    submitTime = jdata["time"]
    battleTime = jdata["begintime"]
    userID = jdata["userid"]
    editionFull = parseEdition(edition)
    
    #增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT * from ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    scoreSuccess = 1
    scoreAdd = 0
    
    dupID = 0
    
    if mapName == "25人英雄达摩洞":
        scoreAdd = 2
        mapDetail = '484'
    elif mapName == '25人普通白帝江关':
        scoreAdd = 1
        mapDetail = '519'
    elif mapName == '25人英雄白帝江关':
        scoreAdd = 4
        mapDetail = '520'
    elif mapName == '25人普通雷域大泽':
        scoreAdd = 1
        mapDetail = '560'
    elif mapName == '25人英雄雷域大泽':
        scoreAdd = 4
        mapDetail = '561'
    elif mapName == '25人普通河阳之战':
        scoreAdd = 4
        mapDetail = '574'
    elif mapName == '25人英雄河阳之战':
        scoreAdd = 4
        mapDetail = '575'
    else:
        scoreSuccess = 0
        response['scoreStatus'] = 'illegal'
        mapDetail = '0'
        
    if win == 0:
        scoreSuccess = 0
        response['scoreStatus'] = 'notwin'
    
    if result and result[0][6] == 1:
        sql = '''SELECT * from ScoreInfo WHERE reason LIKE "%%%s%%"'''%(hash)
        cursor.execute(sql)
        result2 = cursor.fetchall()
        if result2:
            scoreSuccess = 0
            response['scoreStatus'] = 'dupid'
        else:
            lastTime = result[0][11]
            if submitTime - lastTime > 180:
                scoreSuccess = 0
                response['scoreStatus'] = 'expire'
            
        if parseEdition(result[0][4]) >= parseEdition(edition):
            dupID = 1
        else:
            print("Update edition")
            
    sql = '''SELECT * from UserInfo WHERE uuid = "%s"'''%(userID)
    cursor.execute(sql)
    result = cursor.fetchall()
    if not result or result[0][1] == "":
        scoreSuccess = 0
        response['scoreStatus'] = 'nologin'
        
    if scoreSuccess and scoreAdd > 0:
        sql = """UPDATE UserInfo SET score=%d, exp=%d WHERE uuid="%s";"""%(result[0][5]+scoreAdd, result[0][6]+scoreAdd, userID)
        cursor.execute(sql)
        
        sql = """INSERT INTO ScoreInfo VALUES ("", "%s", %d, "%s", %d)"""%(
            userID, int(time.time()), "提交战斗记录：%s"%hash, scoreAdd)
        cursor.execute(sql)
        
        response['scoreStatus'] = 'success'
        response['scoreAdd'] = scoreAdd
        
    if dupID:
        print("Find Duplicated")
        db.commit()
        db.close()
        response['result'] = 'dupid'
        return jsonify(response)
            
    sql = '''DELETE FROM ActorStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
        
    sql = """INSERT INTO ActorStat VALUES ("%s", "%s", "%s", "%s", "%s", "%s", %d, "%s", %d, "%s", %d, %d, "")"""%(
        server, boss, battleDate, mapDetail, edition, hash, win, statistics, editionFull, userID, battleTime, submitTime)
    cursor.execute(sql)
    db.commit()
    db.close()
   
    response['result'] = 'success'
    return jsonify(response)

@app.route('/uploadReplayPro', methods=['POST'])
def uploadReplayPro():
    jdata = json.loads(request.form.get('jdata'))
    #print(jdata)

    server = jdata["server"]
    id = jdata["id"]
    score = jdata["score"]
    battleDate = jdata["battledate"]
    mapDetail = jdata["mapdetail"]
    boss = jdata["boss"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    public = jdata["public"]
    submitTime = jdata["submittime"]
    battleTime = jdata["battletime"]
    userID = jdata["userid"]
    editionFull = jdata["editionfull"]
    occ = jdata["occ"]
    replayedition = jdata["replayedition"]

    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    try:
        sql = '''SELECT score from ReplayProStat WHERE mapdetail = "%s" and boss = "%s" and occ = "%s"''' % (mapDetail, boss, occ)
        cursor.execute(sql)
        result = cursor.fetchall()
        num = 0
        numOver = 0
        for line in result:
            if line[0] == 0:
                continue
            num += 1
            if score > line[0]:
                numOver += 1

        print(num, numOver)

        sql = '''SELECT * from ReplayProStat WHERE hash = "%s"''' % hash
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            if result[0][12] >= editionFull:
                print("Find Duplicated")
                db.close()
                shortID = result[0][8]
                return jsonify({'result': 'dupid', 'num': num, 'numOver': numOver, 'shortID': shortID})
            else:
                print("Update edition")

        sql = '''DELETE FROM ReplayProStat WHERE hash = "%s"''' % hash
        cursor.execute(sql)

        # 更新数量
        sql = '''SELECT * from ReplayProInfo WHERE dataname = "num"'''
        cursor.execute(sql)
        result = cursor.fetchall()
        num = result[0][2]
        shortID = num + 1
        sql = """UPDATE ReplayProInfo SET datavalueint=%d WHERE dataname = "num";""" % shortID
        cursor.execute(sql)

        statistics["overall"]["shortID"] = shortID

        sql = """INSERT INTO ReplayProStat VALUES ("%s", "%s", "%s", %d, "%s", "%s", "%s", "%s", %d, "%s", %d, "%s", %d, "%s", "%s", %d, %d)""" % (
            server, id, occ, score, battleDate, mapDetail, boss, hash, shortID, statistics, public, edition, editionFull, replayedition, userID, battleTime,
            submitTime)
        cursor.execute(sql)
        db.commit()
        db.close()

    except Exception as e:
        traceback.print_exc()
        db.close()
        return jsonify({'result': 'fail', 'num': 0, 'numOver': 0, 'shortID': 0})

    return jsonify({'result': 'success', 'num': num, 'numOver': numOver, 'shortID': shortID})

@app.route('/showReplayPro.html', methods=['GET'])
def showReplayPro():
    id = request.args.get('id')
    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()
    sql = """SELECT statistics, public, replayedition, occ FROM ReplayProStat WHERE shortID = %s OR hash = "%s";"""%(id, id)
    cursor.execute(sql)
    result = cursor.fetchall()
    db.close()
    if len(result) == 0:
        text = "结果未找到."
    elif result[0][1] == 0:
        text = "数据未公开."
    elif result[0][3] in ["xiangzhi", "lingsu", "lijingyidao", "butianjue", "yunchangxinjing"]:
        # 生成复盘页面
        occ = result[0][3]
        text = result[0][0].decode().replace('\n', '\\n').replace('\t', '\\t')
        text1 = text.replace("'", '"')
        jResult = json.loads(text1)
        rc = RankCalculator(jResult)
        rank = rc.getRankFromStat(occ)
        rankStr = json.dumps(rank)
        return render_template("HealerReplay.html", raw=text, rank=rankStr, occ=occ, edition=EDITION)
    return jsonify({'text': text.decode()})

@app.route('/getReplayPro', methods=['GET'])
def getReplayPro():
    id = request.args.get('id')
    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()
    sql = """SELECT statistics, public, replayedition, occ FROM ReplayProStat WHERE shortID = %s OR hash = "%s";"""%(id, id)
    cursor.execute(sql)
    result = cursor.fetchall()
    flag = 0
    if len(result) == 0:
        flag = 0
        text = "结果未找到."
    elif result[0][1] == 0:
        flag = 0
        text = "数据未公开."
    elif result[0][3] in ["xiangzhi", "lingsu", "lijingyidao"]:  #, "butianjue", "yunchangxinjing"]:
        flag = 1
        text = result[0][0]
        text1 = text.decode().replace('\n', '\\n').replace('\t', '\\t').replace("'", '"')
        jResult = json.loads(text1)
        rc = RankCalculator(jResult)
        rank = rc.getRankFromStat(occ)
        rankStr = json.dumps(rank)
    else:
        flag = 0
        text = "不支持的心法，请等待之后的版本更新."
    db.close()
    if flag:
        return jsonify({'available': 1, 'text': "请求成功", 'raw': text, 'rank': rankStr})
    else:
        return jsonify({'available': 0, 'text': text})


@app.route('/getMultiPlayer', methods=['GET'])
def getMultiPlayer():
    server = request.args.get('server')
    ids = request.args.get('ids')
    map = request.args.get('map')

    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()
    ids_split = ids.split(' ')

    overallResJson = {}
    overallResJson["server"] = server
    for id in ids_split:
        sql = '''SELECT score, boss FROM ReplayProStat WHERE server = "%s" AND id = "%s" AND mapdetail = "%s" AND public = 1''' % (server, id, map)
        cursor.execute(sql)
        result = cursor.fetchall()
        resJson = {}
        highestScore = {}
        sumScore = {}
        numRecord = {}
        avgScore = {}
        for record in result:
            score = record[0]
            boss = record[1]
            if score > highestScore.get(boss, -1):
                highestScore[boss] = score
            numRecord[boss] = numRecord.get(boss, 0) + 1
            sumScore[boss] = sumScore.get(boss, 0) + score
        numBoss = 0
        sumHighestScore = 0
        sumAverageScore = 0
        for boss in sumScore:
            numBoss += 1
            avgScore[boss] = roundCent(sumScore[boss] / numRecord[boss])
            sumHighestScore += highestScore[boss]
            sumAverageScore += avgScore[boss]
            resJson[boss] = {"highest": highestScore[boss], "average": avgScore[boss], "num": numRecord[boss]}
        overallAverageScore = roundCent(sumAverageScore / (numBoss + 1e-10))
        overallHighestScore = roundCent(sumHighestScore / (numBoss + 1e-10))
        resJson["overall"] = {"highest": overallHighestScore, "average": overallAverageScore, "num": numBoss}
        overallResJson[id] = resJson
    db.close()
    return jsonify({'available': 1, 'text': "请求成功", 'result': overallResJson})

@app.route('/getSinglePlayer', methods=['GET'])
def getSinglePlayer():
    server = request.args.get('server')
    id = request.args.get('id')
    map = request.args.get('map')
    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    sql = '''SELECT score, boss, occ, edition, battletime, submittime, shortID FROM ReplayProStat WHERE server = "%s" AND id = "%s" AND mapdetail = "%s" AND public = 1''' % (server, id, map)
    cursor.execute(sql)
    result = cursor.fetchall()
    resJson = {"stat": {}}
    highestScore = {}
    sumScore = {}
    numRecord = {}
    avgScore = {}
    allResults = {}
    for record in result:
        score = record[0]
        boss = record[1]
        occ = record[2]
        edition = record[3]
        battleTime = record[4]
        submitTime = record[5]
        shortID = record[6]
        if score > highestScore.get(boss, -1):
            highestScore[boss] = score
        numRecord[boss] = numRecord.get(boss, 0) + 1
        sumScore[boss] = sumScore.get(boss, 0) + score
        if boss not in allResults:
            allResults[boss] = []
        allResults[boss].append({"score": score, "occ": occ, "edition": edition, "battleTime": battleTime, "submitTime": submitTime, "shortID": shortID})
    numBoss = 0
    sumHighestScore = 0
    sumAverageScore = 0
    for boss in sumScore:
        numBoss += 1
        avgScore[boss] = roundCent(sumScore[boss] / (numRecord[boss] + 1e-10))
        sumHighestScore += highestScore[boss]
        sumAverageScore += avgScore[boss]
        resJson["stat"][boss] = {"highest": highestScore[boss], "average": avgScore[boss], "num": numRecord[boss]}
    overallAverageScore = roundCent(sumAverageScore / (numBoss + 1e-10))
    overallHighestScore = roundCent(sumHighestScore / (numBoss + 1e-10))
    resJson["stat"]["overall"] = {"highest": overallHighestScore, "average": overallAverageScore, "num": numBoss}
    resJson["table"] = allResults

    db.close()
    return jsonify({'available': 1, 'text': "请求成功", 'result': resJson})

@app.route('/getRank', methods=['GET'])
def getRank():
    map = request.args.get('map')
    boss = request.args.get("boss")
    occ = request.args.get("occ")
    page = request.args.get("page")
    if page is None:
        page = 1
    else:
        page = int(page)
    db = pymysql.connect(ip, app.dbname, app.dbpwd, "jx3bla", port=3306, charset='utf8')
    cursor = db.cursor()

    numPerPage = 50

    sql = '''SELECT server, id, score, edition, battletime, submittime, shortID FROM ReplayProStat WHERE mapdetail = "%s" AND boss = "%s" AND occ = "%s" AND public = 1''' % (map, boss, occ)
    cursor.execute(sql)
    result = cursor.fetchall()
    resJson = {"table": []}

    result = list(result)
    result.sort(key=lambda x:-x[2])

    for i in range((page-1)*numPerPage, page*numPerPage):
        if i < len(result):
            record = result[i]
            server = record[0]
            id = record[1]
            score = record[2]
            # boss = record[1]
            # occ = record[2]
            edition = record[3]
            battleTime = record[4]
            submitTime = record[5]
            shortID = record[6]
            resJson["table"].append({"score": score, "server": server, "edition": edition, "id": id, "battleTime": battleTime, "submitTime": submitTime, "shortID": shortID})

    resJson["num"] = len(result)
    db.close()
    return jsonify({'available': 1, 'text': "请求成功", 'result': resJson})
    
@app.route('/uploadXiangZhiData', methods=['POST'])
def uploadXiangZhiData():
    jdata = json.loads(request.form.get('jdata'))
    print(jdata)
    server = jdata["server"]
    id = jdata["id"]
    score = jdata["score"]
    battleDate = jdata["battledate"]
    mapDetail = jdata["mapdetail"]
    edition = jdata["edition"]
    hash = jdata["hash"]
    statistics = jdata["statistics"]
    
    if "public" not in jdata:
        jdata["public"] = 0
        
    public = jdata["public"]
    
    if "time" not in jdata:
        jdata["time"] = 0
    if "begintime" not in jdata:
        jdata["begintime"] = 0
    if "userid" not in jdata:
        jdata["userid"] = "unknown"
        
    submitTime = jdata["time"]
    battleTime = jdata["begintime"]
    userID = jdata["userid"]
    editionFull = parseEdition(edition)
    
    #增加五个字段：editionfull INT, userid VARCHAR(32), battletime INT, submittime INT, instanceid VARCHAR(32)
    
    db = pymysql.connect(ip,app.dbname,app.dbpwd,"jx3bla",port=3306,charset='utf8')
    cursor = db.cursor()
    
    sql = '''SELECT score from XiangZhiStat WHERE mapdetail = "%s"'''%mapDetail
    cursor.execute(sql)
    result = cursor.fetchall()
    
    num = 0
    numOver = 0
    for line in result:
        if line[0] == 0:
            continue
        num += 1
        if score > line[0]:
            numOver += 1
            
    print(num, numOver)
    
    sql = '''SELECT * from XiangZhiStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if result:
        if parseEdition(result[0][5]) >= parseEdition(edition):
            print("Find Duplicated")
            db.close()
            return jsonify({'result': 'dupid', 'num': num, 'numOver': numOver})
        else:
            print("Update edition")
    
    sql = '''DELETE FROM XiangZhiStat WHERE hash = "%s"'''%hash
    cursor.execute(sql)
        
    sql = """INSERT INTO XiangZhiStat VALUES ("%s", "%s", %d, "%s", "%s", "%s", "%s", "%s", %d, %d, "%s", %d, %d, "")"""%(
        server, id, score, battleDate, mapDetail, edition, hash, statistics, public, editionFull, userID, battleTime, submitTime)
    cursor.execute(sql)
    db.commit()
    db.close()
    
    return jsonify({'result': 'success', 'num': num, 'numOver': numOver})
    
if __name__ == '__main__':
    import signal
    
    config = configparser.RawConfigParser()
    config.readfp(open('./settings.cfg'))
    
    app.dbname = config.get('jx3bla', 'username')
    app.dbpwd = config.get('jx3bla', 'password')
    app.debug = config.getboolean('jx3bla', 'debug')
    
    app.run(host='0.0.0.0', port=8009, debug=app.debug, threaded=True)

