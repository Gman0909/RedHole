##RedHole##

#A Reddit media scraper with customisable filters#

RedHole is a media scraper for Reddit. It lets you download any image or video embedded within your saved posts, the latest hot media files from all your subscribed subreddits, or specify a specific subreddit to scrape for media. 

With Redhole, you can easily keep an up-to-date local library of Reddit media, instantly create ad-hoc image collections for posting to imgur, or quickly grab a specific number of images from a subject-specific subreddit. RedHole ensures the same file is never downloaded twice, and can also organise your downloaded media into folders by subreddit.

#Setup#

RedHole requires Python 3 with PRAW installed. RedHole has been tested on Windows and MacOS. 

You'll need to get your authentication details from https://www.reddit.com/prefs/apps. Select new app and select script for personal use, then copy the ID and Secret fields into their respective entries in CONFIG.ini. 

Run the script, and you're good to go!

Your command line options are:

* None: Scan for media files only in you Saved posts on Reddit, and filter by any subs specified in CONFIG.ini
* -a to scan all subs in the .ini file, not just Saved posts.
* -m to scan all your subscribed subreddits for the latest Hot posts
* -s [subreddit] to search for a specific subreddit, e.g. **"python Redhole1.0.py -s wallpapers"**
* -q [subreddit] to search and scrape any subreddits matching the keyword, e.g. **"python Redhole1.0.py -s cat"**

Enjoy!
