__author__ = 'jeremypriestner'

import optparse
import urllib
import urllib2
import sys
import json

AVG_TITLE_LENGTH = 4  # assumed


# command line tool that takes file containing
# song titles as input and outputs playlist
# tracks to standard output
#
def main():
    p = optparse.OptionParser()
    p.add_option('--file', '-f')
    options, arguments = p.parse_args()
    for track in make_playlist(options.file):
        print track


def make_playlist(filename):
    title_buffer = []
    playlist = []

    with open(filename, 'r') as f:
        for line in f:
            for word in line.split():
                title_buffer.append(word)
                if len(title_buffer) == AVG_TITLE_LENGTH:
                    playlist.append(find_track(title_buffer))

    while len(title_buffer) != 0:
        playlist.append(find_track(title_buffer))

    return playlist


# queries spotify for matches starting with titles of size AVG_TITLE_LENGTH
# and decreasing incrementally down to a single word.  returns track url as
# string or exits with -1 if no possible match
#
# mutates the buffer appropriately depending on what the match is.
#
def find_track(title_buffer):
    title_length = len(title_buffer)

    while title_length > 0:
        song_title = ' '.join(title_buffer[:title_length])
        track_url = query_spotify(song_title)
        if len(track_url) > 0:
            shift_buffer(title_buffer, title_length)
            return track_url
        title_length -= 1

    print 'sorry, a matching playlist could not be constructed :('
    sys.exit(-1)


# returns spotify url for track if there is an exact title match,
# else returns empty string
#
def query_spotify(song_title):
    s = u'track:"'+song_title+'"'
    url = 'https://api.spotify.com/v1/search?type=track&limit=1&q=' + urllib.quote(s.encode("utf-8"))  # this is wrong request, matches too much
    response = urllib2.urlopen(url).read()
    data = json.loads(response)
    spotify_title = data["tracks"]["items"][0]["name"]
    spotify_url = data["tracks"]["items"][0]["external_urls"]["spotify"]
    return spotify_url if spotify_title.lower() == song_title.lower() else ""


def shift_buffer(title_buffer, title_length):
    copy_idx = title_length
    while copy_idx < len(title_buffer):
        title_buffer[copy_idx - title_length] = title_buffer[copy_idx]
        copy_idx += 1

    if len(title_buffer) == 1:
        del title_buffer[:]
    else:
        del title_buffer[title_length:]


if __name__ == '__main__':
    main()