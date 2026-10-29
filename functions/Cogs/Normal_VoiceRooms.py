import asyncio
import collections
import datetime
import re

import discord
from discord import app_commands
from discord.ext import commands, tasks

# 房名的識別前綴。分類底下只有帶這個前綴的語音頻道會被當成語音房 ——
# 萬一有人把別的頻道放進同一個分類，不會被這支 cog 收掉。
ROOM_MARK = '🔒｜'
IDLE_NAME = f'{ROOM_MARK}空房'
NAME_MAX = 100               # Discord 的頻道名上限

# ⚠️ Discord 對「改頻道名稱／主題」有一條 **2 次 / 10 分鐘（每個頻道）** 的限制，
# 而且這條沒寫進官方文件、被擋住時也不會回報錯誤 —— 請求會直接卡在那裡，
# 連同一起送出的權限變更一起卡住（見 discord-api-docs #1900 / #2190）。
# 所以這支 cog 自己記帳：改名之前先確認額度，沒額度就「不改名、照樣開房」，
# 絕不讓使用者的指令卡在速率限制上。
RENAME_WINDOW_SEC = 600
RENAME_LIMIT = 2

CLAIM_GRACE_SECONDS = 300    # 要了房卻沒人進來：5 分鐘後收回（避免占著不用）
IDLE_GRACE_SECONDS = 60      # 用過之後空了：撐這麼久才收（防斷線重連那一瞬間）
SWEEP_SECONDS = 20           # 掃描週期
DEFAULT_POOL = 5             # 常駐幾間空房
DEFAULT_MAX_ROOMS = 20       # 連同常駐的同時上限
DEFAULT_TTL_HOURS = 24       # 不管裡面有沒有人，開滿這麼久就收
MAX_GUESTS_PER_CALL = 25     # 一次指令最多認幾個人（多打的會被告知，不會默默吃掉）
MAX_ACCESS = 50              # 一間房累積最多開給幾個人

# 字串選項送回來的 mention 長這樣：<@123…>（舊版客戶端可能帶驚嘆號）。
MENTION_RE = re.compile(r'<@!?(\d+)>')
ROLE_MENTION_RE = re.compile(r'<@&(\d+)>')
RAW_ID_RE = re.compile(r'(?<!\d)(\d{17,20})(?!\d)')


def _cfg_int(bot, key, default=None):
    """從 [function] 讀一個整數設定。沒填或填壞就回預設值。"""
    try:
        raw = (bot._config['function'].get(key) or '').strip()
    except Exception:                                       # noqa: BLE001
        return default
    return int(raw) if raw.isdigit() else default


def _room_name(member, custom='') -> str:
    """房名：自己取的名字優先，沒取就用 `🔒｜某某 的房間`。

    前綴一定要留著 —— 那是「這間是臨時語音房」的唯一識別依據（名字會變，
    所以不能靠名字裡的編號；權限覆寫才是房主的依據）。
    """
    custom = re.sub(r'\s+', ' ', (custom or '')).strip()
    if custom.startswith(ROOM_MARK):
        custom = custom[len(ROOM_MARK):].strip()        # 使用者自己打了前綴就不要疊兩層
    if custom:
        return f'{ROOM_MARK}{custom}'[:NAME_MAX]
    tail = ' 的房間'
    who = (member.display_name or member.name)
    budget = NAME_MAX - len(ROOM_MARK) - len(tail)
    return f'{ROOM_MARK}{who[:budget]}{tail}'


def _is_user(target) -> bool:
    """這個權限覆寫的對象是「人」還是身分組。

    ⚠️ 不能只用 `isinstance(target, discord.Member)`：成員不在快取裡時，
    discord.py 會給一個 `Object(type=User)` 代替（2.0 起的行為，見
    `GuildChannel.overwrites`）。漏判的話，正在用的房會被看成閒置而被清掉。
    """
    if isinstance(target, (discord.Member, discord.User)):
        return True
    return isinstance(target, discord.Object) and getattr(target, 'type', None) in (
        discord.User, discord.Member)


def _members_with_access(room):
    """被開過權限的人（不含 @everyone 與 Bot 自己）。"""
    return [t for t, ow in room.overwrites.items()
            if _is_user(t) and t.id != room.guild.me.id and ow.connect is True]


def _owner_id(room) -> int:
    """房主 = 權限覆寫裡被給了「管理頻道」的那個成員。

    刻意不另外存一份房主名單：看門狗一天會重啟這支 Bot 好幾次
    （9/29 早上連著重啟三次），記憶體裡的名單一定會跟現實對不上。
    權限覆寫是 Discord 自己存的，重開之後讀回來還是對的。
    房名也一樣不能當依據 —— 改名有額度限制，收房時不一定改得回來。
    """
    for target, ow in room.overwrites.items():
        if _is_user(target) and ow.manage_channels:
            return target.id
    return 0


def _is_claimed(room) -> bool:
    """有人被開過權限 = 這間正在用。沒有 = 閒置。"""
    return bool(_members_with_access(room))


class Normal_VoiceRooms(commands.Cog):
    """隱藏語音房：常駐 5 間誰都看不到的空房，用 `/voiceroom invite` 要一間。

    ## 為什麼是「要權限」而不是「發連結」

    Discord 的邀請連結只把人帶進伺服器，**不會給任何頻道權限**。
    對一個隱藏頻道來說，連結更是完全沒有意義 —— 看不到的東西點了也進不去。
    唯一的辦法是在那個頻道上替每個人加一條權限覆寫，這支指令做的就是這件事：
    被點到的人，頻道會直接出現在他的頻道列表裡。

    權限開好之後再私訊每個人一條跳轉網址。那**不是**邀請連結 —— 進得去
    靠的還是上面那條覆寫，網址只是省下「自己去頻道列表裡翻」那一步，
    沒權限的人點了一樣進不去。指令的回覆只有房主看得到，所以頻道裡
    不會留下一排「誰邀了誰」的紀錄。

    ## 為什麼先放 5 間在那裡

    每次都現開現刪，頻道建立／刪除會洗滿稽核日誌，而且開房要等 API 來回。
    常駐 5 間閒置房（對 `@everyone` 關掉檢視權，所以平常沒人看得到），
    要用的時候只改權限 + 改名，一個 API 請求就好。
    5 間都占滿才臨時開新的，用完直接刪掉，池子回到 5 間。

    ## 狀態存在哪

    閒置還是使用中、房主是誰，全部從權限覆寫讀回來（Discord 自己存的，
    重啟也不會跑掉）。只有「開多久了」與「改名額度」活在記憶體裡，
    重啟後重新起算。
    """

    room = app_commands.Group(name='voiceroom', description='隱藏語音房',
                              guild_only=True)

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = _cfg_int(bot, 'tmsguildid')
        self.category_id = _cfg_int(bot, 'voiceroom_category')
        self.pool_size = _cfg_int(bot, 'voiceroom_pool', DEFAULT_POOL)
        self.max_rooms = _cfg_int(bot, 'voiceroom_max', DEFAULT_MAX_ROOMS)
        self.ttl_hours = _cfg_int(bot, 'voiceroom_ttl_hours', DEFAULT_TTL_HOURS)
        # room_id -> 開始使用的時間 / 變成空房的時間（重啟後重新起算）
        self.claimed_at = {}
        self.empty_since = {}
        # room_id -> 最近幾次改名的時間，用來擋 2 次/10 分鐘那條限制
        self.renames = collections.defaultdict(collections.deque)

        if self.category_id:
            self.sweep.start()
        else:
            print('VoiceRooms：未設定 [function] voiceroom_category，隱藏語音房停用')

    def cog_unload(self):
        self.sweep.cancel()

    # ── 查詢 ──────────────────────────────────────────────

    def _category(self, guild):
        return guild.get_channel(self.category_id) if self.category_id else None

    def _rooms(self, guild):
        """這個分類底下所有的語音房。"""
        category = self._category(guild)
        if category is None:
            return []
        return [c for c in category.voice_channels if c.name.startswith(ROOM_MARK)]

    def _base_overwrites(self, guild):
        """閒置狀態的權限：對所有人隱藏，只有 Bot 看得到。"""
        return {
            guild.default_role: discord.PermissionOverwrite(view_channel=False,
                                                            connect=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, connect=True,
                                                  manage_channels=True,
                                                  move_members=True),
        }

    def _clean_overwrites(self, room):
        """清成閒置狀態，但**保留身分組那一層**。

        管理員可能在這些頻道上另外掛了身分組覆寫（實測 2~5 號房就各有一條），
        收房時若用一份乾淨的基礎權限整個蓋過去，那些設定會被一起洗掉。
        所以只清「人」的覆寫，身分組原樣留著，再把 @everyone 的隱藏
        與 Bot 自己的權限壓回去。
        """
        out = {t: ow for t, ow in room.overwrites.items() if not _is_user(t)}
        out.update(self._base_overwrites(room.guild))
        return out

    # ── 改名額度 ──────────────────────────────────────────

    def _rename_budget(self, room_id) -> int:
        """這個頻道在 10 分鐘窗內還剩幾次改名額度。"""
        now = discord.utils.utcnow()
        hist = self.renames[room_id]
        while hist and (now - hist[0]).total_seconds() > RENAME_WINDOW_SEC:
            hist.popleft()
        return RENAME_LIMIT - len(hist)

    def _note_rename(self, room_id):
        self.renames[room_id].append(discord.utils.utcnow())

    # ── 指令 ──────────────────────────────────────────────

    @room.command(name='invite', description='開一間隱藏語音房，並讓你 tag 的人看得到、進得去')
    @app_commands.describe(
        邀請對象='在這一格 tag 要邀請的人，幾個都可以（@甲 @乙 @丙 …）',
        房間名稱='選填：自己取房名，留空就是「<你的名字> 的房間」')
    async def room_invite(self, interaction: discord.Interaction,
                          邀請對象: str = '', 房間名稱: str = ''):
        if not self.category_id or self._category(interaction.guild) is None:
            await interaction.response.send_message(
                '隱藏語音房還沒設定好（缺 voiceroom_category），請找管理員。',
                ephemeral=True)
            return

        # ephemeral：開房是房主自己的事，頻道裡不需要留一則公告
        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        me = interaction.user
        wanted = _room_name(me, 房間名稱)

        rooms = self._rooms(guild)
        room = next((r for r in rooms if _owner_id(r) == me.id), None)
        reused = room is not None
        renamed = stale_name = False

        if room is None:
            # 閒置房裡挑改名額度最多的那一間 —— 額度是「每個頻道」各自算的，
            # 這樣輪著用，短時間內連續開關房也不會把同一間的額度用光。
            idle = [r for r in rooms if not _is_claimed(r)]
            idle.sort(key=lambda r: (-self._rename_budget(r.id), r.position))
            room = idle[0] if idle else None

            # 沒有閒置房、或閒置房都改不了名字 → 乾脆開一間新的：
            # 建立時直接取名不受改名限制，一個請求就到位。
            if (room is None or self._rename_budget(room.id) < 1) \
                    and len(rooms) < self.max_rooms:
                fresh = await self._create_room(guild, wanted)
                if fresh is not None:
                    room = fresh
                    renamed = True
            if room is None:
                await interaction.followup.send(
                    f'目前 {self.max_rooms} 間都在使用中，等有人用完再試一次。',
                    ephemeral=True)
                return

        guests, unknown, roles, overflow = await self._parse_guests(guild, 邀請對象, me)

        already = len(_members_with_access(room)) if reused else 0
        if already + len(guests) > MAX_ACCESS:
            guests = guests[:max(0, MAX_ACCESS - already)]
            overflow = True

        overwrites = dict(room.overwrites) if reused else self._clean_overwrites(room)
        overwrites.update(self._base_overwrites(guild))
        # ⚠️ 語音權限一定要在這裡明確給，不能靠伺服器的預設值。
        # 2026-10-29 實測這台的 @everyone 只剩 send_messages —— speak、
        # use_voice_activation、stream、connect 全被收掉了，所以只給
        # view_channel + connect 的話，人進得來卻開不了麥（房主是管理員，
        # Administrator 繞過所有覆寫，所以只有他講得出話，看起來像只有房主能說話）。
        # use_voice_activation 也必須給：沒有它等於被強迫按鍵發言，
        # 沒設過發言鍵的人就是全程靜音。
        voice = dict(view_channel=True, connect=True, speak=True,
                     use_voice_activation=True, stream=True)
        overwrites[me] = discord.PermissionOverwrite(manage_channels=True, **voice)
        for u in guests:
            overwrites[u] = discord.PermissionOverwrite(**voice)

        kwargs = {'overwrites': overwrites}
        if not renamed and room.name != wanted:
            if self._rename_budget(room.id) >= 1:
                kwargs['name'] = wanted          # 跟權限同一個請求送出，不多一次往返
                renamed = True
            else:
                stale_name = True                # 額度用完了：照開，只是名字沒換
        try:
            await room.edit(reason=f'{me} 使用 /voiceroom invite', **kwargs)
        except discord.Forbidden:
            await interaction.followup.send(
                '我沒有權限改這個頻道，請確認 Bot 有「管理頻道」。',
                ephemeral=True)
            return
        if renamed and 'name' in kwargs:
            self._note_rename(room.id)

        self.claimed_at.setdefault(room.id, discord.utils.utcnow())
        self.empty_since.pop(room.id, None)

        who = '、'.join(u.mention for u in guests) or '（只有你自己）'
        # 權限送出去之後才私訊，不然對方點進來的那一刻可能還沒開通
        dm_failed = await self._dm_guests(guests, room, me)

        notes = []
        if unknown:
            notes.append(f'{len(unknown)} 個找不到的人（不在這個伺服器）')
        if roles:
            notes.append('身分組會被忽略，請直接 tag 人')
        if overflow:
            notes.append(f'超過上限的沒加進去（一次最多 {MAX_GUESTS_PER_CALL} 人、'
                         f'一間房累計 {MAX_ACCESS} 人）')
        if stale_name:
            notes.append('這間房剛改過名字，Discord 限制 10 分鐘內只能改 2 次，'
                         '所以名稱暫時沿用舊的（功能不受影響）')
        if dm_failed:
            notes.append('這些人關著私訊、沒收到連結，請直接把上面那條網址給他們：'
                         + '、'.join(u.mention for u in dm_failed))
        tail = ('\n-# ⚠️ ' + '；'.join(notes)) if notes else ''
        await interaction.followup.send(
            f'🔊 {room.mention} {"已加人" if reused else "開好了"}　房主：{me.mention}\n'
            f'已開通（{len(guests)} 人）：{who}\n'
            f'-# 連結：{room.jump_url}' + tail,
            ephemeral=True)

    async def _parse_guests(self, guild, text, host):
        """把一格字串裡 tag 到的人全部挑出來。

        slash 指令的字串選項在輸入時一樣有 @ 自動完成（使用者打 @ 就會跳出成員清單），
        送回伺服器的是 `<@123…>` 這種原始 mention —— 所以「同一格 tag 很多人」
        只要自己剖析就成立，不必為了人數開 N 個欄位（Discord 的選項是固定數量的，
        開 5 格就只能邀 5 個）。直接貼數字 ID 也接受。

        回傳 (成員清單, 找不到的 ID, 有沒有 tag 到身分組, 是否超過一次上限)。
        """
        text = text or ''
        ids, seen = [], set()
        for m in MENTION_RE.finditer(text):
            uid = int(m.group(1))
            if uid not in seen:
                seen.add(uid)
                ids.append(uid)
        roles = bool(ROLE_MENTION_RE.search(text))
        # 把所有 <...> token 拿掉之後再找裸 ID，免得把 mention 裡的數字算第二次
        for m in RAW_ID_RE.finditer(re.sub(r'<[^>]*>', ' ', text)):
            uid = int(m.group(1))
            if uid not in seen:
                seen.add(uid)
                ids.append(uid)

        overflow = len(ids) > MAX_GUESTS_PER_CALL
        members, unknown = [], []
        for uid in ids[:MAX_GUESTS_PER_CALL]:
            if uid == host.id:
                continue                        # 房主本來就有權限
            member = guild.get_member(uid)
            if member is None:
                try:
                    member = await guild.fetch_member(uid)
                except discord.HTTPException:
                    unknown.append(uid)
                    continue
            if member.bot:
                continue
            members.append(member)
        return members, unknown, roles, overflow

    async def _dm_guests(self, guests, room, host):
        """把語音房的連結私訊給被邀請的人。回傳私訊不進去的那幾個。

        私訊裡不能用 `<#頻道>` 這種 mention —— 私訊不屬於任何伺服器，
        客戶端解不出那個頻道，顯示出來是一條點不開的死連結。`jump_url`
        是完整網址（`/channels/<伺服器>/<頻道>`），從哪裡點都會跳過去。

        關私訊、或把 Bot 封鎖的人會丟 Forbidden。那是常態、不是故障：
        權限照開（他自己在頻道列表裡看得到），只是回報給房主，
        讓他自己把網址貼給那幾個人。

        併發壓在 5：每個人都得先開一條私訊頻道再送一則訊息，25 個人同時
        衝很容易撞上速率限制，而指令已經 defer 過了，慢一兩秒沒差。
        """
        if not guests:
            return []
        # 房名與暱稱都是使用者自己取的，直接內插會讓 *_ 之類的符號吃掉排版
        esc = discord.utils.escape_markdown
        text = (f'🔊 **{esc(host.display_name)}** 在 {esc(room.guild.name)} '
                f'開了語音房 **{esc(room.name)}**，已經幫你開好權限了：\n'
                f'{room.jump_url}')
        sem = asyncio.Semaphore(5)

        async def one(user):
            async with sem:
                try:
                    await user.send(text)
                except discord.HTTPException:
                    return user
            return None

        sent = await asyncio.gather(*(one(u) for u in guests))
        return [u for u in sent if u is not None]

    @room.command(name='close', description='把自己開的語音房收回去')
    async def room_close(self, interaction: discord.Interaction):
        rooms = self._rooms(interaction.guild)
        room = next((r for r in rooms if _owner_id(r) == interaction.user.id), None)
        if room is None:
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message('你現在沒有開著的語音房。',
                                                        ephemeral=True)
                return
            # 管理員在語音房裡下指令 = 收掉那一間
            voice = interaction.user.voice
            room = voice.channel if voice and voice.channel in rooms else None
            if room is None:
                await interaction.response.send_message(
                    '你沒有開著的房；要用管理員身分收別人的房，請先進去那一間再下指令。',
                    ephemeral=True)
                return
        # ephemeral：跟 invite 一致，收房也是房主自己的事，頻道裡不留公告
        await interaction.response.defer(thinking=True, ephemeral=True)
        name = room.name
        await self._release(room, '房主關閉')
        await interaction.followup.send(f'🔒 {name} 已收回。', ephemeral=True)

    @room.command(name='status', description='看看目前幾間在用、幾間閒置')
    async def room_status(self, interaction: discord.Interaction):
        rooms = self._rooms(interaction.guild)
        if not rooms:
            await interaction.response.send_message('目前一間語音房都沒有。',
                                                    ephemeral=True)
            return
        lines = []
        for r in rooms:
            if not _is_claimed(r):
                lines.append(f'　{r.name}：閒置')
                continue
            owner = r.guild.get_member(_owner_id(r))
            lines.append(f'　{r.name}：{owner.display_name if owner else "？"} '
                         f'（可進入 {len(_members_with_access(r))} 人，'
                         f'現在裡面 {len(r.members)} 人）')
        await interaction.response.send_message(
            f'常駐 {self.pool_size} 間／上限 {self.max_rooms} 間\n' + '\n'.join(lines),
            ephemeral=True)

    # ── 建立與回收 ────────────────────────────────────────

    async def _create_room(self, guild, name=IDLE_NAME):
        """開一間新的。建立時取的名字不受改名限制，所以臨時開房直接用房主的名字。"""
        try:
            return await guild.create_voice_channel(
                name[:NAME_MAX], category=self._category(guild),
                overwrites=self._base_overwrites(guild),
                reason='隱藏語音房')
        except discord.HTTPException as e:
            print(f'VoiceRooms：開房失敗 {type(e).__name__}: {e}')
            return None

    async def _release(self, room, why):
        """收回一間房：把人請出去、清掉所有成員權限，回到隱藏的閒置狀態。

        超出常駐數的直接刪掉，池子回到原本大小。
        名字能改回「空房」就改，改名額度用完就留著舊名字 —— 反正下次有人要的時候
        會再改一次，而且閒置房本來就沒人看得到。
        """
        guild = room.guild
        for m in list(room.members):
            try:
                await m.move_to(None, reason=f'語音房回收（{why}）')
            except discord.HTTPException:
                pass
        try:
            if len(self._rooms(guild)) > self.pool_size:
                await room.delete(reason=f'語音房回收（{why}）')
            else:
                kwargs = {'overwrites': self._clean_overwrites(room)}
                # 留一格額度給「下次有人開房要改名」，所以這裡要求額度全滿才改回去
                if room.name != IDLE_NAME and self._rename_budget(room.id) >= RENAME_LIMIT:
                    kwargs['name'] = IDLE_NAME
                    self._note_rename(room.id)
                await room.edit(reason=f'語音房回收（{why}）', **kwargs)
        except discord.NotFound:
            pass
        except discord.HTTPException as e:
            print(f'VoiceRooms：回收 {room.name} 失敗 {type(e).__name__}: {e}')
            return
        self.claimed_at.pop(room.id, None)
        self.empty_since.pop(room.id, None)
        print(f'VoiceRooms：回收 {room.name}（{why}）')

    # ── 事件與掃描 ────────────────────────────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """只負責記時間，刪不刪交給掃描迴圈。

        離開的那一刻不能直接收：最後一個人斷線重連、或被拉去別的頻道的
        那一瞬間房間也是空的，立刻收會把人關在門外。
        """
        if member.bot or not self.category_id:
            return
        for channel, joining in ((after.channel, True), (before.channel, False)):
            if channel is None or not channel.name.startswith(ROOM_MARK):
                continue
            if channel.category_id != self.category_id:
                continue
            if joining:
                self.empty_since.pop(channel.id, None)
            elif not channel.members:
                self.empty_since.setdefault(channel.id, discord.utils.utcnow())

    @tasks.loop(seconds=SWEEP_SECONDS)
    async def sweep(self):
        """補滿常駐空房，並回收該收的。重啟後的善後也在這裡做。"""
        for guild in self.bot.guilds:
            if self.guild_id and guild.id != self.guild_id:
                continue
            if self._category(guild) is None:
                continue
            rooms = self._rooms(guild)

            # 常駐池子缺幾間就補幾間
            while len(rooms) < self.pool_size:
                created = await self._create_room(guild)
                if created is None:
                    break
                rooms.append(created)
                print(f'VoiceRooms：補上 {created.name}')

            now = discord.utils.utcnow()
            for room in rooms:
                if not _is_claimed(room):
                    continue
                started = self.claimed_at.setdefault(room.id, now)
                if now - started >= datetime.timedelta(hours=self.ttl_hours):
                    await self._release(room, f'開滿 {self.ttl_hours} 小時')
                    continue
                if room.members:
                    self.empty_since.pop(room.id, None)
                    continue
                since = self.empty_since.get(room.id)
                if since is None:
                    # 要了房還沒人進來過：給 CLAIM_GRACE_SECONDS 的準備時間
                    if (now - started).total_seconds() >= CLAIM_GRACE_SECONDS:
                        await self._release(room, '要了房沒人進來')
                elif (now - since).total_seconds() >= IDLE_GRACE_SECONDS:
                    await self._release(room, '沒人')

    @sweep.before_loop
    async def _before_sweep(self):
        await self.bot.wait_until_ready()

    @sweep.error
    async def _sweep_error(self, e):
        """迴圈丟例外等於永久停擺，至少要印出來，而且要自己接回去。"""
        print(f'VoiceRooms：掃描迴圈出錯 {type(e).__name__}: {e}')
        self.sweep.restart()
