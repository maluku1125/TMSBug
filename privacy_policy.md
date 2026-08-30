# 隱私權政策 / Privacy Policy — TMSBug Discord Bot

**最後更新 / Last updated: August 30, 2026**

---

## 1. 概述 / Overview

TMSBug（以下簡稱「本 Bot」）是一個服務於私人楓之谷台服 Discord 社群的管理與工具 Bot。本隱私權政策說明本 Bot 存取哪些資料、如何使用，以及您身為使用者的相關權利。

TMSBug ("the Bot") is a moderation and utility bot serving a private MapleStory Taiwan community Discord server. This Privacy Policy explains what data the Bot accesses, how it is used, and your rights as a user.

---

## 2. 我們存取的資料 / Data We Access

### 2.1 成員資訊 / Member Information

本 Bot 透過 Discord 的 **Server Members Intent**，在成員加入或離開伺服器時接收以下資料：

- Discord 使用者名稱
- Discord 使用者 ID
- 帳號創建日期
- 加入／離開時間戳記
- 大頭貼網址

這些資料**僅用於**在指定頻道發送歡迎／離開訊息、標示新註冊帳號（帳號建立未滿 14 天者以紅色標示，協助管理員辨識可疑帳號），以及更新人數顯示頻道名稱。資料**不會在事件處理完畢後保留**。

The Bot receives member data via Discord's **Server Members Intent** when members join or leave the server. This includes username, user ID, account creation date, join/leave timestamp, and avatar URL. It is used solely to post welcome/farewell messages, flag newly created accounts (accounts less than 14 days old are highlighted to help moderators identify suspicious accounts), and update the member count channel. Data is **not stored** beyond the execution of these events.

---

### 2.2 訊息內容 / Message Content

本 Bot 透過 Discord 的 **Message Content Intent** 讀取訊息內容，用途如下：

本 Bot 透過 Discord 的 **Message Content Intent** 讀取訊息內容，且**僅限以下兩項用途**：

1. **刪除／編輯訊息記錄**（詳見 2.3）
2. **反垃圾訊息保護**（詳見 2.4）

以下功能同樣會處理訊息文字，但**不依賴** Message Content Intent —— 它們屬於 Discord 官方明訂的例外情形，本 Bot 只在使用者主動觸發的那一則訊息上取得內容：

| 功能 | 觸發方式 | 適用例外 |
|---|---|---|
| **AI 對話助理**（詳見 2.5）| 使用者 @提及 Bot | 提及 Bot 的訊息 |
| **刪除並備份**（管理稽核）| 管理員對訊息按右鍵 → 應用程式 | 訊息右鍵選單指令的目標訊息 |
| **查巴哈**（論壇搜尋）| 使用者對訊息按右鍵 → 應用程式 | 訊息右鍵選單指令的目標訊息 |

其餘所有指令皆為斜線指令（slash command），完全不讀取一般訊息內容。本 Bot 已無任何前綴指令與關鍵字自動回應功能。

The Bot reads message content via the **Message Content Intent** for exactly two purposes: **logging of deleted and edited messages** (2.3) and **anti-spam protection** (2.4). Three further features process message text but do **not** rely on the intent — they operate solely through Discord's documented exceptions (messages that @mention the bot, and messages targeted by a message context-menu command): the AI assistant, the moderation backup command, and the forum search command. Every other command is a slash command and reads no message content. The Bot no longer has any prefix commands or keyword auto-responses.

---

### 2.3 刪除／編輯訊息記錄 / Deleted & Edited Message Logging

**⚠️ 自 2026 年 8 月 30 日起，本 Bot 不再記錄一般聊天訊息。** 您正常發言的內容**不會**被寫入任何檔案。

僅在下列事件發生時，該則訊息才會被寫入加密記錄：

| 事件 | 記錄內容 |
|---|---|
| **訊息被刪除** | 該則已刪除訊息的內容 |
| **訊息被批次刪除** | 同上 |
| **訊息被編輯** | 編輯**前**與編輯**後**兩個版本 |

理由：這些內容一旦發生就無法再從 Discord 取回（Discord 的稽核日誌只記錄「發生了刪除」而不含內容，也沒有任何 API 可以取回已刪除的訊息），因此是管理員處理檢舉與糾紛時唯一可用的依據。未被刪除或編輯的訊息隨時都能在頻道中查看，不需要另行留存。

每筆記錄包含：事件類型與時間戳記、訊息 ID、頻道名稱、作者使用者名稱、訊息內容、附件與貼圖資訊。

| 項目 | 說明 |
|---|---|
| **目的** | 供管理員查核違規行為、處理糾紛及維護社群安全 |
| **記錄範圍** | **僅**被刪除或被編輯的訊息；僅限本社群伺服器；不含 Bot 訊息、不含私訊 |
| **儲存方式** | **以 Fernet（AES）加密**儲存於管理員本機，非明文 |
| **儲存位置** | 僅本機，**不上傳至任何雲端服務或第三方** |
| **保留期限** | **14 天**，到期自動刪除 |
| **存取權限** | 僅具管理員身分組者可透過 Bot 指令存取，不對外公開 |

**As of August 30, 2026, the Bot no longer logs ordinary chat messages.** A message is written to the encrypted log **only** when it is deleted, bulk-deleted, or edited (in which case both the before and after versions are kept). This is because such content can no longer be retrieved from Discord — the audit log records that a deletion occurred but never its content, and there is no API to retrieve a deleted message — making it the only evidence available to moderators handling reports and disputes. Messages that are never deleted or edited remain visible in the channel and are not stored. Logs are **encrypted at rest using Fernet (AES)**, stored only on the administrator's local machine, **never uploaded to any cloud service or third party**, **automatically deleted after 14 days**, and accessible only to server administrators.

---

### 2.4 反垃圾訊息保護 / Anti-Spam Protection

為防範遭盜用帳號的洗版行為，本 Bot 會在記憶體中暫存每位使用者近期的訊息參照（內容特徵、頻道、時間），用以偵測「短時間內於多個頻道張貼相同內容」的模式。

- **偵測條件**：60 秒內、相同內容出現在 3 個以上不同頻道
- **暫存時間**：最多 5 分鐘，僅存於記憶體，**不寫入磁碟**
- **觸發後果**：刪除該使用者近 5 分鐘內的訊息，並將該帳號**禁言 1 小時**，同時在管理員頻道留下記錄

若您認為遭到誤判，請聯繫伺服器管理員，禁言可立即解除。

To protect against compromised accounts, the Bot keeps short-lived in-memory references to recent messages (content fingerprint, channel, timestamp) to detect identical content posted across 3 or more channels within 60 seconds. This data is held **in memory only for at most 5 minutes and is never written to disk**. When triggered, the Bot deletes the offending messages and times the account out for 1 hour, logging the action for moderators. If you believe this was in error, contact a moderator — timeouts can be lifted immediately.

---

### 2.5 AI 對話助理與第三方傳輸 / AI Assistant & Third-Party Transfer

**⚠️ 重要：本功能會將您的訊息內容傳送至 Google。**

當您在訊息中 **@提及本 Bot** 時（且僅在此情況下），本 Bot 會將以下資料傳送至 **Google Gemini API** 以產生回覆：

- 您該則訊息的文字內容（上限 500 字）
- 該則訊息附加的圖片（最多 3 張，單張上限 4 MB）
- 您的 Discord 顯示名稱與使用者 ID（供 AI 在回覆中標記您）

| 項目 | 說明 |
|---|---|
| **觸發條件** | **僅在使用者主動 @提及 Bot 時**；其他所有訊息不會傳送至 Google |
| **接收方** | Google（Gemini API），適用 [Google 隱私權政策](https://policies.google.com/privacy) |
| **使用頻率限制** | 每位使用者每 5 分鐘最多 3 次 |
| **本地保留** | 本 Bot **不另行儲存**送往 AI 的內容或其回覆（若該訊息之後被刪除或編輯，則另依 2.3 處理） |
| **如何避免** | **不要 @提及本 Bot** 即可完全避免資料傳送至 Google |

**When you @mention the Bot**, and only then, the Bot sends that message's text (up to 500 characters), up to 3 attached images (max 4 MB each), and your display name and user ID to the **Google Gemini API** to generate a reply. This is subject to [Google's Privacy Policy](https://policies.google.com/privacy). All other messages are never sent to Google. Usage is limited to 3 requests per user per 5 minutes. **To avoid this entirely, simply do not @mention the Bot.**

---

### 2.6 我們不收集的資料 / Data We Do NOT Collect

- 不收集密碼、電子郵件或付款資訊
- 不使用 Presence Intent，不追蹤您的線上狀態或遊玩活動
- 不跨伺服器或跨平台追蹤使用者
- 不將任何資料出售、分享或轉移給第三方（2.5 所述的 AI 功能除外）
- 不將資料用於廣告、用戶分析或訓練 AI 模型

We do not collect passwords, emails, or payment information. We do not use the Presence Intent and do not track your online status or activity. We do not track users across servers, sell data, or use data for advertising, profiling, or AI model training. The only third-party transfer is the AI feature described in 2.5.

---

## 3. 資料保留 / Data Retention

| 資料類型 / Data Type | 保留期限 / Retention |
|---|---|
| 成員加入／離開資訊 Member join/leave info | 不儲存（僅即時處理）Not stored |
| 刪除／編輯訊息記錄（加密）Deleted & edited message logs (encrypted) | **14 天後自動刪除 / Auto-deleted after 14 days** |
| 反垃圾訊息暫存 Anti-spam cache | 記憶體中最多 5 分鐘 / In memory, max 5 minutes |
| 送往 AI 的內容 Content sent to AI | 本 Bot 不另行保留 / Not retained by the Bot |
| 管理稽核記錄 Moderation audit logs | 留存於管理員專用 Discord 頻道 / Kept in a private staff Discord channel |
| 彙總訊息計數 Aggregate message count | 純數字統計，不含個人資訊 / Aggregate count only, no PII |

---

## 4. 資料安全 / Data Security

本 Bot 運行於私人管理的伺服器上。刪除／編輯訊息記錄以 Fernet（AES）加密儲存，加密金鑰與記錄分開保管。Bot 的設定、金鑰與日誌存取權限僅限伺服器擁有者。除 Discord API 及 2.5 所述的 Google Gemini API 外，資料不會傳輸至其他外部服務。

The Bot runs on a privately operated server. Deleted/edited message logs are encrypted with Fernet (AES), with the key stored separately. Access to configuration, keys, and logs is restricted to the server owner. No data is transmitted to external services other than the Discord API and the Google Gemini API described in 2.5.

---

## 5. 第三方服務 / Third-Party Services

| 服務 / Service | 用途 / Purpose | 是否傳輸個人資料 / Personal Data Sent |
|---|---|---|
| **Discord API** | 核心 Bot 功能 | 是（[Discord 隱私權政策](https://discord.com/privacy)）|
| **Google Gemini API** | AI 對話助理（詳見 2.5）| **是** —— 僅在使用者 @提及 Bot 時（[Google 隱私權政策](https://policies.google.com/privacy)）|
| **Nexon Open API** | 楓之谷遊戲資料查詢 | 否 —— 僅傳送遊戲角色名稱，不含 Discord 個人資料 |

---

## 6. 您的權利 / Your Rights

- **查詢**：您可要求得知本 Bot 持有哪些與您相關的資料
- **刪除**：您可要求刪除與您有關的刪除／編輯訊息記錄（未逾 14 天保留期者）
- **拒絕 AI 功能**：不 @提及本 Bot 即可，無需任何設定
- **退出**：離開伺服器後，本 Bot 不會再收集您的任何資料

請透過第 8 節的方式聯繫我們行使上述權利。

You may request access to or deletion of your data (within the 14-day retention window), opt out of the AI feature simply by not mentioning the Bot, and leaving the server stops all data collection. Contact us via Section 8.

---

## 7. 兒童隱私 / Children's Privacy

本 Bot 服務於遊戲社群伺服器。我們不會有意收集 13 歲以下用戶的資料。若您認為未成年人的資料遭到收集，請立即聯繫我們。

We do not knowingly collect data from users under the age of 13. If you believe a minor's data has been collected, please contact us immediately.

---

## 8. 政策變更與聯絡 / Changes & Contact

本政策可能不定期更新，文件頂端的「最後更新」日期將反映任何修訂。如對本隱私權政策有任何疑問，或欲行使第 6 節所述權利，請透過 TMS 社群 Discord 伺服器聯繫伺服器擁有者或管理員。

We may update this policy from time to time; the "Last updated" date reflects revisions. For questions or to exercise your rights under Section 6, contact the server owner or moderators via the TMS community Discord server.

---

*本政策僅適用於 TMSBug Bot（Discord Application ID: 1541025225326731365）及其運作的私人伺服器。*

*This Privacy Policy applies solely to the TMSBug bot (Discord Application ID: 1541025225326731365) and the private server it operates in.*
