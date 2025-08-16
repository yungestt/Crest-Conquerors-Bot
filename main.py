from disnake import ui
import os
from disnake.ext import commands
from disnake import Member
from dotenv import load_dotenv
import disnake
import motor.motor_asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

intents = disnake.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI) if MONGO_URI else None
db = mongo_client['yung-bot'] if mongo_client else None
bot.db = db

# START

@bot.event
async def on_ready():
	print(f"Бот {bot.user} запущен!")
	if mongo_client:
		try:
			await mongo_client.admin.command('ping')
			print("MongoDB подключен!")
		except Exception as e:
			print(f"Ошибка подключения к MongoDB: {e}")
	else:
		print("MongoDB URI не найден в .env")

# HELP

@bot.slash_command(name="help", description="Показать справку по командам")
async def help_command(inter: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(
        description=(
            "# Справка по командам\n"
            "### Crest Conquerors Bot\n\n"
            "ㅤㅤㅤㅤ  ㅤㅤㅤㅤ**Основные команды**\n"
            "- **`/help`** — Вывести данное справочное сообщение\n"
            "- **`/info`** — Отобразить сведения о системе поинтов, способах заработка и другой информации\n"
            "- **`/inventory [user]`** — Просмотр баланса и списка приобретённых предметов (своего или чужого)\n"
            "- **`/leaderboard`** — Таблица лидеров по количеству поинтов\n"
            "- **`/buy [name]`** — Купить предмет в магазине\n"
            "- **`/pay [user] [amount]`** — Передать поинты другому пользователю\n"
            "- **`/shop`** — Открыть витрину магазина\n\n"
            "ㅤㅤㅤㅤㅤㅤ  ㅤ**Административные команды**\n"
            "- **`/add-points user [amount]`** — Начислить поинты пользователю\n"
            "- **`/remove-points user [amount]`** — Отнять поинты у пользователя\n"
            "- **`/add-item [name] [amount] [class name]`** — Добавить предмет в магазин\n"
            "- **`/remove-item [name]`** — Удалить предмет из магазина"
        ),
        color=0x00b0f4
    )

    embed.set_footer(text="Crest Conquerors")

    await inter.response.send_message(embed=embed)

# INFO

@bot.slash_command(name="info", description="Информация о системе поинтов")
async def info_points(inter):
	if db is not None:
		await db.users.update_one(
			{"user_id": str(inter.author.id)},
			{"$setOnInsert": {"user_id": str(inter.author.id), "points": 0}},
			upsert=True
		)
	await inter.response.defer()
	embed1 = disnake.Embed(
		title="Что такое поинты?",
		color=disnake.Color.blue(),
		description="Поинты — внутренняя валюта Crest Conquerors. Это уникальный коэффициент, благодаря которому можно **приобретать, обменивать, накапливать и делиться**. Система поинтов создана для стимулирования активности, мотивации участников и расширения возможностей игрового процесса. Это дополнительная внутренняя экономика, подчёркивающая индивидуальность проекта."
	)

	embed2 = disnake.Embed(
		title="Как получить поинты?",
		color=disnake.Color.from_rgb(173, 216, 230)
	)
	embed2.add_field(
		name="1. Участие в активностях проекта",
		value="**1.1** События (Events) — внутрисерверные активности, в которых команда выполняет миссии, ставят рекорды или достигают определённых целей. За успешное прохождение или выполнение условий полагается награда в виде поинтов. Размер награды зависит от сложности и условий конкретного события.\n"
			  "**1.1.1** Дополнительные поощрения выдаются участникам, которые проявили активность, внесли весомый вклад, оказывали помощь команде или показали упорство.\n"
			  "**1.2** Конкурсы — периодически на сервере проходят розыгрыши, главным призом в которых часто являются поинты.\n"
			  "**1.3** Gamenights — неформальные вечерние игровые собрания. За участие и время можно получить поинты.\n"
			  "**1.4** Турниры — победа и призовые места часто вознаграждаются поинтами.\n"
			  "**1.5** Проведение машин — игроки, участвующие до самого конца, получают награду аналогично событиям.",
		inline=False
	)
	embed2.add_field(
		name="2. Помощь проекту и активная вовлечённость",
		value="**2.1** Одобренные идеи, предложения и улучшения, которые делают проект лучше.\n"
			  "**2.2** Жалобы на нарушителей, помощь в поддержании порядка.\n"
			  "**2.3** Исправление ошибок, недочётов в текстах, дополнения и корректировки.",
		inline=False
	)
	embed2.add_field(
		name="3. Выполнение квестов и заданий.",
		value="**3.1** На сервере может присутствовать система квестов, ачивок и заданий, позволяющая получать поинты дополнительно.",
		inline=False
	)
	embed2.add_field(
		name="4. Поддержка сервера",
		value="**4.1** Серверные бусты — за буст предоставляется бустер пак в котором присутствует валюта. При 2 и более бустах начисления удваиваются.\n"
			  "**4.2** Финансовая поддержка — донатеры также получают поинты в знак благодарности, помимо возможных других привилегий.",
		inline=False
	)
	embed2.add_field(
		name="5. Работа в составе проекта",
		value="**5.1** Менеджеры, модераторы, организаторы, разработчики и весь персонал — получают заработок в поинтах за проделанную работу, проведённые мероприятия и вклад в развитие.\n"
			  "**5.2** Сотрудничество, партнёрства и взаимодействие с другими проектами также могут быть вознаграждены.",
		inline=False
	)
	embed2.set_footer(text="Спасибо, что поддерживаете проект и участвуете в развитии нашей уникальной экономики.\nCrest Conquerors")

	await inter.edit_original_response(embeds=[embed1, embed2])


ALLOWED_ROLE_IDS = [1380233165955928146, 1087034835534618793, 1290692530999918666, 1087034835534618792, 1281910079192563785, 1108767709648392243] # 1. trailblazer 2. commander 3. strategist 4. protector 5. researcher 6. pathfinder

def has_allowed_role(ctx):
	if ctx.author.guild_permissions.administrator:
		return True
	user_roles = [role.id for role in ctx.author.roles]
	return any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles)

# INVENTORY

@bot.slash_command(name="inventory", description="Показать баланс пользователя и предметы")
async def inventory(inter, name: str = None):
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if not name:
		user_id = str(inter.author.id)
		display_name = inter.author.display_name
	else:
		member = None
		for m in inter.guild.members:
			if m.display_name.lower() == name.lower():
				member = m
				break
		if member:
			user_id = str(member.id)
			display_name = member.display_name
		else:
			embed = disnake.Embed(description=f"У пользователя с именем '{name}' **0** поинтов.", color=disnake.Color.blue())
			await inter.response.send_message(embed=embed)
			return
	user = await db.users.find_one({"user_id": user_id})
	points = user["points"] if user else 0
	items = user.get("items", []) if user else []
	if items:
		items_str = "\n".join(f"- {item}" for item in items)
		desc = f"У пользователя {display_name} **{points}** поинтов.\n\n**Предметы:**\n{items_str}"
	else:
		desc = f"У пользователя {display_name} **{points}** поинтов.\n\n**Предметов нет.**"
	embed = disnake.Embed(description=desc, color=disnake.Color.blue())
	await inter.response.send_message(embed=embed)

# LEADERBOARD

class LeaderboardView(ui.View):
	def __init__(self, entries, per_page=6):
		super().__init__(timeout=60)
		self.entries = entries
		self.per_page = per_page
		self.page = 0
		self.max_page = max(0, (len(entries) - 1) // per_page)
		self.message = None

	def get_embed(self):
		embed = disnake.Embed(
			title=f"Топ по поинтам (стр. {self.page+1}/{self.max_page+1})",
			color=disnake.Color.blue()
		)
		start = self.page * self.per_page
		end = start + self.per_page
		page_entries = self.entries[start:end]
		for idx, entry in enumerate(page_entries, start=self.page * self.per_page + 1):
			embed.add_field(
				name=f"#{idx} {entry['name']}",
				value=f"Поинты: {entry['points']}",
				inline=False
			)
		if not page_entries:
			embed.description = "Нет данных."
		return embed


	@ui.button(label="⬅️", style=disnake.ButtonStyle.primary)
	async def prev_page(self, button: ui.Button, inter: disnake.MessageInteraction):
		if inter.author.id != inter.message.interaction.user.id:
			await inter.response.send_message(embed=self.get_embed(), ephemeral=True)
			return
		if self.page > 0:
			self.page -= 1
			await inter.response.edit_message(embed=self.get_embed(), view=self)
		else:
			await inter.response.defer()

	@ui.button(label="➡️", style=disnake.ButtonStyle.primary)
	async def next_page(self, button: ui.Button, inter: disnake.MessageInteraction):
		if inter.author.id != inter.message.interaction.user.id:
			await inter.response.send_message(embed=self.get_embed(), ephemeral=True)
			return
		if self.page < self.max_page:
			self.page += 1
			await inter.response.edit_message(embed=self.get_embed(), view=self)
		else:
			await inter.response.defer()


@bot.slash_command(name="leaderboard", description="Топ пользователей по количеству поинтам")
async def leaderboard(inter):
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.red())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	await inter.response.defer()
	users = await db.users.find().to_list(length=1000)
	members = {str(m.id): m.display_name for m in inter.guild.members}
	entries = []
	for user in users:
		points = user.get("points", 0)
		if points > 0:
			name = members.get(user["user_id"], f"ID: {user['user_id']}")
			entries.append({"name": name, "points": points})
	entries.sort(key=lambda x: x["points"], reverse=True)
	view = LeaderboardView(entries)
	await inter.edit_original_response(embed=view.get_embed(), view=view)

# SHOP

class ShopView(ui.View):
	def __init__(self, items, tag, tags, page=0, per_page=7, author_id=None):
		super().__init__(timeout=60)
		self.items = items
		self.tag = tag
		self.tags = tags
		self.page = page
		self.per_page = per_page
		self.max_page = max(0, (len(items) - 1) // per_page)
		self.author_id = author_id
		self.add_item(ShopSelect(tags, tag))
		if self.max_page > 0:
			self.add_item(ShopPrevButton())
			self.add_item(ShopNextButton())

	def get_embed(self):
		embed = disnake.Embed(
			title=f"Магазин — {self.tag} (стр. {self.page+1}/{self.max_page+1})",
			color=disnake.Color.green()
		)
		start = self.page * self.per_page
		end = start + self.per_page
		page_items = self.items[start:end]
		if not page_items:
			embed.description = "Нет предметов в этом классе."
		for item in page_items:
			embed.add_field(
				name=f"{item['name']}",
				value=f"Цена: {item['price']} поинтов",
				inline=False
			)
		return embed

class ShopSelect(ui.StringSelect):
	def __init__(self, tags, current_tag):
		options = [disnake.SelectOption(label=tag, value=tag, default=(tag==current_tag)) for tag in tags]
		super().__init__(placeholder="Выберите класс предметов", options=options, custom_id="shop_select")

	async def callback(self, inter: disnake.MessageInteraction):
		view: ShopView = self.view
		if inter.author.id != view.author_id:
			await inter.response.send_message("Это меню не для вас!", ephemeral=True)
			return
		tag = self.values[0]
		all_items = await inter.bot.db["shop/docunets"].find({"tag": tag}).to_list(length=1000)
		tags = view.tags
		new_view = ShopView(all_items, tag, tags, page=0, author_id=view.author_id)
		await inter.response.edit_message(embed=new_view.get_embed(), view=new_view)

class ShopPrevButton(ui.Button):
	def __init__(self):
		super().__init__(label="⬅️", style=disnake.ButtonStyle.primary, custom_id="shop_prev")
	async def callback(self, inter: disnake.MessageInteraction):
		view: ShopView = self.view
		if inter.author.id != view.author_id:
			await inter.response.send_message("Это меню не для вас!", ephemeral=True)
			return
		if view.page > 0:
			view.page -= 1
			await inter.response.edit_message(embed=view.get_embed(), view=view)
		else:
			await inter.response.defer()

class ShopNextButton(ui.Button):
	def __init__(self):
		super().__init__(label="➡️", style=disnake.ButtonStyle.primary, custom_id="shop_next")
	async def callback(self, inter: disnake.MessageInteraction):
		view: ShopView = self.view
		if inter.author.id != view.author_id:
			await inter.response.send_message("Это меню не для вас!", ephemeral=True)
			return
		if view.page < view.max_page:
			view.page += 1
			await inter.response.edit_message(embed=view.get_embed(), view=view)
		else:
			await inter.response.defer()


class ShopWelcomeView(ui.View):
	def __init__(self, author_id, all_items, tags):
		super().__init__(timeout=60)
		self.author_id = author_id
		self.all_items = all_items
		self.tags = tags
		self.add_item(ShopOpenButton())

class ShopOpenButton(ui.Button):
	def __init__(self):
		super().__init__(label="Открыть магазин", style=disnake.ButtonStyle.success, custom_id="shop_open")
	async def callback(self, inter: disnake.MessageInteraction):
		view: ShopWelcomeView = self.view
		if inter.author.id != view.author_id:
			await inter.response.send_message("Это меню не для вас!", ephemeral=True)
			return
		tag = view.tags[0]
		items = [item for item in view.all_items if item.get("tag", "other") == tag]
		shop_view = ShopView(items, tag, view.tags, author_id=view.author_id)
		await inter.response.edit_message(embed=shop_view.get_embed(), view=shop_view)

@bot.slash_command(name="shop", description="Открыть магазин предметов")
async def shop_command(inter):
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.red())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	all_items = await db["shop/docunets"].find().to_list(length=1000)
	if not all_items:
		embed = disnake.Embed(description="В магазине нет предметов.", color=disnake.Color.green())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	tags = sorted(set(item.get("tag", "other") for item in all_items))
	welcome_embed = disnake.Embed(
		title="Магазин предметов",
		description=(
			"Добро пожаловать в магазин!\n\n"
			"Здесь вы можете выбрать класс предметов с помощью выпадающего меню.\n"
			"\n"
			"- Используйте меню для выбора класса.\n"
			"- Если предметов больше 7 — воспользуйтесь ⬅️ ➡️ кнопками для перелистывания страниц.\n"
			"\nНажмите кнопку ниже, чтобы открыть магазин."
		),
		color=disnake.Color.green()
	)
	view = ShopWelcomeView(inter.author.id, all_items, tags)
	await inter.response.send_message(embed=welcome_embed, view=view, ephemeral=False)

@bot.slash_command(name="buy", description="Приобрести предмет в магазине")
async def buy_item(inter, name: str):
    if db is None:
        embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    user_id = str(inter.author.id)
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        await db.users.insert_one({"user_id": user_id, "points": 0, "items": []})
        user = await db.users.find_one({"user_id": user_id})
    points = user.get("points", 0)
    items = user.get("items", [])
    item = await db["shop/docunets"].find_one({"name": name})
    if not item:
        embed = disnake.Embed(description=f"Предмет '{name}' не найден.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    price = item.get("price", 0)
    if points < price:
        embed = disnake.Embed(description=f"Недостаточно средств для покупки '{name}'. Нужно: **{price}**, у вас: **{points}**.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    if name in items:
        embed = disnake.Embed(description=f"У вас уже есть предмет '{name}'!.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    await db.users.update_one({"user_id": user_id}, {"$inc": {"points": -price}, "$push": {"items": name}})
    role_given = False
    role_error = None
    role_id_or_name = item.get("role")
    if role_id_or_name:
        guild = inter.guild
        role_obj = None
        try:
            role_obj = guild.get_role(int(role_id_or_name))
        except Exception:
            role_obj = None
        if not role_obj:
            role_obj = disnake.utils.get(guild.roles, name=role_id_or_name)
        if role_obj:
            try:
                await inter.author.add_roles(role_obj, reason=f"Покупка предмета '{name}' через магазин")
                role_given = True
            except Exception as e:
                role_error = str(e)
        else:
            role_error = f"Роль '{role_id_or_name}' не найдена."
    msg = f"Вы успешно купили '{name}' за **{price}** поинтов!"
    if role_given:
        msg += f"\nВам выдана роль: {role_obj.mention}"
    elif role_error:
        msg += f"\n(Роль не выдана: {role_error})"
    embed = disnake.Embed(description=msg, color=disnake.Color.green())
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="pay", description="Передать поинты другому пользователю")
async def pay_points(inter, member: disnake.Member, points: int):
	if member.id == inter.author.id:
		embed = disnake.Embed(description="Нельзя передавать поинты самому себе.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	sender_id = str(inter.author.id)
	receiver_id = str(member.id)
	sender = await db.users.find_one({"user_id": sender_id})
	receiver = await db.users.find_one({"user_id": receiver_id})
	if not sender or sender.get("points", 0) < points:
		embed = disnake.Embed(description="Недостаточно поинтов для перевода.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if not receiver:
		await db.users.insert_one({"user_id": receiver_id, "points": points})
	else:
		await db.users.update_one({"user_id": receiver_id}, {"$inc": {"points": points}})
	await db.users.update_one({"user_id": sender_id}, {"$inc": {"points": -points}})
	embed = disnake.Embed(description=f"Вы передали **{points}** поинтов пользователю {member.mention}!", color=disnake.Color.blue())
	await inter.response.send_message(embed=embed)

# ADMINS
# POINTS

@bot.slash_command(name="add_points", description="Выдать поинты пользователю")
async def add_points_slash(inter, member: disnake.Member, points: int = 1):
	if not (inter.author.guild_permissions.administrator or any(role.id in ALLOWED_ROLE_IDS for role in inter.author.roles)):
		embed = disnake.Embed(description="У вас нет прав для использования этой команды.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	user_id = str(member.id)
	user = await db.users.find_one({"user_id": user_id})
	if user:
		await db.users.update_one({"user_id": user_id}, {"$inc": {"points": points}})
		embed = disnake.Embed(description=f"Пользователю {member.mention} добавлено **{points}** поинтов!", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed)
	else:
		await db.users.insert_one({"user_id": user_id, "points": points})
		embed = disnake.Embed(description=f"У пользователя {member.mention} **0** поинтов.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed)


@bot.slash_command(name="remove_points", description="Отнять поинты у пользователя")
async def remove_points_slash(inter, member: disnake.Member, points: int = 1):
	if not (inter.author.guild_permissions.administrator or any(role.id in ALLOWED_ROLE_IDS for role in inter.author.roles)):
		embed = disnake.Embed(description="У вас нет прав для использования этой команды.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	user_id = str(member.id)
	user = await db.users.find_one({"user_id": user_id})
	if user:
		current_points = user.get("points", 0)
		remove = min(abs(points), current_points)
		await db.users.update_one({"user_id": user_id}, {"$inc": {"points": -remove}})
		embed = disnake.Embed(description=f"У пользователя {member.mention} успешно отнято **{remove}** поинтов!", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed)
	else:
		await db.users.insert_one({"user_id": user_id, "points": 0})
		embed = disnake.Embed(description=f"У пользователя {member.mention} **0** поинтов.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed)

# ITEMS

@bot.slash_command(name="add_item", description="Добавить предмет в магазин")
async def add_item(inter, name: str, price: int, tag: str, role: str = None):
    if not (inter.author.guild_permissions.administrator or any(role.id in ALLOWED_ROLE_IDS for role in inter.author.roles)):
        embed = disnake.Embed(description="У вас нет прав для использования этой команды.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    if db is None:
        embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    item = await db["shop/docunets"].find_one({"name": name})
    if item:
        embed = disnake.Embed(description=f"Предмет '{name}' уже существует.", color=disnake.Color.blue())
        await inter.response.send_message(embed=embed, ephemeral=True)
        return
    doc = {"name": name, "price": price, "tag": tag}
    if role:
        doc["role"] = role
    await db["shop/docunets"].insert_one(doc)
    role_text = f" (Роль: {role})" if role else ""
    embed = disnake.Embed(description=f"Предмет '{name}' успешно добавлен в магазин за **{price}** поинтов! (Класс: {tag}){role_text}", color=disnake.Color.blue())
    await inter.response.send_message(embed=embed)

@bot.slash_command(name="remove_item", description="Удалить предмет из магазина")
async def remove_item(inter, name: str):
	if not (inter.author.guild_permissions.administrator or any(role.id in ALLOWED_ROLE_IDS for role in inter.author.roles)):
		embed = disnake.Embed(description="У вас нет прав для использования этой команды.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	if db is None:
		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
		await inter.response.send_message(embed=embed, ephemeral=True)
		return
	result = await db["shop/docunets"].delete_one({"name": name})
	if result.deleted_count:
		embed = disnake.Embed(description=f"Предмет '{name}' удалён из магазина!", color=disnake.Color.blue())
	else:
		embed = disnake.Embed(description=f"Предмет '{name}' не найден в магазине.", color=disnake.Color.blue())
	await inter.response.send_message(embed=embed)

# REMOVE_MEMBER

# @bot.slash_command(name="remove_member", description="Удалить пользователя из базы")
# async def remove_member_slash(inter, member: disnake.Member):
# 	if not (inter.author.guild_permissions.administrator or any(role.id in ALLOWED_ROLE_IDS for role in inter.author.roles)):
# 		embed = disnake.Embed(description="У вас нет прав для использования этой команды.", color=disnake.Color.blue())
# 		await inter.response.send_message(embed=embed, ephemeral=True)
# 		return
# 	if db is None:
# 		embed = disnake.Embed(description="База данных недоступна.", color=disnake.Color.blue())
# 		await inter.response.send_message(embed=embed, ephemeral=True)
# 		return
# 	user_id = str(member.id)
# 	result = await db.users.delete_one({"user_id": user_id})
# 	if result.deleted_count:
# 		embed = disnake.Embed(description=f"Пользователь {member.mention} успешно удалён из базы!", color=disnake.Color.blue())
# 	else:
# 		embed = disnake.Embed(description=f"Пользователь {member.mention} не найден в базе.", color=disnake.Color.blue())
# 	await inter.response.send_message(embed=embed)


if __name__ == "__main__":
	bot.run(TOKEN)
# For yung
# By CS:GO (.c.s.g.o.2)
