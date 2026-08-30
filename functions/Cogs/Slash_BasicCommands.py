import discord
from discord import app_commands
from discord.ext import commands
from discord.errors import NotFound
import datetime
import io
import logging
import os
import random
import psutil
import time

from functions.chatlog import chat_log_export_csv
 
process = psutil.Process()

# 獲取 CPU 使用率
cpu_usage = f"{(process.cpu_percent() / psutil.cpu_count()):.2f}"

# 獲取當前進程的記憶體使用量（MB）
memory_usage_mb = process.memory_info().rss / 1024 / 1024
# 獲取系統的總記憶體量（MB）
total_memory_mb = psutil.virtual_memory().total / 1024 / 1024
# 計算記憶體使用率
memory_usage_percent = memory_usage_mb / total_memory_mb * 100

# 作者
owner_id = '310164490391912448'

# 版本  
version = 'v2.9.0'

# 在程式開始運行時記錄當前的時間
start_time = time.time()


def get_now_HMS():
    return datetime.datetime.now().strftime('%H:%M:%S')

def PrintSlash(type, interaction: discord.Interaction):
    print(f'{get_now_HMS()}, Guild：{interaction.guild}, User：{interaction.user} ,Slash：{type}')
    print('-'*40)


# 刪除訊息指令的使用限制（沿用原 !delmsg 的規則）
DELMSG_MAX_PER_WINDOW = 10      # 視窗內最多幾次
DELMSG_WINDOW_SEC = 1800        # 統計視窗（30 分鐘）
DELMSG_LOCK_SEC = 86400         # 超量後鎖定時間（24 小時）
MAX_LOG_ATTACH_MB = 8           # 單一附件超過此大小就只記網址不轉存
ADMIN_ROLE_ID = 477757173863153665   # serverinfo / chatlog 專用管理身分組


class Slash_BasicCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        cfg = client._config["function"]
        self.allowed_role_id = int(cfg.get("delmsgrole", 1067162303411269672))
        self.log_channel_id = int(cfg.get("logchannel", 588950084658528257))
        self.delete_message_count = 0
        self.delete_message_timestamp = time.time()
        self.delete_message_enabled = True
        self.delete_message_locktime = time.time()

        # Context menu 無法用裝飾器定義在 Cog 內，需手動建立並註冊到指令樹
        self.delmsg_menu = app_commands.ContextMenu(
            name="刪除並備份",
            callback=self.delmsg_context,
        )
        client.tree.add_command(self.delmsg_menu)

    async def cog_unload(self):
        self.client.tree.remove_command(self.delmsg_menu.name,
                                        type=self.delmsg_menu.type)

    #-----------------ping-----------------
    @app_commands.command(name="ping", description="ping")
    async def ping(self, interaction: discord.Interaction):
        bot_latency = round(self.client.latency * 1000)
        PrintSlash('ping', interaction)
        await interaction.response.send_message(f"pong, latency is {bot_latency} ms.")

    #-----------------help-----------------
    @app_commands.command(name="help",description="help")
    @app_commands.describe(dev_func = "dev_func")

    async def help(self, interaction: discord.Interaction, dev_func: str = None):

        # 如果 dev_func 為 'load'，並且命令的發送者是作者
        if dev_func == 'load_Slash_CreatePrizeEmbed' and str(interaction.user.id) == '310164490391912448':
            try:
                await self.client.add_cog('Slash_CreatePrizeEmbed')
            except Exception as e:
                print(f'Failed to load extension: {e}')
            print('Load Slash_CreatePrizeEmbed')

        # 如果 dev_func 為 'unload'，並且命令的發送者是作者
        elif dev_func == 'unload_Slash_CreatePrizeEmbed' and str(interaction.user.id) == '310164490391912448':
            try:
                await self.client.remove_cog('Slash_CreatePrizeEmbed')
            except Exception as e:
                print(f'Failed to unload extension: {e}')
            print('Unload Slash_CreatePrizeEmbed')
                

        embed = discord.Embed(
            title=f"**TMS新楓之谷BOT**", 
            description = f'', 
            color=0x32EBA7,
            )
        
        owner = await self.client.fetch_user(owner_id)

        embed.add_field(
            name="**作者**",
            value=f"諭諭({owner.name})",
        )        
        embed.add_field(
            name="版本",
            value=f"{version}",
        )    
        embed.add_field(
            name="BOT",
            value=(
                ""
                f"[__TMS Discord & Support Guild__](https://discord.gg/maplestory-tw)\n"
                f"[__邀請TMSBug__](https://reurl.cc/aLj8V9)\n"
                f"[__功能/指令列表__](https://reurl.cc/kr25Wq)\n"
                ""
            ),
            inline=False,
        )
        embed.add_field(
            name="BOT資料",
            value=(
                "```autohotkey\n"
                f"指令數量: {len(self.client.tree.get_commands())}\n"
                f"群組數量: {len(self.client.guilds):,}\n"
                f"成員人數: {sum([_.member_count or 0 for _ in self.client.guilds if not _.unavailable]):,}\n" 
                "```"
            ),
            inline=False,
        )
        # 在需要的時候計算運行時間
        runtime_seconds = time.time() - start_time
        runtime_minutes, runtime_seconds = divmod(runtime_seconds, 60)
        runtime_hours, runtime_minutes = divmod(runtime_minutes, 60)
        runtime_days, runtime_hours = divmod(runtime_hours, 24)
        if runtime_days > 0:
            runtime_str = f"{int(runtime_days)}天{int(runtime_hours)}時{int(runtime_minutes)}分{int(runtime_seconds)}秒"
        else:
            runtime_str = f"{int(runtime_hours)}小時{int(runtime_minutes)}分{int(runtime_seconds)}秒"


        embed.add_field(
            name="運行狀態",
            value=(
                "```autohotkey\n"
                f"CPU使用率: {cpu_usage}%\n"
                f"MEM使用率: {memory_usage_percent:.2f}%\n"
                f"MEM使用量: {memory_usage_mb:.2f} MB\n"
                f"BOT運行時間: {runtime_str} \n"
                "```"
            ),
            inline=False,
        )
        
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/957283103364235284.webp?size=96&quality=lossless')
        PrintSlash('help', interaction)       
        await interaction.response.send_message(embed=embed)



    #-----------------delmsg（訊息右鍵選單）-----------------
    # 使用 Message Context Menu 而非帶訊息ID的斜線指令：
    # 依 Discord 規範，「右鍵選單指令所作用的訊息」是 Message Content Intent
    # 的四個例外之一，因此即使未取得該 Intent，仍可讀到完整內容與附件。
    async def delmsg_context(self, interaction: discord.Interaction, message: discord.Message):
        if interaction.guild is None:
            await interaction.response.send_message("此指令僅能在伺服器中使用。", ephemeral=True)
            return

        # 權限：需具備指定身分組
        if not any(r.id == self.allowed_role_id for r in getattr(interaction.user, "roles", [])):
            await interaction.response.send_message("你沒有權限使用這個指令。", ephemeral=True)
            return

        # 只允許在「@everyone 可見且可發言」的公開頻道使用
        channel = message.channel
        try:
            everyone_perms = channel.permissions_for(interaction.guild.default_role)
            is_public = everyone_perms.view_channel and everyone_perms.send_messages
        except Exception:
            is_public = False
        if not is_public:
            await interaction.response.send_message(
                "此頻道不是公開頻道（@everyone 無法檢視或發言），不允許在此刪除訊息。",
                ephemeral=True)
            return

        # 使用量限制（超量後鎖定 24 小時）
        now = time.time()
        if not self.delete_message_enabled:
            remain = DELMSG_LOCK_SEC - int(now - self.delete_message_locktime)
            if remain > 0:
                await interaction.response.send_message(
                    f"此指令暫時禁用，{remain} 秒後解鎖。", ephemeral=True)
                return
            self.delete_message_enabled = True
            self.delete_message_count = 0

        if now - self.delete_message_timestamp > DELMSG_WINDOW_SEC:
            self.delete_message_count = 0
            self.delete_message_timestamp = now

        if self.delete_message_count >= DELMSG_MAX_PER_WINDOW:
            self.delete_message_enabled = False
            self.delete_message_locktime = now
            await interaction.response.send_message(
                f"{DELMSG_WINDOW_SEC // 60} 分鐘內只能使用 {DELMSG_MAX_PER_WINDOW} 次此指令。",
                ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
        except NotFound:
            logging.warning("delmsg: Interaction expired before defer")
            return

        # 附件必須在「刪除前」下載：訊息一旦刪除，CDN 連結即失效
        files, oversized = [], []
        for a in message.attachments:
            if a.size > MAX_LOG_ATTACH_MB * 1024 * 1024:
                oversized.append(f"{a.filename} ({a.size / 1024 / 1024:.1f}MB)")
                continue
            try:
                data = await a.read()
                files.append(discord.File(io.BytesIO(data), filename=a.filename,
                                          spoiler=a.is_spoiler()))
            except Exception as e:
                oversized.append(f"{a.filename}（下載失敗：{e}）")

        self.delete_message_count += 1

        log_channel = self.client.get_channel(self.log_channel_id)
        if log_channel:
            embed = discord.Embed(title="訊息刪除備份", color=discord.Color.red(),
                                  timestamp=datetime.datetime.now())
            embed.add_field(name="頻道", value=f"{message.channel.mention}", inline=True)
            embed.add_field(name="訊息ID", value=str(message.id), inline=True)
            embed.add_field(name="原發送者",
                            value=f"{message.author.mention}（{message.author}）", inline=False)
            embed.add_field(name="刪除者",
                            value=f"{interaction.user.mention}（{interaction.user}）", inline=False)
            content = message.content or "（無文字內容）"
            embed.add_field(name="訊息內容", value=content[:1024], inline=False)
            if oversized:
                embed.add_field(name="未轉存的附件", value=chr(10).join(oversized)[:1024], inline=False)
            # 第一張圖直接顯示在 embed 內，其餘以附件形式附上
            first_img = next((f for f in files
                              if f.filename.lower().endswith(
                                  ('.png', '.jpg', '.jpeg', '.gif', '.webp'))), None)
            if first_img:
                embed.set_image(url=f"attachment://{first_img.filename}")
            try:
                await log_channel.send(embed=embed, files=files)
            except Exception as e:
                logging.warning(f"delmsg: 記錄頻道發送失敗 {e}")
                try:
                    await log_channel.send(embed=embed)
                except Exception:
                    pass

        try:
            await message.delete()
        except discord.Forbidden:
            await interaction.followup.send("沒有權限刪除該訊息。", ephemeral=True)
            return
        except discord.HTTPException as e:
            await interaction.followup.send(f"刪除訊息時發生錯誤：{e}", ephemeral=True)
            return

        PrintSlash('delmsg', interaction)
        await interaction.followup.send(
            f"✅ 已刪除訊息（原發送者：{message.author}），備份已存入記錄頻道。",
            ephemeral=True)



    #-----------------hi-----------------
    @app_commands.command(name="hi", description="打聲招呼")
    async def hi(self, interaction: discord.Interaction):
        PrintSlash('hi', interaction)
        await interaction.response.send_message("Hello, world!")

    #-----------------randnumber-----------------
    @app_commands.command(name="randnumber抽籤", description="從 1~m 之中隨機抽出 n 個不重複的數字")
    @app_commands.describe(n="要抽幾個", m="從 1 到多少之間抽")
    async def randnumber(self, interaction: discord.Interaction, n: int, m: int):
        if n < 1 or m < 1:
            await interaction.response.send_message("n 和 m 必須是正整數", ephemeral=True)
            return
        if n > m:
            await interaction.response.send_message("抽的數量不能大於總數", ephemeral=True)
            return
        if m > 10000:
            await interaction.response.send_message("總數上限為 10000", ephemeral=True)
            return
        result = random.sample(range(1, m + 1), n)
        PrintSlash('randnumber', interaction)
        await interaction.response.send_message(f"隨機選出的數字: {result}")

    #-----------------serverinfo-----------------
    @app_commands.command(name="serverinfo伺服器資訊", description="顯示伺服器統計資訊（限管理身分組）")
    async def serverinfo(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("此指令僅能在伺服器中使用。", ephemeral=True)
            return
        if not any(r.id == ADMIN_ROLE_ID for r in getattr(interaction.user, "roles", [])):
            await interaction.response.send_message("你沒有權限使用這個指令。", ephemeral=True)
            return

        g = interaction.guild
        embed = discord.Embed(title=f"**{g}**",
                              description=f'Member Count: {g.member_count}',
                              color=0x32EBA7)
        embed.add_field(name="**Basic Info**",
                        value=("```"
                               f"Owner: {g.owner}\n"
                               f"Since: {g.created_at.strftime('%Y-%m-%d')}\n```"))
        embed.add_field(name="**Premium**",
                        value=("```"
                               f"Premium Tier      : {g.premium_tier}\n"
                               f"Subscription count: {g.premium_subscription_count}\n```"))
        embed.add_field(name="**Channels**",
                        value=("```"
                               f"Total Channels Count: {len(g.channels)}\n"
                               f"Text Channels Count : {len(g.text_channels)}\n"
                               f"Voice Channels Count: {len(g.voice_channels)}\n"
                               f"Threads Count       : {len(g.threads)}\n```"),
                        inline=False)
        embed.add_field(name="**Emojis & Stickers**",
                        value=("```"
                               f"Emojis Count  : {len(g.emojis)}\n"
                               f"Stickers Count: {len(g.stickers)}\n```"),
                        inline=False)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        PrintSlash('serverinfo', interaction)
        await interaction.response.send_message(embed=embed)

    #-----------------chatlog-----------------
    @app_commands.command(name="chatlog聊天記錄", description="匯出今日聊天記錄 CSV（限管理身分組）")
    async def chatlog(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("此指令僅能在伺服器中使用。", ephemeral=True)
            return
        if not any(r.id == ADMIN_ROLE_ID for r in getattr(interaction.user, "roles", [])):
            await interaction.response.send_message("你沒有權限使用這個指令。", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
        except NotFound:
            logging.warning("chatlog: Interaction expired before defer")
            return

        try:
            csv_path = chat_log_export_csv()
        except FileNotFoundError:
            await interaction.followup.send('今日尚無聊天記錄。', ephemeral=True)
            return
        except Exception as e:
            await interaction.followup.send(f'匯出失敗：{e}', ephemeral=True)
            return

        try:
            await interaction.followup.send(file=discord.File(csv_path), ephemeral=True)
        finally:
            try:
                os.remove(csv_path)
            except OSError:
                pass
        PrintSlash('chatlog', interaction)
