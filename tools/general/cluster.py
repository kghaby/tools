#!/usr/bin/env python3

import numpy as np
import sys
import os 

# Help Section (CLI Guidance)
def print_help():
    print("Usage: cluster.py [data_file] [n_clusters] [tolerance]")
    print("  data_file:  File containing frame and data. Default is 'forcluster.dat'.")
    print("  n_clusters: Number of clusters. Default determined by Elbow Method.")
    print("  tolerance:  Tolerance for centroid convergence. Default determined by Davies-Bouldin Index.")
    sys.exit(0)

# K-means algorithm
def kmeans(data, centroids, tol=1e-4, max_iter=100):
    for i in range(max_iter):
        distances = np.linalg.norm(data[:, :, np.newaxis] - centroids.T[np.newaxis, :, :], axis=1)
        labels = np.argmin(distances, axis=0)
        new_centroids = np.array([data[labels == k].mean(axis=0) for k in range(centroids.shape[0])])

        if np.all(np.abs(new_centroids - centroids) < tol):
            break

        centroids = new_centroids

    return centroids, labels

# Elbow Method
def elbow_method(data, k_range):
    inertia = []
    for k in k_range:
        initial_centroids = np.random.choice(data.flatten(), size=k).reshape(-1, 1)
        centroids, _ = kmeans(data, initial_centroids)
        inertia.append(np.sum(np.min(np.linalg.norm(data[:, :, np.newaxis] - centroids.T[np.newaxis, :, :], axis=1), axis=0)))
    return np.argmin(np.diff(np.diff(inertia))) + k_range[0] + 1  # Double differentiation to find elbow ie num_clusters


# Davies–Bouldin index (Heuristic Evaluation)
def davies_bouldin(data, labels, centroids):
    n_cluster = centroids.shape[0]
    s_values = np.array([np.sqrt(np.sum(np.linalg.norm(data[labels == k] - centroids[k], axis=1)**2) / np.sum(labels == k)) for k in range(n_cluster)])
    r_values = np.zeros((n_cluster, n_cluster))
    
    for i in range(n_cluster):
        for j in range(i+1, n_cluster):
            r_values[i, j] = r_values[j, i] = (s_values[i] + s_values[j]) / np.linalg.norm(centroids[i] - centroids[j])
    
    d_values = np.max(r_values, axis=1)
    return np.sum(d_values) / n_cluster

# Generate gnuplot script
def create_gnuplot_script(labels):
    dir_gnu = os.getcwd().replace('_', '\\_')
    with open("plot_cluster.gnu", "w") as f:
        f.write(f'set xlabel "Time (frames)"\n')
        f.write('set ylabel ""\n')
        f.write(f'set title "{dir_gnu}"\n')
        f.write('set key outside\n')
        f.write('plot\\\n')
        
        for label in np.unique(labels):
            f.write(f'"cluster.c{label}.dat" u 1:2 every 10 title "{label}",\\\n')

        f.write('pause -1\n')

# Create output directory
def create_output_dir(base="clusters"):
    counter = 1
    while os.path.exists(f"{base}_{counter}"):
        counter += 1
    os.makedirs(f"{base}_{counter}")
    return f"{base}_{counter}"

# Main
if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help', 'help'):
    print_help()

output_dir = create_output_dir()
print(f"Output directory: {output_dir}")

data_file = sys.argv[1] if len(sys.argv) > 1 else 'forcluster.dat'
n_clusters = int(sys.argv[2]) if len(sys.argv) > 2 else None
tol = float(sys.argv[3]) if len(sys.argv) > 3 else None

data = np.loadtxt(data_file)
frames = data[:, 0]
values = data[:, 1].reshape(-1, 1)

if n_clusters is None:
    print("Determining optimal clusters via Elbow Method...")
    n_clusters = elbow_method(values, range(1, 11))

print(f"Using {n_clusters} clusters.")

initial_centroids = np.random.choice(values.flatten(), size=n_clusters)
centroids, labels = kmeans(values, initial_centroids, tol)

if tol is None:
    print("Calculating optimal tolerance...")
    tol = 0.1 * davies_bouldin(values, labels, centroids)  # Scale factor adjustable

# Output to directory
with open(f"{output_dir}/cluster.all.dat", 'w') as f:
    f.write("#Frame Data Cluster\n")
    for frame, value, label in zip(frames, values.flatten(), labels):
        f.write(f"{int(frame)} {value:.6f} {label}\n")

np.savetxt(f"{output_dir}/cluster.centroids", centroids, header="Cluster Centroids")

# Generate Gnuplot script
create_gnuplot_script(labels)
print("Generated Gnuplot script.")

# Run Gnuplot
os.system("gnuplot plot_cluster.gnu")