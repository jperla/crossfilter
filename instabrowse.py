import json
import os
import subprocess

import numpy as np
from flask import Flask
app = Flask(__name__)

from flask import request,redirect

@app.route("/")
def index():
    return open('index.html', 'r').read()

@app.route("/ulink/<uid>")
def user_profile(uid):
    filename = '../employees/uids/%s.json' % uid
    pics = json.loads(open(filename, 'r').read())
    url = pics[0]['user']['profile_pic_url']
    username = pics[0]['user']['username']
    #return redirect(url)
    return redirect('http://followgram.me/%s' % username)

@app.route("/usrc/<uid>")
def user_src(uid):
    filename = '../employees/uids/%s.json' % uid
    pics = json.loads(open(filename, 'r').read())
    url = pics[0]['user']['profile_pic_url']
    return redirect(url)

@app.route("/u/<uid>/src/<pid>")
def pic_src(uid, pid):
    filename = '../employees/uids/%s.json' % uid
    pics = json.loads(open(filename, 'r').read())
    for p in pics:
        if p['id'] == pid:
            return redirect(p['image_versions'][-1]['url'])
    else:
        return "not found"

@app.route("/u/<uid>/link/<pid>")
def pic_link(uid, pid):
    from instagram.client import InstagramAPI
    import instagram_keys
    api = InstagramAPI(client_id=instagram_keys.CLIENT_ID, client_secret=instagram_keys.CLIENT_SECRET)
    pic = api.media(pid)

    return redirect(pic.link)

@app.route("/<filename>")
def filename(filename):
    if os.path.exists(filename):
        return open(filename, 'r').read()
    else:
        return 'file not found...'

def getDistanceByHaversine(loc1, loc2):
   '''Haversine formula - give coordinates as a 2D numpy array of
   (lat_decimal,lon_decimal) pairs'''
   # earth's mean radius = 6,371km
   EARTHRADIUS = 6371.0
   from numpy import sin,cos,arctan2,sqrt,pi # import from numpy
   #      
   # "unpack" our numpy array, this extracts column wise arrays
   lat1 = loc1[:,0]
   lon1 = loc1[:,1]
   lat2 = loc2[:,0]
   lon2 = loc2[:,1]
   #
   # convert to radians ##### Completely identical
   lon1 = lon1 * pi / 180.0
   lon2 = lon2 * pi / 180.0
   lat1 = lat1 * pi / 180.0
   lat2 = lat2 * pi / 180.0
   #
   # haversine formula #### Same, but atan2 named arctan2 in numpy
   dlon = lon2 - lon1
   dlat = lat2 - lat1
   a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2.0))**2
   c = 2.0 * arctan2(sqrt(a), sqrt(1.0-a))
   km = EARTHRADIUS * c
   return km

@app.route("/pics/<lat>/<lon>")
def pics(lon, lat):
    loc = np.repeat([[float(lat), float(lon)]], all_locs.shape[0], axis=0)
    distance = getDistanceByHaversine(loc, all_locs)
    r = all_pics[distance < 50.0] # 50km
    return first_line + '\n' + ''.join(r).rstrip('\n')

if __name__ == "__main__":
    all_pics = []
    all_locs = []
    first_line = ''
    print 'loading data...'
    with open('full.csv', 'r') as f:
        for i,p in enumerate(f.readlines()):
            if i == 0:
                first_line = p
            else:
                _, lat, lon = p.rsplit(',', 2)
                all_pics.append(p)
                all_locs.append((float(lat), float(lon)))
    all_locs = np.array(all_locs)
    all_pics = np.array(all_pics)

    print 'data loaded...'
    app.run(port=8888, debug=True)

