import numpy as np
import pandas as pd
from scipy.spatial import KDTree

def find_closest_phase_indices(gaussian_phase: np.ndarray, available_phases: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    avail_angles = np.angle(available_phases) if np.iscomplexobj(available_phases) else available_phases
    gauss_angles = np.angle(gaussian_phase) if np.iscomplexobj(gaussian_phase) else gaussian_phase
    pts = lambda a: np.column_stack([np.cos(a), np.sin(a)])
    _, idx = KDTree(pts(avail_angles)).query(pts(gauss_angles.ravel()))
    idx = idx.reshape(gaussian_phase.shape)
    return idx, available_phases[idx]

f=5.8e9
c=3e8
lam=c/f
F=1
L=np.sqrt(F*lam)
L_cell=20.27e-3
num_pts=int(L/L_cell)
print(num_pts)
x=np.linspace(-L/2, L/2, num_pts)
y=np.linspace(-L/2, L/2, num_pts)
X, Y    = np.meshgrid(x, y)          # shape (num_pts, num_pts)
phase_gauss= np.exp(1j*2*np.pi/lam*(np.sqrt(X**2+Y**2+F**2)-F))
print(np.rad2deg(np.angle(phase_gauss)).min(), np.rad2deg(np.angle(phase_gauss)).max())
df = pd.read_csv('cp_sparams.csv')
phase = df['ang_deg(S(FloquetPort1:1,FloquetPort1:1)) [deg]'].to_numpy()
d = df['d [mm]'].to_numpy()

# Later on the guassian profile will need to be offset by incedent phase at each point
indexes, _ = find_closest_phase_indices(phase_gauss, np.deg2rad(phase))
np.savetxt('diameters.csv', d[indexes], delimiter=',', fmt='%.4f')
np.savetxt('x_pos.csv', x*1000, delimiter=',', fmt='%.4f')
np.savetxt('y_pos.csv', y*1000, delimiter=',', fmt='%.4f')

import csv
with open('diameters.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    diameters = list(reader)

# Accessing data[row][column]
print(np.array(diameters).shape) 