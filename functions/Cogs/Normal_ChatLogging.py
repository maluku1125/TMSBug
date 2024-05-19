from discord.ext import commands
import time
import discord
import datetime

from functions.chatlog import chat_log_save

class Normal_ChatLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):  

        if datetime.datetime.now().strftime('%m%d') != self.bot.time_date:
            self.bot.time_date = datetime.datetime.now().strftime('%m%d')
            self.bot.speak_count = 0      

        now_HMS = datetime.datetime.now().strftime('%H:%M:%S')   
        # 略自己
        if message.author == self.bot.user:
            return   
             
        # TMS only function
        if message.guild.id == int(self.bot._config["function"]["tmsguildid"]):

            self.bot.speak_count += 1  

            if message.author.bot != True :                  
                print(f'{now_HMS} #{self.bot.speak_count}, Guild:{message.guild}, Channel：{message.channel}, User：{message.author}')
                print("Content：", message.content, message.stickers, message.attachments)
                print('-'*40)
            else:
                print(f'{now_HMS} #BOTSpeak, Guild:{message.guild}, Channel：{message.channel}, User：{message.author}')
                print("Content：", message.content, message.stickers, message.attachments)
                print('-'*40)

            #Chat Log
            #----------------------------------------
            #write
        
            if message.author.bot != True :
                chat_log_save(self.bot.speak_count, message.channel, message.author, message.content, message.attachments, message.stickers)
        
            #read
            if message.content == 'chatlog' :
                for r in message.author.roles:
                    if r.id == 477757173863153665:
                        
                        date = time.strftime('%Y%m%d', time.localtime(time.time()))

                        await message.channel.send(file = discord.File(f'C:\\Users\\User\\Desktop\\DiscordChatlog\\ChatLog\\{date}_TMS新楓之谷_Chatlog.csv'))
                        return
                    
    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_after.author.bot != True :
            chat_log_save('Edit_Before', message_before.channel, message_before.author, message_before.content, message_before.attachments, message_before.stickers)
            chat_log_save('Edit_After', message_after.channel, message_after.author, message_after.content, message_after.attachments, message_after.stickers)
            
            print(f'Edit_Before, Channel：{message_before.channel}, User：{message_before.author}')
            print("Content：", message_before.content, message_before.stickers, message_before.attachments)
            print(f'Edit_After, Channel：{message_after.channel}, User：{message_after.author}')
            print("Content：", message_after.content, message_after.stickers, message_after.attachments)
            print('-'*40) 
            
