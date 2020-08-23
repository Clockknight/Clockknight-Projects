import os
import sys
import shutil
import urllib
import requests
from pytube import YouTube
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

#Global Variables
ua = UserAgent()
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13'}

#Functions for
def optionSelect():
    option = input('''
    Welcome to Clockknight's Album Downloader. Please choose from an option below by entering the option number:

    1) Cache Mode
    Provide a .txt file with links to album's google result pages, seperated by lines.

    2) Search Mode
    Search for an artist's discography, and pull songs directly.

    0) Exit

    ''')

    if option == '1':
        cacheMode()
    elif option == '2':
        searchMode()
    elif option == '0':
        sys.exit()
    else:
        print('Invalid option selected. Please try again.\n\n')
        optionSelect()

def cacheMode():
    fileDir = ''
    resultArray = []

    #Find text file with links to google searches of albums' songs
    fileDir = input('Please enter the directory of the text file that has the links to appropriate files seperated by newlines.\n')

    #Use readlines to seperate out the links of albums
    file = open(fileDir, 'r')
    resultArray = file.readlines()
    #Run downloadAlbum
    downloadAlbum(resultArray)
def searchMode():
    '''
    resultCount = 0
    resultLinks = []

    #Get input for a songwriter
    #artist = input('\nPlease input the name of the artist you want to search the discography of.\n\t')
    #Temporarily listing searchArtist as Masami Ueda by default
    artist = 'Masami Ueda'
    searchLen = len(artist)
    searchArtist = urllib.parse.quote_plus(artist)

    #discogs Google results scrape
    query = 'https://www.google.com/search?q=discogs+' + searchArtist
    try:
        page = requests.get(query, headers=headers)#Use requests on the new URL
        soup = BeautifulSoup(page.text, "html.parser")#Take requests and decode it
        aList = soup.find_all('a', href=True)
        for item in aList:
            if item['href'][:30] == 'https://www.discogs.com/artist':
                temp = item['href'] + '?type=Releases&subtype=Albums&filter_anv=0'
                print('Going to page ' + temp + '...')
                break#Take the first viable link and then process it.
    except:
        print('Error:')

    #Find album name and find google results based on previous inputs & results
    try:
    albumCheck = artist + ' - '#Create string to check against later
    page = requests.get(temp, headers=headers)#Use requests on the new URL
    soup = BeautifulSoup(page.text, "html.parser")#Take requests and decode it
    imgList = soup.find_all('img', alt=True)#Make array of img tags with alt
    for item in imgList:
        if item['alt'][:searchLen+3] == albumCheck:#Check alt text against albumCheck string, based on Discogs formatting
            #Convert all info into one google search URL
            temp = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(artist + ' ' +  item['alt'][searchLen+3:-10]) + '+songs'
            resultLinks.append(temp)#Add Link to array
    except:
       print('Error:')

    '''
    #TEST FOR DOWNLOAD ALBUM
    resultLinks = ['https://www.google.com/search?q=madeon+adventure+songs&rlz=1C1CHBF_enUS899US899&oq=madeon+adventure+songs&aqs=chrome..69i57.311j0j7&sourceid=chrome&ie=UTF-8']

    downloadAlbum(resultLinks)#Call download Album with all songs wanted

def downloadAlbum(givenArray):
    blacklist = '.\'/\\' #String of characters that cannot be in filenames
    for link in givenArray:
        #Refresh variables for each link
        songNameList = []
        songList = []
        infoList = []
        videoTitle = []
        titleDict = {}
        dirStorage = ''
        searchInput = ''
        artistName = ''
        albumName = ''
        songName = ''
        songCount = 0
        artistIndex = 0

        #Process each link and grab song titles from the pages
        #try:
        page = requests.get(link, headers=headers)#Use requests on the new URL
        soup = BeautifulSoup(page.text, "html.parser")#Take requests and decode it

        #Get album and artist title to save as folder
        searchInput = soup.find('title')
        searchInput = searchInput.contents[0][:-22]

        #Ask user for input regarding the artist's name in the search
        infoList = searchInput.split()
        for item in infoList:
            print(item)

        #Processing search query to find album and artist names
        artistName = searchParse(infoList)
        #Let user know about album info
        print('Artist name: ' + artistName)
        #Update infoList to exclude the artist name
        for word in infoList[len(artistName.split()):]:
            albumName += word + ' '
        print('Album name: ' + albumName + '\n')
        #Create folder based on album info
        dirStorage = artistName + ' - ' + albumName
        dirStorage = dirStorage[:-1]#Remove whitespace at the end of the string
        os.makedirs(dirStorage, exist_ok=True)#Make the folder
        print('Creating folder:' + dirStorage)

        divList = soup.find_all('div', {'class': 'title'})
        for div in divList:
            songList.append(div.contents[0])#Refer to the first item of contents, since .contents returns an array

        #Process each song by appending the song title to the search
        songIndex = songCount
        for item in songList:
            songName = item
            print('\nSong name: ' + songName)
            songIndex -= 1
            #temp stores each song's google search video results
            temp = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(item) + '+' + link[32:]
            #try:
            page = requests.get(temp, headers=headers)#Use requests on the new URL
            soup = BeautifulSoup(page.text, "html.parser")#Take requests and decode it

            #Look for links in search results
            aList = soup.find_all('a', href=True)

            for a in aList:
                if a['href'][:29] == 'https://www.youtube.com/watch':
                    matchIndex = 0
                    titleDict = {}

                    #Check title for matching song title
                    #Try:
                    #Beautiful soup the page, to check the title of the video
                    page = requests.get(a['href'], headers=headers)
                    soup = BeautifulSoup(page.text, "html.parser")
                    nameTag = soup.find('meta', {'name': 'title'})

                    videoTitle = nameTag['content']#store the title of the video in this variable

                    for char in blacklist:
                        videoTitle = videoTitle.replace(char, '')

                    songNameList = songName.split()#Make an array of words from the song title for later

                    #Add each word in the video title to a dictionary
                    for word in videoTitle.split():
                        titleDict[word] = True

                    #Compare words in the song title to words in the dictionary. All words should be present, otherwise don't download the video.
                    for word in songNameList:
                        if word in titleDict:
                            matchIndex += 1

                    #If everything checks out, download the video then break from the loop, moving onto the next song
                    if matchIndex == len(songNameList):
                        print('Saved as: ' + songName)#Print the title of the video for the user to know what files to look for.
                        temp = a['href']
                        YouTube(temp).streams.first().download()
                        songCount += 1

                        scrubbedName = songName
                        for char in blacklist:
                            scrubbedName = scrubbedName.replace(char, '')
                        scrubbedVideoTitle = videoTitle
                        for char in blacklist:
                            scrubbedVideoTitle = scrubbedVideoTitle.replace(char, '')
                        print(scrubbedVideoTitle)

                        #Move downloaded video into folder
                        originDir = os.path.join('.\\' + scrubbedVideoTitle + '.mp4')
                        targetDir = os.path.join('.\\' + dirStorage + '\\' + scrubbedName + '.mp4')
                        shutil.move(originDir, targetDir)

                        #Change file into an mp3
                        fileLoc = convertFile(targetDir)

                        #TODO Figure out how to convert to mp3, then insert tags


                        break



#TODO figure out how to implement try except cases fully
'''
                except TypeError:
                    print('Error:' + str(TypeError.content))

            except TypeError:
                print('Error:' + str(TypeError.content))


        except TypeError:
            print('Error:' + str(TypeError.content))
'''

#Converts given mp4 file into an mp3 file
def convertFile(givenFile):
    resultDirectory = ''

    #TODO: Make file at givenDirectory into an mp3 file instead
    resultFile = givenFile

    return resultFile

#Takes list of words from search, returns words that should be the artist's name
def searchParse(searchTerms):
    artistIndex = 0
    confirmedString = ''

    while artistIndex == 0:
        artistIndex = input('Please input how many words long the artist\'s name is. (Elvis Presley is two words, for example.)\n')
        if artistIndex.isnumeric():#Check to make sure the string is made of numbers
            artistIndex = int(artistIndex)#Convert the string into an integer
            if artistIndex <= 0 or artistIndex > len(searchTerms):#Check if the input is within the
                 print('Sorry, not a valid response. Please try again.')
                 artistIndex = 0
            else:
                for i in range(0, artistIndex):
                    confirmedString += (str(searchTerms[i])) + ' '



        return confirmedString

optionSelect()
