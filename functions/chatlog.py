import time
import os
import glob
import pandas as pd
import csv
from datetime import datetime, timedelta

CHATLOG_PATH = 'C:\\Users\\User\\Desktop\\DiscordBotlog\\ChatLog'
LOG_RETENTION_DAYS = 180

saveddate = ''
firstfile = False

def chat_log_cleanup():
    """刪除超過 LOG_RETENTION_DAYS 天的 ChatLog CSV 檔案"""
    cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    deleted = []

    for filepath in glob.glob(f'{CHATLOG_PATH}\\*_TMS新楓之谷_Chatlog.csv'):
        filename = os.path.basename(filepath)
        datestr = filename.split('_')[0]  # 取出 YYYYMMDD
        try:
            filedate = datetime.strptime(datestr, '%Y%m%d')
            if filedate < cutoff:
                os.remove(filepath)
                deleted.append(filename)
                print(f'[ChatLog] 已刪除過期記錄：{filename}')
        except (ValueError, OSError):
            pass

    if deleted:
        print(f'[ChatLog] 清理完成，共刪除 {len(deleted)} 個檔案')
    else:
        print(f'[ChatLog] 清理完成，無過期檔案')


def chat_log_save(SpeakCount, MessageChannel, MessageAuthor, MessageContent, MessageAttachments, MessageStickers):
    global saveddate
    date = time.strftime('%Y%m%d', time.localtime(time.time()))

    if date != saveddate :
        saveddate = date
        firstfile = True
        chat_log_cleanup()  # 每天第一次寫入時自動清理過期檔案
    else:
        firstfile = False

    ChatLog_output_path = CHATLOG_PATH
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

    if MessageContent == [] :
        MessageContent = '-'
    if MessageAttachments == [] :
        MessageAttachments = '-'
    if MessageStickers == [] :
        MessageStickers = '-'

    with open(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.csv', 'a', newline='', encoding='utf-8') as csvfile:

        fieldnames = ['No.', 'Time', 'Chennal', 'Author', 'Content', 'Attachments', 'Stickers']        
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames) # 將 dictionary 寫入 CSV 檔 
        if firstfile == True :
            firstfile = False
            writer.writeheader()

        # 寫入資料
        writer.writerow(
            {
            'No.': SpeakCount,
            'Time' : timestamp,
            'Chennal': MessageChannel,
            'Author': MessageAuthor,
            'Content' : MessageContent,
            'Attachments' :MessageAttachments,
            'Stickers' : MessageStickers        
            }
        ) 

def get_speak_count():
    date = time.strftime('%Y%m%d', time.localtime(time.time()))

    try:
        Chat_log_df = pd.read_csv(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.csv')
        Chat_log_df['No.'] = pd.to_numeric(Chat_log_df['No.'], errors='coerce')
        speak_count = Chat_log_df['No.'].max()
    except FileNotFoundError:
        speak_count = 0

    return int(speak_count)


def chat_log_get():
    date = time.strftime('%Y%m%d', time.localtime(time.time()))

    Chat_log_df = pd.read_csv(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.csv')

    return Chat_log_df