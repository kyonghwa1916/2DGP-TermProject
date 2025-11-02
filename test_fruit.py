import os
from fruit import Fruit

print('Testing Fruit class (no canvas, no image load)')
for i in range(6):
    f = Fruit.from_index(i, load_image_now=False)
    print(i, f.name, f.filename, os.path.exists(f.path))

# test by filename
f2 = Fruit.from_filename('fruit_002.png', load_image_now=False)
print('filename test:', f2.name, f2.filename, os.path.exists(f2.path))

# test an index outside DEFAULT_NAME_MAP
f3 = Fruit.from_index(15, load_image_now=False)
print('out-of-map index:', f3.name, f3.filename, os.path.exists(f3.path))

