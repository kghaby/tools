#!/usr/bin/env python3

import numpy as np
import sys
import os 
from datetime import datetime
import argparse



# Function to log information to a file
def log_to_file(message, log_file,printmsg=True):
    if printmsg:
        print(message)
    with open(log_file, 'a') as f:
        f.write(f"{message}\n")

# K-means algorithm (Lloyd's Algorithm)
def kmeans(data, k, initial_centroids=None, tol=1e-4, max_iter=100):
    if initial_centroids is None:
        centroids = data[np.random.choice(data.shape[0], size=k, replace=False)]
    else:
        if len(initial_centroids) != k:
            raise ValueError("Number of initial centroids must match k")
        centroids = initial_centroids

    for _ in range(max_iter):
        distances = np.linalg.norm(data - centroids[:, np.newaxis], axis=2)
        labels = np.argmin(distances, axis=0)
        new_centroids = np.array([data[labels == i].mean(axis=0) for i in range(k)])

        if np.all(np.abs(new_centroids - centroids) < tol):
            break
        centroids = new_centroids

    return centroids, labels


# Elbow Method (Scree Plot)
def elbow_method(data, k_range, initial_centroids=None):
    inertia = []
    for k in k_range:
        centroids, _ = kmeans(data, k, initial_centroids=initial_centroids)
        inertia.append(np.sum(np.min(np.linalg.norm(data - centroids[:, np.newaxis], axis=2), axis=0)))
    
    rate_change = np.diff(np.diff(inertia))
    return np.argmax(rate_change) + k_range[0] + 1

def cluster_summary(data, labels, centroids):
    unique_labels = np.unique(labels)
    n_frames = len(data)
    summary = []
    
    for label in unique_labels:
        cluster_data = data[labels == label]
        n_cluster_frames = len(cluster_data)
        fraction = n_cluster_frames / n_frames
        avg_dist = np.mean([np.mean(np.abs(point - cluster_data)) for point in cluster_data])

        sum_distances, sum_squared_distances, n = 0, 0, 0
        for point in cluster_data:
            distances = np.abs(point - cluster_data)
            sum_distances += np.sum(distances)
            sum_squared_distances += np.sum(distances ** 2)
            n += len(distances)

        mean_distance = sum_distances / n
        stdev = np.sqrt((sum_squared_distances - (mean_distance ** 2 * n)) / (n - 1))
        
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
def create_gnuplot_script(labels, output_dir):
    dir_gnu = f"{os.getcwd()}/{output_dir}".replace('_', '\\\_')
    with open(f"{output_dir}/plot_cluster.gnu", "w") as f:
        # Set up the multiplot layout
        f.write('set multiplot layout 2, 1\n')

        # First plot (main plot)
        f.write(f'set xlabel "Frames"\n')
        f.write('set ylabel "Data"\n')
        f.write(f'set title "{dir_gnu}"\n')
        f.write('set key outside\n')
        f.write('plot\\\n')
        for label in np.unique(labels):
            f.write(f'"cluster.c{label}.dat" u 1:2 every 10 title "C{label}",\\\n')
        f.write('\n')

        # Second plot (histogram)
        f.write('set xlabel "Data"\n')
        f.write('set ylabel "Count"\n')
        f.write('plot\\\n')
        for label in np.unique(labels):
            f.write(f'"cluster.c{label}.histo" u 1:2 every 1 title "C{label}",\\\n')
        f.write('\nunset multiplot\n')
        f.write('\npause -1\n')


# Create output directory
def create_output_dir(base="clusters"):
    counter = 1
    while os.path.exists(f"{base}_{counter}"):
        counter += 1
    os.makedirs(f"{base}_{counter}")
    return f"{base}_{counter}"


# Argument Parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description='Cluster data using K-means algorithm.')
    parser.add_argument('--data_file', default='forcluster.dat', help='File containing data to be clustered.')
    parser.add_argument('--col', type=int, default=1, help='Column of data to cluster. Indexing starts at 0.')
    parser.add_argument('--n_clusters', type=int, default=None, help='Number of clusters. Default determined by Elbow Method.')
    parser.add_argument('--tol', type=float, default=None, help='Tolerance for centroid convergence. Default determined by Davies-Bouldin Index.')
    parser.add_argument('--approx_centroids', nargs='+', type=float, default=None, help='List of initial centroid guesses. Example usage to pass multiple values "--approx_centroids 1.2 9.3"')
    return parser.parse_args()
args = parse_arguments()

data_file = args.data_file
col = args.col
n_clusters = args.n_clusters
tol = args.tol
approx_centroids = args.approx_centroids

if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help', 'help'):
    print_help()

output_dir = create_output_dir()
log_file = f"{output_dir}/cluster.log"
log_to_file(f"Run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
log_to_file(f"Output directory: {output_dir}", log_file)

if approx_centroids:
    log_to_file(f"Initially guessing {len(approx_centroids)} centroids at {approx_centroids}", log_file)
approx_centroids=np.array(approx_centroids).reshape(-1, 1)

values = np.loadtxt(data_file,usecols=(col,),unpack=True)
values = values.reshape(-1,1)
frames = np.arange(1,len(values)+1)

if n_clusters is None:
    log_to_file("Determining optimal clusters via Elbow Method...",log_file)
    n_clusters = elbow_method(values, range(1, 11),initial_centroids=approx_centroids)

log_to_file(f"Using {n_clusters} clusters.", log_file)

# Main
# ... (other parts remain the same)

if tol is None:
    log_to_file("Calculating initial tolerance...",log_file)
    tol = 0.1 * np.std(values)  # 10% of standard deviation as initial tolerance
    log_to_file(f"Initial tolerance set to {tol}",log_file)

centroids, labels = kmeans(values, n_clusters, initial_centroids=approx_centroids, tol=tol)
summary_data = cluster_summary(values, labels, centroids)

# Sort summary data by number of frames (Descending)
summary_data.sort(key=lambda x: x[1], reverse=True)

# Relabel clusters based on sorted summary
new_labels = {}
for new_label, (old_label, *_rest) in enumerate(summary_data):
    new_labels[old_label] = new_label

# Update the labels array
for i, label in enumerate(labels):
    labels[i] = new_labels[label]

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
    f.write("#Cluster   Frames     Frac  AvgDist    Stdev  Centroid AvgCDist   CValue \n")
    for new_label, row in enumerate(summary_data):
        f.write(f"{new_label:7d} {row[1]:9d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:8.3f} {row[7]:8.3f}\n")

# Use histogram script
for label in np.unique(labels):
    os.system(f"histogram.py -i '{output_dir}/cluster.c{label}.dat' -o '{output_dir}/cluster.c{label}.histo' -col 1")

# Generate Gnuplot script
create_gnuplot_script(labels,output_dir)
log_to_file("Generated Gnuplot script.", log_file)
log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
# Run Gnuplot
os.system(f"cd {output_dir}; gnuplot plot_cluster.gnu; cd -")
