import random
import json
import os
import glob

from functions.tinyfunctions import probably

# Blacklist cheannel
prizechannelblacklist = [
    477755023787556866, #弓箭手村
    945930059179520010,
    1049599921143164948,
    656213230976237628, #W0
    656213444621631508, #W1
    656213502163419196, #W2
    656213580533727233, #W3
    656213648435445775, #W4
    656213683155763259, #W6
    656213779360776242 #W45
    ]

def use_apple(AppleProbabilityTableDate, channelid, messageauthor):

    if channelid in prizechannelblacklist:
        GoldAppleMessage = '請到<#578080016634609664>進行'
    else: 
        # open file
        AplleProbabilityFile = f'C:\\Users\\User\Desktop\\maplestory_discordbot\\Data\\GoldAppleProbabilityTable.json'

        with open(AplleProbabilityFile, 'r', encoding='utf-8') as file:
            data = json.load(file)
            apple_chance_dict = data[AppleProbabilityTableDate]['apple_chance']
            box_chance_dict = data[AppleProbabilityTableDate]['box_chance']

        applecnt = 0
        boxcnt = 0
        boxgetprize = False

        while True:
            randnumber = random.random()

            if applecnt == 100:  # apple > 100抽箱子
                boxcnt += 1
                applecnt = 0
                randnumber = random.random()

                totalchanceupper = 0
                totalchancelower = 0
                for i in box_chance_dict:
                    totalchanceupper += box_chance_dict[i]
                    if randnumber < totalchanceupper and totalchancelower < randnumber:
                        prize = i
                        boxgetprize = True
                        totalchancelower += box_chance_dict[i]
                        break  # 箱子抽到break for迴圈
                else:
                    continue
                break

            applecnt += 1
            totalchanceupper = 0
            totalchancelower = 0
            for i in apple_chance_dict:
                totalchanceupper += apple_chance_dict[i]
                if randnumber < totalchanceupper and totalchancelower < randnumber:
                    prize = i
                    totalchancelower += apple_chance_dict[i]
                    break
            else:
                continue
            break
        total_count = boxcnt*100 + applecnt
        if boxgetprize == True:
            GoldAppleMessage = f"{messageauthor}在第{boxcnt}箱金箱子中，抽到了{prize}"
        else:
            GoldAppleMessage = f"{messageauthor}在第{total_count}顆蘋果中，抽到了{prize}"

    return GoldAppleMessage

def use_fashionbox(FashionBoxProbabilityTableDate, channelid, messageauthor):
    
    if channelid in prizechannelblacklist:
        FashionboxMessage = '請到<#578080016634609664>進行'
    else:         
        FashionBoxProbabilityFile = f'C:\\Users\\User\Desktop\\maplestory_discordbot\\Data\\FashionBoxProbabilityTable.json'

        with open(FashionBoxProbabilityFile, 'r', encoding='utf-8') as file:
            data = json.load(file)
            fashion_box_chance_dict = data[FashionBoxProbabilityTableDate]    

        boxcnt = 0
        boxgetprize = False
        while True:
            randnumber = random.random()
            if boxcnt == 10:
                prize = 0
                break
                        
            boxcnt += 1
            totalchanceupper = 0
            totalchancelower = 0
            for item in fashion_box_chance_dict:
                totalchanceupper += fashion_box_chance_dict[item]
                if randnumber < totalchanceupper and totalchancelower < randnumber:
                    prize = item
                    boxgetprize = True                    
                    break                
                totalchancelower += fashion_box_chance_dict[item]
            else:
                continue
            break     

        if boxgetprize == True:
            FashionboxMessage = f"{messageauthor}在第{boxcnt}箱時尚隨機箱中，抽到了**{prize}**"
        else:
            FashionboxMessage = f"{messageauthor}<a:pootong_gif:802915645670293514>"

    return FashionboxMessage



