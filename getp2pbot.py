import os
import re
import requests
import discord
from discord.ext import commands
from lxml import html

# Add the bot:
# https://discord.com/api/oauth2/authorize?client_id=866933457967513630&permissions=2147585024&scope=bot

# Setting Up
token = '*** YOUR TOKEN ***'
bot = commands.Bot(command_prefix='/')

@bot.command()
async def rutor(ctx, *args):
	regex = re.compile(r'\'([\wА-Яа-я\s]+)\'\s*?(\d+)*$')
	parsed_args = regex.match(' '.join(args))
	query = parsed_args.group(1)
	try:
		rownum = int(parsed_args.group(2))
	except TypeError:
		rownum = 0

	page = requests.get(f'http://rutor.info/search/{query}')
	page_tree = html.fromstring(page.content)
	table = page_tree.xpath('//div[@id="index"]')[0]
	rows = table.xpath('.//tr[@class="gai" or @class="tum"]')

	if rownum != 0:
		# The 2nd cell (index=1) is the main text
		# with a link to download and a title,
		# the 1st anchor (index=0) is a download link
		cells = rows[rownum-1].xpath('.//td')
		dllink = cells[1].xpath('.//a//@href')[0]

		linkparts = dllink.split('/')
		torrentid = int(linkparts[len(linkparts)-1])
		filename = f'{torrentid}.torrent'

		torrent = requests.get(dllink).content
		dlfile = open(filename, 'wb')
		dlfile.write(torrent)
		dlfile.close()

		hascomments = len(cells) > 4
		size = cells[3 if hascomments else 2].text
		title = cells[1].xpath('.//a')[2].text.strip().replace('\'', '')

		await ctx.send(
			f'`{torrentid}: {title} ({size})`',
			file=discord.File(filename)
			)
		os.remove(filename)
	else:
		choose_text = ''
		i = 1
		for row in rows:
			if (i > 10):
				break
			# The 3rd anchor (index=2) in the 2nd cell (index=1) is a title,
			# the 4th cell (index=3) contains the size of a film
			cells = row.xpath('.//td')
			maincell = cells[1]

			hascomments = len(cells) > 4
			size = cells[3 if hascomments else 2].text
			title = maincell.xpath('.//a')[2].text.strip().replace('\'', '')

			choose_text += f'${i} {title}  \'{size}\'\n'
			i += 1
		await ctx.send(f'Choose torrent:```bash\n{choose_text}```')

# Starting
bot.run(token)
