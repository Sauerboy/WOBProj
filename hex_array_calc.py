import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from build123d import Cylinder, Compound, Location, export_stl, export_step
import matplotlib.pyplot as plt

def find_closest_phase_indices(desired_phase, available_phases):
    avail_angles = np.angle(available_phases) if np.iscomplexobj(available_phases) else available_phases
    gauss_angles = np.angle(desired_phase) if np.iscomplexobj(desired_phase) else desired_phase
    pts = lambda a: np.column_stack([np.cos(a), np.sin(a)])
    _, idx = KDTree(pts(avail_angles)).query(pts(gauss_angles.ravel()))
    return idx.reshape(desired_phase.shape)

def in_hexagon(px, py, R):
    # Regular hexagon with flat top, circumradius R
    return abs(py) <= R * np.sqrt(3)/2 and \
           abs(px) + abs(py) / np.sqrt(3) <= R

horn_d = 1.9
horn_theta = np.deg2rad(80)
src_x = np.cos(horn_theta) * horn_d
src_y = 0
src_z = np.sin(horn_theta) * horn_d
f = 5.8e9
c = 3e8
lam = c/f
F = 10
L = 1.216
L_cell = 20.27e-3
num_pts = int(L / L_cell)
R = L / 2  # hexagon circumradius

# Square lattice, hexagonal boundary
x = np.linspace(-L/2, L/2, num_pts)
y = np.linspace(-L/2, L/2, num_pts)

points = [(xi, yi) for yi in y for xi in x if in_hexagon(xi, yi, R)]
points = np.array(points)
px_m, py_m = points[:, 0], points[:, 1]

# Phase calculations
phase_gauss = (2*np.pi/lam) * (np.sqrt(px_m**2 + py_m**2 + F**2) - F)
phase_gauss = (phase_gauss + np.pi) % (2*np.pi) - np.pi

dist = np.sqrt((px_m - src_x)**2 + (py_m - src_y)**2 + src_z**2)
phase_incident = (2*np.pi/lam) * dist
phase_incident = (phase_incident + np.pi) % (2*np.pi) - np.pi

phase_shift = (phase_gauss - phase_incident + np.pi) % (2*np.pi) - np.pi

# Element selection
df = pd.read_csv('cp_sparams.csv')
phase_element = df['ang_deg(S(FloquetPort1:1,FloquetPort1:1)) [deg]'].to_numpy()
d = df['d [mm]'].to_numpy()

indexes = find_closest_phase_indices(phase_shift, np.deg2rad(phase_element))
radii = d[indexes] / 2  # mm

# Plot
# plt.figure(figsize=(8, 7))
# plt.scatter(px_m*1000, py_m*1000, c=phase_shift, cmap='hsv', vmin=-np.pi, vmax=np.pi, s=10)
# plt.colorbar(label='Phase shift (rad)')
# plt.xlabel('x (mm)')
# plt.ylabel('y (mm)')
# plt.title('Reflectarray Phase (Hexagonal Aperture)')
# plt.axis('equal')
# plt.tight_layout()
# plt.show()

# CAD
patches = [
    Cylinder(radius=float(radii[k]), height=0.034).locate(Location((float(px_m[k]*1000), float(py_m[k]*1000), 0)))
    for k in range(len(points))
]

compound = Compound(children=patches)
export_step(compound, "hex_reflectarray.step")
print("Saved hex_reflectarray.step with {} patches".format(len(points)))