import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from build123d import Cylinder, Compound, Location, export_step, export_stl

def find_closest_phase_indices(gaussian_phase, available_phases):
    avail_angles = np.angle(available_phases) if np.iscomplexobj(available_phases) else available_phases
    gauss_angles = np.angle(gaussian_phase) if np.iscomplexobj(gaussian_phase) else gaussian_phase
    pts = lambda a: np.column_stack([np.cos(a), np.sin(a)])
    _, idx = KDTree(pts(avail_angles)).query(pts(gauss_angles.ravel()))
    return idx.reshape(gaussian_phase.shape)

f = 5.8e9
c = 3e8
lam = c/f
F = 1
L = 1
L_cell = 20.27e-3
num_pts = int(L/L_cell)

x = np.linspace(-L/2, L/2, num_pts) * 1000  # mm
y = np.linspace(-L/2, L/2, num_pts) * 1000
X, Y = np.meshgrid(x/1000, y/1000)

phase_gauss = np.exp(1j*2*np.pi/lam*(np.sqrt(X**2+Y**2+F**2)-F))

df = pd.read_csv('cp_sparams.csv')
phase = df['ang_deg(S(FloquetPort1:1,FloquetPort1:1)) [deg]'].to_numpy()
d = df['d [mm]'].to_numpy()

indexes = find_closest_phase_indices(phase_gauss, np.deg2rad(phase))
radii = d[indexes] / 2  # mm

# Build all cylinders as a single compound (much faster than Assembly)
patches = [
    Cylinder(radius=radii[i][j], height=0.034).locate(Location((x[i], y[j], 0)))
    for i in range(num_pts)
    for j in range(num_pts)
]

compound = Compound(children=patches)
export_stl(compound, "reflectarray.stl")
print("Saved reflectarray.step with {} patches".format(num_pts**2))