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

# K-means algorithm (Lloyd's Algorithm)
def kmeans(data, k, tol=1e-4, max_iter=100):
    centroids = data[np.random.choice(data.shape[0], size=k, replace=False)]
    for _ in range(max_iter):
        distances = np.linalg.norm(data - centroids[:, np.newaxis], axis=2)
        labels = np.argmin(distances, axis=0)
        new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(k)])
        
        if np.all(np.abs(new_centroids - centroids) < tol):
            break
        centroids = new_centroids
    
    return centroids, labels

# Elbow Method (Scree Plot)
def elbow_method(data, k_range):
    inertia = []
    for k in k_range:
        centroids, _ = kmeans(data, k)
        inertia.append(np.sum(np.min(np.linalg.norm(data - centroids[:, np.newaxis], axis=2), axis=0)))
    
    rate_change = np.diff(np.diff(inertia))
    return np.argmax(rate_change) + k_range[0] + 1


# Generate gnuplot script
def create_gnuplot_script(labels,output_dir):
    dir_gnu = os.getcwd().replace('_', '\\_')
    with open(f"{output_dir}/plot_cluster.gnu", "w") as f:
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
values = data[:, 1:].reshape(-1, 1)

if n_clusters is None:
    print("Determining optimal clusters via Elbow Method...")
    n_clusters = elbow_method(values, range(1, 11))

print(f"Using {n_clusters} clusters.")

# Main
# ... (other parts remain the same)

if tol is None:
    print("Calculating initial tolerance...")
    tol = 0.1 * np.std(values)  # 10% of standard deviation as initial tolerance
    print(f"Initial tolerance set to {tol}")

centroids, labels = kmeans(values, n_clusters, tol)
  

# Output to directory
with open(f"{output_dir}/cluster.all.dat", 'w') as f:
    f.write("#Frame Data Cluster\n")
    for frame, value, label in zip(frames, values.flatten(), labels):
        f.write(f"{int(frame)} {value:.6f} {label}\n")

# Output individual cluster files
for unique_label in np.unique(labels):
    with open(f"{output_dir}/cluster.c{unique_label}.dat", 'w') as f:
        f.write("#Frame Data Cluster\n")
        for frame, value, label in zip(frames, values.flatten(), labels):
            if label == unique_label:
                f.write(f"{int(frame)} {value:.6f} {label}\n")

np.savetxt(f"{output_dir}/cluster.centroids", centroids, header="Cluster Centroids")

# Generate Gnuplot script
create_gnuplot_script(labels,output_dir)
print("Generated Gnuplot script.")

# Run Gnuplot
os.system(f"gnuplot {output_dir}/plot_cluster.gnu")