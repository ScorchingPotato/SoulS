from world import *

def construct(map,game,pos):
    tiles=[]
    for y,l in enumerate(map):
        for x,t in enumerate(l):
            if not t:continue
            if t[0] == "w": #full water tile
                tiles.append(Tile("water",(x*64,y*64)))
            if t[0] == "s": #shore water tile
                tiles.append(Tile("water",(x*64,y*64)))
                tiles.append(Tile("shore",(x*64,y*64),t[1],int(t[2])*90))
            if t[0] == "p": #path tile
                tiles.append(Tile("path",(x*64,y*64),t[1],int(t[2])*90))
            if t[0] == "@":
                tiles.append(Tile("@",(x*64,y*64)))

    return Wrapper(game,pos,tiles,(len(map[0])*64,len(map)*64))