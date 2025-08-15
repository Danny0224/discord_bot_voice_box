"""

    Discord 機器人
    語音房 主程式 (二代)
    製作人 : Danny0224
    2024 / 10 / 18

"""

# 程式庫匯入
import class_box
import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import random
import json
import os

path = os.path.dirname(os.path.abspath(__file__))   # 取得目前檔案的路徑
token_path = os.path.join(path, "token.json")       # 機器人token資料的位置
config = os.path.join(path, "config.json")          # 設定檔位置

# 檢查token檔案是否存在
if not os.path.exists(token_path):
    with open(token_path, 'w', encoding='utf-8') as file:
        token_data = {
            "token": "Yor_bot_token"
        }
        json.dump(token_data, file, indent=4)

# 檢查設定檔是否存在
if not os.path.exists(config):
    with open(config, 'w', encoding='utf-8') as file:
        config_data = {
            "box_id": 123456789012345678,
            "categorychannel_id": 123456789012345678
        }
        json.dump(config_data, file, indent=4)

# 讀取機器人的token
with open(token_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
token = data.get("token")

# 讀取設定檔位置
with open(config, 'r', encoding='utf-8') as file:
    data = json.load(file)
box_id = data.get("box_id")
category_channel_id = data.get("categorychannel_id")


# 權限設定
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix = "!", intents = intents)


# 程式啟動時執行的程式
@bot.event
async def on_ready(): 
    await bot.tree.sync() # 重新載入指令
    print(f"目前機器人 >>> {bot.user} <<<<")
    
    for i in class_box.all_box(): # 檢查包廂式是否是空的
        channel = bot.get_channel(i)
        voice_channel = class_box.box_id(i)
        if channel.members == []: # 如果是空的就刪除
            if i in class_box.register_owner_leave_list():
                voice_channel.edit_quit_owner_time(True)
            voice_channel = class_box.box_id(i)
            await channel.delete()
            voice_channel.delete()
            
    for i in class_box.register_owner_leave_list(): # 如果檢查到房主回來的話
        voice_channel = class_box.box_id(i)
        channel_bot = bot.get_channel(i)
        if voice_channel.owner in [i.id for i in channel_bot.members]:
            voice_channel.edit_quit_owner_time(True)
    
    replace_owner.start()

# 檢測成員進出語音頻道
@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

    if after.channel != None:
        voice_channel = class_box.box_id(after.channel.id)
        if after.channel.id == box_id: # 檢查成員是否進入創建語音

            for channel_id in class_box.register_owner_leave_list(): # 檢查加入的成員是否為某個語音房的擁有者
                voice_channel = class_box.box_id(channel_id)
                if member.id == voice_channel.owner:
                    channel = bot.get_channel(channel_id)
                    await member.move_to(channel)
                    return
            
            # 創建語音房
            category_channel = bot.get_channel(categorychannel_id) 
            voice_channel = await category_channel.create_voice_channel(f"║🔊║{member.display_name}的語音")
            await member.move_to(voice_channel)

            class_box.app_box(member.id, voice_channel.id)

            embed = discord.Embed(title="你剛剛創建了語音房🎉",
                      colour=0xfff94d)

            embed.add_field(name="📝在這使用指令，可以調整語音房的一切",
                            value="",
                            inline=False)

            await voice_channel.send(embed=embed)
            return # 回傳
        
        elif voice_channel.exist and member.id == voice_channel.owner: # 當房主回到自己的語音房時
            if voice_channel.quit_owner_time != None:
                voice_channel.edit_quit_owner_time(True)
    

    if before.channel != None: # 當有人離開語音時

        voice_channel = class_box.box_id(before.channel.id)
        if voice_channel.exist:
            if before.channel.members == []: # 判斷是否為語音房，如果是空的就刪除
                if before.channel.id in class_box.register_owner_leave_list():
                    voice_channel.edit_quit_owner_time(True)
                await before.channel.delete()
                voice_channel.delete()
                return # 回傳
        
            elif member.id == voice_channel.owner: # 如果房主離開語音房
                if class_box.register_owner_leave_list() == []:
                    replace_owner.start()
                voice_channel.edit_quit_owner_time(False)
                return # 回傳
            
@tasks.loop(seconds=1)
async def replace_owner():
    if class_box.register_owner_leave_list() == []:
        replace_owner.cancel()

    for channel in class_box.register_owner_leave_list(): 
        voice_channel = class_box.box_id(channel)
        time = datetime.datetime.strptime(voice_channel.quit_owner_time, "%Y-%m-%d %H:%M:%S") 
        if time + datetime.timedelta(minutes=5) <= datetime.datetime.now(): # 當房主離開自己的語音房超過5分鐘時
            if voice_channel.permissions != []: # 優先給有權限的人
                voice_channel.edit_owner(voice_channel.permissions[0])
                voice_channel.delete_permissions(voice_channel.permissions[0])
                voice_channel.edit_quit_owner_time(True)
                channel_bot = bot.get_channel(voice_channel.channel_id)
                member = bot.get_user(voice_channel.owner)
            else: # 如果沒有權限的人就隨機給予一個人
                channel_bot = bot.get_channel(voice_channel.channel_id)
                voice_channel.edit_owner(channel_bot.members[random.randint(0, len(channel_bot.members)-1)].id)
                voice_channel.edit_quit_owner_time(True)
                member = bot.get_user(voice_channel.owner)

            embed = discord.Embed(title=f"房主權限已轉移給 {member.display_name}",
                      description=">>> [系統檢測] 房主離開語音房超過五分鐘",
                      colour=0xfff94d)
            await channel_bot.send(embed=embed)


@bot.tree.command(name="語音名稱", description="更改你的語音房名稱")
@app_commands.describe(名稱 = "語音頻道名稱")
async def edit_channel_name(interaction: discord.Interaction, 名稱: str):
    voice_channel = class_box.box_id(interaction.channel.id)
    
    # 檢查是否在語音房輸入指令
    if voice_channel.exist != True: 
        embed = discord.Embed(title="請在〔語音房文字頻道〕輸入〔指令〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查使用指令的人是否有權限
    elif voice_channel.have_permission(interaction.user.id) != True: 
        embed = discord.Embed(title="你沒有這〔語音房〕的〔操作權〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return

    await interaction.channel.edit(name=名稱)

    embed = discord.Embed(title="已變更語音房名稱🎉",
                      colour=0x17c101)

    embed.add_field(name=f"變更名稱: {名稱}",
                    value="",
                    inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="踢出成員", description="將一位成員踢出語音房")
@app_commands.describe(成員 = "指定一位成員")
async def edit_channel_name(interaction: discord.Interaction, 成員: discord.Member):
    voice_channel = class_box.box_id(interaction.channel.id)
    channel_bot = bot.get_channel(interaction.channel.id)

    # 檢查是否是在語音房輸入指令
    if voice_channel.exist != True: 
        embed = discord.Embed(title="請在〔語音房文字頻道〕輸入〔指令〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查使用者是否有權限
    elif voice_channel.have_permission(interaction.user.id) != True: 
        embed = discord.Embed(title="你沒有這〔語音房〕的〔操作權〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查要被踢出的人是否在語音房
    elif 成員 not in channel_bot.members:
        embed = discord.Embed(title="你無法踢出不在〔語音房〕的人!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return

    # 檢查要被踢出的人是否有權限 (只有房主才可以踢出權限列表裡的人)
    elif voice_channel.have_permission(成員.id) == True and voice_channel.owner != interaction.user.id:
        embed = discord.Embed(title="你不能踢出有〔操作權〕的人，除非你是〔房主〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    await 成員.move_to(None)

    embed = discord.Embed(title=f"已踢出成員✅",
                        colour=0x17c101)
    embed.add_field(name=f"踢出成員: {成員.display_name}",
                    value="",
                    inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="給予權限", description="給予成員語音房操作權")
@app_commands.describe(成員 = "指定一位成員")
async def edit_channel_name(interaction: discord.Interaction, 成員: discord.Member):
    voice_channel = class_box.box_id(interaction.channel.id)

    # 檢查是否在語音房輸入指令
    if voice_channel.exist != True: 
        embed = discord.Embed(title="請在〔語音房文字頻道〕輸入〔指令〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查使用者是否有權限
    elif voice_channel.is_owner(interaction.user.id) != True: 
        embed = discord.Embed(title="有只有這〔語音房〕的〔擁有者〕才可以這樣做!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查要給予權限的人是否在語音房
    elif 成員 not in interaction.channel.members:
        embed = discord.Embed(title="你無法給予不在〔語音房〕的人權限!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查要給予權限的人是否已經有權限
    elif voice_channel.have_permission(成員.id) == True:
        embed = discord.Embed(title="這個成員已經有〔語音房操作權〕了!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    voice_channel.add_permissions(成員.id)

    embed = discord.Embed(title=f"成功給予語音房操作權🎉",
                      colour=0x17c101)
    embed.add_field(name=f"給予成員: {成員.display_name}",
                    value="",
                    inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="移除權限", description="移除成員語音房操作權")
@app_commands.describe(成員 = "指定一位成員")
async def edit_channel_name(interaction: discord.Interaction, 成員: discord.Member):
    voice_channel = class_box.box_id(interaction.channel.id)

    # 檢查是否在語音房輸入指令
    if voice_channel.exist != True: 
        embed = discord.Embed(title="請在〔語音房文字頻道〕輸入〔指令〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 檢查使用者是否有權限
    elif voice_channel.have_permission(interaction.user.id) != True: 
        embed = discord.Embed(title="你沒有這〔語音房〕的〔操作權〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    # 只有自己的權限可以移除，除非是房主
    elif voice_channel.have_permission(成員.id) == True and voice_channel.owner != interaction.user.id:
        embed = discord.Embed(title="你不能移除有〔操作權〕的人，除非你是〔房主〕!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return

    # 檢查要移除權限的人是否沒有權限
    elif voice_channel.have_permission(成員.id) == False:
        embed = discord.Embed(title="這個成員沒有〔語音房操作權〕了!",
                      colour=0xc10101)
        await interaction.response.send_message(embed=embed ,ephemeral=True)
        return
    
    voice_channel.delete_permissions(成員.id)

    embed = discord.Embed(title=f"成功移除語音房操作權🎉",
                      colour=0x17c101)
    embed.add_field(name=f"移除成員: {成員.display_name}",
                    value="",
                    inline=False)
    
    await interaction.response.send_message(embed=embed)
        
# 程式末尾 載入機器人token
bot.run(token)