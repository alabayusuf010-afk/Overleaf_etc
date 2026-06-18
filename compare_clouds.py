import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt


def load_ply(path: Path) -> np.ndarray:
    lines = path.read_text().splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == 'end_header':
            data_lines = lines[idx + 1 :]
            break
    return np.array([list(map(float, line.split())) for line in data_lines if line.strip()])

original_path = Path('cloud_backup.ply')
clean_path = Path('cloud.ply')
image_path = Path('cloud_compare.png')

original = load_ply(original_path)
cleaned = load_ply(clean_path)

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=200)
for ax, pts, title in [
    (axes[0], original, 'Original Point Cloud'),
    (axes[1], cleaned, 'Cleaned Point Cloud'),
]:
    scatter = ax.scatter(pts[:, 0], pts[:, 1], s=1, c=pts[:, 2], cmap='viridis')
    ax.set_title(f'{title}\nVertices: {len(pts):,}', fontsize=14, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.axis('equal')

fig.colorbar(scatter, ax=axes, label='Z value', orientation='vertical', fraction=0.02, pad=0.04)
plt.tight_layout()
plt.savefig(image_path)
print('Saved comparison image to', image_path)
