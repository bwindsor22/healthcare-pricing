from img_loader import load_imgs_as_dfs
from pathlib import Path
grid_out_dir = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/grid_out/')
source_grids = load_imgs_as_dfs()

for grid, df in source_grids.items():
        out_file = grid_out_dir / f'{grid}.csv'
        df.to_csv(str(out_file))
print('hi')
