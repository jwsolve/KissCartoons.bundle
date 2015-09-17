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

import os
import sys
from lxml import html
import updater
updater.init(repo = '/jwsolve/KissCartoons.bundle', branch = 'master')

try:
	path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0]+"Plug-ins/KissCartoons.bundle/Contents/Code/Modules/KissCartoons"
except:
	path = os.getcwd().split("Plug-in Support")[0]+"Plug-ins/KissCartoons.bundle/Contents/Code/Modules/KissCartoons"
if path not in sys.path:
	sys.path.append(path)

import cfscrape
scraper = cfscrape.create_scraper()

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_SERIES)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_SERIES)
	VideoClipObject.art = R(ART)

	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Host'] = "kisscartoon.me"
	HTTP.Headers['Referer'] = "kisscartoon.me"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	return Shows()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/shows")	
def Shows():

	container = ObjectContainer()
	updater.add_button_to(container, PerformUpdate)
	container.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search Kisscartoon', prompt='Search for...'))
	page = scraper.get(BASE_URL + '/CartoonList')
	page_data = html.fromstring(page.text)

	for each in page_data.xpath("//div[@class='alphabet']/a"):
		title = each.xpath("./text()")[0].strip()
		url = each.xpath("./@href")[0]
		if title != "All":
			container.add(DirectoryObject(
				key = Callback(ShowCartoons, title = title, url = url, page_count = 1),
					title = title,
					thumb = R(ICON_SERIES)
					)
			)
	return container
######################################################################################
@route(PREFIX + "/showcartoons")	
def ShowCartoons(title, url, page_count):

	oc = ObjectContainer(title1 = title)
	thisurl = url
	thisletter = url.split("=",1)[1]
	page = scraper.get(BASE_URL + '/CartoonList' + url + '&page=' + page_count)
	page_data = html.fromstring(page.text)

	for each in page_data.xpath("//tr/td[1]"):
		content = HTML.ElementFromString(each.xpath("./@title")[0])
		url = content.xpath("./div/a[@class='bigChar']/@href")[0]
		title = content.xpath("./div/a[@class='bigChar']/text()")[0].strip()

		thumbhtml = scraper.get(BASE_URL + url)
		page_html = html.fromstring(thumbhtml.text)
		thumb = page_html.xpath("//link[@rel='image_src']/@href")[0]
		Log(thumb)

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
@route(PREFIX + "/performupdate")
def PerformUpdate():
	return updater.PerformUpdate()

######################################################################################
@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	page = scraper.get(BASE_URL + url)
	page_data = html.fromstring(page.text)
	thumb = page_data.xpath("//link[@rel='image_src']/@href")[0]
	showtitle=title
	for each in page_data.xpath("//table[@class='listing']/tr/td[1]"):
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
	page = scraper.get(BASE_URL + url)
	page_data = html.fromstring(page.text)
	title = page_data.xpath("//meta[@name='keywords']/@content")[0].split(' - ')[0].strip()
	description = page_data.xpath("//meta[@name='description']/@content")[0]
	thumb = page_data.xpath("//meta[@property='og:image']/@content")[0]
	
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
	searchdata = scraper.get(SEARCH_URL + '?keyword=%s' % String.Quote(query, usePlus=True))
	pagehtml = html.fromstring(searchdata.text)

	for each in pagehtml.xpath("//tr/td[1]"):
		url = each.xpath("./a/@href")[0]
		page = scraper.get(BASE_URL + url)
		thumbhtml = html.fromstring(page.text)
		title = thumbhtml.xpath("//a[@class='bigChar']/text()")[0].strip()
		thumb = thumbhtml.xpath("//link[@rel='image_src']/@href")[0]
		oc.add(DirectoryObject(
			key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
		)
	return oc
