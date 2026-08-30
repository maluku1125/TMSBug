"""訊息記錄（僅記錄「被刪除」與「被編輯」的訊息）

自 2026-08-30 起不再記錄所有訊息，僅在下列事件發生時寫入：
  Delete      —— 訊息被刪除（含使用者自刪、管理員刪除、反洗版自動刪除）
  BulkDelete  —— 訊息被批次刪除
  Edit_Before —— 訊息被編輯前的內容
  Edit_After  —— 訊息被編輯後的內容

正常聊天不落地，大幅縮小留存範圍；只有「事後無法從 Discord 取回」的內容才保存。
"""

import time
import os
import glob
import json
import pandas as pd
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

CHATLOG_PATH = 'C:\\Users\\User\\Desktop\\DiscordBotlog\\ChatLog'
KEY_PATH     = 'C:\\Users\\User\\Desktop\\DiscordBotlog\\chatlog.key'
# 訊息內容保留天數：依 Discord Developer Policy，訊息內容不應留存超過
# 達成功能所需的時間；14 天亦對齊 Discord bulk-delete API 的上限。
LOG_RETENTION_DAYS = 14

# 匯出 CSV 的欄位順序
_COLUMNS = ['Event', 'Time', 'Channel', 'Author', 'Content',
            'Attachments', 'Stickers', 'MessageID']

saveddate = ''

# ── 金鑰管理 ────────────────────────────────────────────────

def _load_or_create_key():
    """載入金鑰；若不存在則自動產生並儲存"""
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
    print(f'[ChatLog] 新加密金鑰已產生：{KEY_PATH}')
    print(f'[ChatLog] ⚠️  請備份此金鑰，遺失將無法讀取歷史記錄')
    return key

_fernet = Fernet(_load_or_create_key())

# ── 清理過期檔案 ─────────────────────────────────────────────

def chat_log_cleanup():
    """刪除超過 LOG_RETENTION_DAYS 天的 .enc 檔案"""
    cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    deleted = []

    for filepath in glob.glob(f'{CHATLOG_PATH}\\*_TMS新楓之谷_Chatlog.enc'):
        filename = os.path.basename(filepath)
        datestr = filename.split('_')[0]
        try:
            if datetime.strptime(datestr, '%Y%m%d') < cutoff:
                os.remove(filepath)
                deleted.append(filename)
                print(f'[ChatLog] 已刪除過期記錄：{filename}')
        except (ValueError, OSError):
            pass

    print(f'[ChatLog] 清理完成，共刪除 {len(deleted)} 個檔案' if deleted else '[ChatLog] 清理完成，無過期檔案')

# ── 寫入 ─────────────────────────────────────────────────────

def chat_log_save(Event, MessageChannel, MessageAuthor, MessageContent,
                  MessageAttachments, MessageStickers, MessageID=None):
    """寫入一筆事件記錄。

    Event：'Delete' / 'BulkDelete' / 'Edit_Before' / 'Edit_After'
    僅由 Normal_ChatLogging 的刪除／編輯事件呼叫；一般訊息不會進到這裡。
    """
    global saveddate
    date = time.strftime('%Y%m%d', time.localtime(time.time()))

    if date != saveddate:
        saveddate = date
        chat_log_cleanup()  # 每天第一次寫入時自動清理

    timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

    row = {
        'Event'      : str(Event),
        'Time'       : timestamp,
        'Channel'    : str(MessageChannel),
        'Author'     : str(MessageAuthor),
        'Content'    : str(MessageContent)     if MessageContent     else '-',
        'Attachments': str(MessageAttachments) if MessageAttachments else '-',
        'Stickers'   : str(MessageStickers)    if MessageStickers    else '-',
        'MessageID'  : str(MessageID)          if MessageID          else '-',
    }

    encrypted_line = _fernet.encrypt(json.dumps(row, ensure_ascii=False).encode()).decode()

    os.makedirs(CHATLOG_PATH, exist_ok=True)
    with open(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.enc', 'a', encoding='utf-8') as f:
        f.write(encrypted_line + '\n')

# ── 讀取（內部用）────────────────────────────────────────────

def _decrypt_log(filepath) -> pd.DataFrame:
    """解密 .enc 檔案並回傳 DataFrame"""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(_fernet.decrypt(line.encode()).decode())
            except Exception:
                continue  # 略過損壞的行
            # 相容 2026-08-30 前的舊格式（欄位名為 'No.'，且為逐則記錄的流水號）
            if 'Event' not in row:
                old = str(row.pop('No.', '-'))
                row['Event'] = 'Message(舊)' if old.isdigit() else old
            row.pop('No.', None)
            rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # 補齊缺漏欄位並固定順序
    for col in _COLUMNS:
        if col not in df.columns:
            df[col] = '-'
    return df[_COLUMNS].fillna('-')

def get_log_count() -> int:
    """今日已記錄的事件筆數（不解密，只數行）"""
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    try:
        with open(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.enc', 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except FileNotFoundError:
        return 0

def chat_log_get() -> pd.DataFrame:
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    return _decrypt_log(f'{CHATLOG_PATH}\\{date}_TMS新楓之谷_Chatlog.enc')

# ── 匯出（管理員查閱用）──────────────────────────────────────

def chat_log_export_csv(date_str: str = None) -> str:
    """
    將指定日期的加密記錄解密並匯出為臨時 CSV，回傳 CSV 路徑。
    date_str 格式：'YYYYMMDD'，預設為今天。
    查閱完畢後請自行刪除匯出的 CSV。
    """
    if date_str is None:
        date_str = time.strftime('%Y%m%d', time.localtime(time.time()))

    enc_path = f'{CHATLOG_PATH}\\{date_str}_TMS新楓之谷_Chatlog.enc'
    csv_path = f'{CHATLOG_PATH}\\{date_str}_TMS新楓之谷_Chatlog_export.csv'

    df = _decrypt_log(enc_path)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f'[ChatLog] 匯出完成：{csv_path}')
    return csv_path
