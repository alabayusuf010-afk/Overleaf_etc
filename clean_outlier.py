import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

ply_path = Path('cloud.ply')
clean_path = Path('cloud_clean.ply')
image_path = Path('cloud_clean.png')

lines = ply_path.read_text().splitlines()
for idx, line in enumerate(lines):
    if line.strip() == 'end_header':
        header_lines = lines[: idx + 1]
        data_lines = lines[idx + 1 :]
        break
points = np.array([list(map(float, line.split())) for line in data_lines if line.strip()])

centroid = points.mean(axis=0)
distances = np.linalg.norm(points - centroid, axis=1)
outlier_idx = np.argmax(distances)
outlier_point = points[outlier_idx]
print('Detected outlier index:', outlier_idx)
print('Outlier point:', outlier_point)
print('Max distance from centroid:', distances[outlier_idx])

# Remove outlier and write cleaned ply
cleaned_points = np.delete(points, outlier_idx, axis=0)
with clean_path.open('w', encoding='utf-8') as f:
    for line in header_lines:
        f.write(line + '\n')
    for x, y, z in cleaned_points:
        f.write(f'{x} {y} {z}\n')

# Create a 2D projection image for report
plt.figure(figsize=(10, 8), dpi=200)
plt.scatter(cleaned_points[:, 0], cleaned_points[:, 1], s=1, c=cleaned_points[:, 2], cmap='viridis')
plt.colorbar(label='Z value')
plt.title('Cleaned Point Cloud (XY projection)')
plt.xlabel('X')
plt.ylabel('Y')
plt.axis('equal')
plt.tight_layout()
plt.savefig(image_path)
print('Saved cleaned point cloud to', clean_path)
print('Saved plot image to', image_path)
