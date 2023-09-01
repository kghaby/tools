#!/usr/bin/env python3

import numpy as np
import sys
import os 
from datetime import datetime

# Help Section (CLI Guidance)
def print_help():
    print("Usage: cluster.py [data_file] [n_clusters] [tolerance]")
    print("  data_file:  File containing frame and data. Default is 'forcluster.dat'.")
    print("  n_clusters: Number of clusters. Default determined by Elbow Method.")
    print("  tolerance:  Tolerance for centroid convergence. Default determined by Davies-Bouldin Index.")
    sys.exit(0)

# Function to log information to a file
def log_to_file(message, log_file,printmsg=True):
    if printmsg:
        print(message)
    with open(log_file, 'a') as f:
        f.write(f"{message}\n")

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

def incremental_std(cluster_data):
    n = len(cluster_data)
    squared_diff_sum = 0
    
    for point in cluster_data:
        squared_diff_sum += np.sum((point - cluster_data) ** 2)
        
    return np.sqrt(squared_diff_sum / (n * (n - 1)))  # n * (n - 1) because of pairwise comparisons


def cluster_summary(data, labels, centroids):
    unique_labels = np.unique(labels)
    n_frames = len(data)
    summary = []
    
    for label in unique_labels:
        cluster_data = data[labels == label]
        n_cluster_frames = len(cluster_data)
        fraction = n_cluster_frames / n_frames
        avg_dist = np.mean([np.mean(np.abs(point - cluster_data)) for point in cluster_data])

        stdev = incremental_std(cluster_data)

        
        # Centroid calculation
        cumulative_dists = [np.sum(np.abs(point - cluster_data)) for point in cluster_data]
        centroid_frame = frames[labels == label][np.argmin(cumulative_dists)]
        centroid_value = centroids[label][0]
        
        # AvgCDist: Average distance to other clusters
        other_clusters = np.concatenate([data[labels == other_label] for other_label in unique_labels if other_label != label])
        avg_cdist = np.mean(np.abs(cluster_data.mean() - other_clusters))
        
        summary.append([label, n_cluster_frames, fraction, avg_dist, stdev, int(centroid_frame), avg_cdist,centroid_value])
        
    return summary



# Generate gnuplot script
def create_gnuplot_script(labels,output_dir):
    dir_gnu = os.getcwd().replace('_', '\\\_')
    with open(f"{output_dir}/plot_cluster.gnu", "w") as f:
        f.write(f'set xlabel "Time (frames)"\n')
        f.write('set ylabel ""\n')
        f.write(f'set title "{dir_gnu}"\n')
        f.write('set key outside\n')
        f.write('plot\\\n')
        
        for label in np.unique(labels):
            f.write(f'"cluster.c{label}.dat" u 1:2 every 10 title "{label}",\\\n')

        f.write('\npause -1\n')

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
log_file = f"{output_dir}/cluster.log"
log_to_file(f"Run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
log_to_file(f"Output directory: {output_dir}", log_file)

data_file = sys.argv[1] if len(sys.argv) > 1 else 'forcluster.dat'
n_clusters = int(sys.argv[2]) if len(sys.argv) > 2 else None
tol = float(sys.argv[3]) if len(sys.argv) > 3 else None

data = np.loadtxt(data_file)
frames = data[:, 0]
values = data[:, 1:].reshape(-1, 1)

if n_clusters is None:
    log_to_file("Determining optimal clusters via Elbow Method...",log_file)
    n_clusters = elbow_method(values, range(1, 11))

log_to_file(f"Using {n_clusters} clusters.", log_file)

# Main
# ... (other parts remain the same)

if tol is None:
    log_to_file("Calculating initial tolerance...",log_file)
    tol = 0.1 * np.std(values)  # 10% of standard deviation as initial tolerance
    log_to_file(f"Initial tolerance set to {tol}",log_file)

centroids, labels = kmeans(values, n_clusters, tol)
summary_data = cluster_summary(values, labels, centroids)

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

# Output cluster summary
with open(f"{output_dir}/cluster.sum", 'w') as f:
    f.write("#Cluster   Frames     Frac  AvgDist    Stdev Centroid AvgCDist  CValue \n")
    for row in summary_data:
        f.write(f"{row[0]:7d} {row[1]:9d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:8.3f} {row[7]:8.3f}\n")



# Generate Gnuplot script
create_gnuplot_script(labels,output_dir)
log_to_file("Generated Gnuplot script.", log_file)
log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
# Run Gnuplot
os.system(f"cd {output_dir}; gnuplot plot_cluster.gnu; cd -")