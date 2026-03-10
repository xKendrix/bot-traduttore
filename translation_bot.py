"""
🌍 Discord Translation Bot — powered by Google Gemini AI
=========================================================
SETUP:
  1. pip install discord.py google-generativeai
  2. Ottieni la tua API key GRATUITA su https://aistudio.google.com/app/apikey
  3. Imposta le variabili d'ambiente oppure incolla i valori direttamente qui sotto
  4. Invita il bot nel server con i permessi: Send Messages, Read Message History, Add Reactions

VARIABILI D'AMBIENTE (opzionale):
  DISCORD_TOKEN    → Token del tuo bot Discord
  GEMINI_API_KEY   → La tua API key di Google Gemini

COMANDI:
  !traduci <lingua> <testo>   → Traduce il testo nella lingua scelta
  !traduzione [lingua]        → Rispondi a un messaggio per tradurlo (default: italiano)
  !lingue                     → Mostra le lingue supportate

REAZIONI:
  Reagisci con una flag (es. 🇮🇹 🇬🇧 🇫🇷 🇩🇪 🇪🇸 🇯🇵) per tradurre automaticamente quel messaggio!
"""

import os
import discord
from discord.ext import commands
import google.generativeai as genai

# ─── Configurazione ──────────────────────────────────────────────────────────

DISCORD_TOKEN  = os.getenv("DISCORD_TOKEN",  "IL_TUO_TOKEN_DISCORD_QUI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "LA_TUA_API_KEY_GEMINI_QUI")

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-2.0-flash")

# Mappa emoji flag → nome lingua
FLAG_TO_LANGUAGE = {
    "🇮🇹": "italiano",
    "🇬🇧": "inglese",
    "🇺🇸": "inglese",
    "🇫🇷": "francese",
    "🇩🇪": "tedesco",
    "🇪🇸": "spagnolo",
    "🇵🇹": "portoghese",
    "🇧🇷": "portoghese brasiliano",
    "🇯🇵": "giapponese",
    "🇨🇳": "cinese",
    "🇰🇷": "coreano",
    "🇷🇺": "russo",
    "🇸🇦": "arabo",
    "🇳🇱": "olandese",
    "🇵🇱": "polacco",
    "🇹🇷": "turco",
    "🇸🇪": "svedese",
    "🇳🇴": "norvegese",
    "🇩🇰": "danese",
    "🇫🇮": "finlandese",
    "🇬🇷": "greco",
    "🇭🇺": "ungherese",
    "🇨🇿": "ceco",
    "🇷🇴": "rumeno",
    "🇺🇦": "ucraino",
}

# ─── Setup bot ───────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Funzione di traduzione ───────────────────────────────────────────────────

def translate(text: str, target_language: str) -> str:
    """Chiama Gemini per tradurre il testo nella lingua target."""
    prompt = (
        f"Traduci il seguente testo in {target_language}. "
        f"Rispondi SOLO con la traduzione, senza spiegazioni o note aggiuntive.\n\n"
        f"{text}"
    )
    response = gemini.generate_content(prompt)
    return response.text.strip()

# ─── Evento: bot pronto ───────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Bot connesso come {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🌍 !traduci <lingua> <testo>"
        )
    )

# ─── Comando: !traduci ────────────────────────────────────────────────────────

@bot.command(name="traduci")
async def traduci(ctx, lingua: str, *, testo: str):
    """
    Traduce il testo nella lingua specificata.
    Uso: !traduci <lingua> <testo>
    Esempio: !traduci inglese Ciao come stai?
    """
    async with ctx.typing():
        try:
            risultato = translate(testo, lingua)
            embed = discord.Embed(color=0x5865F2)
            embed.set_author(name="🌍 Traduttore AI", icon_url=bot.user.display_avatar.url)
            embed.add_field(name="📝 Testo originale", value=f"```{testo}```", inline=False)
            embed.add_field(name=f"✅ Traduzione in {lingua.capitalize()}", value=f"```{risultato}```", inline=False)
            embed.set_footer(text=f"Richiesto da {ctx.author.display_name} • Powered by Gemini",
                             icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.reply(f"❌ Errore durante la traduzione: `{e}`")

# ─── Comando: !traduzione (risposta a un messaggio) ───────────────────────────

@bot.command(name="traduzione")
async def traduzione(ctx, lingua: str = "italiano"):
    """
    Rispondi a un messaggio con !traduzione per tradurlo.
    Uso: !traduzione [lingua]  (default: italiano)
    """
    if ctx.message.reference is None:
        await ctx.reply("❌ Devi rispondere a un messaggio per tradurlo! Usa: `!traduzione [lingua]`")
        return

    async with ctx.typing():
        try:
            msg_originale = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            testo = msg_originale.content
            if not testo:
                await ctx.reply("❌ Il messaggio non contiene testo da tradurre.")
                return

            risultato = translate(testo, lingua)
            embed = discord.Embed(color=0x57F287)
            embed.set_author(name="🌍 Traduttore AI", icon_url=bot.user.display_avatar.url)
            embed.add_field(name="📝 Testo originale", value=f"```{testo[:1000]}```", inline=False)
            embed.add_field(name=f"✅ Traduzione in {lingua.capitalize()}", value=f"```{risultato}```", inline=False)
            embed.set_footer(
                text=f"Messaggio di {msg_originale.author.display_name} | Richiesto da {ctx.author.display_name} • Powered by Gemini"
            )
            await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.reply(f"❌ Errore: `{e}`")

# ─── Comando: !lingue ─────────────────────────────────────────────────────────

@bot.command(name="lingue")
async def lingue(ctx):
    """Mostra le flag supportate per la traduzione automatica."""
    embed = discord.Embed(
        title="🌍 Lingue supportate tramite flag",
        description="Reagisci a qualsiasi messaggio con una di queste flag per tradurlo automaticamente!",
        color=0xFEE75C
    )
    lista = "\n".join(f"{flag} → {lingua.capitalize()}" for flag, lingua in FLAG_TO_LANGUAGE.items())
    embed.add_field(name="Flag disponibili", value=lista, inline=False)
    embed.add_field(
        name="Comando diretto",
        value="`!traduci <lingua> <testo>` — supporta qualsiasi lingua tramite Gemini",
        inline=False
    )
    await ctx.reply(embed=embed)

# ─── Evento: reazione con flag ────────────────────────────────────────────────

@bot.event
async def on_reaction_add(reaction, user):
    """Traduce automaticamente un messaggio quando si reagisce con una flag."""
    if user.bot:
        return

    emoji = str(reaction.emoji)
    if emoji not in FLAG_TO_LANGUAGE:
        return

    lingua = FLAG_TO_LANGUAGE[emoji]
    testo = reaction.message.content

    if not testo:
        return

    try:
        risultato = translate(testo, lingua)
        embed = discord.Embed(color=0xEB459E)
        embed.set_author(name="🌍 Traduttore AI", icon_url=bot.user.display_avatar.url)
        embed.add_field(name="📝 Testo originale", value=f"```{testo[:1000]}```", inline=False)
        embed.add_field(name=f"{emoji} Traduzione in {lingua.capitalize()}", value=f"```{risultato}```", inline=False)
        embed.set_footer(
            text=f"Messaggio di {reaction.message.author.display_name} | Richiesto da {user.display_name} • Powered by Gemini"
        )
        await reaction.message.reply(embed=embed)
    except Exception as e:
        await reaction.message.channel.send(f"❌ Errore nella traduzione: `{e}`")

# ─── Avvio bot ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
