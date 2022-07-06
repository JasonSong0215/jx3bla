# Created by moeheart at 10/10/2020
# 实时模式的基础方法库。

import threading
import os
import time
import traceback
import hashlib
import urllib.request
import requests
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tools.Functions import *
from Constants import *
import pyperclip

from data.DataController import DataController
from replayer.ActorReplayPro import ActorProReplayer
from replayer.boss.General import GeneralWindow

from replayer.boss.HuTangLuoFen import HuTangLuoFenWindow
from replayer.boss.ZhaoBasao import ZhaoBasaoWindow
from replayer.boss.HaiTu import HaiTuWindow
from replayer.boss.JiangJiku import JiangJikuWindow
from replayer.boss.YuwenMie import YuwenMieWindow
from replayer.boss.GongWei import GongWeiWindow
from replayer.boss.GongAo import GongAoWindow

from replayer.boss.JuxingJianwenfeng import JuxingJianwenfengWindow
from replayer.boss.SangQiao import SangQiaoWindow
from replayer.boss.XidaLuomo import XidaLuomoWindow
from replayer.boss.YoujiaLuomo import YoujiaLuomoWindow
from replayer.boss.YuequanHuai import YuequanHuaiWindow
from replayer.boss.WuMenggui import WuMengguiWindow

from replayer.boss.LeQina import LeQinaWindow
from replayer.boss.AGeno import AGenoWindow
from replayer.boss.ZhouTongji import ZhouTongjiWindow
from replayer.boss.ZhouZhi import ZhouZhiWindow
from replayer.boss.ChangXiu import ChangXiuWindow

class ToolTip(object):
    '''
    浮动标签类，用于实现简单的浮动标签。
    '''
    def build(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
 
    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        tf = tk.Frame(tw, relief=tk.SOLID, borderwidth=1, bg="#ffffe0")
        tf.pack(ipadx=1)
        
        textList = text.split('\n')
        
        for line in textList:
            if line == "":
                fg = "#000000"
            if line[0] == "-":
                fg = "#ff0000"
            elif line[0] == "+":
                fg = "#007700"
            else:
                fg = "#000000"
            label = tk.Label(tf, text=line, fg=fg, justify=tk.LEFT,
                          background="#ffffe0", anchor='nw', 
                          font=("Aaril", "10", "normal"))
            label.pack(anchor=tk.NW)
 
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def createToolTip(self, widget, text):
        toolTip = self.build(widget)
        def enter(event):
            self.showtip(text)
        def leave(event):
            self.hidetip()
        self.widget = widget
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        
    def remove(self):
        self.widget.unbind('<Enter>')
        self.widget.unbind('<Leave>')
        
    def __init__(self, widget, text):
        self.createToolTip(widget, text)
        
class CommentWindow():
    '''
    评论窗口类。用于维护评论窗口的逻辑。
    '''
    def final(self):
        '''
        关闭窗口。
        '''
        self.windowAlive = False
        self.window.destroy()
        
    def submit(self):
        '''
        尝试提交评论。
        '''
        result = {}
        result["type"] = int(self.var1.get())
        result["power"] = int(self.var2.get())
        result["content"] = self.commentEntry.get()
        result["pot"] = self.potDescription
        result["server"] = self.server
        result["userid"] = self.userid
        result["mapdetail"] = self.mapDetail
        result["time"] = self.beginTime
        result["player"] = self.targetID
        
        hashStr = result["server"] + result["player"] + result["userid"] + result["mapdetail"] + str(result["time"])
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        
        result["hash"] = hashres
        
        if result["type"] == 0 or result["power"] == 0:
            messagebox.showinfo(title='错误', message='提交失败，请检查类型与能量是否正确。')
            return

        Jdata = json.dumps(result)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://%s:8009/uploadComment' % IP, data=jparse)
        res = json.load(resp)
        
        if res['result'] == 'success':
            messagebox.showinfo(title='成功', message='评价成功！')
            self.final()
        elif res['result'] == 'lack':
            messagebox.showinfo(title='失败', message='评价失败，你的积分与能量卡不足以进行此次评价，请尝试使用更低的能量等级。')
        elif res['result'] == 'duplicate':
            messagebox.showinfo(title='失败', message='评价失败，你对该玩家提交过相同的评价。')
        elif res['result'] == 'denied':
            messagebox.showinfo(title='失败', message='评价失败，你的等级无法以使用此功能。')
        
        
    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()
        
    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('评价')
        window.geometry('500x400')
        
        targetID = self.targetID
        targetColor = getColor(self.targetOcc)
        IDlabel = tk.Label(window, text=targetID, height=1, fg=targetColor)
        IDlabel.grid(row=0, column=0)
        
        self.var1 = tk.IntVar()
        
        label1 = tk.Label(window, text="评价类别", height=1)
        label1.grid(row=1, column=0)
        
        ToolTip(label1, "选取评价类别。点赞会增加目标的信誉分，而吐槽会扣除目标的信誉分。\n在同一场战斗数据中，只能对同一名玩家评价一次。")
        
        frame1 = tk.Frame(window)
        radio11 = tk.Radiobutton(frame1,text='点赞',variable=self.var1,value=1)
        radio11.grid(row=0, column=0)
        radio12 = tk.Radiobutton(frame1,text='吐槽',variable=self.var1,value=2)
        radio12.grid(row=0, column=1)
        frame1.grid(row=1, column=1)
        
        self.var2 = tk.IntVar()
        
        label2 = tk.Label(window, text="评价能量", height=1)
        label2.grid(row=2, column=0)
        
        frame2 = tk.Frame(window)
        radio21 = tk.Radiobutton(frame2,text='低',variable=self.var2,value=1)
        radio21.grid(row=0, column=1)
        radio22 = tk.Radiobutton(frame2,text='中',variable=self.var2,value=2)
        radio22.grid(row=0, column=2)
        radio23 = tk.Radiobutton(frame2,text='高',variable=self.var2,value=3)
        radio23.grid(row=0, column=3)
        frame2.grid(row=2, column=1)
        
        ToolTip(label2, "选取评价能量，会影响分数变化的多少。")
        
        ToolTip(radio21, "使用低能量，分数变化为2，无消耗。")
        ToolTip(radio22, "使用中能量，分数变化为8，消耗中级能量卡或8点积分。")
        ToolTip(radio23, "使用高能量，分数变化为20，消耗高级能量卡或20点积分。")
        
        potDesLabel = tk.Label(window, text="犯错记录")
        potDesLabel.grid(row=3, column=0)
        potLabel = tk.Label(window, text=self.potDescription)
        potLabel.grid(row=3, column=1, ipadx=75)
        
        commentDesLabel = tk.Label(window, text="评论内容")
        commentDesLabel.grid(row=4, column=0)
        self.commentEntry = tk.Entry(window, show=None, width=50)
        self.commentEntry.grid(row=4, column=1, ipady=25)
        
        submitButton = tk.Button(window, text='提交', command=self.submit)
        submitButton.grid(row=5, column=1)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        
        
    def alive(self):
        return self.windowAlive

    def __init__(self, id, occ, pots, server, userid, mapDetail, beginTime):
        self.windowAlive = False
        self.targetID = id
        self.targetOcc = occ
        self.potDescription = pots
        self.server = server
        self.userid = userid
        self.mapDetail = mapDetail
        self.beginTime = beginTime
    
        
class PotExtendWindow():
    '''
    锅的扩展窗口类。用于维护添加锅的窗体。
    '''
    
    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''
        self.windowAlive = False
        self.singleBossWindow.potExtendRunning = False
        self.window.destroy()
        
    def Act(self):
        '''
        实施加锅。
        '''
        playerID = self.playerValue.get()
        potLevel = self.lvlValue.get()
        potDescription = "[手动]" + self.descEntry.get()
        try:
            score = int(self.scoreEntry.get())
        except:
            score = 0
        
        potLevelNum = 1
        if potLevel == "轻微":
            potLevelNum = 0
        elif potLevel == "严重":
            potLevelNum = 1
        elif potLevel == "补贴":
            potLevelNum = 3
            
        if playerID in self.playerIDDict:
            playerOcc = self.playerIDDict[playerID]
            self.pot = [playerID, playerOcc, potLevelNum, self.bossName, potDescription, []]
            self.singleBossWindow.AddPot(self.pot, score)
        self.final()
    
    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('加锅')
        window.geometry('300x120')
        
        tk.Label(window, text="玩家ID", height=1).grid(row=0, column=0)
        self.playerValue = tk.StringVar()
        playerCombobox = ttk.Combobox(window, textvariable=self.playerValue)
        playerCombobox["values"] = self.playerIDList 
        playerCombobox.current(0) 
        playerCombobox.grid(row=0, column=1)
        
        tk.Label(window, text="分锅描述", height=1).grid(row=1, column=0)
        self.descEntry = tk.Entry(window, show=None)
        self.descEntry.grid(row=1, column=1)
        
        tk.Label(window, text="分锅等级", height=1).grid(row=2, column=0)
        self.lvlValue = tk.StringVar()
        lvlCombobox = ttk.Combobox(window, textvariable=self.lvlValue)
        lvlCombobox["values"] = ("严重", "轻微", "补贴")  
        lvlCombobox.current(0) 
        lvlCombobox.grid(row=2, column=1)
        
        tk.Label(window, text="评分", height=1).grid(row=3, column=0)
        self.scoreEntry = tk.Entry(window, show=None)
        self.scoreEntry.grid(row=3, column=1)
        
        tk.Button(window, text='加锅', width=10, height=1, command=self.Act).grid(row=4, column=0)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
    
    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()
        
    def alive(self):
        return self.windowAlive

    def __init__(self, singleBossWindow):
        self.windowAlive = False
        self.singleBossWindow = singleBossWindow
        self.playerList = singleBossWindow.analyser.getPlayer()
        self.playerIDDict = {}
        self.playerIDList = []
        for line in self.playerList:
            self.playerIDDict[line[0]] = line[1]
            self.playerIDList.append(line[0])
        self.bossName = singleBossWindow.detail["boss"]

class SingleBossWindow():
    '''
    单个BOSS复盘结果类。维护复盘结果的窗体，与简单的信息收集逻辑。
    '''
        
    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"
            
    def AddPot(self, pot, score):
        '''
        新增一条锅。暂时的处理方式为添加的锅不会在记录中显示，而是添加到记录中，刷新后才显示。
        params
        - pot 锅
        '''
        self.potList.append(pot)
        self.scoreList.append(score)
        
    def StartPotExtend(self):
        '''
        开启加锅界面。
        '''
        if self.potExtendRunning == False:
            self.potExtendWindow = PotExtendWindow(self)
            self.potExtendWindow.start()
            self.potExtendRunning = True
            
    def getPot(self, tmp, num):
        '''
        分锅结果变化的处理函数。
        params
        - tmp 记录编号
        - num 锅数
        '''
        self.scoreList[tmp] += num
        scoreStr = ""
        scoreColor = "#000000"
        if self.scoreList[tmp] > 0:
            scoreStr = "+%d"%self.scoreList[tmp]
            scoreColor = "#007700"
        elif self.scoreList[tmp] < 0:
            scoreStr = "%d"%self.scoreList[tmp]
            scoreColor = "#ff0000"
        self.scoreLabels[tmp].config(text=scoreStr, fg=scoreColor)

        #self.analyser.potListScore[-self.numPot + tmp][-1] = self.scoreList[tmp]

        self.analyser.setSinglePotScore(self.bossNum, tmp, self.scoreList[tmp])
        
        self.analyser.getPlayerPotList()
        
        text = self.analyser.getPlayerText(self.nameList[tmp])
        self.toolTips[tmp].remove()
        toopTip = ToolTip(self.toolTips[tmp].widget, text)
        self.toolTips[tmp] = toopTip
        
    def copyPot(self, tmp):
        '''
        点击复制按钮的处理函数。
        params
        - tmp 记录编号
        '''
        text = self.potList[tmp][4]
        player = self.potList[tmp][0].strip('"')
        copyText = "[%s]：%s"%(player, text)
        pyperclip.copy(copyText)
        messagebox.showinfo(title='提示', message='复制成功！')
        
    def final(self):
        '''
        收集分锅结果并关闭窗口。
        '''

        # print("[Test]SingleBoss")
        # print(self.potWindowActivated)
        # print(self.potList)
        # print(self.scoreList)
        
        if self.potExtendRunning:
            self.potExtendWindow.final()

        if self.potWindowActivated:
            for i in range(len(self.potList)):
                self.potList[i][6] = self.scoreList[i]
            self.analyser.changeResult(self.potList, self.bossNum)

        # print("[Test]After modified")
        # print(self.potWindowActivated)
        # print(self.potList)
        # print(self.scoreList)

        if self.windowAlive:
            self.window.destroy()
            self.windowAlive = False
                
    def constructReplayByNum(self, num):
        '''
        根据序号来打开对应的BOSS复盘窗口，要求序号必须合法
        params
        - num 对应的序号，如果序号为-1，表示选择最后一个BOSS
        '''
        if num == -1:
            num = self.analyser.getLastBossNum()
        if num == "None":
            return
        self.bossNum = int(num)
        self.addPotList(self.analyser.potContainer.getBoss(num))
        a, b, c, d, e = self.analyser.potContainer.getDetail(num)
        self.setDetail(a, b, c, d, e)
        # self.start()
        self.specificBossWindow.start()
        
    def finalPrev(self):
        '''
        收集分锅结果并关闭窗口，尝试打开前一个BOSS的窗口。
        '''
        prevNum = self.bossNum - 1
        if self.analyser.checkBossExists(prevNum):
            self.final()
            self.specificBossWindow.final()
            self.potWindowActivated = False
            self.constructReplayByNum(prevNum)
        else:
            messagebox.showinfo(title='嘶', message='前序BOSS未找到。')
    
    def finalNext(self):
        '''
        收集分锅结果并关闭窗口，尝试打开后一个BOSS的窗口。
        '''
        nextNum = self.bossNum + 1
        if self.analyser.checkBossExists(nextNum):
            self.final()
            self.specificBossWindow.final()
            self.potWindowActivated = False
            self.constructReplayByNum(nextNum)
        else:
            messagebox.showinfo(title='嘶', message='后继BOSS未找到。')
            
    def setDetail(self, potList, effectiveDPSList, detail, occResult, bh):
        '''
        初始化详细复盘的数据.
        - params
        potList 分锅记录.
        effectiveDPSList DPS详细统计，包括每名玩家在特定算法下的DPS.
        detail 详细复盘记录.
        occResult 心法复盘记录.
        bh 战斗事件记录.
        '''
        self.effectiveDPSList = effectiveDPSList
        self.detail = detail
        self.occResult = occResult
        self.bh = bh
        self.hasDetail = 1
        if "boss" in detail:
            if detail["boss"] == "胡汤&罗芬":
                self.specificBossWindow = HuTangLuoFenWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "赵八嫂":
                self.specificBossWindow = ZhaoBasaoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "海荼":
                self.specificBossWindow = HaiTuWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "姜集苦":
                self.specificBossWindow = JiangJikuWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "宇文灭":
                self.specificBossWindow = YuwenMieWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "宫威":
                self.specificBossWindow = GongWeiWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "宫傲":
                self.specificBossWindow = GongAoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "巨型尖吻凤":
                self.specificBossWindow = JuxingJianwenfengWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "桑乔":
                self.specificBossWindow = SangQiaoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "悉达罗摩":
                self.specificBossWindow = XidaLuomoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "尤珈罗摩":
                self.specificBossWindow = YoujiaLuomoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "月泉淮":
                self.specificBossWindow = YuequanHuaiWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "乌蒙贵":
                self.specificBossWindow = WuMengguiWindow(self.mainWindow.config, effectiveDPSList, detail, occResult)
            elif detail["boss"] == "勒齐那":
                self.specificBossWindow = LeQinaWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            elif detail["boss"] == "阿阁诺":
                self.specificBossWindow = AGenoWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            elif detail["boss"] == "周通忌":
                self.specificBossWindow = ZhouTongjiWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            elif detail["boss"] == "周贽":
                self.specificBossWindow = ZhouZhiWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            elif detail["boss"] == "常宿":
                self.specificBossWindow = ChangXiuWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            else:
                self.specificBossWindow = GeneralWindow(self.mainWindow.config, effectiveDPSList, detail, occResult, bh)
            self.specificBossWindow.setPotWindow(self)

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        #window = tk.Tk()
        window.title('战斗复盘')
        window.geometry('650x700')

        numPot = len(self.potList)
        self.numPot = numPot
        self.potWindowActivated = True
        
        canvas=tk.Canvas(window,width=600,height=500,scrollregion=(0,0,580,numPot*30)) #创建canvas
        canvas.place(x=25, y=25) #放置canvas的位置
        frame=tk.Frame(canvas) #把frame放在canvas里
        frame.place(width=580, height=500) #frame的长宽，和canvas差不多的
        vbar=tk.Scrollbar(canvas,orient=tk.VERTICAL) #竖直滚动条
        vbar.place(x = 580,width=20,height=500)
        vbar.configure(command=canvas.yview)
        canvas.config(yscrollcommand=vbar.set) #设置  
        canvas.create_window((265,numPot*15), window=frame)  #create_window
        
        self.scoreLabels = []
        self.scoreList = []
        self.toolTips = []
        self.nameList = []

        for i in range(len(self.potList)):
            assert len(self.potList[i]) == 7
            self.scoreList.append(self.potList[i][6])
                
        if not self.analyser.checkBossExists(self.bossNum):
            self.analyser.addResult(self.potList, self.bossNum, self.effectiveDPSList, self.detail, self.occResult, self.bh)
        
        self.analyser.getPlayerPotList()
        
        for i in range(numPot):
            line = self.potList[i]
            name = line[0].strip('"')
            occ = line[1]
            color = getColor(occ)
            nameLabel = tk.Label(frame, text=name, width = 13, height=1, fg=color)
            nameLabel.grid(row=i, column=0)
            pot = line[4]
            color = self.getPotColor(line[2])
            potLabel = tk.Label(frame, text=pot, height=1, fg=color)
            potLabel.grid(row=i, column=1)
            
            if len(line) > 5:
                potDetail = '\n'.join(line[5])
                if potDetail != "":
                    ToolTip(potLabel, potDetail)
            
            scoreLabel = tk.Label(frame, text="", width=5, height=1, font=("Arial", 12, "bold"))
            scoreLabel.grid(row=i, column=2)
            self.scoreLabels.append(scoreLabel)
            
            tmp = i
            button1 = tk.Button(frame, text='接锅', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, -1), bg='#ffcccc')
            button1.grid(row=i, column=3)
            button2 = tk.Button(frame, text='领赏', width=6, height=1, command=lambda tmp=tmp: self.getPot(tmp, 1), bg='#ccffcc')
            button2.grid(row=i, column=4)
            button3 = tk.Button(frame, text='复制', width=6, height=1, command=lambda tmp=tmp: self.copyPot(tmp), bg='#ccccff')
            button3.grid(row=i, column=5)
            
            text = self.analyser.getPlayerText(name)
            toolTip = ToolTip(nameLabel, text)
            self.toolTips.append(toolTip)
            self.nameList.append(name)
            
        for i in range(len(self.potList)):
            self.getPot(i, 0)
            
        buttonFinal = tk.Button(window, text='分锅完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=250, y=540)
        
        # buttonPrev = tk.Button(window, text='<<', width=2, height=1, command=self.finalPrev)
        # buttonPrev.place(x = 220, y = 540)
        #
        # buttonNext = tk.Button(window, text='>>', width=2, height=1, command=self.finalNext)
        # buttonNext.place(x = 340, y = 540)
        
        buttonDetail = tk.Button(window, text='手动设置', width=10, height=1, command=self.StartPotExtend)
        buttonDetail.place(x=200, y=580)
        
        # buttonDetail = tk.Button(window, text='数据统计', width=10, height=1, command=self.showDetail)
        # buttonDetail.place(x = 300, y = 570)
        
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def openDetailWindow(self):
        '''
        开启详细复盘界面。这是由于在7.0版本更新后，先显示复盘界面，再显示分锅界面。
        '''
        self.potWindowActivated = False
        self.specificBossWindow.start()

    def start(self):
        self.windowAlive = True
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()
        
    def addPotList(self, potList):
        self.potList = potList
        
    def alive(self):
        return self.windowAlive

    def __init__(self, analyser, bossNum, mainWindow):
        self.analyser = analyser
        self.bossNum = bossNum
        self.mainWindow = mainWindow
        self.effectiveDPSList = []
        self.detail = {}
        self.windowAlive = False
        self.potExtendRunning = False
        self.potWindowActivated = False
            
class PotContainer():
    '''
    锅的记录类。
    '''
    
    def getAll(self):
        '''
        返回所有的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        result = []
        for line in self.pot:
            result.extend(self.pot[line])
        return result
        
    def getPlayerOcc(self):
        '''
        获取记录中的角色与门派。用effectiveDpsList作为信息来源。
        return
        - list格式的角色与门派组合。
        '''
        playerOcc = {}
        playerOccNum = {}
        for key in self.effectiveDPSList:
            dpsList = self.effectiveDPSList[key]
            for line in dpsList:
                if line[0] not in playerOcc:
                    playerOcc[line[0]] = line[1]
                    occ = line[1]
                    if occ[-1] in ['d', 't', 'h', 'p', 'm']:
                        occ = occ[:-1]
                    playerOccNum[line[0]] = int(occ)
                        
        playerList = []
        for line in playerOccNum:
            playerList.append([line.strip('"'), playerOccNum[line], playerOcc[line]])
        playerList.sort(key = lambda x:x[1])
        
        playerListSort = []
        for line in playerList:
            playerListSort.append([line[0], line[2]])
            
        return playerListSort
        
    def getDetail(self, bossid):
        '''
        返回对应boss的详细记录。
        return
        - 分锅与打分的列表，list格式
        - 战斗复盘中的DPS列表
        - 战斗复盘中的特定BOSS细节
        '''
        bossidStr = str(bossid)
        return self.pot[bossidStr], self.effectiveDPSList[bossidStr], self.detail[bossidStr], self.occResult[bossidStr], self.bh[bossidStr]
    
    def getBoss(self, bossid):
        '''
        返回对应boss的锅。
        return
        - 分锅与打分的列表，list格式
        '''
        bossidStr = str(bossid)
        return self.pot[bossidStr]
        
    def getBossName(self, bossid):
        '''
        查找对应boss的名称。
        return
        - 字符串格式的BOSS名。
        '''
        bossidStr = str(bossid)
        return self.detail[bossidStr]["boss"]
    
    def addBoss(self, bossid, potListScore, effectiveDPSList=[], detail={}, occResult={}, bh=None, change=1):
        '''
        当一个BOSS结束时，把分锅记录加入总记录中。
        或是当修改锅时，按对应的bossid取代原有的分锅记录。
        params
        - bossid 按时间顺序的BOSS编号。
        - potListScore 分锅与打分的列表，list格式
        - effectiveDPSList 战斗复盘中的DPS列表
        - detail 战斗复盘中的特定BOSS细节
        '''
        bossidStr = str(bossid)
        self.pot[bossidStr] = potListScore
        if change:
            self.effectiveDPSList[bossidStr] = effectiveDPSList
            self.detail[bossidStr] = detail
            self.occResult[bossidStr] = occResult
            self.bh[bossidStr] = bh
    
    def __init__(self):
        self.pot = {}
        self.effectiveDPSList = {}
        self.detail = {}
        self.occResult = {}
        self.bh = {}

class LiveActorAnalysis():
    '''
    实时演员信息类。维护当前结果信息的存储与获取。
    '''

    def getBossName(self):
        '''
        从结果记录中提取所有BOSS的名称，记录为字典形式。
        return
        - bossDict key为数字，value为boss名称。
        '''
        bossDict = {}
        lastNum = int(list(self.potContainer.pot.keys())[-1])
        for i in range(1, lastNum + 1):
            bossDict[str(i)] = self.potContainer.getBossName(i)
        return bossDict

    def getPlayer(self):
        '''
        从结果记录中提取所有ID与门派，按门派顺序排序
        return
        - playerListSort 排好序的ID与门派列表
        '''
        return self.potContainer.getPlayerOcc()

    def getPlayerPotList(self):
        playerPot = {}
        self.potListScore = self.potContainer.getAll()
        for line in self.potListScore:
            name = line[0].strip('"')
            if name not in playerPot:
                playerPot[name] = {"occ": line[1], "numPositive": 0, "numNegative": 0, "pot": []}
            playerPot[name]["pot"].append(line[1:])
            if line[-1] > 0:
                playerPot[name]["numPositive"] += line[-1]
            elif line[-1] < 0:
                playerPot[name]["numNegative"] += line[-1]
        self.playerPotList = playerPot
        return playerPot
        
    def getPlayerText(self, player):
        first = 1
        s = ""
        if player in self.playerPotList:
            for line in self.playerPotList[player]["pot"]:
                if first:
                    first = 0
                else:
                    s += '\n'
                s += "%s %s %s"%(line[2], line[3], str(line[-1]))
            
        return s
        
    def setSinglePotScore(self, bossNum, pos, pot):
        '''
        设定单个分锅记录的锅数。
        params
        - bossNum BOSS编号
        - tmp 记录的位置
        - pot 修改后的锅数
        '''
        bossidStr = str(bossNum)
        self.potContainer.pot[bossidStr][pos][-1] = pot
        
    def setServer(self, server):
        self.server = server
        
    def getServer(self):
        return self.server
        
    def setMapDetail(self, mapDetail):
        self.mapDetail = mapDetail
        
    def getMapDetail(self):
        return self.mapDetail
        
    def setBeginTime(self, beginTime):
        self.beginTime = beginTime
        
    def getBeginTime(self):
        return self.beginTime
        
    def changeResult(self, potListScore, bossNum):
        self.potContainer.addBoss(bossNum, potListScore, change=0)

    def addResult(self, potListScore, bossNum, effectiveDPSList, detail, occResult, bh):
        #self.potListScore.extend(potListScore)
        self.potContainer.addBoss(bossNum, potListScore, effectiveDPSList, detail, occResult, bh)
        
    def checkBossExists(self, bossNum):
        bossNumStr = str(bossNum)
        return bossNumStr in self.potContainer.pot
        
    def getLastBossNum(self):
        return list(self.potContainer.pot.keys())[-1]

    def checkEmpty(self):
        return list(self.potContainer.pot.keys()) == []
    
    def __init__(self):
        #self.potListScore = []
        self.potContainer = PotContainer()
        self.server = "未知"

class LiveListener():
    '''
    复盘监听类，在实时模式中控制开始复盘的时机。
    '''

    def getOneBattleLog(self, basepath, fileName):
        '''
        在对一条战斗记录进行复盘。
        params
        - basepath 监控的路径
        - lastFile 复盘数据对应的文件名
        - raw raw文件。如果是实时模式则为空，现场读取；否则从之前的记录中继承。
        return
        - liveGenerator 实时复盘对象，用于后续处理流程。
        '''
        controller = DataController(self.config)
        if self.mainWindow.bldDict != {}:
            controller.setRawData(self.mainWindow.bldDict)
        controller.getSingleData(self.mainWindow, fileName)  # 此处将MainWindow类本身传入
        
        try:
            fileNameInfo = [fileName, 0, 1]
            # print(self.mainWindow.bldDict)
            # print(fileNameInfo)
            # print(basepath)
            actorRep = ActorProReplayer(self.config, fileNameInfo, basepath, self.mainWindow.bldDict, self.mainWindow)

            analysisExitCode = actorRep.FirstStageAnalysis()
            if analysisExitCode == 1:
                messagebox.showinfo(title='提示', message='数据格式错误，请再次检查设置。如不能解决问题，尝试重启程序。\n在此状态下，大部分功能将不能正常使用。')
                raise Exception("数据格式错误，请再次检查设置。如不能解决问题，尝试重启程序。")
                
            actorRep.SecondStageAnalysis()
            if not actorRep.available:
                # 分片，记录
                self.mainWindow.lastBld = actorRep.bld
                return actorRep
            actorRep.ThirdStageAnalysis()
            
            self.analyser.setServer(actorRep.bld.info.server)
            self.analyser.setMapDetail(actorRep.bld.info.map)
            self.analyser.setBeginTime(actorRep.bld.info.battleTime)
            
            if actorRep.upload:
                actorRep.prepareUpload()
            # if liveGenerator.win:  # TODO 移除失败的复盘
            #     self.mainwindow.addRawData(fileName, liveGenerator.getRawData())
            # else:
            #     DestroyRaw(liveGenerator.getRawData())
        except Exception as e:
            traceback.print_exc()
            self.mainWindow.setNotice({"t1": "[%s]分析失败！"%actorRep.bld.info.boss, "c1": "#000000", "t2": "请保留数据，并反馈给作者~", "c2": "#ff0000"})
            return actorRep
            
        self.bossNum += 1
        self.mainWindow.setTianwangInfo(actorRep.ids, actorRep.server)
        return actorRep

    def getAllBattleLog(self, basepath, fileList):
        '''
        复盘模式中对所有战斗记录进行复盘。
        params
        - basepath 监控的路径
        - fileList 需要复盘的文件名列表.
        '''

        for file in fileList:
            actorRep = self.getOneBattleLog(basepath, file)
            if not actorRep.available:
                continue
            #print("[Detail]", actorRep.detail)
            potListScore = []
            for i in range(len(actorRep.potList)):
                if len(actorRep.potList[i]) <= 6:
                    potListScore.append(actorRep.potList[i] + [0])
                else:
                    potListScore.append(actorRep.potList[i])
            self.analyser.addResult(potListScore, self.bossNum, actorRep.effectiveDPSList, actorRep.detail, actorRep.occResult, actorRep.bh)

    def getNewBattleLog(self, basepath, lastFile):
        '''
        实时模式中复盘战斗记录，并控制窗口弹出、数据记录。
        params
        - basepath: 监控的路径
        - lastFile: 新增的文件，通常是刚刚完成的战斗复盘
        '''
        actorRep = self.getOneBattleLog(basepath, lastFile)
        if not actorRep.available:
            self.mainWindow.setNotice({"t1": "[%s]分析中断，等待完整记录..." % actorRep.bossname, "c1": "#000000"})
            return

        if self.window is not None and self.window.alive():
            self.window.final()
        
        if self.mainWindow is not None:
            self.mainWindow.setNotice({"t1": "[%s]分析完成！"%actorRep.bossname, "c1": "#000000"})
        
        window = SingleBossWindow(self.analyser, self.bossNum, self.mainWindow)

        self.window = window
        window.addPotList(actorRep.potList)
        window.setDetail(actorRep.potList, actorRep.effectiveDPSList, actorRep.detail, actorRep.occResult, actorRep.bh)
        window.openDetailWindow()

        self.mainWindow.notifier.show("分锅结果已生成", "[%s]的战斗复盘已经解析完毕，请打开结果界面分锅。"%actorRep.bossname)

    def listenPath(self, basepath):
        '''
        开始监控对应的路径。
        params
        - basepath: 监控的路径
        '''
        filelist = os.listdir(basepath)
        if self.config.item["general"]["datatype"] == "jx3dat":
            dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
        else:
            dataList = [x for x in filelist if x[-4:] == '.jcl']
        if dataList != []:
            newestFile = dataList[-1]
        else:
            newestFile = ""
        while(self.listenFlag):
            time.sleep(3)
            filelist = os.listdir(basepath)
            if self.config.item["general"]["datatype"] == "jx3dat":
                dataList = [x for x in filelist if x[-12:] == '.fstt.jx3dat']
            else:
                dataList = [x for x in filelist if x[-4:] == '.jcl']
            if dataList != []:
                lastFile = dataList[-1]
            else:
                lastFile = ""
            if lastFile != newestFile:
                newestFile = lastFile
                print("检测到新的复盘记录: %s"%lastFile)
                time.sleep(0.5)
                self.getNewBattleLog(basepath, lastFile)

    def stopListen(self):
        '''
        中止监听。
        '''
        self.listenFlag = False

    def startListen(self):
        '''
        产生监听线程，开始监控对应的路径。
        '''
        self.listenFlag = True
        self.listenThread = threading.Thread(target = self.listenPath, args = (self.basepath,)) 
        self.listenThread.setDaemon(True);
        self.listenThread.start()
    
    def __init__(self, basepath, config, analyser, mainWindow):
        '''
        构造方法。
        params
        - basepath: 战斗记录生成的路径。
        '''
        self.basepath = basepath
        self.config = config
        self.dpsThreshold = {"qualifiedRate": config.item["actor"]["qualifiedrate"],
                             "alertRate": config.item["actor"]["alertrate"],
                             "bonusRate": config.item["actor"]["bonusrate"]}
        self.analyser = analyser
        self.mainWindow = mainWindow
        
        self.bossNum = 0
        self.window = None

class AllStatWindow():
        
    def getPotColor(self, level):
        if level == 0:
            return "#777777"
        elif level == 1:
            return "#000000"
        else:
            return "#0000ff"
            
    def TryComment(self, tmp):
        '''
        准备评论窗口的函数。
        params
        - tmp 玩家编号
        '''
        id = self.playerID[tmp][0].strip('"')
        occ = self.playerID[tmp][1]
        pots = self.analyser.getPlayerText(id)
        server = self.analyser.getServer()
        userid = self.mainWindow.config.items_user["uuid"]
        mapDetail = self.analyser.getMapDetail()
        beginTime = self.analyser.getBeginTime()
        commentWindow = CommentWindow(id, occ, pots, server, userid, mapDetail, beginTime)
        commentWindow.start()
        
    def openBoss(self, bossID):
        '''
        打开对应BOSS的复盘界面。
        params
        - bossID 需要打开的BOSS的ID。
        '''
        replayWindow = SingleBossWindow(self.analyser, bossID, self.mainWindow)
        replayWindow.constructReplayByNum(bossID)
        
    def final(self):
        '''
        关闭窗口。
        '''
        self.window.destroy()

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('总结')
        window.geometry('600x700')
        
        frame1 = tk.Frame(window)
        frame1.pack()

        bossDict = self.analyser.getBossName()
        for id in bossDict:
            idNum = int(id)
            button = tk.Button(frame1, text=bossDict[id], width=10, height=1, command=lambda idNum=idNum:self.openBoss(idNum))
            row = (idNum-1) // 6
            column = (idNum-1) % 6
            button.grid(row=row, column=column)
            
        frame2 = tk.Frame(window)
        frame2.pack()
        
        numPlayer = len(self.playerID)
        
        i = 0
        
        self.toolTips = []
        
        for player in self.playerID:
            
            if player[0] in self.playerPotList:
                line = self.playerPotList[player[0]]
            else:
                line = {"occ": player[1], "numPositive": 0, "numNegative": 0, "pot": []}

            name = player[0].strip('"')
            occ = line["occ"]
            color = getColor(occ)
            nameLabel = tk.Label(frame2, text=name, width = 13, fg=color)
            nameLabel.grid(row=i, column=0)
            
            posNumText = ""
            if line["numPositive"] > 0:
                posNumText = "+%s"%str(line["numPositive"])
            positiveLabel = tk.Label(frame2, text=posNumText, width=5, fg="#007700", font=("Arial", 12, "bold"))
            positiveLabel.grid(row=i, column=1)
            
            negNumText = ""
            if line["numNegative"] < 0:
                negNumText = "%s"%str(line["numNegative"])
            negativeLabel = tk.Label(frame2, text=negNumText, width=5, fg="#ff0000", font=("Arial", 12, "bold"))
            negativeLabel.grid(row=i, column=2)
            
            tmp = i
            button1 = tk.Button(frame2, bitmap="warning", text="评价", width=60, height=15, compound=tk.LEFT, command=lambda tmp=tmp: self.TryComment(tmp))
            button1.grid(row=i, column=3)
            
            text = self.analyser.getPlayerText(name)
            toopTip = ToolTip(nameLabel, text)
            self.toolTips.append(toopTip)
            
            i += 1
            
        buttonFinal = tk.Button(window, text='查看完成', width=10, height=1, command=self.final)
        buttonFinal.place(x=250, y=670)
        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)
        #window.mainloop()

    def start(self):
        self.windowThread = threading.Thread(target=self.loadWindow)
        self.windowThread.start()
        
    def addPotList(self):
        self.potListScore = self.analyser.potContainer.getAll()
        self.playerPotList = self.analyser.getPlayerPotList()
        self.playerID = self.analyser.getPlayer()

    def __init__(self, analyser, mainWindow):
        self.analyser = analyser
        self.mainWindow = mainWindow
        self.addPotList()
        
        