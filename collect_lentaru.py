import feedparser,urllib,requests,re
from pymongo import MongoClient
from bs4 import BeautifulSoup
from time import strftime,localtime


DEBUG_MODE = True


def get_content(url):

	# месяцы для поиска в дате публикации

	months = ('января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', \
	'сентября', 'октября', 'ноября', 'декабря')
	
	text = ''
	
	# скачиваем страницу
    		
	page = requests.get(url)
	
	soup = BeautifulSoup(page.text, 'html.parser')
	
	# парсим элементы

	title = soup.find('h1').text.strip().replace(u'\xa0', u' ')
	
	for a in soup.find_all('p'): text += str(a).strip() + '\n\n' 
	
	# парсим дату
		
	date = soup.find('time', 'g-date').text.strip().replace(u'\xa0', u' ')
	
	for i, j in enumerate(months):

		if j in date: mon = '%02d' % (i+1)
	
	result = re.search('\d{4}',date)

	year = result.group(0)
	
	result = re.search('\s\d{1,2}\s',date)

	day = '%02d' % (int(result.group(0)))
	
	result = re.search('\d{2}\:\d{2}',date)

	time = result.group(0).strip()
		
	return({'id': url,\
	
			'date_pub': year+'-'+mon+'-'+day+' '+time+':00',
			
			'date_add': strftime("%Y-%m-%d %H:%M:%S", localtime()),
			
			'title': title, 
			
			'text': text})




url = 'https://lenta.ru/rss'

url_list = []

count_added = 0

count_exist = 0
    


feed = feedparser.parse(url)

for item in feed['entries']: url_list.append(item['id'])

client = MongoClient('mongodb://localhost:27017/')

with client:

	db = client.sitedb

	for url in url_list:
	
		if not db.sites.find_one({'id': url}):
	
			count_added += 1
			
			out = get_content(url)
			
			print('Добавление:',out['title'])
			
			db.sites.insert_one(out)
			
		else:
		
			count_exist += 1
	
	if DEBUG_MODE: count_total = db.sites.count_documents({})
		
	
if DEBUG_MODE:

	print('Добавлено:',count_added)
	
	print('Уже в базе:',count_exist)
	
	print('Всего в базе:',count_total)
			
