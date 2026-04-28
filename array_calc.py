import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from build123d import Cylinder, Compound, Location, export_step, export_stl
import matplotlib.pyplot as plt

def find_closest_phase_indices(desired_phase, available_phases):
    avail_angles = np.angle(available_phases) if np.iscomplexobj(available_phases) else available_phases
    gauss_angles = np.angle(desired_phase) if np.iscomplexobj(desired_phase) else desired_phase
    pts = lambda a: np.column_stack([np.cos(a), np.sin(a)])
    _, idx = KDTree(pts(avail_angles)).query(pts(gauss_angles.ravel()))
    return idx.reshape(desired_phase.shape)

horn_d=1.9
horn_theta=np.deg2rad(80)
src_x=np.cos(horn_theta)*horn_d
src_y=0
src_z=np.sin(horn_theta)*horn_d
f = 5.8e9
c = 3e8
lam = c/f
F = 10
L = 1.216
L_cell = 20.27e-3
num_pts = int(L/L_cell)

x = np.linspace(-L/2, L/2, num_pts)  # meters
y = np.linspace(-L/2, L/2, num_pts)  # meters
X, Y = np.meshgrid(x, y)

# Gaussian phase (meters)
phase_gauss = (2*np.pi/lam) * (np.sqrt(X**2+Y**2+F**2) - F)
phase_gauss = (phase_gauss + np.pi) % (2*np.pi) - np.pi

# Incident phase (meters, no unit conversion needed)
dx = X - src_x
dy = Y - src_y
dz = 0 - src_z
dist = np.sqrt(dx**2 + dy**2 + dz**2)
phase_incident = (2*np.pi/lam) * dist
phase_incident = (phase_incident + np.pi) % (2*np.pi) - np.pi

phase_shift = (phase_gauss - phase_incident + np.pi) % (2*np.pi) - np.pi

# Convert to mm only for plotting and CAD
# X_mm, Y_mm = X*1000, Y*1000

# plt.figure(figsize=(8, 6))
# plt.pcolormesh(X, Y, phase_shift, cmap='hsv', vmin=-np.pi, vmax=np.pi)
# plt.colorbar(label='Phase (rad)')
# plt.xlabel('x (mm)')
# plt.ylabel('y (mm)')
# plt.title('Reflector Phase')
# plt.axis('equal')
# plt.tight_layout()
# plt.show()

df = pd.read_csv('cp_sparams.csv')
phase_element = df['ang_deg(S(FloquetPort1:1,FloquetPort1:1)) [deg]'].to_numpy()
d = df['d [mm]'].to_numpy()

indexes = find_closest_phase_indices(phase_shift, np.deg2rad(phase_element))
radii = d[indexes] / 2  # mm
print(np.min(radii))

# Build all cylinders as a single compound (much faster than Assembly)
patches = [
    Cylinder(radius=radii[i][j], height=0.034).locate(Location((x[i]*1000, y[j]*1000, 0)))
    for i in range(num_pts)
    for j in range(num_pts)
]

compound = Compound(children=patches)
export_stl(compound, "reflectarray.stl")
print("Saved reflectarray.step with {} patches".format(num_pts**2))