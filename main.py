import discord
from discord.ext import commands
from discord.ext.commands import *
import t
import json

#invite link https://discord.com/api/oauth2/authorize?client_id=861496737491189780&permissions=2147552416&scope=bot

prefix = 'cl!'
bot = commands.Bot(prefix)

max_rooms = 2

bot.remove_command('help')

@bot.event
async def on_guild_join(guild):
    bot_entry = await guild.audit_logs(action=discord.AuditLogAction.bot_add).flatten()
    await bot_entry[0].user.send("Use cl!commands in the server to get started!")

@bot.event
async def on_guild_remove(guild):
    with open('channels.json', 'r') as f:
        channels = json.load(f)
    with open('channels.json', 'w') as f:
        del channels[str(guild.id)]
        json.dump(channels, f, indent=4)
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    with open('rooms.json', 'w') as f:
        for room in rooms:
            del rooms[room][str(guild.id)]
        json.dump(rooms, f, indent=4)

@bot.event
async def on_message(message):
    if message.author != bot.user:
        if not str(message.content).startswith(prefix):
            msg = message.author.name + ': ' +  str(message.content)
            with open('channels.json', 'r') as channel_file:
                channels = json.load(channel_file)
            server_id = str(message.guild.id)
            room_id = channels[server_id][message.channel.name][0]
            with open('blacklist.json', 'r') as blacklist_file:
                bl = json.load(blacklist_file)
            for u_id in bl[room_id]:
                if str(message.author.id) == u_id:
                    await bot.process_commands(message)
                    return
            with open('rooms.json', 'r') as rooms_file:
                rooms = json.load(rooms_file)
                for server in rooms[room_id]:
                    for channel in rooms[room_id][server]:
                        if channel != message.channel.name or int(server) != message.guild.id:
                            c = discord.utils.get(bot.get_guild(int(server)).channels, name=channel)
                            await c.send(msg)
    await bot.process_commands(message)

@bot.command()
@has_permissions(manage_guild=True)
async def link(ctx, room_name, password):
    with open('channels.json', 'r') as f:
        channels = json.load(f)
    with open('channels.json', 'w') as f:
        with open('room_ids.json', 'r') as rf:
            room_ids = json.load(rf)
        for room_id in room_ids:
            if str(room_id).startswith(room_name):
                if password == room_ids[room_name][0]:
                    try:
                        channels[str(ctx.guild.id)].update({ctx.channel.name:[room_name]})
                    except:
                        channels.update({str(ctx.guild.id):{ctx.channel.name:[room_name]}})
                    json.dump(channels, f, indent=4)
                    await ctx.channel.send('Successfully linked **' + room_name + '**')
                    with open('rooms.json', 'r') as rrf:
                        rooms = json.load(rrf)
                    with open('rooms.json', 'w') as rrf:
                        for server_id in rooms[room_name]:
                            if server_id == str(ctx.guild.id):
                                rooms[room_name][str(ctx.guild.id)].append(ctx.channel.name)
                                json.dump(rooms, rrf, indent=4)
                                return
                        rooms[room_name].update({str(ctx.guild.id):[ctx.channel.name]})
                        json.dump(rooms, rrf, indent=4)
                        return
                else:
                    json.dump(channels, f, indent=4)
                    await ctx.channel.send('Incorrect Room Password')
        await ctx.channel.send(room_name + ' does not exist')
        json.dump(channels, f, indent=4)

@bot.command()
@has_permissions(manage_guild=True)
async def unlink(ctx, room_name):
    with open('channels.json', 'r') as f:
        channels = json.load(f)
    with open('channels.json', 'w') as f:
        try:
            del channels[str(ctx.guild.id)][ctx.channel.name]
            await ctx.channel.send('Successfully unlinked **' + room_name + '**')
        except:
            await ctx.channel.send('You are not in **' + room_name + '**')
            json.dump(channels, f, indent=4)
            return
        json.dump(channels, f, indent=4)
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    with open('rooms.json', 'w') as f:
        try:
            del rooms[room_name][str(ctx.guild.id)]
            json.dump(rooms, f, indent=4)
            await ctx.channel.send('Unlinked from **' + room_name + '**')
            return
        except:
            pass
        await ctx.channel.send('You are not in **' + room_name + '**')

@bot.command()
@has_permissions(manage_guild=True)
async def create(ctx, room_name, password):
    special = False
    with open('room_ids.json', 'r') as f:
        room_ids = json.load(f)
    with open('room_ids.json', 'w') as f:
        for room_id in room_ids:
            if room_id.startswith(room_name):
                json.dump(room_ids, f, indent=4)
                await ctx.channel.send('**' + room_name + '** already exists')
                return
        with open('specialusers.json', 'r') as sf:
            special_users = json.load(sf)
            for user in special_users['users']:
                if user == str(ctx.message.author.id):
                    special = True
        with open('users.json', 'r') as uf:
            users = json.load(uf)
        with open('users.json', 'w') as uf:
            x = False
            for user in users:
                if user == str(ctx.message.author.id):
                    if users[user][0] < max_rooms or special:
                        users[user][0] += 1
                        x = True
                    else:
                        await ctx.channel.send('You already have ' + str(max_rooms) + ' channels\nDelete one to create another')
                        json.dump(users, uf, indent=4)
                        json.dump(room_ids, f, indent=4)
                        return
            if not x:
                users.update({str(ctx.message.author.id): [1]})
            json.dump(users, uf, indent=4)
        room_ids.update({room_name:[password, str(ctx.message.author.id)]})
        json.dump(room_ids, f, indent=4)
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    with open('rooms.json', 'w') as f:
        rooms.update({room_name:{}})
        json.dump(rooms, f, indent=4)
    with open('blacklist.json', 'r') as f:
        bl = json.load(f)
    with open('blacklist.json', 'w') as f:
        bl.update({room_name:["861496737491189780"]})
        json.dump(bl, f, indent=4)
    await ctx.channel.send('Successfully created **' + room_name + '**')

@bot.command()
@has_permissions(manage_guild=True)
async def delete(ctx, room_name, password):
    with open('room_ids.json', 'r') as f:
        room_ids = json.load(f)
        try:
            if room_ids[room_name][1] != str(ctx.message.author.id):
                await ctx.channel.send('**' + room_name + '** does not belong to you')
                return
        except:
            await ctx.channel.send('**' + room_name + '** does not exist')
            return
    with open('room_ids.json', 'w') as f:
        del room_ids[room_name]
        json.dump(room_ids, f, indent=4)
    with open('blacklist.json', 'r') as f:
        bl = json.load(f)
    with open('blacklist.json', 'w') as f:
        del bl[room_name]
        json.dump(bl, f, indent=4)
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    with open('rooms.json', 'w') as f:
        del rooms[room_name]
        json.dump(rooms, f, indent=4)
    with open('channels.json', 'r') as f:
        channels = json.load(f)
    with open('channels.json', 'w') as f:
        ret = []
        for server in channels:
            for channel in channels[server]:
                for room in channels[server][channel]:
                    if room == room_name:
                        ret.append([server, channel])
        for c in ret:
            del channels[c[0]][c[1]]
        json.dump(channels, f, indent=4)
    await ctx.channel.send('Successfully deleted **' + room_name + '**')

@bot.command()
@has_permissions(manage_guild=True)
async def blacklist(ctx, true, room, password, user: discord.User):
    with open('room_ids.json', 'r') as f:
        passwords = json.load(f)
    if password != passwords[room][0]:
        await ctx.channel.send('Incorrect password')
        return
    with open('blacklist.json', 'r') as f:
        bl = json.load(f)
    with open('blacklist.json', 'w') as f:
        try:
            for i in range(len(bl[room])):
                if bl[room][i] == str(user.id):
                    if true == 'off':
                        bl[room].pop(i)
                        await ctx.channel.send('**' + user.name + '** was unblacklisted from **' + room + '**')
                        json.dump(bl, f, indent=4)
                        return
                    else:
                        await ctx.channel.send('**' + user.name + '** is already blacklisted')
                        json.dump(bl, f, indent=4)
                        return
            if true == 'on':
                bl[room].append(str(user.id))
                await ctx.channel.send('**' + user.name + '** was blacklisted from **' + room + '**')
        except:
            await ctx.channel.send('Cannot find user, **' + user.name + '**')
        json.dump(bl, f, indent=4)

@bot.command()
@has_permissions(manage_guild=True)
async def commands(ctx):
    embed = discord.Embed(title="Commands:", color=0x738f96)
    embed.add_field(name="cl!link (Room Name) (Password)", value="-Links the current channel to a room", inline=False)
    embed.add_field(name="cl!unlink (Room Name)", value="-Unlinks a room from the current channel", inline=False)
    embed.add_field(name="cl!create (Room Name) (Password)", value="-Creates a room", inline=False)
    embed.add_field(name="cl!delete (Room Name) (Password)", value="-Deletes a room", inline=False)
    embed.add_field(name="cl!blacklist (on/off) (Room Name) (Password) (@user)", value="-Sets blacklist status for a user", inline=False)
    embed.set_footer(text="Keep in mind a channel can only have 1 room linked to it and you can only create up to 2 rooms.")
    await ctx.send(embed=embed)
bot.run(t.token)