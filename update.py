import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time

def main():
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
            
    now = datetime.now()
    cur_time = now.strftime("%D,%H:%M:%S")

    out = 0
    #finds how many entries are out of date (older than 24 hours)
    for t in time_log:
        if int(cur_time[6:8]) - int(t[6:8]) > 1:
            out+=1
        elif int(cur_time[6:8]) - int(t[6:8]) == 1 and 12-int(t[0:2])+int(cur_time[0:2]) == 1:
            if month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) > 1:
                out += 1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) <= int(cur_time[9:11]):
                out += 1
        elif t[:2] != cur_time[:2]:
            if abs(int(cur_time[:2]) - int(t[:2])) > 1:
                out+=1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) > 1:
                out+=1
            elif month_days[t[:2]] - int(t[3:5]) + int(cur_time[3:5]) == 1 and int(t[9:11]) <= int(cur_time[9:11]):
                out+=1
        elif int(cur_time[3:5]) - int(t[3:5]) > 1:
            out+=1
        elif int(cur_time[3:5]) - int(t[3:5]) == 1 and int(t[9:11]) <= int(cur_time[9:11]):
            out+=1

    #deletes out of date entries
    time_log[:out] = []
    if out > 0:
        for key in dic:
            dic[key][:out] = []

    time_log.append(cur_time)

    with open('extensions.txt', 'r', encoding='utf-8') as f:
        #"line" represents 1 extension 
        for line in f.readlines():
            temp = line[:-1] #no \n
            page = requests.get('https://tarkov-market.com'+temp)
            soup = BeautifulSoup(page.content, 'html.parser')
            data = []
            #if link works execute try 
            try:
                #add item name to data
                data.append(temp[6:].replace("_"," "))
                #each block-item has a piece of information 
                for i in soup.find_all("div", {"class": "block-item"}):
                    temp_ = ""
                    #extarcts data from block-item
                    for j in i.find_all("div",{"class": ["bold","price"]}):
                        temp_+=(" ".join(j.getText().split())+" ")
                    if temp_!="":
                        data.append(temp_[:-1])
                #if there is an image associated with the item add to data
                try:
                    data.append(soup.find("img", {"class": "icon"})['src'])
                except:
                    pass
                #redundant piece of information 
                del data[3]
                print(data)
                name = data.pop(0)
                #adds data to key if key exists else creates new key 
                if name not in dic:
                    dic[name] = [data]
                else: 
                    dic[name].append(data)
            #if link does not work except is exected and appends link to "error,txt"
            except:
                with open('error.txt', 'a+', encoding='utf-8') as e:
                    e.write(temp+"\n")
                name = data[0]
                #adds blank entry to key if key exists else creates new key
                if name not in dic:
                    dic[name] = [['']]
                else: 
                    dic[name].append([''])
    
    #writes updated data to "data.txt"
    with open('data.txt', 'w', encoding='utf-8') as f:
        for key in dic:
            line = ""
            for i in dic[key]:
                line+='|'
                line+=str(i)
            f.write(key)
            f.write(line+'\n')
        line = ""
        for time in time_log:
            line+=time
            line+='|'
        f.write(line.strip('|'))

        #name|[price,perslot,trader sell,trader buy]|[another entry]

#runs function every hour (time is not counted during ~15 min runtime)
main()
schedule.every(45).minutes.do(main)
while True:
    schedule.run_pending()
    time.sleep(1)
