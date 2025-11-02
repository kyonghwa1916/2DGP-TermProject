from pico2d import open_canvas, close_canvas
import os
from witch import Witch
from fruit import Fruit
from item import Item

# 프로젝트 루트에서 resources 경로 계산
current_path = os.path.dirname(__file__)
resources_path = os.path.join(current_path, 'resources')
witch_img = os.path.join(resources_path, 'B_witch_run.png')

print('Opening canvas and creating Witch...')
open_canvas(800, 600)
try:
    w = Witch(witch_img)
    print('Witch created at', w.x, w.y)

    # create items without loading images (meta only)
    f0 = Fruit.from_index(0, load_image_now=False)  # apple
    i1 = Item.from_name('blue_1', load_image_now=False)

    print('Add apple to inventory at index:', w.add_to_inventory(f0))
    print('Add blue_1 to inventory at index:', w.add_to_inventory(i1))

    # Fill up a couple more
    for idx in range(3):
        w.add_to_inventory(Fruit.from_index(idx+1, load_image_now=False))

    print('Inventory summary (after adds):')
    for slot, name in w.inventory_summary():
        print(slot, name)

    # swap first two
    w.swap_inventory(0, 1)
    print('\nAfter swap 0<->1:')
    for slot, name in w.inventory_summary():
        print(slot, name)

    # remove slot 1
    removed = w.remove_from_inventory(1)
    print('\nRemoved from slot 1:', getattr(removed, 'name', getattr(removed, 'filename', removed)))

    print('\nFinal inventory summary:')
    for slot, name in w.inventory_summary():
        print(slot, name)

finally:
    close_canvas()
    print('Canvas closed')

