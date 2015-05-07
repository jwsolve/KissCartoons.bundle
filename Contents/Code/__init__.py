######################################################################################
#
#	Kiss Cartoons - v0.10
#
######################################################################################

TITLE = "Kiss Cartoons"
PREFIX = "/video/kisscartoons"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_SERIES = "icon-tv.png"
ICON_NEXT = "icon-next.png"
BASE_URL = "http://kisscartoon.me"
SEARCH_URL = "http://kisscartoon.me/Search/Cartoon"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_SERIES)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_SERIES)
	VideoClipObject.art = R(ART)

	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Host'] = "kisscartoon.me"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	return Shows()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/shows")	
def Shows():

	oc = ObjectContainer()
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Kisscartoon', prompt='Search for...'))
	html = HTML.ElementFromURL(BASE_URL + '/CartoonList')

	for each in html.xpath("//div[@class='alphabet']/a"):
		title = each.xpath("./text()")[0]
		url = each.xpath("./@href")[0]
		if title != "All":
			oc.add(DirectoryObject(
				key = Callback(ShowCartoons, title = title, url = url, page_count = 1),
					title = title,
					thumb = R(ICON_SERIES)
					)
			)
	return oc
######################################################################################
@route(PREFIX + "/showcartoons")	
def ShowCartoons(title, url, page_count):

	oc = ObjectContainer(title1 = title)
	thisurl = url
	thisletter = url.split("=",1)[1]
	html = HTML.ElementFromURL(BASE_URL + '/CartoonList' + url + '&page=' + page_count, cacheTime=CACHE_1HOUR)

	for each in html.xpath("//tr/td[1]"):
		content = HTML.ElementFromString(each.xpath("./@title")[0])
		url = content.xpath("./div/a[@class='bigChar']/@href")[0]
		title = content.xpath("./div/a[@class='bigChar']/text()")[0]
		thumb = content.xpath("./img/@src")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	oc.add(NextPageObject(
		key = Callback(ShowCartoons, title = thisletter.upper(), url = thisurl, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	return oc

######################################################################################
@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	html = HTML.ElementFromURL(BASE_URL + url, cacheTime=CACHE_1HOUR)
	try:
		thumb = html.xpath("//div[@class='barContent']/div[2]/img/@src")[0]
	except:
		thumb = R(ICON_SERIES)
	showtitle=title
	for each in html.xpath("//table[@class='listing']/tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/text()")[0].strip().replace(showtitle + ' ','')
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page = HTML.ElementFromURL(BASE_URL + url, cacheTime=CACHE_1HOUR)
	title = page.xpath("//option[@selected='selected']/text()")[0].strip()
	description = page.xpath("//meta[@name='description']/@content")[0]
	thumb = page.xpath("//meta[@property='og:image']/@content")[0]
	
	oc.add(VideoClipObject(
		title = title,
		summary = description,
		thumb = thumb,
		url = BASE_URL + url
		)
	)	
	
	return oc	

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(SEARCH_URL + '?keyword=%s' % String.Quote(query, usePlus=True), headers="").content

	html = HTML.ElementFromString(data)

	for each in html.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		thumbhtml = HTML.ElementFromURL(BASE_URL + url, cacheTime=CACHE_1HOUR)
		title = thumbhtml.xpath("//a[@class='bigChar']/text()")[0]
		try:
			thumb = thumbhtml.xpath("//div[@class='barContent']/div/img/@src")[0]
		except:
			thumb = R(ICON_SERIES)
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc
