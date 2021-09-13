from bs4 import BeautifulSoup

#uses set to eliminate duplicates
items = set()
f = open('Tarkov_Market.txt', 'r', encoding='utf-8')
soup = BeautifulSoup(f.read(), 'html.parser')

data = soup.find_all('a', {"class": ""}, href=True)
#finds all hyperlinks
for i in data:
  if i['href'][:6] == "/item/":
    items.add(i['href'])
    print(i['href'])

#writes all links to "extensions.txt"
with open('extensions.txt', 'w', encoding='utf-8') as f:
  for i in items:
      f.write(i+'\n')
