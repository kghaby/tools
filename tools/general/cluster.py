#!/usr/bin/env python3

import numpy as np
import sys
import os 
from datetime import datetime
import argparse

# Moved heavy imports to respective functions 
# from sklearn.cluster import AgglomerativeClustering,KMeans
# from sklearn.neighbors import NearestCentroid

#TODO: Expand it to use arbitrary amount of columns ie dimensions

def log_to_file(message, log_file, printmsg=True):
    if printmsg:
        print(message)
    with open(log_file, 'a') as f:
        f.write(f"{message}\n")

def kmeans(data, k, initial_centroids=None, tol=1e-4, max_iter=100):
    from sklearn.cluster import KMeans # heavy import
    if initial_centroids is not None:
        if len(initial_centroids) != k:
            raise ValueError("Number of initial centroids must match k")
        init = np.array(initial_centroids)
        n_init = 1
    else:
        init = "k-means++"
        n_init = 10
    model = KMeans(n_clusters=k, init=init, n_init=n_init, tol=tol, max_iter=max_iter)
    model.fit(data)
    return model, model.cluster_centers_, model.labels_

def agglomerative_clustering(data, n_clusters, linkage):
    from sklearn.cluster import AgglomerativeClustering # heavy import
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    model.fit(data)
    centroids = np.array([data[model.labels_ == i].mean(axis=0) for i in range(n_clusters)])
    return model, centroids, model.labels_

def elbow_method(data, k_range, initial_centroids=None):
    # "discrete curvature" via second finite difference on inertia (≈ L-curve heuristic)
    inertia = []
    for k in k_range:
        model, centroids, _ = kmeans(data, k, initial_centroids)
        # inertia compatible with np.linalg.norm on broadcasted [k,d] vs [n,d]
        d = np.linalg.norm(data - centroids[:, np.newaxis], axis=2)
        inertia.append(np.sum(np.min(d, axis=0)))
    rate_change = np.diff(np.diff(inertia))
    return np.argmax(rate_change) + k_range[0] + 1

def label_full_data(model, method, full_data, subset_data=None, subset_labels=None):
    if method == "kmeans":
        return model.predict(full_data)
    else:
        from sklearn.neighbors import NearestCentroid # heavy import
        clf = NearestCentroid()
        clf.fit(subset_data, subset_labels)
        return clf.predict(full_data)

def cluster_summary(data, labels, centroids, frames):
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

def create_gnuplot_script(labels, output_dir):
    dir_gnu = f"{os.getcwd()}/{output_dir}".replace('_', '\\\\_')
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
        f.write(f'set notitle \n')
        f.write('set xlabel "Data"\n')
        f.write('set ylabel "Count"\n')
        f.write('plot\\\n')
        for label in np.unique(labels):
            f.write(f'"cluster.c{label}.histo" u 1:2 every 1 title "C{label}",\\\n')
        f.write('\nunset multiplot\n')
        f.write('\npause -1\n')

def create_output_dir(base="clusters"):
    counter = 1
    while os.path.exists(f"{base}_{counter}"):
        counter += 1
    os.makedirs(f"{base}_{counter}")
    return f"{base}_{counter}"

def parse_arguments():
    parser = argparse.ArgumentParser(description='Cluster data using various algorithms.')
    parser.add_argument('-i','--input_file', default='forcluster.dat', help='File containing data to be clustered.')
    parser.add_argument('-c','--col', type=int, default=1, help='Column of data to cluster. Indexing starts at 0.')
    parser.add_argument('-e','--every', type=int, default=1, help='Select every nth data point for initial clustering')
    parser.add_argument('-m','--method', default='kmeans', choices=['kmeans', 'agglomerative'], help='Clustering method to use: kmeans or agglomerative')
    parser.add_argument('-n','--n_clusters', type=int, default=None, help='Number of clusters. Default determined by Elbow Method.')
    parser.add_argument('-t','--tol', type=float, default=None, help='Tolerance for centroid convergence for Kmeans. Default determined by Davies-Bouldin Index.')
    parser.add_argument('-a','--approx_centroids', nargs='+', type=float, default=None, help='Initial centroid guesses for Kmeans. Example usage to pass multiple values "--approx_centroids 1.2 9.3"')
    parser.add_argument('-l','--linkage', default='ward', choices=['ward', 'complete', 'average', 'single'], help='Linkage criterion for Agglomerative Clustering')
    
    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help', 'help', 'h'):
        parser.print_help(sys.stderr)
        sys.exit(1) 
        
    return parser.parse_args()
        
def main():
    args = parse_arguments()
    
    input_file = args.input_file
    col = args.col
    n_clusters = args.n_clusters
    tol = args.tol
    approx_centroids = args.approx_centroids

    output_dir = create_output_dir()
    log_file = f"{output_dir}/cluster.log"
    log_to_file(f"Run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    log_to_file(f"Output directory: {output_dir}", log_file)

    values = np.loadtxt(input_file, usecols=(col,), unpack=True).reshape(-1, 1)
    frames = np.arange(1, len(values)+1)
    frames_subset = np.arange(1, len(values)+1, args.every)
    values_subset = values[frames_subset-1]

    # Get clusters
    if n_clusters is None:
        log_to_file("Determining optimal clusters via Elbow Method...", log_file)
        n_clusters = elbow_method(values_subset, range(1, 11), initial_centroids=approx_centroids)

    log_to_file(f"Using {n_clusters} clusters.", log_file)
    log_to_file(f"Using {args.method} clustering method on every {args.every} datapoints...", log_file)

    # Fit data 
    if args.method == 'kmeans':
        if approx_centroids is not None:
            log_to_file(f"Initially guessing {len(approx_centroids)} centroids at {approx_centroids}", log_file)
            approx_centroids = np.array(approx_centroids, dtype=float).reshape(-1, 1)
            if n_clusters is None or n_clusters != len(approx_centroids):
                n_clusters = len(approx_centroids)
                log_to_file(f"Setting n_clusters={n_clusters} based on initial guesses", log_file)
        if tol is None:
            tol = 0.1 * np.std(values_subset)
            log_to_file(f"Initial tolerance set to {tol}", log_file)
        model, centroids, labels_subset = kmeans(values_subset, n_clusters, initial_centroids=approx_centroids, tol=tol)

    elif args.method == 'agglomerative':
        log_to_file(f"Using {args.linkage} linkage method", log_file)
        model, centroids, labels_subset = agglomerative_clustering(values_subset, n_clusters, args.linkage)

    # Fit labels to full dataset
    if args.every > 1:
        labels = label_full_data(model, args.method, values, values_subset, labels_subset)
    else:
        labels = labels_subset

    # Summarize clusters
    summary_data = cluster_summary(values, labels, centroids, frames)
    summary_data.sort(key=lambda x: x[1], reverse=True)
    relabel_map = {old: new for new, (old, *_) in enumerate(summary_data)}
    labels = np.array([relabel_map[l] for l in labels])

    # Write outputs
    with open(f"{output_dir}/cluster.all.dat", 'w') as f:
        f.write("#Frame Data Cluster\n")
        for frame, val, lab in zip(frames, values.flatten(), labels):
            f.write(f"{int(frame)} {val:.6f} {lab}\n")

    for unique_label in np.unique(labels):
        with open(f"{output_dir}/cluster.c{unique_label}.dat", 'w') as f:
            f.write("#Frame Data Cluster\n")
            for frame, val, lab in zip(frames, values.flatten(), labels):
                if lab == unique_label:
                    f.write(f"{int(frame)} {val:.6f} {lab}\n")

    with open(f"{output_dir}/cluster.sum", 'w') as f:
        f.write("#Cluster   Frames     Frac  AvgDist    Stdev  Centroid AvgCDist   CValue \n")
        for new_label, row in enumerate(summary_data):
            f.write(f"{new_label:7d} {row[1]:9d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:8.3f} {row[7]:8.3f}\n")

    # Histograms and plotting
    bin_range = np.max(values) - np.min(values)
    binsize = bin_range / 100
    for lab in np.unique(labels):
        os.system(f"histogram.py -i '{output_dir}/cluster.c{lab}.dat' -o '{output_dir}/cluster.c{lab}.histo' -col 1 -binsize {binsize}")

    create_gnuplot_script(labels, output_dir)
    log_to_file("Generated Gnuplot script.", log_file)
    log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    os.system(f"cd {output_dir}; gnuplot plot_cluster.gnu; cd -")

if __name__ == "__main__":
    main()
