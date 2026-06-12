# 隱私權政策 / Privacy Policy — TMSBug Discord Bot

**最後更新 / Last updated: June 12, 2026**

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

這些資料**僅用於**在指定頻道發送歡迎／離開訊息，以及更新人數顯示頻道名稱。資料**不會在事件處理完畢後保留**。

The Bot receives member data via Discord's **Server Members Intent** when members join or leave the server. This includes username, user ID, account creation date, join/leave timestamp, and avatar URL. Data is used solely to post welcome/farewell messages and update the member count channel. It is **not stored** beyond the execution of these events.

---

### 2.2 訊息內容與聊天記錄 / Message Content & Chat Logging

本 Bot 透過 Discord 的 **Message Content Intent** 讀取訊息內容，用途如下：

- 偵測特定觸發詞以處理入會申請
- 回應管理員指令（例如 `serverinfo`）
- 依訊息內容觸發表情符號反應
- **記錄伺服器聊天紀錄**（詳見下方說明）

**聊天記錄儲存（Chat Logging）**

本 Bot 會將伺服器內所有人類使用者（非 Bot）的訊息以 CSV 格式記錄於伺服器管理員的本機裝置。每筆記錄包含：

- 訊息序號與時間戳記
- 頻道名稱
- 作者使用者名稱
- 訊息完整內容
- 附件與貼圖資訊
- 訊息編輯前後的版本

**記錄目的**：供伺服器管理員查核違規行為、處理糾紛及維護社群安全。

**存取權限**：聊天記錄僅限具有管理員身份組的成員透過 Bot 指令存取，不對外公開。

**儲存位置**：記錄以每日 CSV 檔案儲存於管理員本機，不上傳至任何雲端服務或第三方。

**保留期限**：聊天記錄保留 **6 個月**，到期後刪除。

The Bot reads message content via Discord's **Message Content Intent** for join request handling, moderator commands, emoji triggers, and **chat logging**.

**Chat Logging**: The Bot records all non-bot messages in the server to local CSV files on the administrator's machine. Each entry includes a sequence number, timestamp, channel name, author username, full message content, attachments, stickers, and edit history (before/after). This data is used solely for moderation purposes (reviewing rule violations and resolving disputes). Access is restricted to server administrators via a bot command. Logs are stored locally, not uploaded to any cloud service or third party, and are **deleted after 6 months**.

---

### 2.3 我們不收集的資料 / Data We Do NOT Collect

- 不收集密碼、電子郵件或付款資訊
- 不跨伺服器或跨平台追蹤使用者
- 不將任何資料出售、分享或轉移給第三方
- 不將資料用於廣告或用戶分析

We do not collect passwords, emails, or payment information. We do not track users across servers or platforms, sell data to third parties, or use data for advertising or profiling.

---

## 3. 資料保留 / Data Retention

| 資料類型 / Data Type | 保留期限 / Retention |
|---|---|
| 成員加入／離開資訊 Member join/leave info | 不儲存（僅即時處理）Not stored |
| 訊息內容、作者、頻道 Message content, author, channel | 本地 CSV 儲存，保留 6 個月後刪除 Stored locally in CSV, deleted after 6 months |
| 訊息編輯紀錄 Message edit history | 同上 Same as above |
| 彙總訊息計數 Aggregate message count | 本地儲存為累計數字，不含個人資訊 Stored locally, no PII |

---

## 4. 資料安全 / Data Security

本 Bot 運行於私人管理的伺服器上。除 Discord 官方 API 外，成員資料不會傳輸至任何外部服務。Bot 的設定與日誌存取權限僅限伺服器擁有者。

The Bot runs on a privately operated server. No member data is transmitted to external services beyond Discord's own API. Access to the Bot's configuration and logs is restricted to the server owner.

---

## 5. 第三方服務 / Third-Party Services

本 Bot 使用以下外部 API：

- **Discord API** — 核心 Bot 功能（適用 [Discord 隱私權政策](https://discord.com/privacy)）
- **楓之谷相關 API** — 遊戲資料查詢（不傳輸個人資料）

The Bot interacts with the Discord API and MapleStory-related game data APIs. No personal data is transmitted to game data APIs.

---

## 6. 兒童隱私 / Children's Privacy

本 Bot 服務於遊戲社群伺服器。我們不會有意收集 13 歲以下用戶的資料。若您認為未成年人的資料遭到收集，請立即聯繫我們。

We do not knowingly collect data from users under the age of 13. If you believe a minor's data has been collected, please contact us immediately.

---

## 7. 政策變更 / Changes to This Policy

本政策可能不定期更新。繼續使用本 Bot 即代表接受更新後的政策內容。文件頂端的「最後更新」日期將反映任何修訂。

We may update this policy from time to time. Continued use of the Bot constitutes acceptance of any changes. The "Last updated" date will reflect revisions.

---

## 8. 聯絡我們 / Contact

如對本隱私權政策有任何疑問，請透過 TMS 社群 Discord 伺服器聯繫伺服器擁有者或管理員。

For questions or concerns, please contact the server owner or moderators via the TMS community Discord server.

---

*本政策僅適用於 TMSBug Bot（Discord Application ID: 684625575729561609）及其運作的私人伺服器。*

*This Privacy Policy applies solely to the TMSBug bot (Discord Application ID: 684625575729561609) and the private server it operates in.*
