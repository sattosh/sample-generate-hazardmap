import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

# 画像を保存するディレクトリが存在しない場合は作成する
if not os.path.exists('dist'):
    os.mkdir('dist')


#  Shapefileの読み込み
gdf = gpd.read_file('data/宮城県津波浸水想定の設定に係る最大浸水深データ.shp')

print(gdf.crs)

if gdf.crs !=  'EPSG:2452':
    gdf = gdf.to_crs('EPSG:2452')

# 範囲とグリッドサイズの設定
xmin, ymin, xmax, ymax = gdf.total_bounds
grid_size = 10  # 10m grid

print(grid_size)

# これらの値は画像の四隅の座標（緯度経度）となります。
print(f"Lower left corner: ({xmin}, {ymin})")
print(f"Lower right corner: ({xmax}, {ymin})")
print(f"Upper left corner: ({xmin}, {ymax})")
print(f"Upper right corner: ({xmax}, {ymax})")


# xとy座標の取得
x_coords = gdf.geometry.x
y_coords = gdf.geometry.y

# 属性値の取得
values = gdf['浸水深_m']

# x, y座標をグリッドに変換
x_index = ((x_coords - xmin) / grid_size).astype(int)
y_index = ((y_coords - ymin) / grid_size).astype(int)

# 属性値を2Dグリッドに変換
grid = np.full((y_index.max() + 1, x_index.max() + 1), -1)
grid[y_index, x_index] = values

# 0以下の値を持つピクセルをマスク（透明にする）
grid = ma.masked_where(grid < 0, grid)

# RGB値とそれに対応する属性値の範囲
rgb_values = [
    (247, 245, 169),   # "0~0.5"
    (255, 216, 192),  # "0.5~3"
    (255, 183, 183),  # "3~5"
    (255, 145, 145),  # "5~10"
    (242, 133, 201),  # "10~20"
    (220, 122, 220),  # "20 ~"
]

# RGB値をHEXコードに変換
colors = [ rgb_to_hex(rgb) for rgb in rgb_values]

print(colors)

# カラーマップの作成
cmap = ListedColormap(colors) # type: ignore

# ノーマライゼーション（値に基づいて色を指定）
# bounds = [20, 10, 5, 3, 0.5,  0.001,0]  # 境界値
bounds = [0, 0.5, 3, 5, 10, 20, 50] 
norm = BoundaryNorm(bounds, cmap.N) # type: ignore


# 画像の作成
fig, ax = plt.subplots()
im = ax.imshow(grid, cmap=cmap, norm=norm, origin='lower', extent=(xmin, xmax, ymin, ymax))
ax.axis('off')

# PNGとして保存
plt.savefig('dist/output.png', bbox_inches='tight', pad_inches=0, transparent=True,dpi=10000)