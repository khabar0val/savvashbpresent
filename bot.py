import discord
import config

from discord import utils
from loguru import logger

intents = discord.Intents.all()
intents.members = True

logger.add('bot_logs.log', format = "{time} {level} {message}", level = "WARNING", rotation = "1 week", compression = "zip")

class MyClient(discord.Client):
	async def on_ready(self):
		try:
			print("Logged on as {0}!".format(self.user))

		except:
			logger.warning("WARNING with on_ready")
			logger.error("ERROR with on_ready")
			logger.critical("CRITICAL with on_ready")

	async def on_raw_reaction_add(self, payload):
		channel = self.get_channel(payload.channel_id)
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

	async def on_raw_reaction_remove(self, payload):
		channel = self.get_channel(payload.channel_id)
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

	client = discord.Client(intents=intents)

# RUN

client = MyClient(intents=discord.Intents.all())
client.run(config.TOKEN)