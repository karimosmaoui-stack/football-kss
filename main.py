import discord
from discord.ext import commands
import json
import os
import random
import time
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
# -------------------------
# JSON helpers & files
# -------------------------


USERS_FILE = os.path.join( "users.json")
CARDS_FILE = os.path.join( "cards.json")
DROP_FILE  = os.path.join( "drop.json")
import json

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_cards():
    with open("cards.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---- Filter by rarity ----
def filter_cards(cards, rarity):
    return [p for p in cards.values() if p["rarity"] == rarity]

# ---- Packs configuration ----
PACKS = {
    "bronze": {
        "count": 3,
        "weights": {
            "bronze": 80,
            "common": 15,
            "rare": 5
        }
    },
    "silver": {
        "count": 3,
        "weights": {
            "common": 60,
            "rare": 30,
            "legendary": 10
        }
    },
    "gold": {
        "count": 3,
        "weights": {
            "common": 50,
            "rare": 35,
            "legendary": 15
        }
    },
    "legendary": {
        "count": 3,
        "weights": {
            "rare": 40,
            "legendary": 60
        }
    }
}

@bot.command()
async def pack(ctx, pack_name: str):
    pack_name = pack_name.lower()

    if pack_name not in PACKS:
        await ctx.send("❌ Pack mawjoudch.")
        return

    # --- Step 1: Animation Start ---
    loading = discord.Embed(
        title="🎁 Opening Pack...",
        description="🔄 Preparing animation...",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=loading)

    await asyncio.sleep(1.5)

    flash = discord.Embed(
        title="✨ Flash!",
        description="Cards are coming...",
        color=discord.Color.gold()
    )
    await msg.edit(embed=flash)

    await asyncio.sleep(1)

    # --- Step 2: Generate Cards ---
    cards = load_cards()
    pack_data = PACKS[pack_name]
    count = pack_data["count"]
    weights = pack_data["weights"]

    pulled = []
    for _ in range(count):
        rarities = list(weights.keys())
        w = list(weights.values())
        chosen_rarity = random.choices(rarities, weights=w)[0]

        available = filter_cards(cards, chosen_rarity)
        card = random.choice(available)
        pulled.append(card)

    # --- Step 3: Final Reveal ---
    result = discord.Embed(
        title=f"🎉 {pack_name.capitalize()} Pack Result",
        description="Your cards:",
        color=discord.Color.green()
    )

    for c in pulled:
        result.add_field(
            name=f"{c['name']} ({c['rating']})",
            value=f"Rarity: {c['rarity']}",
            inline=False
        )
        result.set_thumbnail(url=c["image"])

    await msg.edit(embed=result)

import asyncio
PRICES = {
    "bronze": 500,
    "silver": 1500,
    "gold": 3000,
    "legendary": 7000
}

def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@bot.command()
async def buy(ctx, pack_type: str):
    pack_type = pack_type.lower()

    if pack_type not in PACK_PRICES:
        return await ctx.send("❌ Pack mawjoudch. Options: low, common, rare, legendary")

    users = read_json("users.json")
    user_id = str(ctx.author.id)

    if user_id not in users:
        users[user_id] = {"coins": 0, "cards": []}

    price = PACK_PRICES[pack_type]

    if users[user_id]["coins"] < price:
        return await ctx.send(f"❌ Maandekch coins barsha. T5assar: **{price}** coins.")

    users[user_id]["coins"] -= price
    save_json("users.json", users)

    await ctx.send(f"🎁 {ctx.author.mention} ashtar **{PACK_NAMES[pack_type]}** b siker!")


@bot.command()
async def inspect(ctx, card_id=None):
    import json

    if not card_id:
        return await ctx.send("❌ استعمل:\n`!inspect <card_id>`")

    # ✅ Load cards
    try:
        cards = json.load(open("cards.json"))
    except:
        return await ctx.send("❌ ما نجمتش نقرا cards.json")

    if card_id not in cards:
        return await ctx.send("❌ البطاقة غير موجودة.")

    card = cards[card_id]

    # ✅ Embed
    embed = discord.embed(
        title=f"{card['name']} — {card['rating']} ⭐",
        description=f"**Card ID:** `{card_id}`",
        color=0x00ffcc
    )

    embed.add_field(name="Position", value=card["pos"])
    embed.add_field(name="Club", value=card["club"])
    embed.add_field(name="Nation", value=card["nation"])
    embed.add_field(name="Rarity", value=card["rarity"])

    # ✅ Stats (إذا موجودين)
    if "stats" in card:
        stats_txt = ""
        for s, v in card["stats"].items():
            stats_txt += f"**{s.upper()}**: {v}\n"
        embed.add_field(name="Stats", value=stats_txt, inline=False)

    # ✅ Card image
    if "image" in card:
        embed.set_thumbnail(url=card["image"])

    await ctx.send(embed=embed)

@bot.command()
async def sellcard(ctx, card_id: str, price: int):
    user_id = str(ctx.author.id)
    users = load_users()

    if card_id not in users["users"][user_id]["cards"]:
        await ctx.send("❌ Ma3andekch el card.")
        return

    market = load_market()
    market["listings"].append({
        "seller": user_id,
        "card_id": card_id,
        "price": price
    })
    save_market(market)

    users["users"][user_id]["cards"].remove(card_id)
    save_users(users)

    await ctx.send(f"💸 Card listed for **{price} coins**.")


@bot.command()
async def buycard(ctx, index: int):
    user_id = str(ctx.author.id)
    users = load_users()
    market = load_market()

    if index >= len(market["listings"]):
        await ctx.send("❌ Index ghalet.")
        return

    item = market["listings"][index]

    price = item["price"]

    if users["users"][user_id]["coins"] < price:
        await ctx.send("❌ coins mkafi4.")
        return

    # pay seller
    users["users"][item["seller"]]["coins"] += price
    users["users"][user_id]["coins"] -= price

    # give card
    users["users"][user_id]["cards"].append(item["card_id"])

    # remove from market
    market["listings"].pop(index)

    save_users(users)
    save_market(market)

    await ctx.send("✅ Card bought successfully!")


def load_cards():
    with open("cards.json", "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def safe_read(path, default):
    ensure_dir(os.path.dirname(path) if os.path.dirname(path) else ".")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # reset to default if corrupted
            with open(path, "w", encoding="utf-8") as f2:
                json.dump(default, f2, ensure_ascii=False, indent=2)
            return default

def safe_write(path, data):
    ensure_dir(os.path.dirname(path) if os.path.dirname(path) else ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def read_json(path):
    ensure_file(path, {})
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # recover by resetting
            with open(path, "w", encoding="utf-8") as f2:
                json.dump({}, f2, ensure_ascii=False, indent=2)
            return {}

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===========================
#   BOT READY
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

    # Sync to specific guild for instant commands
    guild = discord.Object(id=1434566037084307596)  # Paste your server ID here
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Commands synced to guild!")




# ===========================
#   DROP COMMAND
# ===========================
import string

def generate_unique_id(length=10):
    """Generate unique random ID (letters + digits)"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def get_user(uid: str):
    data = read_json(USERS_FILE)
    if uid not in data:
        data[uid] = {
            "coins": 0,
            "cards": [],
            "last_drop": 0,
            "wins": 0,
            "xp": 0
        }
        write_json(USERS_FILE, data)
    return data[uid]

import json
from datetime import datetime, timedelta
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    users = load_users()

    # create user if not exist
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "inventory": [],
            "last_daily": None
        }

    user = users[user_id]

    now = datetime.utcnow()

    # if first time — give reward directly
    if user["last_daily"] is None:
        reward = 500
        user["coins"] += reward
        user["last_daily"] = now.isoformat()
        save_users(users)
        return await ctx.send(f"🎁 **Daily collected!** You earned **{reward} coins**!")

    # check delay
    last = datetime.fromisoformat(user["last_daily"])
    diff = now - last

    if diff < timedelta(hours=24):
        remaining = timedelta(hours=24) - diff
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        return await ctx.send(
            f"⏳ Tzid tsenné **{hours}h {minutes}m** bech taakhodh daily mra o5ra."
        )

    # give reward
    reward = 500
    user["coins"] += reward
    user["last_daily"] = now.isoformat()
    save_users(users)

    await ctx.send(f"🎉 **Daily collected!** You got **{reward} coins**!")


def read_cards():
    with open("cards.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_card_obj(card):
    db = read_json_file(CARDS_FILE)  # Read the whole file

    if "players" not in db:
        db["players"] = {}


    card_key = card["name"].lower().replace(" ", "")
    db["players"][card_key] = card


    write_json_file(CARDS_FILE, db)


@bot.command()
async def debug_drop(ctx):
    db = read_json(CARDS_FILE)
    await ctx.send(f"1. DB type: {type(db)}")
    await ctx.send(f"2. DB keys: {list(db.keys())}")

    if "players" in db:
        cards_db = db["players"]
        await ctx.send(f"3. Players count: {len(cards_db)}")
        await ctx.send(f"4. Player keys: {list(cards_db.keys())[:5]}")

        all_cards = [p for p in cards_db.values() if p.get("drop", True)]
        await ctx.send(f"5. Eligible cards: {len(all_cards)}")

        if all_cards:
            await ctx.send(f"6. First card: {all_cards[0].get('name', 'No name')}")
def remove_card_obj(card_id):
    cards = read_cards()
    if card_id in cards:
        del cards[card_id]
        write_json(CARDS_FILE, cards)

# -------------------------
# Utility: pick cards for drop
# -------------------------
def eligible_cards_for_drop():
    """
    Return list of card objects eligible for drop.
    Preference:
      1) Cards created by BOT_OWNER_ID (if set)  --> this matches "ena ili nsna3hom"
      2) If none found, return all created cards (cards that have 'created_by')
      3) If none, return all cards (fallback)
    """
    cards = list(read_cards().values())
    if not cards:
        return []

    # 1) filter by BOT_OWNER_ID
    if 924732202397364226:
        by_owner = [c for c in cards if str(c.get("created_by")) == str(924732202397364226)]
        if by_owner:
            return by_owner

    # 2) filter by any created_by present
    created_any = [c for c in cards if c.get("created_by")]
    if created_any:
        return created_any

    # 3) fallback: return all cards
    return cards

import discord
from discord.ext import commands
import json
import os



# Load players database
def load_players():
    with open("cards.json", "r", encoding="utf-8") as f:
        return json.load(f)["players"]

import random
import string

def generate_random_id(length=7):
    """Generate a random ID with letters and numbers like Karuta"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@bot.command()
async def createcard(ctx, player_id):
    print("saving to:",CARDS_FILE)
    player_id =f"card_{generate_random_id()}"

    # Load JSON file
    with open("cards.json", "r", encoding="utf-8") as f:
        players_db = json.load(f)["players"]

    # Check if player exists in JSON
    if player_id not in players_db:
        return await ctx.send("❌ Player not found in database!")

    # Get player data
    p = players_db[player_id]

    # Create embed
    embed = discord.Embed(
        title=f"{p['name']} - {p['rating']}",
        description=(
            f"**Position:** {p['position']}\n"
            f"**Club:** {p['club']}\n"
            f"**Nation:** {p['nation']}\n"
            f"**Rarity:** {p['rarity']}\n"
            f"**league:** {p['league']}"
        ),
        color=0x00ff9d
    )

    # Set image (card picture)
    embed.set_image(url=p["image"])



    await ctx.send(embed=embed)



def get_last_drop(uid):
    d = safe_read(DROP_FILE, {"last_drops": {}})
    return d.get("last_drops", {}).get(uid, 0)

def set_drop_time(uid):
    d = safe_read(DROP_FILE, {"last_drops": {}})
    if "last_drops" not in d:
        d["last_drops"] = {}
    d["last_drops"][uid] = int(time.time())
    safe_write(DROP_FILE, d)

def can_drop(uid):
    return (time.time() - get_last_drop(uid)) >= DROP_COOLDOWN

@bot.command()
async def profile(ctx):
    uid = str(ctx.author.id)
    u = get_user(uid)
    await ctx.send(f"**Profile — {ctx.author.display_name}**\nCoins: {u['coins']}\nCards: {len(u.get('cards',[]))}")




from discord.ui import View, Button
import discord

CARDS_PER_PAGE = 10

class MyCardsView(View):
    def __init__(self, user_id, cards, page=0):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.cards = cards
        self.page = page

        # Buttons
        self.add_item(Button(label="⏮️", style=discord.ButtonStyle.secondary, custom_id="first"))
        self.add_item(Button(label="◀️", style=discord.ButtonStyle.primary, custom_id="prev"))
        self.add_item(Button(label="▶️", style=discord.ButtonStyle.primary, custom_id="next"))
        self.add_item(Button(label="⏭️", style=discord.ButtonStyle.secondary, custom_id="last"))

    async def interaction_check(self, interaction):
        return str(interaction.user.id) == self.user_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    def format_page(self):
        start = self.page * CARDS_PER_PAGE
        end = start + CARDS_PER_PAGE
        page_cards = self.cards[start:end]

        text = ""
        for c in page_cards:
            text += (
                f"**{c['name']}** — ⭐ {c['rating']}\n"
                f"`{c['position']}` • {c['club']} • {c['rarity']}\n"
                f"ID: `{c['id']}`\n\n"
            )
        return text



@bot.event
async def on_interaction(interaction: discord.Interaction):

    if interaction.data["custom_id"] not in ["first", "prev", "next", "last"]:
        return

    uid = str(interaction.user.id)

    users = read_json(USERS_FILE)
    cards = users[uid]["cards"]

    view = interaction.message.components
    msg_embed = interaction.message.embeds[0]

    # Extract exist view
    original_view = interaction.message._state.store_view(interaction.message.id)

    page = original_view.page
    total_pages = (len(cards)-1)//CARDS_PER_PAGE + 1

    # Page logic
    if interaction.data["custom_id"] == "first":
        page = 0
    elif interaction.data["custom_id"] == "prev":
        page = max(0, page - 1)
    elif interaction.data["custom_id"] == "next":
        page = min(total_pages - 1, page + 1)
    elif interaction.data["custom_id"] == "last":
        page = total_pages - 1

    # New view
    new_view = MyCardsView(uid, cards, page)

    # New embed
    new_embed = discord.Embed(
        title="📘 Card Collection",
        description=f"Cards owned by <@{uid}>",
        color=discord.Color.blue()
    )
    new_embed.add_field(
        name=f"Page {page+1} / {total_pages}",
        value=new_view.format_page(),
        inline=False
    )

    await interaction.response.edit_message(embed=new_embed, view=new_view)





def read_json_file(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)



# Add this to your constants at the top
COINS_EMOJI = "🪙"


@bot.command()
async def balance(ctx):
    """Check your coins balance"""
    uid = str(ctx.author.id)

    users_db = read_json(USERS_FILE)
    if uid not in users_db:
        users_db[uid] = {"cards": [], "coins": 0}
        write_json(USERS_FILE, users_db)

    coins = users_db[uid].get("coins", 0)
    cards_count = len(users_db[uid].get("cards", []))

    embed = discord.Embed(
        title=f"💰 محفظة {ctx.author.display_name}",
        color=discord.Color.gold()
    )
    embed.add_field(name=f"{COINS_EMOJI} العملات", value=f"*{coins:,}*", inline=True)
    embed.add_field(name="🎴 البطاقات", value=f"*{cards_count}*", inline=True)
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)


@bot.command()
async def quicksell(ctx, card_number: int):
    """
    Sell a card quickly for coins
    Usage: !quicksell <card_number>
    """
    uid = str(ctx.author.id)

    users_db = read_json(USERS_FILE)
    if uid not in users_db or not users_db[uid].get("cards"):
        return await ctx.send("❌ ليس لديك بطاقات للبيع!")

    user_cards = users_db[uid]["cards"]
    card_data = user_cards[card_number - 1]
    card_id = card_data["id"] if isinstance(card_data, dict) else card_data
    if isinstance(card_id, str):
        card_id = int(card_id)
    # Validate card number
    if card_number < 1 or card_number > len(user_cards):
        return await ctx.send(f"❌ رقم البطاقة غير صحيح! لديك {len(user_cards)} بطاقة فقط.")

    # Get the card


    # Find card details
    cards_db = read_json_file(CARDS_FILE)
    card = None
    for key, c in cards_db.get("players", {}).items():
        if c.get("id") == card_id  or key == card_id:
            card = c
            break

    if not card:
        return await ctx.send("❌ خطأ: البطاقة غير موجودة!")

    # Calculate sell price based on rating and rarity
    base_price = card['rating'] * 10

    rarity_multiplier = {
        "common": 1.0,
        "rare": 1.5,
        "legendary": 2.5
    }

    multiplier = rarity_multiplier.get(card.get('rarity', 'common'), 1.0)
    sell_price = int(base_price * multiplier)

    # Remove card from user
    user_cards.pop(card_number - 1)
    users_db[uid]["cards"] = user_cards

    # Add coins
    users_db[uid]["coins"] = users_db[uid].get("coins", 0) + sell_price

    # Save
    write_json(USERS_FILE, users_db)

    # Create embed
    rarity_emoji = {
        "common": "⚪",
        "rare": "🟢",
        "legendary": "🟡"
    }.get(card.get("rarity", "common"), "⚪")

    embed = discord.Embed(
        title="💰 بيع سريع",
        description=f"لقد بعت *{card['name']}* {rarity_emoji}",
        color=discord.Color.green()
    )

    embed.add_field(
        name="تفاصيل البطاقة",
        value=f"⭐ {card['rating']} • {card['position']} • {card['club']}",
        inline=False
    )

    embed.add_field(
        name=f"{COINS_EMOJI} السعر",
        value=f"*+{sell_price:,}* عملة",
        inline=False
    )

    new_balance = users_db[uid]["coins"]
    embed.add_field(
        name="💼 رصيدك الجديد",
        value=f"*{new_balance:,}* {COINS_EMOJI}",
        inline=False
    )

    if card.get("image"):
        embed.set_thumbnail(url=card["image"])

    await ctx.send(embed=embed)


@bot.command()
async def sell(ctx):
    """
    Interactive sell menu - shows your cards and lets you choose which to sell
    """
    uid = str(ctx.author.id)

    users_db = read_json(USERS_FILE)
    if uid not in users_db or not users_db[uid].get("cards"):
        return await ctx.send("❌ ليس لديك بطاقات للبيع!")

    user_cards = []
    cards_db = read_json_file(CARDS_FILE)

    for card_id in users_db[uid]["cards"]:
        for key, card in cards_db.get("players", {}).items():
            if card["id"] == card_id:
                user_cards.append(card)
                break

    # Show first 10 cards
    embed = discord.Embed(
        title="🏪 بطاقاتك للبيع",
        description=f"استخدم !quicksell <رقم> لبيع بطاقة\nمثال: !quicksell 1",
        color=discord.Color.blue()
    )

    for i, card in enumerate(user_cards[:10], 1):
        base_price = card['rating'] * 10
        rarity_multiplier = {
            "common": 1.0,
            "rare": 1.5,
            "legendary": 2.5
        }.get(card.get('rarity', 'common'), 1.0)

        sell_price = int(base_price * rarity_multiplier)

        rarity_emoji = {
            "common": "⚪",
            "rare": "🟢",
            "legendary": "🟡"
        }.get(card.get("rarity", "common"), "⚪")

        embed.add_field(
            name=f"{i}. {card['name']} {rarity_emoji}",
            value=f"⭐ {card['rating']} • {card['position']}\n💰 {sell_price:,} {COINS_EMOJI}",
            inline=False
        )

    if len(user_cards) > 10:
        embed.set_footer(text=f"...و {len(user_cards) - 10} بطاقة أخرى")

    await ctx.send(embed=embed)


# Update the PickView callback to give coins on pick
class PickView(View):
    def __init__(self, cards, user_id):
        super().__init__(timeout=60)
        self.cards = cards
        self.user_id = user_id
        self.picked = False

        for i in range(3):
            button = Button(
                label=str(i + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"pick_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, index):
        async def button_callback(interaction: discord.Interaction):
            if str(interaction.user.id) != self.user_id:
                return await interaction.response.send_message(
                    "❌ هذا الدروب ليس لك!",
                    ephemeral=True
                )

            if self.picked:
                return await interaction.response.send_message(
                    "❌ تم اختيار بطاقة بالفعل!",
                    ephemeral=True
                )

            self.picked = True
            selected_card = self.cards[index]

            # Add card to user's collection
            users_db = read_json(USERS_FILE)
            if self.user_id not in users_db:
                users_db[self.user_id] = {"cards": [], "coins": 0}

            users_db[self.user_id]["cards"].append(selected_card["id"])

            # Give bonus coins for picking
            bonus_coins = random.randint(10, 50)
            users_db[self.user_id]["coins"] = users_db[self.user_id].get("coins", 0) + bonus_coins

            write_json(USERS_FILE, users_db)

            if self.user_id in DROP_BUFFER:
                del DROP_BUFFER[self.user_id]

            condition = random.choice([
                "good condition",
                "mint condition",
                "excellent condition"
            ])

            embed = discord.Embed(
                title=f"✅ تم الاختيار!",
                description=f"*{interaction.user.display_name}* اختار البطاقة رقم *{index + 1}*",
                color=discord.Color.green()
            )

            embed.add_field(
                name=selected_card['name'],
                value=f"⭐ {selected_card['rating']} • {selected_card['position']} • {selected_card['club']}\n💎 {condition}",
                inline=False
            )

            embed.add_field(
                name=f"🎁 مكافأة",
                value=f"+{bonus_coins} {COINS_EMOJI}",
                inline=False
            )

            if selected_card.get("image"):
                embed.set_thumbnail(url=selected_card["image"])

            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)

        return button_callback

class ClubPages(discord.ui.View):
    def __init__(self, ctx, results):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.results = results
        self.page = 0

    async def update(self, interaction):
        p = self.results[self.page]

        embed = discord.Embed(
            title=f"{p['name']} — {p['rating']}",
            description=f"{p['position']} • {p['rarity']}\n\n{p['club']} • {p['league']}",
            color=discord.Color.blue()
        )
        embed.set_image(url=p["image"])

        embed.set_footer(text=f"Page {self.page+1}/{len(self.results)}")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction, button):
        if self.page > 0:
            self.page -= 1
        await self.update(interaction)

    @discord.ui.button(label="➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction, button):
        if self.page < len(self.results) - 1:
            self.page += 1
        await self.update(interaction)


@bot.command()
async def searchclub(ctx, *, club_name: str):
    data = read_json(CARDS_FILE)
    players = data.get("players", {})

    # بحث club
    results = [
        p for p in players.values()
        if p["club"].lower() == club_name.lower()
    ]

    if not results:
        return await ctx.send(f"❌ ما لقيتش حتى بطاقة من النادي: **{club_name}**")

    view = ClubPages(ctx, results)

    # أول صفحة
    first = results[0]

    embed = discord.Embed(
        title=f"{first['name']} — {first['rating']}",
        description=f"{first['position']} • {first['rarity']}\n\n{first['club']} • {first['league']}",
        color=discord.Color.blue()
    )
    embed.set_image(url=first["image"])
    embed.set_footer(text=f"Page 1/{len(results)}")

    await ctx.send(embed=embed, view=view)

@bot.command()
async def searchplayer(ctx, *, player_name: str):
    data = read_json(CARDS_FILE)
    players = data.get("players", {})

    results = [
        p for p in players.values()
        if player_name.lower() in p["name"].lower()
    ]

    if not results:
        return await ctx.send(f"❌ ما لقيتش حتى لاعب اسمو: **{player_name}**")

    embed = discord.Embed(
        title=f"🔍 نتائج البحث على: {player_name}",
        description=f"{len(results)} نتيجة:",
        color=discord.Color.green()
    )

    for p in results:
        embed.add_field(
            name=f"{p['name']} — {p['rating']}",
            value=f"{p['club']} • {p['position']} • {p['rarity']}\nID: {p['id']}",
            inline=False
        )

    embed.set_thumbnail(url=results[0]["image"])
    await ctx.send(embed=embed)
@bot.command()
async def searchnation(ctx, *, nation: str):
    data = read_json(CARDS_FILE)
    players = data.get("players", {})

    results = [
        p for p in players.values()
        if p["nation"].lower() == nation.lower()
    ]

    if not results:
        return await ctx.send(f"❌ ما لقيتش حتى لاعب من: **{nation}**")

    embed = discord.Embed(
        title=f"🌍 لاعبين من {nation}",
        description=f"{len(results)} نتيجة:",
        color=discord.Color.gold()
    )

    for p in results:
        embed.add_field(
            name=f"{p['name']} — {p['rating']}",
            value=f"{p['club']} • {p['position']} • {p['rarity']}",
            inline=False
        )

    embed.set_thumbnail(url=results[0]["image"])
    await ctx.send(embed=embed)
@bot.command()
async def searchposition(ctx, *, position: str):
    data = read_json(CARDS_FILE)
    players = data.get("players", {})

    results = [
        p for p in players.values()
        if p["position"].lower() == position.lower()
    ]

    if not results:
        return await ctx.send(f"❌ ما فماش لاعبين في مركز: **{position}**")

    embed = discord.Embed(
        title=f"📌 لاعبين مركز {position}",
        description=f"{len(results)} نتيجة:",
        color=discord.Color.blue()
    )

    for p in results:
        embed.add_field(
            name=f"{p['name']} — {p['rating']}",
            value=f"{p['club']} • {p['nation']} • {p['rarity']}",
            inline=False
        )

    embed.set_thumbnail(url=results[0]["image"])
    await ctx.send(embed=embed)
@bot.command()
async def searchrating(ctx, rating: int):
    data = read_json(CARDS_FILE)
    players = data.get("players", {})

    results = [
        p for p in players.values()
        if p["rating"] >= rating
    ]

    if not results:
        return await ctx.send(f"❌ ما فماش لاعبين بريتنغ ≥ **{rating}**")

    embed = discord.Embed(
        title=f"⭐ لاعبين Rating ≥ {rating}",
        description=f"{len(results)} نتيجة:",
        color=discord.Color.purple()
    )

    for p in results:
        embed.add_field(
            name=f"{p['name']} — {p['rating']}",
            value=f"{p['club']} • {p['position']} • {p['rarity']}",
            inline=False
        )

    embed.set_thumbnail(url=results[0]["image"])
    await ctx.send(embed=embed)

@bot.command()
async def searchname(ctx, *, name):
    name = name.lower()

    # Load file
    with open("cards.json", "r", encoding="utf-8") as f:
        cards_db = json.load(f)["players"]

    # Search inside players
    found = []
    for p in cards_db.values():
        if name in p["name"].lower():
            found.append(p)

    if not found:
        return await ctx.send("❌ ما لقيتش حتى لاعب بهالاسم.")

    # If only 1 player found → show full card with image
    if len(found) == 1:
        p = found[0]
        embed = discord.Embed(
            title=f"{p['name']} - {p['rating']}",
            description=(
                f"**Position:** {p['position']}\n"
                f"**Club:** {p['club']}\n"
                f"**Nation:** {p['nation']}\n"
                f"**Rarity:** {p['rarity']}"
            ),
            color=0x0099ff
        )
        embed.set_image(url=p["image"])
        embed.set_footer(text=f"ID: {p['id']}")
        return await ctx.send(embed=embed)

    # If many players found → list them without images
    embed = discord.Embed(
        title=f"🔍 البحث عن: {name}",
        color=discord.Color.blue()
    )

    for c in found[:10]:
        embed.add_field(
            name=f"{c['name']} ({c['rating']})",
            value=f"Club: {c['club']}\nNation: {c['nation']}\nID: {c['id']}",
            inline=False
        )

    await ctx.send(embed=embed)


from discord.ui import Button, View
import random
import time

# At the top with your other constants
COOLDOWN = 3600  # 1 hour in seconds
DROP_BUFFER = {}  # uid: {"cards": [card1, card2, card3], "message_id": msg_id}
DROP_TIMES = {}  # uid: last_drop_timestamp


class PickView(View):
    def __init__(self, cards, user_id):
        super().__init__(timeout=60)  # 60 seconds to pick
        self.cards = cards
        self.user_id = user_id
        self.picked = False

        # Create 3 buttons
        for i in range(3):
            button = Button(
                label=str(i + 1),
                style=discord.ButtonStyle.primary,
                custom_id=f"pick_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, index):
        async def button_callback(interaction: discord.Interaction):
            # Check if correct user
            if str(interaction.user.id) != self.user_id:
                return await interaction.response.send_message(
                    "❌ هذا الدروب ليس لك!",
                    ephemeral=True
                )

            # Check if already picked
            if self.picked:
                return await interaction.response.send_message(
                    "❌ تم اختيار بطاقة بالفعل!",
                    ephemeral=True
                )

            self.picked = True
            selected_card = self.cards[index]

            # Add card to user's collection
            users_db = read_json(USERS_FILE)
            if self.user_id not in users_db:
                users_db[self.user_id] = {"cards": [], "coins": 0}

            users_db[self.user_id]["cards"].append(selected_card["id"])
            write_json(USERS_FILE, users_db)

            # Remove from buffer
            if self.user_id in DROP_BUFFER:
                del DROP_BUFFER[self.user_id]

            # Determine condition
            condition = random.choice([
                "good condition",
                "mint condition",
                "excellent condition"
            ])

            # Create success embed
            embed = discord.Embed(
                title=f"✅ تم الاختيار!",
                description=f"*{interaction.user.display_name}* اختار البطاقة رقم *{index + 1}*",
                color=discord.Color.green()
            )

            embed.add_field(
                name=selected_card['name'],
                value=f"⭐ {selected_card['rating']} • {selected_card['position']} • {selected_card['club']}\n💎 {condition}",
                inline=False
            )

            if selected_card.get("image"):
                embed.set_thumbnail(url=selected_card["image"])

            # Disable all buttons
            for item in self.children:
                item.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)

        return button_callback

    async def on_timeout(self):
        # Disable buttons when timeout
        for item in self.children:
            item.disabled = True





from PIL import Image
import io
import aiohttp
import asyncio


async def create_drop_image(cards):
    """Create a horizontal image with 3 cards side by side"""
    card_width = 250
    card_height = 350
    spacing = 20

    total_width = (card_width * 3) + (spacing * 2)
    combined = Image.new('RGB', (total_width, card_height), (47, 49, 54))

    # Add headers to avoid rate limiting
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for i, card in enumerate(cards):
            try:
                image_url = card.get('image', '')

                if not image_url:
                    print(f"Warning: Card {i} has no image URL")
                    continue

                print(f"Loading card {i}: {card.get('name')} from {image_url}")

                # Add delay between requests to avoid rate limiting
                if i > 0:
                    await asyncio.sleep(0.5)

                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    print(f"Card {i} response: HTTP {resp.status}")

                    if resp.status == 200:
                        img_data = await resp.read()
                        card_img = Image.open(io.BytesIO(img_data))

                        if card_img.mode != 'RGB':
                            card_img = card_img.convert('RGB')

                        card_img = card_img.resize((card_width, card_height), Image.LANCZOS)

                        x_position = i * (card_width + spacing)
                        combined.paste(card_img, (x_position, 0))
                        print(f"Successfully loaded card {i}")
                    else:
                        print(f"Failed to load card {i}: HTTP {resp.status}")
            except Exception as e:
                print(f"Error loading card {i}: {e}")

    return combined

@bot.command()
async def drop(ctx):
    uid = str(ctx.author.id)

    # Check cooldown
    if uid in DROP_TIMES:
        time_passed = time.time() - DROP_TIMES[uid]
        if time_passed < COOLDOWN:
            remaining = int(COOLDOWN - time_passed)
            mins = remaining // 60
            secs = remaining % 60
            return await ctx.send(f"⏰ انتظر *{mins}* دقيقة و *{secs}* ثانية قبل الدروب القادم!")

    # Get cards
    db = read_json_file(CARDS_FILE)
    if "players" not in db or not db["players"]:
        return await ctx.send("❌ لا توجد بطاقات متاحة")

    all_cards = list(db["players"].values())
    if len(all_cards) < 3:
        return await ctx.send("❌ تحتاج 3 بطاقات على الأقل في القاعدة")

    options = random.sample(all_cards, 3)

    # Store in buffer
    DROP_BUFFER[uid] = {"cards": options}
    DROP_TIMES[uid] = time.time()

    # Create combined image
    try:
        combined_image = await create_drop_image(options)

        # Save to bytes
        with io.BytesIO() as image_binary:
            combined_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='drop.png')

        # Create embed
        embed = discord.Embed(
            description=f"*@{ctx.author.display_name}* is dropping 3 cards!",
            color=discord.Color.blue()
        )

        # Add card info
        card_list = ""
        for i, card in enumerate(options, 1):
            rarity_emoji = {
                "common": "⚪",
                "rare": "🟢",
                "legendary": "🟡"
            }.get(card.get("rarity", "common"), "⚪")

            card_id = card.get('id', 'unknown').replace('card_', '') if isinstance(card.get('id'), str) else card.get(
                'id', 'unknown')
            card_list += f"*{i}* {card['name']} {rarity_emoji} · ⭐{card['rating']} · `#{card_id}`\n"

        embed.add_field(name="البطاقات المتاحة", value=card_list, inline=False)
        embed.set_image(url="attachment://drop.png")
        embed.set_footer(text="اضغط على الزر لاختيار بطاقة! ⏱️ لديك 60 ثانية")

        # Create buttons
        view = PickView(options, uid)

        message = await ctx.send(embed=embed, file=file, view=view)
        DROP_BUFFER[uid]["message_id"] = message.id

    except Exception as e:
        await ctx.send(f"❌ خطأ في إنشاء الصورة: {e}")







import random
def generate_random_id(length=7):
    """Generate a random ID with letters and numbers like Karuta"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
import math
@bot.command()
async def mycards(ctx):
    """View your card collection with IDs"""
    uid = str(ctx.author.id)

    users_db = read_json(USERS_FILE)
    if uid not in users_db or not users_db[uid].get("cards"):
        return await ctx.send("📭 ليس لديك بطاقات بعد! استخدم !drop للحصول على بطاقات")

    cards_db = read_json_file(CARDS_FILE)
    user_cards = []

    for card_id in users_db[uid]["cards"]:
        for key, card in cards_db.get("players", {}).items():
            if card["id"] == card_id:
                user_cards.append(card)
                break

    embed = discord.Embed(
        title=f"🎴 مجموعة {ctx.author.display_name}",
        description=f"لديك *{len(user_cards)}* بطاقة",
        color=discord.Color.gold()
    )

    for i, card in enumerate(user_cards[:10], 1):
        rarity_emoji = {
            "common": "⚪",
            "rare": "🟢",
            "legendary": "🟡"
        }.get(card.get("rarity", "common"), "⚪")

        card_id =str(card.get("id",""))

        embed.add_field(
            name=f"{i}. {card['name']} {rarity_emoji}",
            value=f"⭐ {card['rating']} • {card['position']} • {card['club']}\n`Player ID: #{card_id}`",
            inline=False
        )
        cards_per_page = 10
        total_pages = math.ceil(len(user_cards) / cards_per_page)

        def get_page(page):
            start = page * cards_per_page
            end = start + cards_per_page

            embed = discord.Embed(
                title=f"📦 بطاقاتك — الصفحة {page + 1}/{total_pages}",
                color=0x00ff99
            )

            rarity_emoji = {"common": "⚪", "rare": "🟣", "legendary": "🟡"}

            for i, card in enumerate(user_cards[start:end], start + 1):
                card_id = str(card.get("id", ""))
                embed.add_field(
                    name=f"{i}. {card['name']} {rarity_emoji.get(card['rarity'], '⚪')}",
                    value=f"⭐ {card['rating']} | {card['position']} | {card['club']}\n🆔 ID: {card_id}",
                    inline=False
                )

            return embed

        # --------------------------
        #     Buttons View
        # --------------------------
        class CardsView(View):
            def __init__(self):
                super().__init__(timeout=60)
                self.page = 0

            # ⬅️ Previous Page
            @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.primary)
            async def previous(self, interaction, button):
                if self.page > 0:
                    self.page -= 1
                    await interaction.response.edit_message(embed=get_page(self.page),view=self)

            # ➡️ Next Page
            @discord.ui.button(label="Next ➡️", style=discord.ButtonStyle.primary)
            async def next(self, interaction, button):
                if self.page < total_pages - 1:
                    self.page += 1
                    await interaction.response.edit_message(embed=get_page(self.page),view=self)

        view = CardsView()
        await ctx.send(embed=get_page(0), view=view)






# Add command to view a specific card by ID
@bot.command()
async def card(ctx, card_id: str):
    """View details of a specific card by ID"""
    # Add 'card_' prefix if not included
    if not card_id.startswith('card_'):
        card_id = f'card_{card_id}'

    cards_db = read_json_file(CARDS_FILE)

    # Find card
    card = None
    for key, c in cards_db.get("players", {}).items():
        if c.get("id") == card_id:
            card = c
            break

    if not card:
        return await ctx.send(f"❌ البطاقة {card_id} غير موجودة!")

    rarity_emoji = {
        "common": "⚪",
        "rare": "🟢",
        "legendary": "🟡"
    }.get(card.get("rarity", "common"), "⚪")

    embed = discord.Embed(
        title=f"{card['name']} {rarity_emoji}",
        description=f"Player ID: {card_id}",
        color=discord.Color.blue()
    )

    embed.add_field(name="⭐ Rating", value=card['rating'], inline=True)
    embed.add_field(name="📍 Position", value=card['position'], inline=True)
    embed.add_field(name="🏆 Club", value=card['club'], inline=True)
    embed.add_field(name="🌍 Nation", value=card['nation'], inline=True)
    embed.add_field(name="🎖️ League", value=card.get('league', 'N/A'), inline=True)
    embed.add_field(name="💎 Rarity", value=card.get('rarity', 'common'), inline=True)

    if card.get("image"):
        embed.set_image(url=card["image"])

    await ctx.send(embed=embed)

@bot.command()
async def trade(ctx, member: discord.Member, offer):
    trades = read_trades()
    uid = str(ctx.author.id)
    target = str(member.id)

    if uid == target:
        return await ctx.send("❌ ما تنجمش تتاجر مع روحك.")

    # Check if player exists
    users = read_json(USERS_FILE)
    cards = read_json(CARDS_FILE)

    # Offer = coin or card
    offer_type = None
    offer_value = None

    if offer.endswith("coins"):
        amount = int(offer.replace("coins", ""))
        if users[uid]["coins"] < amount:
            return await ctx.send("❌ ما عندكش كفاية فلوس.")
        offer_type = "coins"
        offer_value = amount

    else:
        card_id = offer
        if card_id not in cards or cards[card_id]["owner"] != uid:
            return await ctx.send("❌ البطاقة غير موجودة أو ما هيّش ملكك.")
        offer_type = "card"
        offer_value = card_id

    trade_id = f"trade_{int(time.time())}"
    trades[trade_id] = {
        "from": uid,
        "to": target,
        "offer_type": offer_type,
        "offer_value": offer_value,
        "status": "pending"
    }

    write_trades(trades)

    await ctx.send(
        f"✅ تم إرسال عرض تجارة إلى {member.mention}\n"
        f"اكتب: !accept {trade_id} للقبول أو !decline {trade_id} للرفض."
    )

PACKS_FILE = "packs.json"
CARDS_FILE = "cards.json"
USER_CARDS_FILE = "user_cards.json"
@bot.command()
async def openpack(ctx, pack_type: str):
    import asyncio
    import random

    pack_type = pack_type.lower()

    # Check if pack exists
    if pack_type not in ["low", "common", "rare", "legendary"]:
        return await ctx.send("❌ Pack mawjoudech.")

    # Load prices
    PACK_PRICES = {
        "low": 500,
        "common": 1500,
        "rare": 3000,
        "legendary": 7000
    }

    # Load user data
    users = read_json("users.json")
    user_id = str(ctx.author.id)

    if user_id not in users:
        users[user_id] = {"coins": 0, "cards": []}

    user_coins = users[user_id]["coins"]
    price = PACK_PRICES[pack_type]

    # Check money
    if user_coins < price:
        return await ctx.send(f"❌ Ma 3andekch flous! T7eb {price} coins.")

    # Load cards
    data = read_json("cards.json")
    players = data["players"]

    # Filter players by rarity
    filtered = []
    for key in players:
        pl = players[key]
        if pl.get("drop") == True and pl.get("rarity") == pack_type:
            filtered.append({"name": key, "rating": pl["rating"]})

    if not filtered:
        return await ctx.send("❌ Ma fama hata player f hedha pack.")

    # ANIMATION
    msg = await ctx.send("📦 Na7al fel pack... 🎁")
    await asyncio.sleep(1.2)
    await msg.edit(content="✨ Na5tar fel player...")
    await asyncio.sleep(1.2)

    # Pick random player
    card = random.choice(filtered)
    pl = players[card["name"]]

    # Build embed
    embed = discord.Embed(
        title=f"🎉 You got {pl['name']}!",
        description=f"⭐ Rating: **{pl['rating']}**\n🎮 Rarity: **{pl['rarity']}**",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=pl["image"])

    # Remove user coins
    users[user_id]["coins"] -= price

    # Add card
    users[user_id]["cards"].append(pl["name"])

    # Save
    save_json("users.json", users)

    # Final message
    await msg.edit(content="", embed=embed)


def get_pack_type(overall):
    if overall < 76:
        return "low"
    elif 77 <= overall <= 83:
        return "common"
    elif 84 <= overall <= 87:
        return "rare"
    else:
        return "legendary"
PACK_PRICES = {
    "low": 500,
    "common": 1500,
    "rare": 3000,
    "legendary": 7000
}

PACK_NAMES = {
    "low": "Low Pack",
    "common": "Common Pack",
    "rare": "Rare Pack",
    "legendary": "Legendary Pack"
}





# ===========================
#   RUN BOT
# ===========================
bot.run("MTQzNDU0ODE1NTUxNjU4ODAzMg.GnHr6M.Uj9kNfbIm13vUx_W2bzwscxLdxMop-CXSPBCxg")
