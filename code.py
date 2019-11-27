import board
import displayio
import adafruit_imageload
from displayio import Palette
from adafruit_pybadger import PyBadger

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

MAP = {}
 
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
        "can_walk": False,
        "entity": True,
    },
    "heart": {
        "sprite_index": 2,
        "can_walk": True,
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

#print(palette[0])
#palette[0] = 0xFFFFFF
palette.make_transparent(5)

entity_sprites = []

# Create the sprite TileGrid
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width = 1,
                            height = 1,
                            tile_width = 16,
                            tile_height = 16,
                            default_tile = 0)

# Create the castle TileGrid
castle = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width = 10,
                            height = 8,
                            tile_width = 16,
                            tile_height = 16)

# Create a Group to hold the sprite and add it
sprite_group = displayio.Group(max_size=48)
sprite_group.append(sprite)

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
            
            print("%s '%s'" % (len(tile_name), str(tile_name)))
            if tile_name in TILES.keys():
                castle[x, y] = TILES[tile_name]['sprite_index']
                if 'entity' in TILES[tile_name].keys() and TILES[tile_name]['entity']:
                    entity_srite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                width = 1,
                                height = 1,
                                tile_width = 16,
                                tile_height = 16,
                                default_tile = TILES[tile_name]['sprite_index'])
                    entity_srite.x = x*16
                    entity_srite.y = y*16
                    entity_sprites.append(entity_srite)
                    castle[x, y] = TILES['floor']['sprite_index']
                else:
                    castle[x, y] = TILES[tile_name]['sprite_index']
            else:
                print("tile: %s not found in TILES dict" % tile_name)
                



# put the sprite somewhere in the castle
sprite.x = 16*3
sprite.y = 16*2


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
        return TILES[MAP[tile_above_coords[0], tile_above_coords[1]]]['can_walk']
        
    if direction == DOWN:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_below_coords = [player_map_coords[0], player_map_coords[1] + 1]
        return TILES[MAP[tile_below_coords[0], tile_below_coords[1]]]['can_walk']
        
    if direction == LEFT:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_left_of_coords = [player_map_coords[0]-1, player_map_coords[1]]
        return TILES[MAP[tile_left_of_coords[0], tile_left_of_coords[1]]]['can_walk']
        
    if direction == RIGHT:
        player_map_coords = [sprite.x/16, sprite.y/16]
        tile_right_of_coords = [player_map_coords[0] + 1, player_map_coords[1]]
        return TILES[MAP[tile_right_of_coords[0], tile_right_of_coords[1]]]['can_walk']

while True:
    #badger.auto_dim_display(delay=10)
    cur_up = badger.button.up
    cur_down = badger.button.down
    cur_right = badger.button.right
    cur_left = badger.button.left
    
    if not cur_up and prev_up:
        if can_player_move(UP):
            sprite.y -= 16*1
        
    if not cur_down and prev_down:
        if can_player_move(DOWN):
            sprite.y += 16*1
        
    if not cur_right and prev_right:
        if can_player_move(RIGHT):
            sprite.x += 16*1
        
    if not cur_left and prev_left:
        if can_player_move(LEFT):
            sprite.x -= 16*1
    
    prev_up = cur_up
    prev_down = cur_down
    prev_right = cur_right
    prev_left = cur_left