import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

#makes plt axes white
plt.rc('axes',edgecolor='white')

#command prefix 
client = commands.Bot(command_prefix = '!')

dic = {}
month_days = {"01":31, "02":28, "03":31, "04":30, "05":31, "06":30, "07":31, "08":31, "09":30, "10":30, "11":30, "12":31}
time_log = []

#fills dic with data and time log with times 
with open('data.txt', 'r', encoding='utf-8') as f:
    data = f.readlines()
    for line in data[:-1]:
        temp = line.split('|')
        #dic[key] = data entry for i in entries
        dic[temp[0]] = [i[:-1].strip("[]").replace("'","").split(", ") for i in temp[1:]]
    time_log = data[-1].split('|')

#prints "Bot is ready" when script is finshed debugging 
@client.event
async def on_ready():
    print("Bot is ready.")

#clear chat (10 messages unless specified)
@client.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)

#uses data from dic and matplotlib to create png file with graphed data
def info(item):
    now = datetime.now()
    cur_time = now.strftime("%D,%H:%M:%S")
    x_vals = []
    y_vals = []
    avg = 0
    out = 0
    for t in time_log:
        if int(cur_time[6:8]) - int(t[6:8]) > 1:
            out += 1
        elif int(cur_time[6:8]) - int(t[6:8]) == 1 and 12-int(t[0:2])+int(cur_time[0:2]) > 1:
            out += 1
        elif int(cur_time[6:8]) - int(t[6:8]) == 1 and 12-int(t[0:2])+int(cur_time[0:2]) == 1:
            if month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) > 1:
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) < int(cur_time[9:11]):
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) >= int(cur_time[9:11]):
                x_vals.append(int(t[9:11])-24-int(cur_time[9:11]))
        elif t[:2] != cur_time[:2]:
            if int(cur_time[:2]) - int(t[:2]) > 1:
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) > 1:
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) < int(cur_time[9:11]):
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) >= int(cur_time[9:11]):
                x_vals.append(int(t[9:11])-24-int(cur_time[9:11]))
        elif int(cur_time[3:5]) - int(t[3:5]) > 1:
            out += 1
        elif int(cur_time[3:5]) - int(t[3:5]) == 1 and int(t[9:11]) >= int(cur_time[9:11]):
            x_vals.append(int(t[9:11])-24-int(cur_time[9:11]))
        else:
            x_vals.append(int(t[9:11])-int(cur_time[9:11]))
    for i in range(out,len(dic[item])):
        a = int(dic[item][i][0].replace(",","")[:-1])
        y_vals.append(a)
        avg += a
    #average price (over 24 hour period)
    avg //= len(dic[item])
    colour = "white"
    x = np.array(x_vals)
    y = np.array(y_vals)
    #regression with numpy
    fig = plt.figure(None,[5,5])
    plt.rcParams['text.color'] = colour
    plt.rcParams['axes.labelcolor'] = colour
    plt.rcParams['xtick.color'] = colour
    plt.rcParams['ytick.color'] = colour
    plt.title('Prices')
    if out < len(dic[item]):
        m, b = np.polyfit(x, y, 1)
        plt.plot(x_vals,y_vals,'r.')
        plt.plot(x, m*x + b)
    plt.xlabel("Time")
    plt.savefig("cur.png",transparent=True)
    #returns average price with comma every 3 digits (starting from right) with rouble symbol at the end
    #mini-language for string formatting ({:,})
    return "{:,}".format(avg)+"₽", out == len(dic[item]), x_vals
    
pos = []
count = 0 

#price command
@client.command()
async def price(ctx, *, arg): #keyword-only argument
    global count 
    #if user has searched for item already and the user enters a number (corresponding to one of the options) 
    #this try statement is executed and the data for the specified item is returned 
    try:
        index = int(arg)-1
        item = pos[index]
        avg, out, times = info(item)
        file = discord.File("cur.png")
        length = 0 
        embed=discord.Embed(title=item.title())
        #checks if there is an image associated with the item
        if  "https://" in dic[item][-1][-1]:
            embed.set_thumbnail(url=dic[item][-1][-1])
            length = 5
        else:
            length = 4
        if out:
            embed.add_field(name="Price", value="NA", inline=True)
            embed.add_field(name="Price Per Slot", value="NA", inline=True)
            embed.add_field(name="24 Hour Average Price", value="NA", inline=False)
        else:
            embed.add_field(name="Price", value=dic[item][-1][0]+" ("+str(abs(times[-1]))+" hour(s) ago)", inline=True)
            embed.add_field(name="Price Per Slot", value=dic[item][-1][1], inline=True)
            embed.add_field(name="24 Hour Average Price", value=avg, inline=False)
        #if there is trader sell price available add it to the embed 
        if len(dic[item][-1]) == length:
            embed.add_field(name="Trader Buy", value=dic[item][-1][3], inline=True)
            embed.add_field(name="Trader Sell", value=dic[item][-1][2], inline=True)
        else:
            embed.add_field(name="Trader Buy", value=dic[item][-1][2], inline=True)
        #send to chat that command was typed in
        await ctx.send(embed=embed)
        await ctx.send(file=file)
        pos.clear()
        count = 0
    except:
        if count > 0:
            pos.clear()
        count += 1
        #splits search into all separate keywords
        item = arg.lower().split()
        #checks if each keyword in search is at the start of a word in each key 
        for key in dic:
            check = True
            temp = key.lower().split()
            for i in item:
                if not (i in temp or sum([t.startswith(i) for t in temp])>=1):
                    check = False
                    break
            if check:
                pos.append(key)
        #prints all results 
        for i in range(len(pos)):
            await ctx.send(str(i+1)+": "+pos[i])

client.run("")
