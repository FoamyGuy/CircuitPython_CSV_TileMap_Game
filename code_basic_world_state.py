import board
import displayio
import adafruit_imageload
from displayio import Palette
from adafruit_pybadger import PyBadger

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

MAP_HEIGHT = 8
MAP_WIDTH = 10

MAP = {}

WORLD_STATE = {}


def is_tile_moveable(tile_coords):
    return TILES[WORLD_STATE[tile_coords[0], tile_coords[1]]]['can_walk']

def allow_push(to_coords, from_coords):
    print("inside allow push")
    print("%s -> %s" % (from_coords, to_coords))
    if to_coords[0] < from_coords[0]:
        print("moving left")
        if is_tile_moveable((to_coords[0]-1, to_coords[1])):
            tile_name = WORLD_STATE[to_coords]
            WORLD_STATE[to_coords] = "floor"
            WORLD_STATE[(to_coords[0]-1, to_coords[1])] = tile_name
            
            #entity_sprites[entity_sprites_dict[to_coords]].x = int((to_coords[0]-1)*16)
            print("dict before %s" % entity_sprites_dict)
            entity_sprites_dict[int(to_coords[0]-1), int(to_coords[1])] = entity_sprites_dict[to_coords]
            del entity_sprites_dict[to_coords]
            print("dict after %s" % entity_sprites_dict)
            return True
        # moving left
    elif to_coords[0] > from_coords[0]:
        print("moving right")
        if is_tile_moveable((to_coords[0]+1, to_coords[1])):
            tile_name = WORLD_STATE[to_coords]
            WORLD_STATE[to_coords] = "floor"
            WORLD_STATE[(to_coords[0]+1, to_coords[1])] = tile_name
            
            #entity_sprites[entity_sprites_dict[to_coords]].x = int((to_coords[0]-1)*16)
            print("dict before %s" % entity_sprites_dict)
            entity_sprites_dict[int(to_coords[0]+1), int(to_coords[1])] = entity_sprites_dict[to_coords]
            del entity_sprites_dict[to_coords]
            print("dict after %s" % entity_sprites_dict)
            return True
        # moving right
        pass
    elif to_coords[1] < from_coords[1]:
        print("moving up")
        if is_tile_moveable((to_coords[0], to_coords[1]-1)):
            tile_name = WORLD_STATE[to_coords]
            WORLD_STATE[to_coords] = "floor"
            WORLD_STATE[(to_coords[0], to_coords[1]-1)] = tile_name
            
            #entity_sprites[entity_sprites_dict[to_coords]].x = int((to_coords[0]-1)*16)
            print("dict before %s" % entity_sprites_dict)
            entity_sprites_dict[int(to_coords[0]), int(to_coords[1]-1)] = entity_sprites_dict[to_coords]
            del entity_sprites_dict[to_coords]
            print("dict after %s" % entity_sprites_dict)
            return True
        # moving up
        pass
    elif to_coords[1] > from_coords[1]:
        print("moving down")
        if is_tile_moveable((to_coords[0], to_coords[1]+1)):
            tile_name = WORLD_STATE[to_coords]
            WORLD_STATE[to_coords] = "floor"
            WORLD_STATE[(to_coords[0], to_coords[1]+1)] = tile_name
            
            #entity_sprites[entity_sprites_dict[to_coords]].x = int((to_coords[0]-1)*16)
            print("dict before %s" % entity_sprites_dict)
            entity_sprites_dict[int(to_coords[0]), int(to_coords[1]+1)] = entity_sprites_dict[to_coords]
            del entity_sprites_dict[to_coords]
            print("dict after %s" % entity_sprites_dict)
            return True
        # moving down
        pass
    
    return False
 
TILES = {
    "floor": {
        "sprite_index": 7,
        "can_walk": True
    },
    "top_wall": {
        "sprite_index": 4,
        "can_walk": False
    },
    "top_right_wall": {
        "sprite_index": 5,
        "can_walk": False
    },
    "top_left_wall": {
        "sprite_index": 3,
        "can_walk": False
    },
    "bottom_right_wall": {
        "sprite_index": 11,
        "can_walk": False
    },
    "bottom_left_wall": {
        "sprite_index": 9,
        "can_walk": False
    },
    "right_wall": {
        "sprite_index": 8,
        "can_walk": False
    },
    "left_wall": {
        "sprite_index": 6,
        "can_walk": False
    },
    "bottom_wall": {
        "sprite_index": 10,
        "can_walk": False
    },
    "robot": {
        "sprite_index": 1,
        "can_walk": True,
        "entity": True,
        "before_move": allow_push
    },
    "heart": {
        "sprite_index": 2,
        "can_walk": True,
        "entity": True,
    },
    "player": {
        "sprite_index": 0,
        "entity": True,
    }
    
    
}

# Badger object for easy button handling
badger = PyBadger()

display = board.DISPLAY

# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("/castle_sprite_sheet.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

#print(palette.get_len())
#palette[0] = 0xFFFFFF
palette.make_transparent(5)

entity_sprites = []
entity_sprites_dict = {}



# Create the castle TileGrid
castle = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width = 10,
                            height = 8,
                            tile_width = 16,
                            tile_height = 16)

# Create a Group to hold the sprite and add it
sprite_group = displayio.Group(max_size=48)


# Create a Group to hold the castle and add it
castle_group = displayio.Group()
castle_group.append(castle)

# Create a Group to hold the sprite and castle
group = displayio.Group()

# Add the sprite and castle to the group
group.append(castle_group)
group.append(sprite_group)

f = open("map.csv", 'r')
map_csv_str = f.read()
f.close()

map_csv_lines = map_csv_str.replace("\r", "").split("\n")

print(TILES.keys())

print("===")

print(map_csv_lines)
for y, line in enumerate(map_csv_lines):
    if line != "":
        print(line)
        for x, tile_name in enumerate(line.split(",")):
            MAP[x,y] = tile_name
            WORLD_STATE[x,y] = tile_name
            
            print("%s '%s'" % (len(tile_name), str(tile_name)))
            if tile_name in TILES.keys():
                castle[x, y] = TILES[tile_name]['sprite_index']
                if 'entity' in TILES[tile_name].keys() and TILES[tile_name]['entity']:
                    castle[x, y] = TILES['floor']['sprite_index']
                    if tile_name == "player":
                        # Create the sprite TileGrid
                        sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width = 1,
                            height = 1,
                            tile_width = 16,
                            tile_height = 16,
                            default_tile = TILES[tile_name]['sprite_index'])
                            
                        sprite.x = x*16
                        sprite.y = y*16
                        sprite_group.append(sprite)
                        
                    else:
                        entity_srite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width = 1,
                                    height = 1,
                                    tile_width = 16,
                                    tile_height = 16,
                                    default_tile = TILES[tile_name]['sprite_index'])
                        entity_srite.x = x*16
                        entity_srite.y = y*16
                        entity_sprites.append(entity_srite)
                        entity_sprites_dict[x,y] = len(entity_sprites) - 1
                        
                else:
                    castle[x, y] = TILES[tile_name]['sprite_index']
            else:
                print("tile: %s not found in TILES dict" % tile_name)
                



# put the sprite somewhere in the castle
#sprite.x = 16*3
#sprite.y = 16*2



for entity in entity_sprites:
    sprite_group.append(entity)
    
# Add the Group to the Display
display.show(group)

prev_up = False
prev_down = False
prev_left = False
prev_right = False



def can_player_move(direction):
    if direction == UP:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_above_coords = [player_map_coords[0], player_map_coords[1] - 1]
        return TILES[WORLD_STATE[tile_above_coords[0], tile_above_coords[1]]]['can_walk']
        
    if direction == DOWN:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_below_coords = [player_map_coords[0], player_map_coords[1] + 1]
        return TILES[WORLD_STATE[tile_below_coords[0], tile_below_coords[1]]]['can_walk']
        
    if direction == LEFT:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_left_of_coords = [player_map_coords[0]-1, player_map_coords[1]]
        return TILES[WORLD_STATE[tile_left_of_coords[0], tile_left_of_coords[1]]]['can_walk']
        
    if direction == RIGHT:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_right_of_coords = [player_map_coords[0] + 1, player_map_coords[1]]
        return TILES[WORLD_STATE[tile_right_of_coords[0], tile_right_of_coords[1]]]['can_walk']

        
        
def draw_world_state():
    for y in range(0, MAP_HEIGHT):
        for x in range(0, MAP_WIDTH):
            tile_name = WORLD_STATE[x, y]
            if 'entity' in TILES[tile_name].keys() and TILES[tile_name]['entity']:
                if tile_name != "player":
                    castle[x, y] = TILES["floor"]['sprite_index']
                    
                    entity_sprites[entity_sprites_dict[x,y]].x = x*16
                    entity_sprites[entity_sprites_dict[x,y]].y = y*16
            
            
while True:
    #badger.auto_dim_display(delay=10)
    cur_up = badger.button.up
    cur_down = badger.button.down
    cur_right = badger.button.right
    cur_left = badger.button.left
    
    if not cur_up and prev_up:
        if can_player_move(UP):
            if "before_move" in TILES[WORLD_STATE[sprite.x/16, (sprite.y-16)/16]].keys():
                print("need to call before_move")
                if TILES[WORLD_STATE[sprite.x/16, (sprite.y-16)/16]]['before_move']((sprite.x/16, (sprite.y-16)/16),(sprite.x/16, sprite.y/16)):
                    WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                    sprite.y -= 16*1
            else:
                WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                sprite.y -= 16*1
        
    if not cur_down and prev_down:
        if can_player_move(DOWN):
            if "before_move" in TILES[WORLD_STATE[sprite.x/16, (sprite.y+16)/16]].keys():
                print("need to call before_move")
                if TILES[WORLD_STATE[sprite.x/16, (sprite.y+16)/16]]['before_move']((sprite.x/16, (sprite.y+16)/16),(sprite.x/16, sprite.y/16)):
                    WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                    sprite.y += 16*1
            else:
                WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                sprite.y += 16*1
        
    if not cur_right and prev_right:
        if can_player_move(RIGHT):
            if "before_move" in TILES[WORLD_STATE[(sprite.x+16)/16, sprite.y/16]].keys():
                if TILES[WORLD_STATE[(sprite.x+16)/16, sprite.y/16]]['before_move'](((sprite.x+16)/16, sprite.y/16),(sprite.x/16, sprite.y/16)):
                    WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                    sprite.x += 16*1
            else:
                WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                sprite.x += 16*1
            WORLD_STATE[sprite.x/16, sprite.y/16] = "player"
        
    if not cur_left and prev_left:
        if can_player_move(LEFT):
            if "before_move" in TILES[WORLD_STATE[(sprite.x-16)/16, sprite.y/16]].keys():
                print("need to call before_move")
                if TILES[WORLD_STATE[(sprite.x-16)/16, sprite.y/16]]['before_move'](((sprite.x-16)/16, sprite.y/16),(sprite.x/16, sprite.y/16)):
                    WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                    sprite.x -= 16*1
            else:
                WORLD_STATE[sprite.x/16, sprite.y/16] = "floor"
                sprite.x -= 16*1
    
    WORLD_STATE[sprite.x/16, sprite.y/16] = "player"
    prev_up = cur_up
    prev_down = cur_down
    prev_right = cur_right
    prev_left = cur_left
    
    draw_world_state()