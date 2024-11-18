#!/usr/bin/env python
 
# Please contact me by emailing: josj@wjaag.com
#
# LICENSE
# Copyright (c) 2022 Josjuar Lister

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import urllib3
import requests
import sys
import argparse
import webbrowser
from bs4 import BeautifulSoup
from colored import fg
from datetime import datetime
from dateutil.parser import parse
from pip._internal.locations import USER_CACHE_DIR as user_cache_dir

# include these variables in a print() function to output different clours to your terminal
txt_blue = fg('blue')
txt_green = fg('green')
txt_white = fg('white')
txt_red = fg('red')

def set_date(date, language): 
    # The Website address we will be targeting
    # I concatonate todays date onto the end of the URL
    if language == "en":
        base_url = "https://wol.jw.org/en/wol/h/r1/lp-e/"
    elif language == "es":
        base_url = "https://wol.jw.org/es/wol/h/r4/lp-s/"
    elif language == "it":
        base_url = "https://wol.jw.org/it/wol/h/r6/lp-i"
    else:
        print(f"{txt_blue}[warning]{txt_white}I don't recognise this language.")
        print(f"{txt_blue}[info]{txt_white}Please set the endpoint for this language")
        print(f"{txt_blue}[info]{txt_white}Defaulting to English")
        return set_date(date, "en")
    url = base_url + date.strftime('%Y/%m/%d')
    return url

# Including generic User-Agent http header to make us look like a browser
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}

# Fetch todays days text
def fetch(url, verbose):
    if verbose: print("Attempting to fetch the days text from jw.org")
    # Here is where we package our parameters that we will send to our target, they are put into an array that will be passed to 'requests.get' as params
    payload = {}

    # We will wait 15 seconds for a response and try again, if we fail to get a response 3 times we skip that name and move on.
    try:
        r = requests.get(url, params=payload, headers=HEADERS, timeout=15)
    except:
        print(txt_blue + "  (info)\t" + txt_white + " Timed out, retrying")
        try:
            r = requests.get(url, params=payload, headers=HEADERS, timeout=15)
        except:
            print(txt_blue + "  (info)\t" + txt_white + " Timed out, twice, retrying")
            try:
                r = requests.get(url, params=payload, headers=HEADERS, timeout=15)
            except:
                print(txt_red + "  (warn)\t" + txt_white + " Timed out, tree times, skipping")
                pass

    # Decode response from binary into UTF-8 charcters
    ret = r.content.decode('utf-8')

    # Use Beautiful Soup Module to parse html then find and extract all paragraph elements
    soup = BeautifulSoup(ret, "html.parser")
    paragraphs = soup.select("p")
    """
        TODO
        CACHE PARAGRAPHS INSTEAD OF JUST THE DAYS TEXT.
        THIS WILL REDUCE THE AMOUNT THAT WE HAVE TO HIT JW.ORG
    """
    page = 1

    # jw.org sends yesterdays, todays and tomorrows days text, so we need to select the two correct elements.
    # Page 3 is the scripture quote for today.
    # Page 4 is the comments
    for p in paragraphs:
        if page == 3:
            text = txt_green + p.getText() + "\n" + txt_white
        if page == 4:
            text = text + p.getText()
        page = page+1

    return text

# Initialize -- Start Here! Here is where we parse command line argyments.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description='''Here is my lovelly little python script to fetch todays days text from wol.jw.org :-). ''',
        epilog="""Josjuar Lister 2024""")
    parser.add_argument('-d', '--date', help='Specify a date (show today\'s as the default)')
    parser.add_argument('-c', '--cache', help='Enable caching', action='store_true')
    parser.add_argument('-l', '--language', help='Specify the language to fetch', default='en')
    parser.add_argument('-v', '--verbose', help='Increase the verbosity', action='store_true')

    # To use arguments parsed here call 'args.<argument>'
    args=parser.parse_args()

    # Set the correct date and fetch the days text
    if args.date is not None: 
        date = parse(args.date)
    else:
        date = datetime.today()

    url = set_date(date, args.language)
    print(txt_red + date.strftime('%A, %d %B'))
    if args.cache:
        cachedir = user_cache_dir.replace("/.cache/pip", "/.cache/daysTest")
        cached_date_path = cachedir + "/date"
        cached_text_path = cachedir + "/text"
        cached_date_file = None
        cached_text_file = None

        if os.path.exists(cachedir):
            # Check to see if the date is the one we're looking for
            cached_date_file = open(cached_date_path,"r")
            if cached_date_file is None:
                print("Couldn't open the cached date file at " + cached_date_path + " Fetching the days text")
                exit(print(fetch(url)))
            cached_date = cached_date_file.read()
            if cached_date == date.strftime("%d%m%Y"):
                # We got the correct day
                if args.verbose: print("Here's the cached text:")
                cached_text_file = open(cached_text_path,"r")
                if cached_text_file is None:
                    print("Couldn't open the cached text file at " + cached_text_path + " Fetching the days text")
                    exit(print(fetch(url)))
                print(cached_text_file.read())
            else:
                if args.verbose: print("We have an old cache, updating")
                cached_text_file = open(cached_text_path, "w")

                text = fetch(url, args.verbose)
                print(text)
                cached_text_file.write(text)
                cached_date_file.close()
                cached_date_file = open(cached_date_path, "w")
                cached_date_file.write(date.strftime("%d%m%Y"))
        else:
            # Make the Cache directory
            if args.verbose: print("We have never cached before")
            try:
                os.mkdir(cachedir)
            except:
                print("Couldn't create the cache directory at: " + cachedir + " Nothing was cached")
                exit(print(fetch(url, args.verbose)))
            # Cache the days text
            cached_date_file = open(cached_date_path,"w")
            cached_text_file = open(cached_text_path,"w")
            
            # Ok Now let's get the text
            text = fetch(url, args.verbose)
            print(text)

            cached_date_file.write(date.strftime("%d%m%Y"))
            cached_text_file.write(text)
        cached_date_file.close()
        cached_text_file.close()

    else:
        print(fetch(url, args.verbose))
    
else:
    exit(1)
