import json
import os
import datetime

def getFromWeek(week, year):
    d = str(year) + "-W" + str(week)
    r = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")
    t = {}
    t[0] = str(int(datetime.datetime.timestamp(r) - 86400 * 7))
    t[1] = str(int(datetime.datetime.timestamp(r)) - 1)
    return t

def average(lst): 
    return int(sum(lst) / len(lst))

DATATREE = {}
HTMLOBJ = '''<div class="card xl-2">
                <div class="card-header">
                    <h4 class="my-0 font-weight-normal">Week [WEEK] - [YEAR]</h4>
                </div>
                <div class="card-body">
                    <div class="maps" id="map-[YEAR]-[WEEK]"></div>
                    <script>var map_[YEAR]_[WEEK] = [ [LONGLAT] ]</script>
                    <div>
                        <h5>Stats for this week</h5>
                    </div>
                    <ul class="list mb-2">
                        <li>📨 <b>[EMAIL_IN]</b> emails received and <b>[EMAIL_OUT]</b> sent.</li>
                        <li>👨‍💻 <b>[COMMITS]</b> <a href="https://github.com/bobvanluijt?tab=overview&from=[YEAR]-12-01&to=[YEAR]-12-08" target="_blank">commits</a> on Github.</li>
                        <li>🐦 <a href="[TWEETLINK]" target="_blank">Tweets this week</a>.</li>
                        <li>📅 I've had [MEETINGS] meetings with [PEOPLE] people.</li>
                        <li>🌍 Cities I've visited [VISITS]</li>
                        <li>🎵 Albums I've listened to [TRACKS]</li>
                    </ul>
                </div>
            </div>'''
HTMLFINALOBJ = ""

directory = './data'
for filename in os.listdir(directory):
    if filename.endswith(".json"):
        with open(os.path.join(directory, filename)) as json_file:
            data = json.load(json_file)
            for key, value in data.items():
                if key not in DATATREE:
                    DATATREE[key] = {}
                for keyWeek, valueWeek in value.items():
                    DATATREE[key][keyWeek] = valueWeek

ALLWEEKS = []
ALLEMAILSIN = []
ALLEMAILSOUT = []
ALLCOMMITS = []
ALLMEETINGS = []
ALLPEOPLE = []

year = 2100
counter = 0
while year > 2015:
    if str(year) in DATATREE:
        week = 52
        while week >= 1:
            if str(week) in DATATREE[str(year)]:

                current = DATATREE[str(year)][str(week)]

                HTMLOBJIND = ""

                if (counter % 2) == 0:
                    HTMLOBJIND = '<div class="card-deck mb-2">' + "\n" + HTMLOBJ
                else:
                    HTMLOBJIND = HTMLOBJ

                HTMLOBJIND = HTMLOBJIND.replace('[WEEK]', str(week))
                HTMLOBJIND = HTMLOBJIND.replace('[YEAR]', str(year))
                HTMLOBJIND = HTMLOBJIND.replace('[EMAIL_IN]', str(current['email']['toMe']))
                HTMLOBJIND = HTMLOBJIND.replace('[EMAIL_OUT]', str(current['email']['fromMe']))
                HTMLOBJIND = HTMLOBJIND.replace('[COMMITS]', str(current['commits']))
                HTMLOBJIND = HTMLOBJIND.replace('[MEETINGS]', str(current['meetings']['meetings']))
                HTMLOBJIND = HTMLOBJIND.replace('[PEOPLE]', str(current['meetings']['people']))

                ALLWEEKS.append("'week " + str(week) + ' ' + str(year))
                ALLEMAILSIN.append(int(current['email']['toMe']))
                ALLEMAILSOUT.append(int(current['email']['fromMe']))
                ALLCOMMITS.append(int(current['commits']))
                ALLMEETINGS.append(int(current['meetings']['meetings']))
                ALLPEOPLE.append(int(current['meetings']['people']))

                pins = ''
                if 'location' in current:
                    for key, value in current['location'].items():
                        for location in value[0]:
                            pins = pins + '{ "lng": ' + str(location['lng']) + ', "lat": ' + str(location['lat']) + ' }' + ','
                    HTMLOBJIND = HTMLOBJIND.replace('[LONGLAT]', pins[:-1])

                visits = '<ul class="list mb-2">'
                if 'location' in current:
                    for key, value in current['location'].items():
                        visits = visits + '<li><a href="https://en.wikipedia.org/w/index.php?title=Special%3ASearch&go=Go&ns0=1&search=' + key + '" target="_blank">' + key + '</a>' + '</li>'
                    visits = visits + '</ul>'
                    HTMLOBJIND = HTMLOBJIND.replace('[VISITS]', visits)
                else:
                    HTMLOBJIND = HTMLOBJIND.replace('<li>🌍 I\'ve visited [VISITS]</li>', '')

                tracks = '<ul class="list mb-2">'
                if 'music' in current:
                    for key, value in current['music'].items():
                        tracks = tracks + '<li><a href="' + value + '" target="_blank">' + key + '</a>' + '</li>'
                    tracks = tracks + '</ul>'
                    HTMLOBJIND = HTMLOBJIND.replace('[TRACKS]', tracks)
                else:
                    HTMLOBJIND = HTMLOBJIND.replace('<li>🎵 Albums I\'ve listened to [TRACKS]</li>', '')

                weekT = getFromWeek(week, year)
                weekT0 = datetime.datetime.fromtimestamp(float(weekT[0]))
                weekT1 = datetime.datetime.fromtimestamp(float(weekT[1]))
                HTMLOBJIND = HTMLOBJIND.replace('[TWEETLINK]', 'https://twitter.com/search?q=(from%3Abobvanluijt)%20since%3A'+str(weekT0.year)+'-'+str(weekT0.month)+'-'+str(weekT0.day)+'%20until%3A'+str(weekT1.year)+'-'+str(weekT1.month)+'-'+str(weekT1.day)+'%20-filter:replies&src=typed_query&f=live')

                if (counter % 2) == 1:
                    HTMLOBJIND = HTMLOBJIND + "\n" + '</div>'

                counter += 1

                HTMLFINALOBJ = HTMLFINALOBJ + HTMLOBJIND

            week -= 1

        if (counter % 2) != 0:
            HTMLFINALOBJ = HTMLFINALOBJ + '</div>'

    year -= 1

##
# SET FINAL DATA AND SAVE TO INDEX
##
html_file = open('./html/index.template.html', 'r')
html_file = html_file.read().replace('[VISITCONTENT]', HTMLFINALOBJ)
html_file = html_file.replace('[ALLWEEKS]', '"📨 in", "📨 out", "📅", "👩👨in 📅", "Github 👨‍💻"') 
html_file = html_file.replace('[ALLEMAILSIN]', str(average(ALLEMAILSIN)))
html_file = html_file.replace('[ALLEMAILSOUT]', str(average(ALLEMAILSOUT)))
html_file = html_file.replace('[ALLMEETINGS]', str(average(ALLMEETINGS)))
html_file = html_file.replace('[ALLPEOPLE]', str(average(ALLPEOPLE)))
html_file = html_file.replace('[ALLCOMMITS]', str(average(ALLCOMMITS)))

##
# Get foursquare data
##
with open(os.path.join(directory, 'foursquare_full.json')) as json_file:
    data = json.load(json_file)
    html_file = html_file.replace(
        '[FOURSQUARE]', 'var full_map = ' + str(json.dumps(data)))

file = open('index.html', 'w')
file.write(html_file)
file.close()
