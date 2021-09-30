import discord
from discord.ext import commands
import datetime
import firebase_admin
from firebase_admin import credentials, db, storage
from PIL import ImageFont, ImageDraw, Image
import datetime
import cv2
import numpy as np
import os
import csv
import urllib.request
import io
import img2pdf
from uuid import uuid4
from urllib import parse, request
import re
import aiocron
import asyncio
from sheet import *
import toml

# Read configurations
config = toml.load('config.toml')

# Initialize Firebase app
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': config["database"]["firebaseDB"],
    'storageBucket': config["database"]["firebaseStorage"],
})

ref = db.reference('vitask')
tut_ref = ref.child('owasp')
new_ref = tut_ref.child('leaderboard-act2')
proj_ref = tut_ref.child('projects')
cert_ref = tut_ref.child('certificates')
ctf_ref = tut_ref.child('ctf')

bucket = storage.bucket()
blob = bucket.blob('dynamic certificate/')
counter = 0

bot = commands.Bot(command_prefix='!owasp ', description="The official OWASP VITCC Discord Bot.", activity=discord.Game(name="OWASP Leaderboard"))

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    await ctx.send(numOne + numTwo)

@bot.command(pass_context=True)
@commands.has_any_role("Board Member")
async def add_data(ctx, name, discord_name, rating=0, contributions=0):
    try:
        data = ref.child("owasp").child("leaderboard-act2").get()
        count = 0
        for i in data:
            # Check if already added
            if(data[i]["Name"].casefold()==name.casefold() and data[i]["Discord"].casefold()==discord_name.casefold()):
                count += 1
                embed = discord.Embed(title=f"{ctx.guild.name}", description="User already exists.", color=discord.Color.blue())
                embed.add_field(name="Name", value=f"{data[i]['Name']}")
                embed.add_field(name="Discord Name", value=f"{data[i]['Discord']}")
                embed.add_field(name="Rating", value=f"{data[i]['Rating']}")
                embed.add_field(name="Contributions", value=f"{data[i]['Contributions']}")
                embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

                await ctx.send(embed=embed)

        if(count==0):
            # Insert if not added already
            new_ref.push({
                'Rating': rating,
                'Name': name,
                'Discord': discord_name,
                'Contributions': contributions
            })
            embed = discord.Embed(title=f"{ctx.guild.name}", description="Added data to the OWASP Leaderboard.", color=discord.Color.blue())
            embed.add_field(name="Name", value=f"{name}")
            embed.add_field(name="Discord Name", value=f"{discord_name}")
            embed.add_field(name="Rating", value=f"{rating}")
            embed.add_field(name="Contributions", value=f"{contributions}")
            embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

            await ctx.send(embed=embed)

    except Exception as e:
        print(e)


@bot.command(pass_context=True)
@commands.has_any_role("Board Member")
async def update_data(ctx, name, discord_name, rating=0, contributions=0):
    try:
        data = ref.child("owasp").child("leaderboard-act2").get()
        count = 0
        for i in data:
            # Check if already added
            if(data[i]["Name"].casefold()==name.casefold() and data[i]["Discord"].casefold()==discord_name.casefold()):
                selector = ref.child("owasp").child("leaderboard-act2").child(i)
                selector.update({
                    'Rating': rating,
                    'Name': name,
                    'Discord': discord_name,
                    'Contributions': contributions
                })
                embed = discord.Embed(title=f"{ctx.guild.name}", description="Updated data to the OWASP Leaderboard.", color=discord.Color.blue())
                embed.add_field(name="Name", value=f"{name}")
                embed.add_field(name="Discord Name", value=f"{discord_name}")
                embed.add_field(name="Rating", value=f"{rating}")
                embed.add_field(name="Contributions", value=f"{contributions}")
                embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

                await ctx.send(embed=embed)

    except Exception as e:
        print(e)

@bot.command(pass_context=True)
@commands.has_any_role("Leaderboard")
async def contribution(ctx, name, discord_name, task):
    try:
        data = ref.child("owasp").child("leaderboard-act2").get()
        count = 0
        for i in data:
            # Check if already added
            if(data[i]["Name"].casefold()==name.casefold() and data[i]["Discord"].casefold()==discord_name.casefold()):
                selector = ref.child("owasp").child("leaderboard-act2").child(i).get()
                selector_update = ref.child("owasp").child("leaderboard-act2").child(i)
                points = 0
                if(task.casefold()=="pull request".casefold()):
                    points = 20
                elif(task.casefold()=="blog medium".casefold()):
                    points = 20
                elif(task.casefold()=="blog".casefold()):
                    points = 15
                elif(task.casefold()=="sm posting".casefold()):
                    points = 7
                elif(task.casefold()=="weekly work".casefold()):
                    points = 5
                elif(task.casefold()=="idea".casefold()):
                    points = 3
                elif(task.casefold()=="brochure".casefold()):
                    points = 10
                elif(task.casefold()=="news".casefold()):
                    points = 5
                elif(task.casefold()=="demos".casefold()):
                    points = 20
                elif(task.casefold()=="oc volunteer".casefold()):
                    points = 30
                elif(task.casefold()=="oc assigned".casefold()):
                    points = 20
                elif(task.casefold()=="oc no work".casefold()):
                    points = -10
                elif(task.casefold()=="oc manager".casefold()):
                    points = 50
                elif(task.casefold()=="wtf".casefold()):
                    points = 50
                elif(task.casefold()=="discord".casefold()):
                    points = 10
                elif(task.casefold()=="marketing".casefold()):
                    points = 2
                elif(task.casefold()=="mini project".casefold()):
                    points = 100
                elif(task.casefold()=="complete project".casefold()):
                    points = 200
                elif(task.casefold()=="promotion medium".casefold()):
                    points = 25
                elif(task.casefold()=="promotion large".casefold()):
                    points = 50

                rating = selector["Rating"]+points
                contributions = selector["Contributions"]+1
                selector_update.update({
                    'Rating': rating,
                    'Name': name,
                    'Discord': discord_name,
                    'Contributions': contributions
                })
                embed = discord.Embed(title=f"{ctx.guild.name}", description="Added contribution to the OWASP Leaderboard.", color=discord.Color.blue())
                embed.add_field(name="Name", value=f"{name}")
                embed.add_field(name="Discord Name", value=f"{discord_name}")
                embed.add_field(name="Rating", value=f"{rating}")
                embed.add_field(name="Contributions", value=f"{contributions}")
                embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

                await ctx.send(embed=embed)

    except Exception as e:
        print(e)


@bot.command()
async def fetch_data(ctx, name, discord_name):
    data = ref.child("owasp").child("leaderboard-act2").get()
    for i in data:
        if(data[i]["Name"].casefold()==name.casefold() and data[i]["Discord"].casefold()==discord_name.casefold()):
            embed = discord.Embed(title=f"{ctx.guild.name}", description="Fetched OWASP Leaderboard profile.", color=discord.Color.blue())
            embed.add_field(name="Name", value=f"{data[i]['Name']}")
            embed.add_field(name="Discord Name", value=f"{data[i]['Discord']}")
            embed.add_field(name="Rating", value=f"{data[i]['Rating']}")
            embed.add_field(name="Contributions", value=f"{data[i]['Contributions']}")
            embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

            await ctx.send(embed=embed)

#Sheet commands
@bot.command()
async def sheets(ctx, arg):
    if arg == "Technical":
        sheet_range = "Technical!a1:u23"

    elif arg == "Operations":
        sheet_range = "Operations!a1:u31"

    elif arg == "Design":
        sheet_range = "Design!a1:u11"

    elif arg == "Web-dev":
        sheet_range = "Web-dev!a1:u30"

    values = easy(sheet_range)
    #print(values)
    for i in values:
        name = i[0]
        discord_name = i[1]
        task = i[2]
        for j in range(int(i[3])):
            finale = "!owasp contribution " + name + " " + discord_name + " " + task
            await ctx.send(finale)
            await contribution(ctx, name, discord_name, task)


@bot.command()
async def cleanup(ctx,arg):
    if arg == "Technical":
        sheet_range = "Technical!C2:U"

    elif arg == "Operations":
        sheet_range = "Operations!C2:U"

    elif arg == "Design":
        sheet_range = "Design!C2:U"

    elif arg == "Web-dev":
        sheet_range = "Web-dev!C2:U"
    clear(sheet_range)

@bot.command()
async def fix_leaderboard(ctx):
    values = fix()
    for i in values:
        name = i[0]
        disc_name = i[1]
        points = i[2]
        contributions = i[3]
        finale = "!owasp update_data " + name + " " + disc_name + " " + points + " " + contributions
        await ctx.send(finale)
        await update_data(ctx, name, disc_name, int(points), int(contributions))

@bot.command()
async def delete_data(ctx, name, discord_name):
	for key, value in new_ref.get().items():
		if( value["Name"].casefold()==name.casefold() and value["Discord"].casefold()==discord_name.casefold() ):
			embed = discord.Embed(title=f"{ctx.guild.name}", description="Deleted data to the OWASP Leaderboard.", color=discord.Color.blue())
			embed.add_field(name="Name", value=f"{name}")
			embed.add_field(name="Discord Name", value=f"{discord_name}")
			embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")
			new_ref.child(key).set({})
			await ctx.send(embed=embed)

@bot.command()
async def delete_testing_data(ctx, username):
	for key, value in ctf_ref.get().items():
		if(value['username'].casefold() == username.casefold()):
			embed = discord.Embed(title=f"{ctx.guild.name}", description="Deleted testing data to the OWASP Leaderboard.", color=discord.Color.blue())
			embed.add_field(name="Name", value=f"{value['username']}")
			embed.add_field(name="emailid", value=f"{value['emailid']}")
			embed.add_field(name="isFile", value=f"False")
			embed.add_field(name="isRootflag", value=f"False")
			embed.add_field(name="isUserflag", value=f"False")
			embed.add_field(name="scores", value=f"0")
			ctf_ref.child(key).set({'emailid':value['emailid'], 'isFile': False, 'isRootflag': False, 'isUserflag' : False, 'scores' : 0, 'username' : value['username']})
			await ctx.send(embed=embed)

@bot.command()
async def get_email_data(ctx):
    done = []
    for key, value in ctf_ref.get().items():
        if value['emailid'] not in done:
            await ctx.send(value['emailid'])
            done.append(value['emailid'])
    await ctx.send("The whole list!")

@bot.command()
async def get_user_data(ctx, check):
	for key, value in ctf_ref.get().items():
		if value['emailid'].casefold() == check.casefold() or value['username'].casefold() == check.casefold():
			print(value)
			print(key)

@bot.command(pass_context=True)
@commands.has_any_role("Board Member")
async def add_project(ctx, project_name, username, repo_name, project_tag):
    try:
        data = ref.child("owasp").child("projects").get()
        count = 0
        for i in data:
            # Check if already added
            if(data[i]["Username"].casefold()==username.casefold() and data[i]["RepoName"].casefold()==repo_name.casefold()):
                count += 1
                embed = discord.Embed(title=f"{ctx.guild.name}", description="Project already exists.", color=discord.Color.blue())
                embed.add_field(name="Project Name", value=f"{data[i]['ProjectName']}")
                embed.add_field(name="Username", value=f"{data[i]['Username']}")
                embed.add_field(name="Repo Name", value=f"{data[i]['RepoName']}")
                embed.add_field(name="Project Tag", value=f"{data[i]['ProjectTag']}")
                embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

                await ctx.send(embed=embed)

        if(count==0):
            # Insert if not added already
            proj_ref.push({
                'ProjectName': project_name,
                'Username': username,
                'RepoName': repo_name,
                'ProjectTag': project_tag
            })
            embed = discord.Embed(title=f"{ctx.guild.name}", description="Added project to OWASP Projects.", color=discord.Color.blue())
            embed.add_field(name="Project Name", value=f"{project_name}")
            embed.add_field(name="Username", value=f"{username}")
            embed.add_field(name="Repo Name", value=f"{repo_name}")
            embed.add_field(name="Project Tag", value=f"{project_tag}")
            embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

            await ctx.send(embed=embed)

    except Exception as e:
        print(e)

@bot.command(pass_context=True)
@commands.has_any_role("Board Member")
async def add_certificate(ctx, name, discord_name, year):
    maincounter=0
    Fname = ''
    data = ref.child("owasp").child("leaderboard-act2").get()
    for i in data:
        if(data[i]["Name"].casefold()==name.casefold() and data[i]["Discord"].casefold()==discord_name.casefold()):
            Fname = name
            key = name.casefold()+"-"+discord_name.casefold()
            cert_ref.child(f'{key}').push({
                'Year':year,
            })
            embed = discord.Embed(title=f"{ctx.guild.name}", description="Certificate added.", color=discord.Color.blue())
            embed.add_field(name="Username", value=f"{name}")
            embed.add_field(name="Discord Name", value=f"{discord_name}")
            embed.add_field(name="Year", value=f"{year}")
            embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

            await ctx.send(embed=embed)
            maincounter=1
            break

    if maincounter==0:
        embed = discord.Embed(title=f"{ctx.guild.name}", description="Certificate NOT added.", color=discord.Color.blue())
        embed.add_field(name="Error", value=f"User not found. Make sure the real name and discord name is correct.")
        embed.set_thumbnail(url="https://owaspvit.com/assets/owasp-logo.png")

        await ctx.send(embed=embed)

    elif maincounter!=0:
        username = name.casefold()+"-"+discord_name.casefold()
        useryear = year
        blob = bucket.blob(f'dynamic certificate/{username}-{useryear}')
        url = "https://firebasestorage.googleapis.com/v0/b/vitask.appspot.com/o/Certificate.png?alt=media&token=a97843cf-e0da-4bd6-a5e7-3ee86d3e0bea"
        url_response = urllib.request.urlopen(url)
        img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        cv2_im_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im_rgb)
        new_token = uuid4()
        metadata  = {"firebaseStorageDownloadTokens": new_token}
        draw = ImageDraw.Draw(pil_im)
        font = ImageFont.truetype('botdata/poppins.ttf', 55)
        x = 625-(len(Fname)*13.6)
        draw.text(xy=(x,350),text=Fname,fill=(255,255,255),font=font)
        draw.text(xy=(775,565),text=year,fill=(255,255,255),font=font)
        img_bytes = io.BytesIO()
        pil_im.save(img_bytes, format = 'PNG')
        img_byte_arr = img_bytes.getvalue()

        blob.metadata = metadata
        blob.upload_from_string(img_byte_arr,content_type = 'image/png')
        url = blob.generate_signed_url(datetime.timedelta(seconds = 600), method = 'GET')

        await ctx.send(f'{url}')

# Events
@bot.event
async def on_ready():
    print('OWASP VITCC Bot v1.0')

@bot.listen()
async def on_message(message):
    if "owasp github" in message.content.lower():
        await message.channel.send('Our GitHub is https://github.com/owaspvit')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp landlord" in message.content.lower():
        await message.channel.send('My landlord is https://github.com/apratimshukla6')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp mailman" in message.content.lower():
        await message.channel.send('My mailman is https://github.com/princesinghr1')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp plumber" in message.content.lower():
        await message.channel.send('My plumber is https://arnavtripathy98.medium.com/')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp firefighter" in message.content.lower():
        await message.channel.send('My firefighter is https://medium.com/@lakshaybaheti1')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp carpenter" in message.content.lower():
        await message.channel.send('My carpenter is https://github.com/aakashratha1006')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp janitor" in message.content.lower():
        await message.channel.send('My janitor is https://github.com/MarkRaghav')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp electrician" in message.content.lower():
        await message.channel.send('My electrician is https://github.com/Swapnil0115')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp photographer" in message.content.lower():
        await message.channel.send('My photographer is https://github.com/ShubhamManna')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if "owasp website" in message.content.lower():
        await message.channel.send('Our Website is https://owaspvit.com')
        await bot.process_commands(message)

# Cron
@aiocron.crontab('0 0 * * 0')
async def five():
    ctx = bot.get_channel(config["bot"]["channel"])
    await sheets(ctx, 'Technical')
    await cleanup(ctx, 'Technical')

    await sheets(ctx, 'Operations')
    await cleanup(ctx, 'Operations')

    await sheets(ctx, 'Design')
    await cleanup(ctx, 'Design')

    await sheets(ctx, 'Web-dev')
    await cleanup(ctx, 'Web-dev')

bot.run(config["bot"]["token"])
