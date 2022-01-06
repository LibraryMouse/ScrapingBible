import bs4 as bs
import requests


base_url = "https://biblia.deon.pl/rozdzial.php?id="

for nr_podstrony in range(1,1991):
    url = base_url + str(nr_podstrony)
    with requests.get(url) as req:
        with open(f"raw-chapter{nr_podstrony}.html", "wb") as file:
            file.write(req.content)


calendar_url = "https://paulus.org.pl/czytania,details,"

for nr_podstrony in range(1,902):
    url = calendar_url + str(nr_podstrony)
    with requests.get(url) as req:
        with open(f"raw-calendar{nr_podstrony}.html", "wb") as file:
            file.write(req.content)


calendar_specials = "https://www.paulus.org.pl/czytania,uroczystosci"
calendar_specials_list = []

with requests.get(calendar_specials) as req:
    soup = bs.BeautifulSoup(req.content)
    for link in soup.find_all('a'):
        special_event = link.get('href')
        if special_event.startswith("u"):
            calendar_specials_list.append("https://www.paulus.org.pl/"+special_event)

nr = 1
for items in calendar_specials_list:
    with requests.get(items) as req:
        with open(f"raw-calendar-s{nr}.html", "wb") as file:
            file.write(req.content)
            nr +=1
