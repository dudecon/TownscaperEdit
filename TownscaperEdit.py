# Townscaper Level Editor Utility
# released to the public domain by Paul Spooner
# Latest version at: http://github.com/dudecon/TownscaperEdit
# Version 1.1 2020-07-18
# Run from the save file folder
# (in Windows):
# %user\AppData\LocalLow\Oskar Stalberg\Townscaper

# Version History
# 1.1 2020-07-18 added filllayer(), default for save()
# 
# 1.0 2020-07-15 initial release
# included level load, save(), and functions levelcolor(), randcolor()
# buildoffset(), killrand(), hkill(),and hcull()

infiletemplate = "Town{}.scape"
ALLCOLORS = [i for i in range(15)]
filedata = ""
lev_num = -1
while True:
    userinput = input("Load level #? ")
    try:
        lev_num = int(userinput)
        infile = infiletemplate.format(lev_num)
        print("Loading:",infile)
    except:
        print("That's not a number!")
        continue
    try:
        f = open(infile,'r')
        filedata = f.read()
        f.close()
        print(infile, "successfully read from disc")
        break
    except:
        print("loading",infile,"didn't work")
        continue

def get_tag(s, tag):
    strtstr = '<{}>'.format(tag)
    endstr = '</{}>'.format(tag)
    strtpos = s.find(strtstr) + len(strtstr)
    endpos = s.find(endstr)
    tagdata = s[strtpos:endpos]
    return tagdata
coords_raw = get_tag(filedata,'corners').split('<C>')[1:]
coords = []
coordserial = [] #only for file loading
voxelcount = 0
for raw_str in coords_raw:
    newcoord = {}
    for x in ('x','y','count'): newcoord[x] = int(get_tag(raw_str, x))
    count = newcoord['count'] # recalc on save, no need to keep updated
    newcoord['vox'] = []
    coordserial += [newcoord]*count
    coords.append(newcoord)
    voxelcount += count
del coords_raw
voxels_raw = get_tag(filedata,'voxels').split('<V>')[1:]
voxels = []
voxelsin = 0
heightmap = {}
for raw_str in voxels_raw:
    newcoord = {}
    for x in ('t','h'): newcoord[x] = int(get_tag(raw_str, x))
    newcoord['coord'] = coordserial[voxelsin]
    coordserial[voxelsin]['vox'].append(newcoord)
    h = newcoord['h']
    if h in heightmap.keys(): heightmap[h].append(newcoord)
    else: heightmap[h] = [newcoord]
    voxelsin += 1
    voxels.append(newcoord)
del voxels_raw
if len(coordserial) != voxelcount: print('len(coordserial) != voxelcount')
if len(voxels) != voxelsin: print('len(voxels) != voxelsin')
if voxelcount != voxelsin: print('voxelcount != voxelsin')
if len(coordserial) == voxelcount == len(voxels) == voxelsin: print(voxelsin,'voxels')
del coordserial
del voxelcount
del voxelsin
print("Import complete!\nCall save() to save the file")
print("Call levelcolor() to recolor all at the specified height")
print("Call randcolor() to recolor all blocks with a random value")
print("Call buildoffset() to add voxels on top of or beneath a layer")
print("Call killrand() to remove voxels randomly")
print("Call hkill() to remove a whole layer")
print("Call hcull() to remove all coordinates represented in a layer")
print("Call filllayer() to place blocks at most coordinates on the map")

def save(level_number = -1):
    global lev_num
    if level_number == -1: level_number = lev_num
    global filedata
    try:
        lev_num = int(level_number)
        outfile = infiletemplate.format(lev_num)
    except:
        print("That's not a number! Aborting")
        return False
    print("Serializing data")
    coordtemp = '''
    <C>
      <x>{}</x>
      <y>{}</y>
      <count>{}</count>
    </C>'''
    voxtemp = '''
    <V>
      <t>{}</t>
      <h>{}</h>
    </V>'''
    cornerstring = ""
    voxelstring = ""
    for coord in coords:
        count = len(coord['vox']) # recalc on save, no need to keep updated
        if count == 0: continue
        cornerstring += coordtemp.format(coord['x'],coord['y'],count)
        for vox in coord['vox']:
            t = vox['t']
            h = vox['h']
            if h < 0: h = 0
            if h > 255: h = 255
            if h == 0: t = 15 # tiny bit of error checking
            voxelstring += voxtemp.format(t,h)
    cornerstring += "\n  "
    voxelstring += "\n  "
    filedata = filedata.replace(get_tag(filedata, 'corners'),cornerstring)
    filedata = filedata.replace(get_tag(filedata, 'voxels'),voxelstring)
    print("Saving:",outfile,"with",len(voxels),"voxels")
    try:
        f = open(outfile,'w')
        f.write(filedata)
        f.close()
        print(outfile, "successfully saved to disc")
    except:
        print("saving",outfile,"didn't work")
        return False
    return True

from random import choice
def levelcolor(height, color = -1):
    global heightmap
    if color == -1: color = choice(ALLCOLORS)
    for vox in heightmap[height]:
        if isinstance(color,(list,tuple)):
            thiscolor = choice(color)
        else: thiscolor = color
        vox['t'] = thiscolor
    return True

from random import random
def randcolor(colors = ALLCOLORS, frac = 1):
    global voxels
    for vox in voxels:
        if random() > frac: continue
        thiscolor = choice(colors)
        vox['t'] = thiscolor
    return True

def buildoffset(basis_layer, offset = 0, frac = 0.1, color = -1):
    if color == -1: color = choice(ALLCOLORS)
    global voxels
    global heightmap
    build_height = basis_layer + offset
    if build_height > 255:
        print("built too high")
        return False
    if build_height < 0:
        print("built too low")
        return False
    for vox in heightmap[basis_layer]:
        if random() > frac: continue
        coord = vox['coord']
        alreadythere = False
        for othervox in coord['vox']:
            if othervox['h'] == build_height:
                alreadythere = othervox
                break
        if isinstance(color,(list,tuple)): thiscolor = choice(color)
        else: thiscolor = color
        if alreadythere:
            alreadythere['t'] = thiscolor
        else:
            nv = {}
            nv['coord'] = coord
            nv['t'] = thiscolor
            nv['h'] = build_height
            coord['vox'].append(nv)
            voxels.append(nv)
            if build_height in heightmap.keys():
                heightmap[build_height].append(nv)
            else: heightmap[build_height] = [nv]
    return True

def killrand(frac = 0.1):
    global voxels
    global heightmap
    for vox in voxels:
        if random() > frac: continue
        coord = vox['coord']
        del vox['coord']
        h = vox['h']
        coord['vox'].remove(vox)
        voxels.remove(vox)
        heightmap[h].remove(vox)
    return True

def hkill(height):
    global heightmap
    for vox in heightmap[height]:
        coord = vox['coord']
        del vox['coord']
        coord['vox'].remove(vox)
        voxels.remove(vox)
    del heightmap[height]
    return True

def hcull(height):
    global coords
    global voxels
    global heightmap
    for vox in heightmap[height]:
        coord = vox['coord']
        for ovox in coord['vox']:
            del ovox['coord']
            voxels.remove(ovox)
        coords.remove(coord)
    del heightmap[height]
    return True

def filllayer(height = 0, color = -1):
    if color == -1: color = choice(ALLCOLORS)
    global coords
    global voxels
    global heightmap
    if height not in heightmap.keys():
        heightmap[height] = []
    x = coords[0]['x']
    y = coords[0]['y']
    xl = x
    xs = x
    yl = y
    ys = y
    pci = {} # pre-existing coordinate index (x,y)
    for c in coords:
        x = c['x']
        y = c['y']
        xl = max(x,xl)
        xs = min(x,xs)
        yl = max(y,yl)
        ys = min(y,ys)
        pci[(x,y)] = c
    for xi in range(xs//9,1+xl//9):
        for yi in range(ys//9,1+yl//9):
            if isinstance(color,(list,tuple)): thiscolor = choice(color)
            else: thiscolor = color
            xn = xi*9
            yn = yi*9
            nv = {}
            nv['t'] = thiscolor
            nv['h'] = height
            if (xn,yn) not in pci:
                cn = {}
                cn['count'] = 0
                cn['x'] = xn
                cn['y'] = yn
                cn['vox'] = [nv]
                coords.append(cn)
                nv['coord'] = cn
                voxels.append(nv)
                heightmap[height].append(nv)
            else:
                cn = pci[(xn,yn)]
                #check for existing voxel at specified height
                voxexists = False
                for v in cn['vox']:
                    if v['h'] == height:
                        voxexists = True
                        v['t'] = thiscolor
                    if voxexists: break
                if voxexists: continue
                nv['coord'] = cn
                voxels.append(nv)
                heightmap[height].append(nv)
