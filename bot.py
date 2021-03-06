import os
import json
import discord
import config
import string
import sqlite3

from discord import utils
from loguru import logger

bot = discord.Client(intents=discord.Intents.all())

logger.add('bot_logs.log', format = "{time} {level} {message}", level = "WARNING", rotation = "1 week", compression = "zip")

@bot.event
async def on_ready():
	global base, cursor
	base = sqlite3.connect('bot.db')
	cursor = base.cursor()

	if base:
		print("Database has already connected...OK")

	try:
		print("Logged on!")

	except:
		logger.warning("WARNING with on_ready")
		logger.error("ERROR with on_ready")
		logger.critical("CRITICAL with on_ready")

@bot.event
async def on_member_join(member):
	await member.send('Привет! Я бот этого сервера!')

	for channel in bot.get_guild(member.guild.id).channels:
		if channel.name == 'основной' or 'general':
			await bot.get_channel(channel.id).send(f'{member}, добро пожаловать!')

@bot.event
async def on_member_remove(member):
	for channel in bot.get_guild(member.guild.id).channels:
		if channel.name == 'основной' or 'general':
			await bot.get_channel(channel.id).send(f'{member}, нам будет тебя не хватать!')

@bot.event
async def on_raw_reaction_add(payload):
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	member = utils.get(message.guild.members, id=payload.user_id)

	try:
		emoji = str(payload.emoji)
		role = utils.get(message.guild.roles, id=config.ROLES[emoji])

		if len([i for i in member.roles if i.id not in config.EXCROLES]) <= config.MAX_ROLES_PER_USER:
			await member.add_roles(role)
			print('[SUCCESS] User {0.display_name} has been granted with role {1.name}'.format(member, role))

		else:
			await message.remove_reaction(payload.emoji, member)
			print('[ERROR] Too many roles for user {0.display_name}' + emoji.format(member, role))

	except KeyError as e:
		print('[ERROR] KeyError, no role found for' + emoji)

	except Exception as e:
		print(repr(e))

		logger.warning("WARNING with on on_raw_reaction_add")
		logger.error("ERROR with on on_raw_reaction_add")
		logger.critical("CRITICAL with on on_raw_reaction_add")

@bot.event
async def on_raw_reaction_remove(payload):
	channel = bot.get_channel(payload.channel_id)
	message = await channel.fetch_message(payload.message_id)
	member = utils.get(message.guild.members, id=payload.user_id)

	try:
		emoji = str(payload.emoji)
		role = utils.get(message.guild.roles, id=config.ROLES[emoji])

		await member.remove_roles(role)
		print('[SUCCESS] Role {1.name} has been remove for user {0.display_name}'.format(member, role))

	except KeyError as e:
		print('[ERROR] KeyError, no role found for' + emoji)

	except Exception as e:
		print(repr(e))

		logger.warning("WARNING with on on_raw_reaction_remove")
		logger.error("ERROR with on on_raw_reaction_remove")
		logger.critical("CRITICAL with on on_raw_reaction_remove")

@bot.event
async def on_message(message):
	if 'как' and 'дела' in message.content.lower():
		await message.channel.send('Спасибо, всё отлично!')

	elif {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}.intersection(set(json.load(open('ban_words.json')))) != set():
		await message.channel.send(f'{message.author.mention}, да я смотрю тебе давно рот мылом не мыли... Это было первое предупреждение, после трех предупреждений тебя забанят!')
		await message.delete()

		name = message.guild.name

		base.execute('CREATE TABLE IF NOT EXISTS ban(user_id INT, count INT)'.format(name))
		base.commit()

		warning = cursor.execute('SELECT * FROM ban WHERE user_id = ?'.format(name), (message.author.id,)).fetchone()

		if warning == None:
			cursor.execute('INSERT INTO ban VALUES(?, ?)'.format(name), (message.author.id, 1))
			base.commit()

			await message.channel.send(f'{message.author.mention}, !!!')

		elif warning[1] == 1:
			cursor.execute('UPDATE ban SET count = ? WHERE user_id = ?'.format(name), (2, message.author.id))
			base.commit()

			await message.channel.send(f'{message.author.mention}, 2-ое предупреждение, на 3-ее вас забанят!')

		elif warning[1] == 2:
			cursor.execute('UPDATE ban SET count = ? WHERE user_id = ?'.format(name), (3, message.author.id))
			base.commit()

			await message.channel.send(f'{message.author.mention}, забанили за мат в группе!')
			await message.author.ban(reason='Нецензурные выражения')

# RUN
bot.run(config.TOKEN)