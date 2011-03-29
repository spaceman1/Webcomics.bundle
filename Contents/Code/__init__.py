from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import mimetypes
import re
import urlparse
import datetime

PLUGIN_PREFIX = '/photos/webcomics'
CACHE_1YEAR = 365 * CACHE_1DAY

kSingleArchive = 1
kMultiArchive = 2
kMultiAndMainArchive = 3
kWhileArchive = 4
kArchiveRangedIDs = 5

####################################################################################################  
  
def Start():
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, L('Webcomics'), 'icon-default.png', 'art-default.png')
	
	Plugin.AddViewGroup('_List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('_InfoList', viewMode='InfoList', mediaType='items')
		
	MediaContainer.viewGroup = '_List'
	MediaContainer.art = R('art-default.png')
	MediaContainer.title1 = L('Webcomics')
	comicList = list()
####################################################################################################

def MainMenu():
	dir = MediaContainer(title=L('Webcomics'), viewGroup='_InfoList')
	for handler, title, thumb, art, subtitle, summary in getComicList():
		dir.Append(Function(DirectoryItem(handler, title=title, thumb=R('icon-default.png'), art=R(art), summary=summary, subtitle=subtitle)))
	dir.Append(PrefsItem(title='Preferences', thumb=R('icon-prefs.png')))
	return dir

####################################################################################################

def CreatePrefs():
	Prefs.Add(id='oldestFirst', type='bool', default=True, label='Oldest comics first')

####################################################################################################  

def getComic(url, sender=None):
	urlEscaped = url.replace(' ', '%20')
#	if HTTP.__cache.has_key(urlEscaped):
#		return DataObject(HTTP.__cache[url]['Content'], mimetypes.guess_type(urlEscaped))
	return DataObject(HTTP.Request(urlEscaped, cacheTime=CACHE_1YEAR), mimetypes.guess_type(urlEscaped))

def getExtComic(url, sender=None):
	baseURL = '.'.join(url.split('.')[:-1])

	urls = list()
	for ext in ['png', 'gif', 'jpg', 'JPG']:
		newURL = baseURL + '.' + ext
#		if HTTP.__cache.has_key(newURL):
#			return DataObject(HTTP.__cache[newURL]['Content'], mimetypes.guess_type(newURL))
		urls.append(newURL)
		
	# here we have no cached copy
	for aURL in urls:
		img = HTTP.Request(aURL, cacheTime=CACHE_1YEAR)
		if img != None:
			return DataObject(HTTP.Request(aURL, cacheTime=CACHE_1YEAR), mimetypes.guess_type(url))

	return None
				
def getComicMime(url, mime, sender=None):
	return DataObject(HTTP.Request(url, cacheTime=CACHE_1YEAR), mime)

def getComicFromPage(url, xpath, sender=None):
	img = urlparse.urljoin(url, XML.ElementFromURL(url, True, cacheTime=CACHE_1YEAR).xpath(xpath)[0].get('src'))
	return getComic(img)

def getComicFromPageWithXPaths(url, xpaths, sender=None):
	page = XML.ElementFromURL(url, True, cacheTime=CACHE_1YEAR)
	for xpath in xpaths:
		imgs = page.xpath(xpath)
		if len(imgs) != 0:
#	    imgs = XML.ElementFromURL(XML.ElementFromURL(url, True).xpath(xpaths[1])[0].get('href'), True).xpath(xpaths[1])
			img = imgs[0].get('src')
			return getComic(img)

####################################################################################################

def AppleGeeks(sender):
	dirTitle = 'AppleGeeks 3.0'
	archiveURL = 'http://www.applegeeks.com/'
	archiveXPath = '//div[@id="comic"]/img'
	imgURL = 'http://www.applegeeks.com/comics/issue%i.jpg'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	lastID = XML.ElementFromURL(archiveURL, True).xpath(archiveXPath)[0].get('src').split('issue')[1].split('.')[0]
	for id in range(1, int(lastID)):
		title = str(id)
		comicURL = imgURL % id
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################  

def AppleGeeksLite(sender):
	dirTitle = 'AppleGeeks Lite'
	archiveURL = 'http://www.applegeeks.com/'
	archiveXPath = '//div[@id="comiclite"]/a/img'
	imgURL = 'http://www.applegeeks.com/lite/strips/aglite%i.jpg'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	lastID = XML.ElementFromURL(archiveURL, True).xpath(archiveXPath)[0].get('src').split('aglite')[1].split('.')[0]
	for id in range(1, int(lastID)):
		title = str(id)
		comicURL = imgURL % id
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir
	
	####################################################################################################  
	
def BetweenFailures(sender):
	# TODO: make progressive
	dirTitle = 'Between Failures'
	archiveURL = 'http://betweenfailures.com/archive-2/'
	archiveXPath = '//tr[@class="webcomic-archive-items"]/td/a'
	imgXPath = '//span[starts-with(@class, "webcomic-object")]/img'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	
	for item in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = item.text
		itemURL = item.get('href')
		dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=itemURL, xpath=imgXPath)), url=itemURL, xpath=imgXPath))
	if not Prefs.Get('oldestFirst'):
		dir.Reverse()
	
	return dir
		
####################################################################################################

def Catena(sender):
	archiveURL = 'http://catenamanor.com/%i'
	archiveXPath = '//img[@class="comicthumbnail"]'
	
	imgXPath = '//img[starts-with(@src, "http://catenamanor.com/comics/catena/")]'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=sender.itemTitle)
	
	for year in reversed(range(2003, datetime.datetime.now().year + 1)):
		for img in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			title = img.get('alt')
			comicURL =  'http://catenamanor.com/comics/' + img.get('src').split('/')[-1]
			dir.Append(PhotoItem(comicURL, title=title))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()

	return dir

####################################################################################################

def CtrlAltDel(sender):
	dirTitle = 'Ctrl+Alt+Del'
	archiveURL = 'http://www.cad-comic.com/cad/archive/%i'
	archiveXPath = '//div[@class = "post"]/a'
	pageXPath = '//img[contains(@src, "/comics/")]'
	base = 'http://www.cad-comic.com/'
	imgURL = 'http://www.cad-comic.com/comics/cad/%s.jpg'
	hasOldestFirst = False

	dir = MediaContainer(title1=dirTitle)

	for year in range(2002, datetime.datetime.now().year + 1):
		for comic in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			title = comic.text
			comicURL = urlparse.urljoin(base, comic.get('href'))
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=pageXPath)), url=comicURL, xpath=pageXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def CyanideAndHappiness(sender):
	dirTitle = 'Cyanide and Happiness'
	archiveURL = 'http://www.explosm.net/comics/archive/%i/'
	base = 'http://www.explosm.net/'
	archiveXPath = '//a[starts-with(@href, "/comics/")]'
	imgXPath = '//img[@alt="Cyanide and Happiness, a daily webcomic"]'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	holes = list()
	for movie in XML.ElementFromURL('http://www.explosm.net/movies/', True).xpath('//a[starts-with(@href, "/comics/")]'):
		holes.append(movie.get('href'))
	
	for year in range(2005, datetime.datetime.now().year + 1):
		for comic in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			href = comic.get('href')
			if href.startswith('/comics/archive'): continue
			if href in holes: continue
			comicURL = urlparse.urljoin(base, href)
			title = comicURL.split('/')[-2]
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
		if Prefs.Get('oldestFirst') != hasOldestFirst:
			dir.Reverse()
	return dir

####################################################################################################

def DanAndMab(sender):
	dirTitle = "Dan and Mab's Furry Adventures"
	archiveURL = 'http://www.missmab.com/arch.php'
	archiveXPath = '//a[starts-with(text(), "Chapter")]'
	archive2XPath = '//a[starts-with(@href, "Vol")]'
	imgURL = 'http://www.missmab.com/Comics/Vol%s.jpg'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	cIndex = 1
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		for img in XML.ElementFromURL(urlparse.urljoin(archiveURL, archive.get('href')), True).xpath(archive2XPath):
			title = img.text
			if cIndex < 7:
				comicURL = imgURL % str(cIndex).zfill(2)
				cIndex += 1
			else:
				comicURL = imgURL % img.get('href').split('Vol_')[1].split('.')[0].lstrip('0').zfill(2)
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def DrMcNinja(sender):
	comicLengths = [14, 22, 45, 48, 42, 52, 0, 12, 49, 34, 56, 56, 5, 47, 72, 73, 5]
	archiveURL = 'http://drmcninja.com/issues/'
	archiveXPath = '//div[@class="serieslist-box"]'
	archive2XPath = '//a[@class = "prepostnav-next"]'
	imgXPath = '//div[@id="comic"]/img'
	hasOldestFirst = True
	lastPage = Dict.Get('DrMcNinja.lastPage')
	cacheTime = CACHE_1YEAR
	dir = MediaContainer(title1=sender.itemTitle)
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		storyTitle = archive.xpath('.//h2/a')[0].text
		pageURL = archive.xpath('.//h2/a')[0].get('href')
		archiveIndex = int(pageURL.split('/')[-1].split('p')[0])
		archiveBase = 'p'.join(pageURL.split('p')[:-1]) + 'p'
		if archiveIndex < len(comicLengths):
			for pageIndex in range(1, comicLengths[archiveIndex] + 1):
				title = '%s page %s' % (storyTitle, str(pageIndex).zfill(2))
				comicURL = archiveBase+str(pageIndex)
				dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
		else:
			if pageURL == lastPage:
				cacheTime = 3600
			page = XML.ElementFromURL(pageURL, True, cacheTime=cacheTime)
			pageIndex = 1 
			hasMore = True
			while hasMore:
				title = '%s page %s' % (storyTitle, str(pageIndex).zfill(2))
				comicURL = page.xpath(imgXPath)[0].get('src')
				dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
				nextPage = page.xpath(archive2XPath)
				if len(nextPage) == 0:
					hasMore = False
				else:
					pageURL = nextPage[0].get('href')
					if pageURL == lastPage:
						cacheTime = 3600
					page = XML.ElementFromURL(pageURL, True, cacheTime=cacheTime)
					pageIndex += 1
	Dict.Set('DrMcNinja.lastPage', lastPage)
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def DominicDeegan(sender):
	holes = [1237, 1242, 1247, 1256, 1270, 1293, 1320, 1340, 1342, 1357, 1369, 1414, 1415, 1530, 1482, 1582, 1583, 1593, 1629, 1645, 1651, 1704, 1713, 1828, 1882, 2080, 2103, 2144, 2201, 2225, 2226, 2294, 2325, 2333, 2335, 2360, 2385]
	dirTitle = 'Dominic Deegan'
	archiveURL = 'http://www.dominic-deegan.com/archive.php?year=%i'
	
	archiveXPath = '//a[starts-with(@href, "view.php?")]'
	imgURL = 'http://www.dominic-deegan.com/comics/%s%s%s.gif'
	
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	for year in range(2002, datetime.datetime.now().year + 1):
		for comic in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			href = comic.get('href')
			year, month, day = re.search(r'(\d{4})-(\d\d)-(\d\d)', href).groups()
			title = '%s-%s-%s' % (year, month, day)
			comicURL = imgURL % (year, month, day)
			dir.Append(PhotoItem(comicURL, title=title, thumb=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def DuelingAnalogs(sender):
	dirTitle = 'Dueling Analogs'
	archiveURL = 'http://www.duelinganalogs.com/archive/?archive_year=%i'
	archiveXPath = '//ul[@class="monthly"]/li/a'
	imgXPath = '//div[@id="comic"]/img'
	hasOldestFirst = True
	holes = set(['super-happy-new-year-world', 'scribblenots', 'the-kojima-code', 'istalkher', 'pong-solitaire', 'super-mario-bros-leftovers', 'dear-final-fantasy-xiii', 'mega-man-10-easy-peasy-lemon-squeezy'])
	dir = MediaContainer(title1=dirTitle)
	for year in range(2005, datetime.datetime.now().year + 1):
		for img in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			title = img.text
			comicURL = img.get('href')
			if comicURL.split('/')[-2] in holes: continue
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def EerieCuties(sender):
	dirTitle = 'Eerie Cuties'
	archiveURL = 'http://www.eeriecuties.com/archive.html'
	archiveXPath = '//a[starts-with(@href, "/d/")]'
	
	imgURL = 'http://www.eeriecuties.com/comics/ec%sa.jpg'
	imgURL2 = 'http://www.eeriecuties.com/comics/ec%s.png'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	imgs = list()
	for img in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		src = img.get('href')
		if src not in imgs: imgs.append(src)
	
	for img in imgs:
		title = img.split('/')[-1].split('.')[0]
		if int(title) > 20101101:
			comicURL = imgURL2 % title
		else:
			comicURL = imgURL % title
		if title == '20090610':
			comicURL = comicURL[:-5] + '.jpg'
		dir.Append(PhotoItem(comicURL, title=title, thumb=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def ErrantStory(sender):
	dirTitle = 'Errant Story'
	archiveURL = 'http://www.errantstory.com/category/comics/page/1'
	archiveXPath = '//div[@class="comicarchiveframe"]/a'
	hasOldestFirst = True
	imgURL = 'http://www.errantstory.com/comics/%s.gif'

	dir = MediaContainer(title1=dirTitle)
	indexURL = archiveURL
	hasMore = True
	
	while(hasMore):
		page = XML.ElementFromURL(indexURL, True)
		
		navLinks = page.xpath('//div[@class="pagenav-right"]/a')
		if len(navLinks) != 0:
			indexURL = navLinks[0].get('href')
		else:
			hasMore = False
			
		for comic in page.xpath(archiveXPath):
			id = comic.get('href').split('/')[-2]
			if id == '2009-08-07' or id == '2009-06-12':
				id = id + '-es' + id.replace('-', '')
			comicURL = imgURL % id
			title = comic.xpath('./small')[-1].text
			
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
	if not Prefs.Get('oldestFirst'):
		dir.Reverse()
	
	Dict.Set('lastPage', int(indexURL.split('/')[-1]))
	
	return dir

####################################################################################################

def ExterminatusNow(sender):
	archiveURL = 'http://7-0-7.co.uk/Miscellaneous/ENtitles.html'
	archiveXPath = '//p[@class="en"]/a'
	imgURL = 'http://exterminatusnow.comicgenesis.com/comics/%s.jpg'
	imgXPath = '//img[starts-with(@src, "http://exterminatusnow.comicgenesis.com/comics/")]'
	hasOldestFirst = True

	dir = MediaContainer(title1=sender.itemTitle)
	
	for img in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = img.text
		href = img.get('href')
		if href == None: continue
		comicURL = imgURL % href.split('/')[-1].split('.')[0]
		Log(comicURL)
		dir.Append(PhotoItem(comicURL, title=title, thumb=comicURL))
#		dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=href, xpath=imgXPath)), url=href, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def EV(sender):
	dirTitle = '+EV *'
	archiveURL = 'http://plusev.keenspot.com/'
	archiveXPath = '//select[@name="menu"]/option'
	imgURL = 'http://plusev.keenspot.com/comics/plusev%s.gif'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath)[1:]:
		#######################################################
		id = comic.get('value').split('/')[-1].split('.')[0]
		title=comic.text
		#######################################################
		comicURL = imgURL % id
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def FlakyPastry(sender):
	dirTitle = 'Flaky Pastry'
	archiveURL = 'http://flakypastry.runningwithpencils.com/archive.php'
	archiveXPath = '//a[starts-with(@href, "comic.php?strip_id=")]'
	
	imgXPath = '//img[starts-with(@src, "comics/")]'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	for img in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = img.text
		comicURL = urlparse.urljoin(archiveURL, img.get('href'))
		dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()

	return dir

####################################################################################################

def Flipside(sender):
	archiveURL = 'http://www.flipsidecomics.com/chapters.php'
	archiveXPath = '/html/body/center/table/tr'
	
	imgXPath = '//a[starts-with(@href, "comic.php?i=")]/img'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=sender.itemTitle)
	
	for chapter in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		chapterTitle = chapter.xpath('./td/div[1]/p[2]//b')
		if len(chapterTitle) == 0:
			chapterTitle = chapter.xpath('./td/p[1]/b/a')
		comics = chapter.xpath('.//table//a')
		if len(comics) == 0:
			comics = chapter.xpath('./p[2]/a')

		for comic in comics:
			title = '%s %s' % (chapterTitle[0].text, comic.text)
			comicURL = urlparse.urljoin(archiveURL, comic.get('href'))
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def GingersBread(sender):
	dirTitle = "Ginger's Bread"
	archiveURL = 'http://www.gingersbread.com/archive/'
	archiveXPath = '//div[@class="archive-yearlist"]/a'
	archive2XPath = '//td[@class="archive-title"]/a'
	
	imgURL = 'http://www.gingersbread.com/comics/%s-%s.png'
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		imgs = XML.ElementFromURL(urlparse.urljoin(archiveURL, archive.get('href')), True).xpath(archive2XPath)
		imgs.reverse()
		for img in imgs:
			title = '-'.join(img.get('href').split('/')[3:6])
			comicURL = imgURL % (title, img.text.split(' ')[-1])
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def GirlGenius(sender):
	dirTitle = 'Girl Genius'
	archiveURL = 'http://www.girlgeniusonline.com/comic.php'
	archiveXPath = '//select[@name="date"]/option'
	imgURL = 'http://www.girlgeniusonline.com/ggmain/strips/ggmain%sb.jpg'
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)

	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		#######################################################
		id = comic.get('value')
		if id == '20090817':
			comicURL = 'http://www.girlgeniusonline.com/ggmain/strips/ggmain20090817a.jpg'
		else:
			comicURL = imgURL % id

		title = comic.text
		if title.startswith('---'): continue
		#######################################################
		
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def GirlsWithSlingshots(sender):
	dirTitle = 'Girls with Slingshots'
	archiveURL = 'http://www.girlswithslingshots.com/archive/?archive_year=%i'
	archiveXPath = '//td[@class="archive-title"]/parent::tr'
	imgURL = 'http://www.girlswithslingshots.com/comics/%s-%s-%s-%s.jpg'
	hasOldestFirst = True
	months = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	dir = MediaContainer(title1=dirTitle)
	
	for year in range(2004, datetime.datetime.now().year + 1):
		comics = list()
		for comic in XML.ElementFromURL(archiveURL % year, True).xpath(archiveXPath):
			date = comic.xpath('./td[@class="archive-date"]')[0].text
			month = str(months.index(date.split(' ')[0])).zfill(2)
			day = date.split(' ')[1].zfill(2)
			title = comic.xpath('./td[@class="archive-title"]/a')[0].text
			comicURL = imgURL % (year, month, day, title)
			comics.append(PhotoItem(comicURL, title=title, thumb=comicURL))
		comics.reverse()
		for item in comics: dir.Append(item)
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def Goats(sender):
	dirTitle = 'Goats'
	
	nowStr = '01.html'
	dir = MediaContainer(title1=dirTitle)
	for indexPage in XML.ElementFromURL('http://www.goats.com/', True).xpath('//select[@name="month"]/option'):
		indexURL = 'http://www.goats.com' + indexPage.get('value')
		if indexURL.endswith(nowStr):
			cacheTime = CACHE_1HOUR
		else:
			cacheTime = CACHE_1DAY * 365
		for comic in XML.ElementFromURL(indexURL, True, cacheTime=cacheTime).xpath('//table[@class="calendar"]//a'):
			id = comic.get('href').split('/')[-1].split('.')[0]
			if id > '970400' or id < '031217':
				ext = 'gif'
			else:
				ext = 'png'
			title = comic.get('title')
			comicURL = 'http://www.goats.com/comix/%s/goats%s.%s' % (id[:4], id, ext)
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
		if not Prefs.Get('oldestFirst'):
			dir.Reverse()
	return dir

####################################################################################################

def Goblins(sender):
	dirTitle = 'Goblins'
	archiveURL = 'http://www.goblinscomic.com/archive/'
	archiveXPath = '//div[@class="post-page"]//a'
	imgURL = 'http://www.goblinscomic.com/comics/%s.jpg'
	
	hasOldestFirst = True

	dir = MediaContainer(title1=dirTitle)
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		id = comic.get('href').split('/')[-2]
		id1 = id[:4]
		id2 = id[4:]
		id = id2 + id1
		title = comic.text
		comicURL = imgURL % id
		dir.Append(PhotoItem(comicURL, title=title))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def GunnerkriggCourt(sender):
	dirTitle = 'Gunnerkrigg Court'
	archiveURL = 'http://www.gunnerkrigg.com/archive.php'
	archiveXPath = '//a[@class="calendarlink"]'
	imgURL = 'http://www.gunnerkrigg.com//comics/%s'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		id = comic.get('href').split('=')[-1]
		if id == '297':
			comicURL = imgURL % '00000297.gif'
		else:
			comicURL = imgURL % (id.zfill(8) + '.jpg')
		title = id
		
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def LasLindas(sender):
	dirTitle = 'Las Lindas'
	archiveURL = 'http://laslindas.katbox.net/?page_id=2&cat=5'
	archiveXPath = '//section[starts-with(@id, "archive_")]//a'
	imgURL1 = 'http://laslindas.katbox.net/wp-content/uploads/2011/01/%s%s%s.jpg'
	imgURL2 = 'http://laslindas.katbox.net/wp-content/uploads/2011/01/%s%s%s.JPG'
	imgURL3 = 'http://laslindas.katbox.net/wp-content/uploads/%s/%s/las_lindas%i.jpg'
	hasOldestFirst = False
	dir = MediaContainer(title1=dirTitle)

	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		index, day, month, year = re.match(r'Comic (\d+) (\d+)/(\d+)/(\d+)', comic.text).groups()
		title = comic.text
		index = int(index)
		if 1 < index < 31 or 278 < index < 304:
			comicURL = imgURL1 % (year, month, day)
		elif index > 303:
			comicURL = imgURL3 % (year, month, index + 6)
		else:
			comicURL = imgURL2 % (year, month, day)
		dir.Append(PhotoItem(comicURL, title=title, thumb=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def LeastICouldDo(sender):
	dirTitle = 'Least I Could Do'
	archiveURL = 'http://www.leasticoulddo.com/archive/calendar'
	archiveXPath = '//div[@id="page-content"]/p/a'
	archive2XPath = '//div[starts-with(@id,"calendar-")]//a' 
	imgURL = 'http://cdn.leasticoulddo.com/comics/%s.gif'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	
	archives = list()
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		archives.append(urlparse.urljoin(archiveURL, archive.get('href')))
	archives.append(archiveURL)
	
	for archive in archives:
		page = XML.ElementFromURL(archive, True)
		for img in page.xpath(archive2XPath):
			title = img.get('href').split('/')[-1]
			comicURL = imgURL % title
			dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir
	
####################################################################################################

def Level99(sender):
	dirTitle = 'Level 99'
	archiveURL = 'http://level99comic.com/comics-archive/'
	archiveXPath = '//td[@class="archive-title"]/a'
	imgXPath = '//div[@id="comic"]/img'
	imgXPath2 = '//div[@class="comicarchiveframe"]/a'
	hasOldestFirst = False
	dir = MediaContainer(title1=dirTitle)
	for img in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = img.text
		comicURL = img.get('href')
		dir.Append(Function(PhotoItem(getComicFromPageWithXPaths, title=title, thumb=Function(getComicFromPageWithXPaths, url=comicURL, xpaths=[imgXPath, imgXPath2])), url=comicURL, xpaths=[imgXPath, imgXPath2]))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def LookingForGroup(sender):
	dirTitle = 'Looking for Group'
	archiveURL = 'http://lfgcomic.com/issues.php'
	archiveXPath = '//div[@id="spines"]//a'
	archive2XPath = '//div[@id="page-thumb"]/a' 
	imgURL = 'http://lfgcomic.com/comics/%s'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)

	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		page = XML.ElementFromURL(urlparse.urljoin(archiveURL, archive.get('href')), True)
		for img in page.xpath(archive2XPath):
			title = img.get('href').split('/')[-1]
			comicURL = imgURL % img.xpath('./img')[0].get('src').split('/')[-1]
			dir.Append(Function(PhotoItem(getComicMime, title=title, thumb=Function(getComicMime, url=comicURL, mime='image/gif')), url=comicURL, mime='image/gif'))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir
	
####################################################################################################

def MAGISA(sender):
	archiveURL = 'http://www.drunkduck.com/MAG_ISA/index.php'

	imgXPath = '//img[starts-with(@src, "http://comics.drunkduck.com/MAG_ISA/pages/")]'
	hasOldestFirst = False

	dir = MediaContainer(title1=sender.itemTitle)
	dropdown = XML.ElementFromURL(archiveURL, True).xpath('//select[@name="p"]')[0]
	for archive in dropdown.xpath('./option'):
		comicURL = 'http://www.drunkduck.com/MAG_ISA/index.php?p=' + archive.get('value')
		title = archive.text
		dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir
	
####################################################################################################

def MegaTokyo(sender):
	dirTitle = 'MegaTokyo'
	archiveURL = 'http://megatokyo.com/archive.php'
	
	archiveXPath = './div/ol/li/a'
	imgURL = 'http://megatokyo.com/strips/%s.gif'
	
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)

	archiveSections = XML.ElementFromURL(archiveURL, True).xpath('//div[@class="content"]')[1:]
	for archive in archiveSections:
		for img in archive.xpath(archiveXPath):
			title = img.text
			comicURL = imgURL % img.get('href').split('/')[-1].zfill(4)
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
	if not Prefs.Get('oldestFirst'):
		dir.Reverse()
	dir.Append(PrefsItem(title='Preferences', thumb=R('icon-prefs.png')))
	return dir

####################################################################################################
	
def MenageATrois(sender):
	dirTitle = 'Menage a Trois'
	archiveURL = 'http://www.menagea3.net/archive.html'
	archiveXPath = '//span[@class="trebuchetbody12pix"]/following-sibling::table//a'
	imgURL = 'http://www.menagea3.net/comics/mat%s.png'
	imgXPath = '//img[starts-with(@src, "/comics/")]'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	processed = list()
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		#######################################################
		if comic.get('href') == None: continue
		id = comic.get('href').split('.')[0].split('/')[-1]
		if id in processed:
			continue
		else:
			processed.append(id)
		
		if len(id) == 0:
			comicURL = 'http://www.menagea3.net/'
			title = 'latest'
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
		else:
			title = '%s-%s-%s' % (id[0:4], id[4:6], id[6:8])
			comicURL = imgURL % id
			dir.Append(Function(PhotoItem(getExtComic, title=title, thumb=Function(getExtComic, url=comicURL)), url=comicURL))
		#######################################################
		
		
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def Misfile(sender):
	dirTitle = 'Misfile'
	archiveURL = 'http://www.misfile.com/index.php?menu=archives'
	archiveXPath = '//a[@class="linkPage"]'
	archive2XPath = '//a[@class="linkPage"]' 
	imgURL = 'http://www.misfile.com/overlay.php?pageCalled=%s'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	dir = MediaContainer()
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		for img in XML.ElementFromURL(urlparse.urljoin(archiveURL, archive.get('href')), True).xpath(archive2XPath):
			title = img.text
			comicURL = imgURL % img.get('href').split('=')[-1]
			dir.Append(Function(PhotoItem(getComicMime, title=title, thumb=Function(getComicMime, url=comicURL, mime='image/png')), url=comicURL, mime='image/png'))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def PeterAndCompany(sender):
	dirTitle = 'Peter and Company'
	archiveURL = 'http://www.peterandcompany.com/archives/'
	archiveXPath = '//ul[@class="lcp_catlist"]/li/a'
	
	imgURL = 'http://www.peterandcompany.com/strips/%s.jpg'
	hasOldestFirst = False
	dir = MediaContainer(title1=dirTitle)

	for img in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = img.text
		href = img.get('href').split('/')
		comicURL = imgURL %  '-'.join(href[3:6])
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def QuestionableContent(sender):
	dir = MediaContainer(title1='Questionable Content')
	for comic in XML.ElementFromURL('http://questionablecontent.net/archive.php', True).xpath('//div[@id="archive"]/a'):
		id = comic.get('href').split('=')[-1]
		comicURL = 'http://questionablecontent.net/comics/%s.png' % id
		title = comic.text
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('Reverse'):
		dir.Reverse()
	return dir

####################################################################################################

def SMBC(sender):
	archiveURL = 'http://www.smbc-comics.com/archive/'
	imgURL = 'http://www.smbc-comics.com/comics/%s.gif'
	imgXPath = '//td[@class="comicboxleft"]/following-sibling::td[1]/table/tr/td/center/img[2]'
	months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

	dirTitle = 'Saturday Morning Breakfast Cereal'
	dir = MediaContainer(title1=dirTitle)
	for link in XML.ElementFromURL(archiveURL, True).xpath('//a[starts-with(@href, "/index.php?db=comics&id=")]'):
		title = link.text
		comicURL = urlparse.urljoin(archiveURL, link.get('href'))
		dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	return dir

####################################################################################################

def SchoolBites(sender):
	dirTitle = 'School Bites'
	archiveURL = 'http://www.schoolbites.net/archive.html'
	archiveXPath = '//a[starts-with(@href, "/d/")]'
	imgURL = 'http://www.schoolbites.net/comics/sb%s'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)

	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		#######################################################
		id = comic.get('href').split('/')[-1].split('.')[0]
		title = '%s-%s-%s' % (id[0:4], id[4:6], id[6:8])
		if id == '20090817':
			id += 'a.jpg'
		elif id < '20091012' or id > '20091115':
			id += '.jpg'
		else:
			id += '.gif'
		#######################################################
		comicURL = imgURL % id
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def SequentialArt(sender):
	dirTitle = 'Sequential Art'
	archiveURL = 'http://www.collectedcurios.com/sequentialart.php'
	
	archiveXPath = '//img[@id="strip"]'
	imgURL = 'http://www.collectedcurios.com/SA_%s_small.jpg'
	
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	lastID = XML.ElementFromURL(archiveURL, True).xpath(archiveXPath)[0].get('src').split('SA_')[1].split('_')[0]
	for id in range(1, int(lastID)):
		title = str(id)
		comicURL = imgURL % str(id).zfill(4)
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir
	
####################################################################################################

def Sinfest(sender):
	dirTitle = 'Sinfest'
	archiveURL = 'http://www.sinfest.net/archive.php'
	archiveXPath = '//select[@name="comicID"]/option'
	imgURL = "http://www.sinfest.net/archive_page.php?comicID=%s"
	imgXPath = '//img[starts-with(@src, "http://sinfest.net/comikaze/comics/")]'
	hasOldestFirst = False
	dir = MediaContainer(title1=dirTitle)
	
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath)[1:]:
		#######################################################
		id = comic.get('value')
		#######################################################
		comicURL = imgURL % id
		dir.Append(Function(PhotoItem(getComicFromPage, title=comic.text, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def SlightlyDamned(sender):
	dirTitle = 'Slightly Damned'
	archiveURL = 'http://www.sdamned.com/archives/'
	imgURL = 'http://www.sdamned.com/comics/%s-%s-%s.jpg'
	hasOldestFirst = False
	months = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	dir = MediaContainer(title2=dirTitle)
	for yearItem in XML.ElementFromURL(archiveURL, True).xpath('//h3'):
		year = yearItem.text
		for item in yearItem.xpath('following-sibling::table/tr/td[@class="archive-date"]'):
			month3Letter, day = item.text.split(' ')
			month = str(months.index(month3Letter)).zfill(2)
			comicURL = imgURL % (year, month, day.zfill(2))
			title = item.xpath('./following-sibling::td[@class="archive-title"]/a')[0].text
			dir.Append(PhotoItem(comicURL, title=title))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def SomethingPositive(sender):
	dirTitle = 'Something Positive'
	archiveURL = 'http://www.somethingpositive.net/archive.shtml'
	archiveXPath = '//b/a'
	archive2XPath = '//pre//a' 
	imgURL = 'http://www.somethingpositive.net/%s.gif'
	imgXPath = '/html/body/table/tr/td/table/tr/td/table/tr/td/table/tr/td/img[2]'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)

	archives = list()
	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		archives.append(urlparse.urljoin(archiveURL, archive.get('href')))
	archives.append(archiveURL)
	
	for archive in archives:
		page = XML.ElementFromURL(archive, True)
		for img in page.xpath(archive2XPath):
			title = XML.etree.tostring(img).split('>')[-1].split('\n')[0].strip()
			date = img.text
			#if title == 'Holiday Sharing pt 2':
			#	comicURL = imgURL % 'sp11301937'
			#elif len(date.split('-')[-1]) == 4:
			#	comicURL = imgURL % ('arch/sp' + img.text.replace('-', ''))
			#else:
			#	comicURL = imgURL % img.get('href').split('.')[0]
			comicURL = urlparse.urljoin(archive, img.get('href'))
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()  
	return dir
	
####################################################################################################

def SomewhereDifferent(sender):
	dirTitle = 'Somewhere Different'
	archiveURL = 'http://somewheredifferent.webs.com/archives.html'
	archiveXPath = '//div[@class="content"]//a'
	archive2XPath = '//div[@class="event"]/a' 
	imgURL = 'http://i944.photobucket.com/albums/ad281/somewheredifferent/%s.png'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)

	for archive in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		page = XML.ElementFromURL(urlparse.urljoin(archiveURL, archive.get('href')), True)
		for img in page.xpath(archive2XPath):
			title = img.text
			comicURL = imgURL % img.get('href').split('.')[0]
			dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
####################################################################################################

def TheSpaceBetween(sender):
	dirTitle = 'The Space Between'
	archiveURL = 'http://www.jellybeansniper.net/spacebetween/archives.html'
	archiveXPath = '//table[@class="archives"]//a'
	imgURL = 'http://www.jellybeansniper.net/spacebetween/comics/%s.jpg'
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		#######################################################
		id = comic.get('href').split('.')[0].split('comic')[-1]
		#######################################################
		comicURL = imgURL % id
		title = comic.text
		dir.Append(Function(PhotoItem(getComic, title=title, thumb=Function(getComic, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def ThreePanelSoul(sender):
	dirTitle = 'Three Panel Soul'
	archiveURL = 'http://threepanelsoul.com/'
	archiveXPath = '//h2[text()="Monthly Archives"]/following-sibling::ul/li/a'
	monthlyArchiveXPath = '//div[@class="comicarchiveframe"]/a'
	
	imgXPath = '//div[@id="comic"]/img'
	
	hasOldestFirst = True
	
	dir = MediaContainer(title1=dirTitle)
	for monthLink in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		for comic in XML.ElementFromURL(monthLink.get('href'), True).xpath(monthlyArchiveXPath):
			title = comic.xpath('./h3')[0].text
			comicURL = comic.get('href')
			thumbURL = comic.xpath('./img')[0].get('src')
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	
	return dir

####################################################################################################

def TwoKinds(sender):
	archiveURL = 'http://2kinds.com/archive.htm'
	archiveXPath = '//table//a'
	imgXPath = '//a[starts-with(@href, "?p=")]/img'
	hasOldestFirst = True
	dir = MediaContainer(title1=sender.itemTitle)
	
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		title = comic.text
		comicURL = comic.get('href')
		dir.Append(Function(PhotoItem(getComicFromPage, title=comic.text, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def VGCats(sender):
	dirTitle = 'VG Cats'
	archiveURL = 'http://www.vgcats.com/archive/'
	archiveXPath = '//a[contains(@href, "../comics/?strip_id=")]'
	
	hasOldestFirst = True
	dir = MediaContainer(title1=dirTitle)
	
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		comicURL = urlparse.urljoin(archiveURL, comic.get('href'))
		try:
			title = comic.xpath('./font')[0].text
		except:
			title = comic.text
		title = re.sub('[\r\n ]+', r' ', title)
		dir.Append(Function(PhotoItem(getVGCats, title=title, thumb=Function(getVGCats, url=comicURL)), url=comicURL))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir
	
def getVGCats(url, sender=None):
	imgSrc = None
	for imgElem in XML.ElementFromURL(url, True).xpath('//img[contains(@src, "images/")]'):
		src = imgElem.get('src')
		if re.match(r'images/\d+\..*', src):
			return Redirect(urlparse.urljoin(url, src))

####################################################################################################

def XKCD(sender):
	dirTitle = 'XKCD'
	archiveURL = 'http://xkcd.com/archive/'
	archiveXPath = '//div[@class="s"]/h1/following-sibling::a'
	
	imgXPaths = ['//div[@class="s"]/img', '//div[@class="s"]/a/img']
	hasOldestFirst = False
	dir = MediaContainer(title1=dirTitle)
	
	for comic in XML.ElementFromURL(archiveURL, True).xpath(archiveXPath):
		comicURL = urlparse.urljoin(archiveURL, comic.get('href'))
		try:
			title = comic.xpath('./font')[0].text
		except:
			title = comic.text
		dir.Append(Function(PhotoItem(getComicFromPageWithXPaths, title=title, thumb=Function(getComicFromPageWithXPaths, url=comicURL, xpaths=imgXPaths)), url=comicURL, xpaths=imgXPaths))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def EightBitTheater(sender):
	base = 'http://nuklearpower.com'
	index = base + '/8-bit-theater-archive/'
	imgURL = base + '/comics/8-bit-theater/%s.png'
	imgXPath = '//div[@id="comic"]/img'
	hasOldestFirst = True
	
	dir = MediaContainer(title1='8-bit Theater')
	years = XML.ElementFromURL(index, True, errors='ignore', cacheTime=CACHE_1DAY).xpath('//div[@class="archive-yearlist"]/a')
	yearCount = len(years)
	cacheTime = CACHE_1YEAR
	for yearIndex in range(0, yearCount):
		if yearIndex == yearCount - 1:
			cacheTime = CACHE_1HOUR
		link = urlparse.urljoin(index, years[yearIndex].get('href'))
		pages = XML.ElementFromURL(link, True, errors='ignore', cacheTime=cacheTime).xpath('//div[@class="cpcal-day"]/a')
		for page in pages:
			#id = page.get('href').split('/')[3:6]
			#comicURL = imgURL % (id[0][2:] + id[1] + id[2])
			comicURL = page.get('href')
			title = page.get('title')
			dir.Append(Function(PhotoItem(getComicFromPage, title=title, thumb=Function(getComicFromPage, url=comicURL, xpath=imgXPath)), url=comicURL, xpath=imgXPath))
	if Prefs.Get('oldestFirst') != hasOldestFirst:
		dir.Reverse()
	return dir

####################################################################################################

def getComicList():
	return [
		[EightBitTheater, "8-bit Theater", "icon-8BitTheater.png", "art-8BitTheater.png", "Fantasy", "Best description is probably a Final Fantasy parody. We're talking old-school Final Fantasy, with the main characters being Fighter, Red Mage, Theif, and Black Mage. Supposedly, they're destined to save the world. But one's an idiot, another's considered delirious, the third a greedy kleptomaniac, and the final one a stabby, murderous psychopath. Nothing seems to go right for them, but the result is pure comedy gold. If you don't find this at least mildly funny, check yourself into an asylum. And last but not least, a quote:\n\"What part of being stabbed do you not understand?\" - Black Mage"],
		[AppleGeeks, "Apple Geeks", "icon-AppleGeeks.png", "art-AppleGeeks.png", "Geeky", "Follow the adventue's of Hawk as he struggles to survive as a Mac user in a World ruled by Windows."],
		[AppleGeeksLite, "AppleGeeks Lite", "icon-AppleGeeksLite.png", "art-AppleGeeksLite.png", "Geeky", "Follow the adventue's of Hawk as he struggles to survive as a Mac user in a World ruled by Windows."],
		[BetweenFailures, "Between Failures", "icon-BetweenFailures.png", "art-BetweenFailures.png", "Workplace", "Thomas Blackwell is a clerk in a store. He believes that 'life is what happens, between failures.' This is the story of his life & friends."],
		[Catena, "Catena", "icon-Catena.png", "art-Catena.png", "Furry", "A house full of cats..."],
		[CtrlAltDel, "Ctrl+Alt+Del", "icon-CtrlAltDel.png", "art-CtrlAltDel.png", "Gaming", "Two die-hard gaming roommates and a Linux user take everyday challenges to the extreme. Ethan, the eccentric gamer with severe illusions of granduer, at the same time being completely out of touch with reality is friendly yet dangerous. Lucas is the brains behind every operation, often keeping a close eye on Ethan and helping him out of trouble, he much prefers the X-Box to any other console, as does Ethan. Scott is the third roommate, not quite a gamer, but an expert with Linux, he is very rarely seen and owns a penguin, a la Linux logo. Lilah is Ethan's girlfriend, Nobody really knows how he is ABLE to get a girlfriend, but Lilah is brainy, beautiful and owns in UT2004."],
		[CyanideAndHappiness, "Cyanide and Happiness", "icon-CyanideAndHappiness.png", "art-CyanideAndHappiness.png", "Weird", "An eclectic mix of cynicism and vile toilet humor. No plot, story, characters or themes. Randomness ensues."],
		[DanAndMab, "Dan and Mab's Furry Adventures", "icon-DanAndMab.png", "art-DanAndMab.png", "Furry", "bunch of cat people, a little dragon that passes for the loch ness monster. an ass kicking ferret, a carnivorois cow. Adventures dosn't even begin to describe this comic. for a bit of mindless fun and possibly some scantly clad Amazons, if the author gets the hint, it's a good time"],
		[DrMcNinja, "Dr. McNinja", "icon-DrMcNinja.png", "art-DrMcNinja.png", "Quirky", "An all around doctor which turns out to be a very skilled ninja. His life is mostly considered not normal to most people but it does to him."],
		[DominicDeegan, "Dominic Deegan Oracle for Hire", "icon-DominicDeegan.png", "art-DominicDeegan.png", "Fantasy", "Dominic Deegan, a grumpy seer, and his friends have faced violent knights, murderous witches, incompetent thieves, furry sea monsters, angry mobs, magical slimes, flesh-eating demon lords, the blight of the undead, and mood swings. Their adventures have only just begun. Come and see for yourself. Just beware of Death From Above!"],
		[DuelingAnalogs, "Dueling Analogs", "icon-DuelingAnalogs.png", "art-DuelingAnalogs.png", "Gaming", "Dueling Analogs is a color semi-weekly webcomic that lampoons the characters, culture and subtext of modern gaming culture."],
		[EerieCuties, "Eerie Cuties", "icon-EerieCuties.png", "art-EerieCuties.png", "Quirky", "Eerie Cuties is a comedy horror meets cute. The cast consists of teenage monsters in high school. By Giz (artist/co-writer of Menage a 3)"],
		[ErrantStory, "Errant Story", "icon-ErrantStory.png", "art-ErrantStory.png", "Fantasy", "Errant Story is a tongue-in-cheek fantasy adventure set in a world of hired guns, ninja time mages, and genocidal elves, with the occasional sarcastic flying cat thrown in for good measure.\n\nAs the one and only teenaged half elf in her entire country, Meji Hinadori is pretty sure her life sucks. She can't seem to make any friends her own age, her grades at mage school are a flaming wreck (literally!), and it even looks like she'll be disowned if she can't ace some impossibly amazing senior project... like, say, becoming an insane, all-powerful demigoddess and enslaving all of reality. That shouldn't be too hard, right?"],  
		[EV, "+EV", "icon-EV.png", "art-EV.png", "Gaming", "+EV is a poker comic that runs MWF. The title means 'positive expected value,' a poker/gambling term meaning a profitable play or bet. It's a humor strip about a guy who quit his job to play online poker and how that affects his family life."],
		#[ExterminatusNow, "Exterminatus Now", "icon-ExterminatusNow.png", "art-ExterminatusNow.png", "Furry", "Follow the missions and lives of four daemon-hunters: Eastwood, Virus, Rogue, and Lothar, as they fight for freedom, liberty, and the pursuit of coffee."],
		[FlakyPastry, "Flaky Pastry", "icon-FlakyPastry.png", "art-FlakyPastry.png", "Quirky", "The unusual life and hijinks of roommates Nitrine, Marelle and Zintiel; a roguish goblin, inquisitive catgirl and insane elf, in a world of randomness and fattening desserts."],
		[Flipside, "Flipside", "icon-Flipside.png", "art-Flipside.png", "Fantasy", "This is no ordinary webcomic! Follow the adventures of two women: Maytag, a nymphmaniac jester girl with split personalities; and Bernadette, a female knight and bodyguard."],

		[GingersBread, "Gingers Bread", "icon-GingersBread.png", "art-GingersBread.png", "Geeky", "Ginger's Bread is the story of Ginger and her friends just trying to get by in life. Ginger is recently unemployed and is now on the hunt for a new job."],
		[GirlGenius, "Girl Genius", "icon-GirlGenius.png", "art-GirlGenius.png", "Fantasy", "Agatha Clay is a young Mad Scientist (or 'Spark' to be polite.) Traveling with her is Krosp I, a 'failed experiment' created to be the King of the Cats. Agatha is also the last of the famous Heterodyne family-beloved heroes who disappeared under mysterious circumstances many years ago. Folk legend claims that they will someday return."],
		[GirlsWithSlingshots, "Girls with Slingshots", "icon-GirlsWithSlingshots.png", "art-GirlsWithSlingshots.png", "Quirky", "The everyday adventures of Hazel, the cynical writer who hasn't met a bottle she doesn't like, Jamie, her volumptous and optimistic best friend, the men in her life, and the women in theirs."],
		[Goblins, "Goblins", "icon-Goblins.png", "art-Goblins.png", "Fantasy", "A D&D satire comic featuring... well.. a buncha goblins."],
		[Goats, "Goats", "icon-Goats.png", "art-Goats.png", "Quirky", "Q: If Diablo is a satanist, and Toothgnip is a goat, when are we gonne see Diablo chasing the goat around trying to sacrifice him?? C'mon, do the math!!\n\nA: Two words: sweeps week"],
		[GunnerkriggCourt, "Gunnerkrigg Court", "icon-GunnerkriggCourt.png", "art-GunnerkriggCourt.png", "Manga", "A young girl with a mysterious past explores the secrets of her strange boarding school. Now updated Mondays, Wednesdays and Fridays."],
		[LasLindas, "Las Lindas", "icon-LasLindas.png", "art-LasLindas.png", "Furry", "Las Lindas is all about the personal development of the main character, Mora Linda. She inherits her dilapidated family farm after her parents passing and strives to restore it in her memory. After attempting the task alone, she hires a cast of characters through the story which shift the genre of the comic from relationship (slice of life) drama to very light hearted and silly comedy. Watch as Mora attempts to restore her farm, fight her childhood rival, handle three trouble making cats, make a new boyfriend while trying to subdue her fanatical ex, and much more."],
		[LeastICouldDo, "Least I Could do", "icon-LeastICouldDo.png", "art-LeastICouldDo.png", "Mature", "Award winning daily webcomic by Ryan Sohmer and Lar deSouza, following the life and antics of Rayne and those who surround him."],
		[Level99, "Level 99", "icon-Level99.png", "art-Level99.png", "Geeky", "A guy and a girl who make gags about anime and gaming. Mostly gag-a-day, but some contuity exists as well."],
		[LookingForGroup, "Looking for Group", "icon-LookingForGroup.png", "art-LookingForGroup.png", "Fantasy", "Looking For Group is the newest brain child of Ryan Sohmer and Lar DeSouza, the brilliant duo that brings us Least I Could Do. The story is set in a parody fantasy universe, lampooning all levels of mainstream lore stories on a bi-weekly basis. The comic focuses on the adventures of a naive Elf, a charming, but frighteningly devious warlock, a priestess, a powerful and tactical Tauren warrior, and their panther, Soomba. "],
		[MAGISA, "MAG ISA", "icon-MAGISA.png", "art-MAGISA.png", "Manga", "A comic about a loner, an angel, and a psycho cult with a sinister agenda."],
		[MegaTokyo, "MegaTokyo", "icon-MegaTokyo.png", "art-MegaTokyo.png", "Manga", "When two friends, Piro and Largo, get stuck in Japan, things can't seem to get much worse. Boy, were they wrong. Stranded with no money, Piro, the quiet artist with no self-confidence, who has the usual manga artist's weakness for girls in school uniforms, the only one who can speak Japanese, must find a job and look after Largo, the beer-guzzling, fantasy world L33t G4m3r. Together they meet up with old friends and enemies, make new ones, and deal with Dom's horrible stick-man fillers. A great comic drawn by a great artist."],
		[MenageATrois, "Menage a Trois", "icon-MenageATrois.png", "art-MenageATrois.png", "Mature", "Set in Montreal, the finest bohemian city in North America, Menage a 3 follows the lives of comic book geek Gary and his way-sexier-than-he-is roomates in their Montreal tight-as-a-sandwhich apartment; where the walls are so thin there are virtually no barriers between their rooms."],
		[Misfile, "Misfile", "icon-Misfile.png", "art-Misfile.png", "Manga", "A comedy about how a pothead angel messes up two distinctively different people's lives. A car-loving boy turned into a girl, and a girl who lost two years of her life. Now they must stick together to fix their problems"],
		[PeterAndCompany, "Peter and Company", "icon-PeterAndCompany.png", "art-PeterAndCompany.png", "Furry", "Peter, an adolescent cat, is having difficulty keeping friends when suddenly a new friend walks into his life in the form of Seth, a white-suited duck. Peter enjoys spending time with Seth, but soon realizes that he is the only one who can see him. Seth is known simply as a 'Guardian.' Other characters have Guardians as well, but the only people who can see them are the children who are already made aware of them."],
		[QuestionableContent, "Questionable Content", "icon-QuestionableContent.png", "art-QuestionableContent.png", "Geeky", "The plot centers on Marten, who is your average frustrated 20-something music nerd, his anthropomorphic PC named Pintsize, and Faye, a somewhat mysterious girl who moved in with him after she accidentally burned her apartment building down while trying to make toast. Lately Marten's friend Steve and Faye's boss Dora have come into the story a little more frequently, ensuring that things will stay nice and complicated."],
		[SMBC, "Saturday Morning Breakfast Cereal", "icon-SMBC.png", "art-SMBC.png", "Weird", "A single panel strip in the vein of the Far Side, if Gary Larson had been allowed to just write whatever he wanted and not had to worry about pleasing an editor"],
		[SchoolBites, "School Bites", "icon-SchoolBites.png", "art-SchoolBites.png", "Mature", "How does a sweet girl learn to become a groovy vampire?!\nWhat all good ghouls do...go to Vampire School!\nJoin Cherri Creeper and her friends in their first adventure at the Shadow Academy.\nJust think of Degrassi High with Fangs or Harry Potter meets Anne Rice.\nLovers of Lolita Goth, Manga & all things cute will dig School Bites!"],
		[SequentialArt, "Sequential Art", "icon-SequentialArt.png", "art-SequentialArt.png", "Furry", "A strange comic about a reasonably normal guy, and his two roomates, who just happen to be furries, one a male penguin, the other a female cat."],
		[Sinfest, "Sinfest", "icon-Sinfest.png", "art-Sinfest.png", "Geeky", "A guy who wants to sell his soul, a girl who thinks she's the center of the universe, the Heavenly Lord, the devil himself... a PIG,etc. What more could you ask for?"],
		[SlightlyDamned, "Slightly Damned", "icon-SlightlyDamned.png", "art-SlightlyDamned.png", "Fantasy", "Rhea is a young Jakkai (an intelligent kangaroo-like species) who suddenly finds herself dead. The problem is her soul is neither good nor evil so death sends her to the ring of the slightly damned to live with Buwaro a happy-go-lucky fire demon and his anti-social sister. The two eventually escape hell and meet a young angel named Kieri who is looking for her brother. Rhea and Buwaro decide to help her."],
#		[SomethingPositive, "Something Positive", "icon-SomethingPositive.png", "art-SomethingPositive.png", "Mature", "A boneless cat and two violent Asian women co-own Davan, a 20-something in Boston. A sex midget, trap-door gators, and Redneck Trees stalk the sets. A little something to offend everyone."],
		[SomewhereDifferent, "Somewhere Different", "icon-SomewhereDifferent.png", "art-SomewhereDifferent.png", "Manga", "Mark Richards, after an unfortunate experiment, becomes Mary-Anne, a girl in almost every sense of the word. With his shirts now blouses, and pants now skirts, will he be able to adapt before he eventually snaps?"],
		[TheSpaceBetween, "The Space Between", "icon-TheSpaceBetween.png", "art-TheSpaceBetween.png", "Manga", "Music, sports, movies, games, we cover it all, and bash it constantly. Updates Mondays and Fridays (usually)."],
		[ThreePanelSoul, "Three Panel Soul", "icon-ThreePanelSoul.png", "art-ThreePanelSoul.png", "Geeky", "From the guys who brought you www.machall.com, Matt Boyd and Ian McConville (sp? sorry :( ) are back with another interestingly amusing comic."],
		[TwoKinds, "TwoKinds", "icon-TwoKinds.png", "art-TwoKinds.png", "Furry", "Waking up without any memory of who he is, the human Trace Legacy soon finds himself in a battle between three races: the human, and catlike Keidran, and the doglike Basitin. Even as he begins to form a relationship with the Keidran Flora, Trace begins to realize what he once was: a Templar, one who kills Keidran."],
		[XKCD, "XKCD", "icon-XKCD.png", "art-XKCD.png", "Quirky", "A webcomic of romance, sarcasm, math, and language."],
	]
