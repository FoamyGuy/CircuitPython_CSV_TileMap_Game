import board
import displayio
import adafruit_imageload
from displayio import Palette
from adafruit_pybadger import PyBadger
import time

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

FPS_DELAY = 1/30

SCREEN_HEIGHT_TILES = 8
SCREEN_WIDTH_TILES = 10

ORIGINAL_MAP = {}
CURRENT_MAP = {}

CAMERA_VIEW = {}
CAMERA_OFFSET_X = 0
CAMERA_OFFSET_Y = 0

ENTITY_SPRITES = []
ENTITY_SPRITES_DICT = {}
NEED_TO_DRAW_ENTITIES = []

PREV_STATE_OF_PLAYER_TILE  = "floor"
PREV_STATE_OF_PUSHING_TILE  = "floor"

PLAYER_LOC = (0,0)

def get_tile(coords):
    return CURRENT_MAP[coords[0], coords[1]]

def get_tile_obj(coords):
    return TILES[CURRENT_MAP[coords[0], coords[1]]]

def is_tile_moveable(tile_coords):
    return TILES[CURRENT_MAP[tile_coords[0], tile_coords[1]]]['can_walk']

def allow_push(to_coords, from_coords, entity_obj):
    global PREV_STATE_OF_PUSHING_TILE
    push_x_offset = 0
    push_y_offset = 0
    print("inside allow push")
    print("prev pushing tile: %s" % PREV_STATE_OF_PUSHING_TILE)
    print("%s -> %s" % (from_coords, to_coords))
    if to_coords[0] < from_coords[0]:
        print("moving left")
        push_x_offset = -1
        push_y_offset = 0
        # moving left
    elif to_coords[0] > from_coords[0]:
        print("moving right")
        push_x_offset = 1
        push_y_offset = 0

        # moving right
        pass
    elif to_coords[1] < from_coords[1]:
        print("moving up")
        push_x_offset = 0
        push_y_offset = -1

        # moving up
        pass
    elif to_coords[1] > from_coords[1]:
        print("moving down")
        push_x_offset = 0
        push_y_offset = 1

        # moving down
    push_to_tile_coords = (to_coords[0]+ push_x_offset, to_coords[1]+ push_y_offset)
    if is_tile_moveable(push_to_tile_coords):
        tile_name = CURRENT_MAP[to_coords]

        print("dict before %s" % ENTITY_SPRITES_DICT)
        if push_to_tile_coords in ENTITY_SPRITES_DICT:
            ENTITY_SPRITES_DICT[push_to_tile_coords].append(entity_obj)
        else:
            ENTITY_SPRITES_DICT[push_to_tile_coords] = [entity_obj]
        ENTITY_SPRITES_DICT[to_coords].remove(entity_obj)
        if len(ENTITY_SPRITES_DICT[to_coords]) == 0:
            del ENTITY_SPRITES_DICT[to_coords]
        print("dict after %s" % ENTITY_SPRITES_DICT)
        return True

    return False

TILES = {
    "": {
        "sprite_index": 7,
        "can_walk": False
    },
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

f = open("map_entity_system_and_camera.csv", 'r')
map_csv_str = f.read()
f.close()

map_csv_lines = map_csv_str.replace("\r", "").split("\n")

MAP_HEIGHT = len(map_csv_lines)
MAP_WIDTH = len(map_csv_lines[0].split(","))

print(TILES.keys())

print("===")

print(map_csv_lines)
for y, line in enumerate(map_csv_lines):
    if line != "":
        print(line)
        for x, tile_name in enumerate(line.split(",")):
            print("%s '%s'" % (len(tile_name), str(tile_name)))
            if tile_name in TILES.keys():
                #castle[x, y] = TILES[tile_name]['sprite_index']
                if 'entity' in TILES[tile_name].keys() and TILES[tile_name]['entity']:
                    ORIGINAL_MAP[x,y] = "floor"
                    CURRENT_MAP[x,y] = "floor"
                    #castle[x, y] = TILES['floor']['sprite_index']
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
                        PLAYER_LOC = (x,y)
                        sprite_group.append(sprite)
                    else:
                        entity_srite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width = 1,
                                    height = 1,
                                    tile_width = 16,
                                    tile_height = 16,
                                    default_tile = TILES[tile_name]['sprite_index'])
                        #entity_srite.x = x*16
                        #entity_srite.y = y*16
                        entity_srite.x = -16
                        entity_srite.y = -16
                        ENTITY_SPRITES.append(entity_srite)
                        print("setting entity_sprites_dict[%s,%s]" % (x,y))
                        entity_obj = {
                            "entity_sprite_index": len(ENTITY_SPRITES) - 1,
                            "map_tile_name": tile_name
                        }
                        if (x,y) not in ENTITY_SPRITES_DICT:
                            ENTITY_SPRITES_DICT[x, y] = [entity_obj]
                        else:
                            ENTITY_SPRITES_DICT[x, y].append(entity_obj)
                else:
                    ORIGINAL_MAP[x, y] = tile_name
                    CURRENT_MAP[x, y] = tile_name
                    pass
            else:
                print("tile: %s not found in TILES dict" % tile_name)


for entity in ENTITY_SPRITES:
    sprite_group.append(entity)

# Add the Group to the Display
display.show(group)

prev_up = False
prev_down = False
prev_left = False
prev_right = False

def can_player_move(direction):
    if direction == UP:
        tile_above_coords = (PLAYER_LOC[0], PLAYER_LOC[1] - 1)
        return TILES[CURRENT_MAP[tile_above_coords[0], tile_above_coords[1]]]['can_walk']

    if direction == DOWN:
        tile_below_coords = (PLAYER_LOC[0], PLAYER_LOC[1] + 1)
        return TILES[CURRENT_MAP[tile_below_coords[0], tile_below_coords[1]]]['can_walk']

    if direction == LEFT:
        tile_left_of_coords = (PLAYER_LOC[0]-1, PLAYER_LOC[1])
        print(TILES[CURRENT_MAP[tile_left_of_coords[0], tile_left_of_coords[1]]])
        return TILES[CURRENT_MAP[tile_left_of_coords[0], tile_left_of_coords[1]]]['can_walk']

    if direction == RIGHT:
        tile_right_of_coords = (PLAYER_LOC[0] + 1, PLAYER_LOC[1])
        return TILES[CURRENT_MAP[tile_right_of_coords[0], tile_right_of_coords[1]]]['can_walk']

def set_camera_view(startX, startY, width, height):
    global CAMERA_OFFSET_X
    global CAMERA_OFFSET_Y
    CAMERA_OFFSET_X = startX
    CAMERA_OFFSET_Y = startY
    for y_index, y in enumerate(range(startY, startY+height)):
        for x_index, x in enumerate(range(startX, startX+width)):
            #print("setting camera_view[%s,%s]" % (x_index,y_index))
            try:
                CAMERA_VIEW[x_index,y_index] = CURRENT_MAP[x,y]
            except KeyError:
                CAMERA_VIEW[x_index,y_index] = "floor"


def draw_camera_view():
    player_drawn = False
    drew_entities = []
    #print(CAMERA_VIEW)
    for y in range(0, SCREEN_HEIGHT_TILES):
        for x in range(0, SCREEN_WIDTH_TILES):
            tile_name = CAMERA_VIEW[x,y]
            if tile_name in TILES.keys():
                if (x + CAMERA_OFFSET_X, y + CAMERA_OFFSET_Y) in ENTITY_SPRITES_DICT:
                    castle[x, y] = TILES["floor"]['sprite_index']
                    if tile_name != "player":
                        #print("trying to set position for %s" % tile_name)
                        #print("trying to set position for entity_sprites_dict[%s,%s]" % (x+CAMERA_OFFSET_X,y+CAMERA_OFFSET_Y))
                        #print("offsets[%s,%s]" % (CAMERA_OFFSET_X,CAMERA_OFFSET_Y))
                        #print(ENTITY_SPRITES_DICT[x + CAMERA_OFFSET_X, y + CAMERA_OFFSET_Y])
                        for entity_obj_at_tile in ENTITY_SPRITES_DICT[x + CAMERA_OFFSET_X, y + CAMERA_OFFSET_Y]:

                            ENTITY_SPRITES[int(entity_obj_at_tile["entity_sprite_index"])].x = x * 16
                            ENTITY_SPRITES[int(entity_obj_at_tile["entity_sprite_index"])].y = y * 16
                            drew_entities.append(entity_obj_at_tile["entity_sprite_index"])
                else:
                    castle[x, y] = TILES[tile_name]['sprite_index']
            else:
                castle[x, y] = TILES["floor"]['sprite_index']

            if PLAYER_LOC == ((x + CAMERA_OFFSET_X, y + CAMERA_OFFSET_Y)):
                # draw player
                #print("drawing player %s,%s " % (x + CAMERA_OFFSET_X, y + CAMERA_OFFSET_Y))
                sprite.x = x*16
                sprite.y = y*16

    for index in range(0, len(ENTITY_SPRITES)):
        if index not in drew_entities:
            ENTITY_SPRITES[index].x = int(-16)
            ENTITY_SPRITES[index].y = int(-16)


last_update_time = 0

x_offset = 0
y_offset = 0
while True:
    badger.auto_dim_display(delay=10)
    cur_up = badger.button.up
    cur_down = badger.button.down
    cur_right = badger.button.right
    cur_left = badger.button.left

    if not cur_up and prev_up:
        if can_player_move(UP):
            x_offset = 0
            y_offset = - 1


    if not cur_down and prev_down:
        if can_player_move(DOWN):
            x_offset = 0
            y_offset = 1

    if not cur_right and prev_right:
        if can_player_move(RIGHT):
            x_offset = 1
            y_offset = 0


    if not cur_left and prev_left:
        if can_player_move(LEFT):
            print("can_move left")
            x_offset = -1
            y_offset = 0


    if x_offset != 0 or y_offset != 0:
        can_move = False
        moving_to_coords = (PLAYER_LOC[0] + x_offset, PLAYER_LOC[1] + y_offset)
        moving_to_tile_name = CURRENT_MAP[moving_to_coords[0], moving_to_coords[1]]
        if moving_to_coords in ENTITY_SPRITES_DICT:
            print("found entity(s) where we are moving to")
            for entity_obj in ENTITY_SPRITES_DICT[moving_to_coords]:
                print("checking entity %s" % entity_obj["map_tile_name"])
                if "before_move" in TILES[entity_obj["map_tile_name"]].keys():
                    #print("need to call before_move")
                    #print(TILES[entity_obj["map_tile_name"]])
                    print("calling before_move %s, %s, %s" % (moving_to_coords,PLAYER_LOC,entity_obj))
                    if TILES[entity_obj["map_tile_name"]]['before_move'](moving_to_coords,PLAYER_LOC,entity_obj):
                        can_move = True
                    else:
                        break;
                        #sprite.y -= 16*1
                else:
                    can_move = True
            if can_move:
                PLAYER_LOC = moving_to_coords
        else:
            PLAYER_LOC = moving_to_coords
    y_offset = 0
    x_offset = 0
    #CURRENT_MAP[sprite.x/16, sprite.y/16] = "player"
    prev_up = cur_up
    prev_down = cur_down
    prev_right = cur_right
    prev_left = cur_left


    now = time.monotonic()
    if now > last_update_time + FPS_DELAY:

        if PLAYER_LOC[0] > 4:
            set_camera_view(int(PLAYER_LOC[0]-4),0,10,8)
        else:
            set_camera_view(0,0,10,8)

        #set_camera_view(0,0,10,8)
        draw_camera_view()
        last_update_time = now