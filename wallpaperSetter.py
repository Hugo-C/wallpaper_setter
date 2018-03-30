# set the wallpaper
# 07/10/2017

import os
import time
import urllib.request
import logging
import ctypes
import praw
#import twitter

SUBREDDIT = "wallpapers+BackgroundArt+wallpaper+videogamewallpapers"
SPI_SETDESKWALLPAPER = 20
URL_FILE = "url.imageLast"
LOGIN_FILE = "login.txt"

DEFAULT_WALLPAPER = "https://cdn.allwallpaper.in/wallpapers/1920x1080/1236/" \
                    "404-error-minimalistic-not-found-text-1920x1080-wallpaper.jpg"


def find_top_image_url(subreddit_name):

    def save_url(url):
        with open(URL_FILE, 'a') as f:
            f.write(url + "\n")

    def load_urls():
        try:
            with open(URL_FILE) as f:
                urls = f.readlines()
        except FileNotFoundError:
            logging.info("can't find the last image used")
            urls = "error"
        return urls

    def load(file, name):
        line = file.readline()[:-1]  # we don't need the last '\n'
        assert line.split("=")[0] == name
        return line.split("=")[1]

    def load_login():
        try:
            with open(LOGIN_FILE) as lf:
                my_client_id = load(lf, "client_id")
                my_client_secret = load(lf, "client_secret")
                my_username = load(lf, "username")
                my_password = load(lf, "password")
        except FileNotFoundError:
            logging.error("can't find the login file")
        except AssertionError:
            logging.error("login file not valid")
        return my_client_id, my_client_secret, my_username, my_password

    res = {'url': DEFAULT_WALLPAPER}
    client_id, client_secret, username, password = load_login()
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent='by /u/Hugo-C',
                         username=username,
                         password=password)
    subreddit = reddit.subreddit(subreddit_name)
    last = load_urls()
    for submission in subreddit.hot(limit=25):
        if (submission.url not in "".join(last)) and \
                (submission.url.endswith(".jpg") or submission.url.endswith(".png")):
            print("wallpaper found : ")
            msg = "{} : {} by  u/{}".format(str(submission.ups), submission.title, submission.author.name)
            print(msg)
            logging.info(msg)
            res = {'url': submission.url, 'title': submission.title, 'author': 'u/' + submission.author.name}
            save_url(res['url'])
            break
    return res


def url_to_local(url):
    return url.split('/')[-1]


def download_image(url):
    """download the image at the given url and give the local_name the image was save in the current directory"""
    local_name = url_to_local(url)
    urllib.request.urlretrieve(url, local_name)
    return local_name


def set_wallpaper(path):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)

"""  NOT USED IN THIS VERSION
def tweet_image(data):
    
    text = "{} posted on @reddit : {} #wallpaper".format(data['author'], data['title'])
    twitter.tweet_media(url_to_local(data['url']), text)
"""


def main():
    logging.basicConfig(filename="log.txt", level=logging.DEBUG)
    logging.debug("---------------------------START----------------------------------")
    log_time = time.gmtime(time.time())
    logging.debug("time : " + str(log_time.tm_min) + ":" + str(log_time.tm_hour) + ", " +
            str(log_time.tm_mday) + "/" + str(log_time.tm_mon) + "/" + str(log_time.tm_year))
    try:
        my_image = find_top_image_url(SUBREDDIT)
        local = download_image(my_image['url'])
        abs_path = os.getcwd() + '\\' + local
        set_wallpaper(abs_path)
        time.sleep(2)
        print("wallpaper changed, you can close this window")
        # if my_image['url'] != DEFAULT_WALLPAPER:
        #    tweet_image(my_image)
    except Exception as e:
        logging.error(e)
    logging.debug("---------------------------STOP----------------------------------\n\n")
    time.sleep(8)

if __name__ == '__main__':
    main()
