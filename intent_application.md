# Discord Privileged Intent Application — TMSBug_v3 (1541025225326731365)

第 2 次申請 / Resubmission — 2026-08-30

---

## ① 應用程式詳細資訊 / Application Details

TMSBug (App ID 1541025225326731365) is a private moderation and utility bot for a
Traditional-Chinese MapleStory ("新楓之谷") community. It is not a public bot: it is not
listed in any bot directory, has no public invite page, and is operated by the community's
own staff. Its primary server is a long-running MapleStory Taiwan community
(guild ID 420666881368784929), and it currently serves roughly 10,000 users.

WHAT THE BOT DOES

1. Moderation and audit
   - "Delete & Archive" — a MESSAGE CONTEXT-MENU command. A staff member right-clicks an
     offending message; the bot copies the text and re-uploads its attachments to a
     staff-only log channel, then deletes the original, so the evidence survives the
     deletion. Restricted to one staff role, usable only in channels @everyone can read
     and write in, and rate-limited (10 uses / 30 minutes, then a 24-hour lock).
   - Encrypted logging of deleted and edited messages for dispute resolution
     (see the Message Content section).
   - Anti-spam protection against compromised member accounts (see the Message Content
     section).

2. Member events
   - Welcome and farewell embeds in dedicated channels.
   - Accounts younger than 14 days are highlighted in red in the welcome embed so staff
     can watch likely scam or raid accounts.
   - A channel whose name displays the live member count.

3. Utility slash commands
   - /serverinfo, /chatlog (staff-only log retrieval), /help, /ping, /hi, /randnumber
   - "Search Bahamut" — a MESSAGE CONTEXT-MENU command that turns the selected message
     into a search query on the Bahamut MapleStory forum, the main community forum in
     Taiwan.

4. AI assistant
   - When a user @mentions the bot, that message is sent to the Google Gemini API and the
     reply is posted in the channel. It is triggered only by an explicit @mention, is
     limited to 3 requests per user per 5 minutes, and the transfer to Google is
     explicitly disclosed in our Privacy Policy.

---

## ② 您是否有公開的隱私權政策 → YES

下拉選 Yes，並確認 App Settings → General Information → Privacy Policy URL 已填公開網址。

---

## ③ Server Members Intent — 為什麼需要

We need GUILD_MEMBERS because four features depend on the GUILD_MEMBER_ADD and
GUILD_MEMBER_REMOVE gateway events and on the member cache, none of which are delivered
without this intent.

1. Welcome and farewell messages.
   On join, the bot posts an embed to the welcome channel; on leave, to the farewell
   channel. Both are driven directly by the member events.

2. New-account safety flag.
   Our community is regularly targeted by scam and phishing accounts, which are almost
   always freshly created. The welcome embed shows the account's creation date and turns
   red when the account is less than 14 days old, so staff know to watch that member from
   the moment they arrive. This uses the member object delivered with the join event.

3. Live member count channel.
   A channel name is updated to the current member count on every join and leave. This
   needs both the events and guild.member_count, which is only accurate with the member
   intent.

4. Moderator exemption in anti-spam.
   Before acting on a suspected spammer, our anti-spam check reads the author's guild
   permissions from the member cache and exempts anyone with Manage Messages. Without the
   member intent that cache is incomplete, and a moderator could be wrongly timed out by
   our own bot.

WHAT WE DO WITH THE DATA

Nothing is persisted. The username, user ID, avatar URL and account-creation date are used
to render the embed and update the channel name, and are discarded when the event handler
returns. We do not build a member database, we do not export or sync member lists anywhere,
and we do not use member data for analytics, profiling or advertising.

---

## ④ 螢幕截圖 / 影片連結

見文件末「需要自己截的圖」。

---

## ⑤ 是否將任何 API 資料儲存在平台外 → YES

Yes — the content of DELETED and EDITED messages only. Ordinary chat messages are not
stored at all. These records are kept on the server owner's own local machine, encrypted at
rest with Fernet (AES-128-CBC with HMAC-SHA256), automatically deleted after 14 days, never
uploaded to any cloud service or third party, and readable only by staff through a
role-restricted slash command. No member data and no other Discord API data is stored
off-platform.

---

## ⑥ Message Content Intent — 為什麼需要

WHAT WE REMOVED SINCE THE LAST REVIEW

After our previous application was declined we audited every place the bot touched message
content and removed or converted everything that had an alternative:

  - All prefix commands (!ping, !serverinfo, !chatlog and others) — converted to slash
    commands.
  - "Delete & Archive" moderation backup — converted to a message context-menu command,
    so Discord delivers the target message's content to the command itself and no intent
    is required.
  - Bahamut forum search — previously triggered by a reaction, which meant reading the
    reacted message; converted to a message context-menu command.
  - A keyword-triggered membership-application helper — removed entirely.
  - A random reaction feature that listened to every message — removed entirely.
  - The AI assistant already relies solely on the @mention exception and needs no intent.
  - Chat logging, which previously wrote every message in the server to disk, now writes
    NOTHING for ordinary messages. It records only messages that are deleted or edited
    (details below). This removed the overwhelming majority of the data we retain.

Two use cases remain. Neither has a workable alternative, and we have narrowed the scope of
both.

USE CASE 1 — ANTI-SPAM AGAINST COMPROMISED ACCOUNTS

Our community is repeatedly hit by hijacked member accounts. The pattern is always the
same: within about a minute, the compromised account posts the same payload into every
channel it can write to.

We detect it by correlating messages across channels. If the same content fingerprint from
the same author appears in 3 or more distinct channels within 60 seconds, the bot deletes
that author's messages from the last 5 minutes across all channels, times the account out
for 1 hour, and logs the action to a staff channel. Moderators are exempt.

WHY AUTOMOD CANNOT COVER THIS

We enabled AutoMod first and keep it enabled. It does not stop this attack, for four
concrete reasons:

  a. AutoMod evaluates each message in isolation. It has no way to express "the same
     author posted the same thing in N different channels within T seconds", and that
     cross-channel repetition is precisely the signal that separates a hijacked account
     from a member chatting normally. Any per-message threshold strict enough to catch the
     spammer also punishes ordinary conversation.

  b. The most damaging variant posts IMAGE-ONLY messages with NO TEXT AT ALL and
     randomised filenames. AutoMod's keyword, keyword-preset and regex rules all match on
     message text, so a message whose content is empty matches nothing. During an actual
     incident on our server, with AutoMod's spam and mention-spam presets active, none of
     the rules fired and the account posted freely across more than ten channels.

  c. Attackers rotate the wording and the image between waves, so a keyword blocklist is
     permanently one incident behind. Our check is content-agnostic: it keys on repetition
     across channels, not on what was posted, so it catches the next wave without an
     update.

  d. AutoMod can only block or flag the single message that matched. It cannot remove the
     messages already posted in the other channels and it cannot apply the timeout, so
     staff would still have to clean up manually, channel by channel, while the spam is
     still going out.

The intent is required because this correlation must run over every message as it arrives.
A spam wave is only recognisable by comparing messages the bot was never mentioned in.

WHAT WE KEEP: an in-memory fingerprint only — the message text, whether an attachment was
present, the channel ID and a timestamp — held for at most 5 minutes, never written to
disk, and discarded on restart.

USE CASE 2 — LOGGING OF DELETED AND EDITED MESSAGES FOR DISPUTE RESOLUTION

This is a private community whose staff regularly have to adjudicate harassment reports,
scam accusations and in-game trade disputes. The evidence is almost always gone by the time
a report is filed: the offender deletes the message, or edits it into something innocuous.
Discord's audit log records that a deletion occurred but never the content, and there is no
API to retrieve a deleted message or a previous revision. Without our own record, every
report becomes one member's word against another's, and we cannot act fairly toward either
party.

SCOPE, NARROWED FOR THIS APPLICATION

Our previous implementation wrote every message in the server to disk. It no longer does.
Nothing is written for an ordinary message. A message is persisted only at the moment it
becomes unrecoverable from Discord itself:

  - the message is deleted (by its author, by a moderator, or by our anti-spam feature),
  - the message is bulk-deleted,
  - the message is edited, in which case we keep the version before the edit and the
    version after it.

This is the smallest set of data that still answers "what did this person actually post
before they removed it", which is the only question the log exists to answer. A message
that is never deleted or edited stays visible in the channel and we store nothing about it.

The record contains: event type and timestamp, message ID, channel name, author username,
message content, and attachment/sticker references — for human (non-bot) messages in the
one configured community server only.

WHY THE INTENT IS STILL REQUIRED

Discord delivers the content of a deleted or edited message only for messages the library
still holds in its in-memory cache, and that cache is populated from the MESSAGE_CREATE
gateway event. Without the Message Content Intent, MESSAGE_CREATE arrives with an empty
content field, so the cache holds empty messages and the subsequent delete or edit event
carries nothing. There is no other way to know what a deleted message said.

SAFEGUARDS

  - Retention of 14 DAYS. Older records are deleted automatically; the purge runs at
    every startup as well as on the first write of each day, so it cannot silently stop.
  - ENCRYPTED AT REST with Fernet (AES-128-CBC with HMAC-SHA256). The key never leaves the
    operator's machine.
  - Stored ONLY on the server owner's local machine. Never uploaded to a cloud service,
    never shared with a third party, never used for training, analytics, profiling or
    advertising, and never sold.
  - Readable only through a slash command gated on a specific staff role.
  - Limited to a single configured guild ID. The bot does not log any other server it is
    in, and does not log direct messages.
  - Fully disclosed in our public Privacy Policy, including how a user can request
    deletion of their data.

---

## 需要自己截的圖 / Screenshots to prepare

Server Members Intent
  1. 歡迎 embed —— 一般帳號 + 未滿 14 天被標紅的帳號（各一張，遮住使用者名稱）
  2. 顯示「全部人數：xxxx」的頻道名稱

Message Content Intent
  3. 反洗版觸發後管理頻道的 log embed（顯示偵測頻道數、刪除則數、禁言）
  4. 你的 AutoMod 規則設定頁（證明「已啟用但沒擋下來」）
  5. 洗版當下的頻道截圖 —— 純圖片、無文字、隨機檔名（重點證據）
  6. /chatlog 匯出結果（遮蔽內容即可）—— 重點是讓審核員看到 Event 欄只有
     Delete / Edit_Before / Edit_After，沒有一般訊息
  7. 訊息右鍵 → 應用程式 選單，顯示「刪除並備份」「查巴哈」兩個指令
