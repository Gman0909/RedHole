#!/usr/bin/env python2
# RedHole - Reddit Media Scraper
# /u/Augmentl, 2017
# This script will download the last [x] images you have saved in your Reddit user account, or from any subreddit.
# Please make sure you edit the client_id and client_secret variables in CONFIG.INI
# You can get your Client ID and Secret from https://www.reddit.com/prefs/apps (create a new app and select script for personal use)

# Use -a at the command line to scan all subs in the ini file, -m to scan all your subscribed subs, -s [string] for specific sub, -q [string] to search matching subs

import sys
import praw
import urllib.request
import getpass
import os
from optparse import OptionParser
from urllib.parse import urlparse
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

reddit = None
parser = OptionParser()
options = None
args = None
client_id=""
client_secret = ""
dl_path = ""
subreddits = 'all'
subreddit_folders = 'no'

image_formats = [".jpg", ".png", ".gif", ".mp4", ".mov"]

image_counter = 0

#Read the CONFIG.ini file to grab the user's client ID and Secret for authentication, download path and subs

def read_ini():
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(thisfolder, 'CONFIG.ini')
    if os.path.isfile('CONFIG.ini'):
        global client_id
        global client_secret
        global dl_path
        global subreddits
        global subreddit_folders

        # instantiate
        config = ConfigParser()
        config.read(config_path)

        # parse existing fileconfig.read('CONFIG.ini')        
        # read values from CLIENT section
        
        client_id = config.get('CLIENT','client_id')
        client_secret = config.get('CLIENT','client_secret')
        dl_path = os.path.abspath(config.get('DOWNLOAD','dl_path'))
        subreddit_folders = config.get('DOWNLOAD','subreddit_folders')
        subreddits = config.get('INCLUDE','subreddits')
        subreddits = subreddits.replace(" ","")
        subreddits = str(subreddits).split(',')
        if  subreddits[0] == '':
            subreddits = ['all']
        
        #print ("Initialising - Client ID: %s , Client Secret: %s" % (client_id, client_secret))
        print ("Subreddits to include in scan:", subreddits)
        print ("Downloading images to:", os.path.abspath(dl_path))

    else:
        create_ini()
        sys.exit(0)

def create_ini():
    global client_id
    global client_secret
    global dl_path
    global subreddits
    global subreddit_folders

    config = ConfigParser()

    with open('CONFIG.ini', 'wb') as configfile:
        configfile.write('# RedHole Reddit Media Scraper configuration file\r\n')
        configfile.write('# Please make sure you edit the client_id and client_secret variables in CONFIG.ini\r\n')
        configfile.write('# You can get your Client ID and Secret from  https://www.reddit.com/prefs/apps (create a new app and select script for personal use)\r\n')
        configfile.write(' \r\n')
        configfile.write('[CLIENT]')
        configfile.write(' \r\n')
        configfile.write('client_id = xxxxxxxxxxxxxxxxxx')
        configfile.write(' \r\n')
        configfile.write('client_secret = xxxxxxxxxxxxxxxxxx')
        configfile.write(' \r\n')
        configfile.write('[DOWNLOAD]')
        configfile.write(' \r\n')
        configfile.write('dl_path = RedditImages')
        configfile.write(' \r\n')
        configfile.write('subreddit_folders = no')
        configfile.write(' \r\n')
        configfile.write('# Below is a comma separated list of subs from which to download saved images.\r\n')
        configfile.write('# Leave blank for all subreddits.\r\n')
        configfile.write(' \r\n')
        configfile.write('[INCLUDE]')
        configfile.write(' \r\n')
        configfile.write('subreddits = aww, pics, funny, wallpapers')

        config.write(configfile)
    

class ImageFile(object):
    def  __init__(self, name,extension):
        self.name = name
        self.extension = extension
        
class User(object):
    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd
        
def login():
    global reddit
    name = ''
    passwd = ''    
    while len(name) == 0: 
        name = input("Reddit username: ")
    while len(passwd) == 0: 
        passwd = getpass.getpass("Reddit password: ")        
    reddit = praw.Reddit(client_id=client_id,
        client_secret=client_secret,
        user_agent="RedHole Reddit Media Scraper by /u/%s" % ("Augmentl"),
        username = name,
        password = passwd)
    return User(name , passwd)      

# Check if a URL is an image by comparing it against the supported domain names and extensions

def check_if_image(url):
    filename = url.split('/')[-1]
    extension = '.' + filename.split('.')[-1]
    if extension in image_formats:
        return True
    else:
        return False
                    
# Change to the download path, or create it if it's not there.

def changepath(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    os.chdir(path)
    
# Download an image file!

def download(url, subreddit):
    global image_counter
    if subreddit_folders ==  'yes':
        
        changepath(os.path.abspath(dl_path + os.path.sep + subreddit))
    else:
        changepath(os.path.abspath(dl_path))
    file_name = subreddit + "-" + url.split('/')[-1]
    print ("downloading " + file_name)
    urllib.request.urlretrieve(url, file_name)
    image_counter +=1

    
# Go through the list of the latest [x] url's on the user's Saved list (based on the value of limiter)
# and, if they're images, feed them to the downloader 

def get_saved_images(limiter):
        global subreddits
        print ('Scanning saved images')    
        for submission in reddit.redditor(user.name).saved(limit = limiter):
            subreddit = str(submission.subreddit)
            try:
                url = submission.url
            except:
                None            
            if subreddits != ['all']:
                if check_if_image(url) and subreddit in subreddits:
                    try:
                        download(url, subreddit)
                    except:
                        print (url, 'could not be downloaded')
            else:
                if check_if_image(url):
                    try:
                        download(url, subreddit)
                    except:
                        print (url, 'could not be downloaded')   

# Go through the list of the latest [x] url's on any sub matching the list in the .ini.
# and, if they're images, feed them to the downloader.
# Activated if -a is used as a startup parameter

def get_sub_images(limiter):
        for sub in subreddits:
            print ('scanning', sub)
            for submission in reddit.subreddit(sub).hot(limit=limiter):
                subreddit = str(submission.subreddit)
                try:
                    url = submission.url
                except:
                    None
                if check_if_image(url):
                    try:
                        download(url, subreddit)
                    except:
                        print (url, 'could not be downloaded')


def get_my_images(limiter):
    print ('Scanning all subscribed subreddits')
    subreddits = list(reddit.user.subreddits(limit=None))
    for entry in subreddits:
        sub = entry.display_name
        print ('Scanning', sub)
        for submission in reddit.subreddit(sub).hot(limit=limiter):
            subreddit = str(submission.subreddit)
            try:
                url = submission.url
            except:
                None
            if check_if_image(url):
                try:
                    download(url, subreddit)
                except:
                    print (url, 'could not be downloaded')

def get_input_parameters():
    global parser
    global options
    global args
    parser.add_option('-a', action ='store_true', dest='allsubs', default = False)
    parser.add_option('-m', action ='store_true', dest='mysubs', default = False)
    parser.add_option('-s', action='store', type='string', nargs = 1, dest='query', default = '')
    parser.add_option('-q', action='store', type='string', nargs = 1, dest='subsearch', default = '')
    (options, args) = parser.parse_args()
    
def get_matching_subs(query):
    global reddit
    global subreddits
    subreddits = []
    results = list(reddit.subreddits.search_by_name(query, include_nsfw=True, exact=False))
    for item in results:
        try:
            #print item.display_name
            subreddits.append(item.display_name)
        except:
            None
    #print subreddits

print ("RedHole - Reddit Media Scraper, @Augmentl, 2017")
print ('Scan options: -a for all subs in CONFIG.ini, -m for all subscribed subs, -s [string] for specific sub')
print ()

#Check for a config file, or create one if it does not exist

if os.path.isfile('CONFIG.ini'):
    read_ini()
else:
    create_ini()
    print ("CONFIG.ini not found. I've created one now, go edit it!")
    sys.exit(0)
    
get_input_parameters()

# Get onto Reddit, and create a Reddit instance we can manipulate 
   
user = login()

# Ask the user how many posts from the latest to go back to scan for images

limiter = input("Max. number of posts to scan back? (leave blank for all):    ")
print ()
if not limiter:
    limiter = 9999    
    
# Get the list of images in the user's Saved folder on Reddit, and get downloadin'


try:
    if options.allsubs:
        #print 'option 1 - allsubs'
        get_sub_images(int(limiter))    
    elif options.mysubs:
        #print 'option 2 - mysubs'
        get_my_images(int(limiter))
    elif len(options.query) > 0:
        #print 'option 3 - seach query', options.query
        subreddits = []
        subreddits += options.query.split(',')
        get_sub_images(int(limiter))
    elif len(options.subsearch) > 0:
        #print 'option 4 - seach for subs', options.subsearch
        get_matching_subs(options.subsearch)
        get_sub_images(int(limiter))
    else:
        #print 'default - saved posts'
        get_saved_images(int(limiter))

except:
    print ('Failed to retrieve images. Have you checked your authentication details?')
    sys.exit(0)

print ()
print ("%s images matched your selected subreddits. Have a nice day!" % (image_counter))
print ()

endprompt = input("Press any key to close.")
