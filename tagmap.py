"""
Manage and report on locations of sensors on a factory floor

Jeff Oxenberg
"""
import hug
from PIL import Image, ImageDraw, ImageFont
import MySQLdb
from contextlib import closing

#tag radius
r = 25
#initial locations
locations = {"tag1": "maint","tag2": "maint","tag3": "store","tag4": "oper"}
idmap = {"503130303030303300000000": "tag1", "503130303030303100000000": "tag2",\
    "201311248725010001000002": "tag3","503130303030303200000000": "tag4"}
locmap = {"1": "oper", "2": "maint", "3": "store"}

def updateLocations():
    db=MySQLdb.connect(host="16.91.22.180",user="admin",
                      passwd="Moonshot1",db="mysql_png_poc")
    with closing( db.cursor() ) as c:
        #http://stackoverflow.com/questions/17327043/how-can-i-select-rows-with-most-recent-timestamp-for-each-key-value
        c.execute("""SELECT * FROM rfid_tool_tracking L LEFT JOIN rfid_tool_tracking R ON L.RFID_tag = R.RFID_tag AND L.Date_Time < r.Date_Time WHERE isnull (r.RFID_tag)""")
        result = c.fetchall()
    #update location dictionary
    for x in result:
        locations[idmap[x[1]]] = locmap[x[0]]
    db.close()

def redraw():
    updateLocations()
    #initial coordinates
    mxy = [450,100]
    oxy = [75,650]
    sxy = [950,650]

    img = Image.open("RFID_map.png")
    fnt = ImageFont.truetype('arial.ttf', 20)
    pt = ImageDraw.Draw(img)
    #todo: separate this into its own function
    for sens in locations:
        if locations[sens] == "maint":
            pt.ellipse((mxy[0]-r, mxy[1]-r, mxy[0]+r, mxy[1]+r), fill=(0,255,0))
            pt.text((mxy[0]-20,mxy[1]-10), sens, font=fnt, fill=(0,0,0,255))
            mxy[0] += 75
        elif locations[sens] == "oper":
            pt.ellipse((oxy[0]-r, oxy[1]-r, oxy[0]+r, oxy[1]+r), fill=(0,255,0))
            pt.text((oxy[0]-20,oxy[1]-10), sens, font=fnt, fill=(0,0,0,255))
            oxy[0] += 75
        elif locations[sens] == "store":
            pt.ellipse((sxy[0]-r, sxy[1]-r, sxy[0]+r, sxy[1]+r), fill=(0,255,0))
            pt.text((sxy[0]-20,sxy[1]-10), sens, font=fnt, fill=(0,0,0,255))
            sxy[0] += 75
    return img

@hug.post('/addtag')
def addtag(body):
    """
    Add new tag
    POST to /addtag
    {
            "tagid": "tagID", // unique tag ID
            "name": "tagname", // tag short name (tag1, 2, etc)
            "initial": "1" // initial tag location
    }
    """
    #check whether correct params given
    if set(["tagid", "name", "initial"]).issubset(body):
        idmap[body["tagid"]] = body["name"]
        locations[body["name"]] = locmap[body["initial"]]
        return "tag added"
    else:
        return "improper format, need tagid, name"

@hug.get('/map.png', output=hug.output_format.png_image)
def getmap():
    """
        Get map of tag locations
    """
    i = redraw()
    return i
