import os
import numpy as np
import numpy.ma as ma
import pandas as pd
import geopandas as gpd
import cv2

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def map_color(val, bounds, colors):
    for i, bound in enumerate(bounds):
        if val >= bound:
            return colors[i]
    return colors[-1]

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


bounds = [0, 0.5, 3, 5, 10, 20, 50] 
output_img = np.zeros((*grid.shape, 3), dtype=np.uint8)

for i in range(grid.shape[0]):
    for j in range(grid.shape[1]):
        output_img[i, j] = map_color(grid[i, j], bounds, rgb_values)

# 画像を保存
cv2.imwrite('dist/output_cv2.png', cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))