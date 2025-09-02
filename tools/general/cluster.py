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
    with open(log_file, "a") as f:
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

        sum_distances, sum_squared_distances, n = 0.0, 0.0, 0
        for point in cluster_data:
            distances = np.abs(point - cluster_data)
            sum_distances += np.sum(distances)
            sum_squared_distances += np.sum(distances ** 2)
            n += len(distances)

        mean_distance = sum_distances / n
        stdev = np.sqrt((sum_squared_distances - (mean_distance ** 2 * n)) / max(n - 1, 1))
        
        # Centroid calculation
        cumulative_dists = [np.sum(np.abs(point - cluster_data)) for point in cluster_data]
        centroid_frame = frames[labels == label][np.argmin(cumulative_dists)]
        centroid_value = centroids[label][0]
        
        # AvgCDist: Average distance to other clusters
        other_clusters = np.concatenate(
            [data[labels == other_label] for other_label in unique_labels if other_label != label]
        ) if len(unique_labels) > 1 else np.array([np.nan])
        avg_cdist = np.mean(np.abs(cluster_data.mean() - other_clusters)) if other_clusters.size else np.nan

        summary.append([label, n_cluster_frames, fraction, avg_dist, stdev, int(centroid_frame), avg_cdist, centroid_value])
        
    return summary

def plot_timeseries_with_right_hist(frames, values, labels, out_pdf, bins=100, show=True):
    import matplotlib
    matplotlib.use("Agg" if not show else matplotlib.get_backend())
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    y = values.flatten()
    labs = np.asarray(labels)
    uniq = np.unique(labs)

    fig = plt.figure(figsize=(10, 4.8), constrained_layout=True)
    gs = GridSpec(nrows=1, ncols=2, width_ratios=[5.0, 1.6], wspace=0.0, figure=fig)
    ax = fig.add_subplot(gs[0, 0])
    axh = fig.add_subplot(gs[0, 1], sharey=ax)

    color_map = {}
    for i, lab in enumerate(uniq):
        color_map[lab] = plt.rcParams["axes.prop_cycle"].by_key()["color"][i % len(plt.rcParams["axes.prop_cycle"].by_key()["color"])]

    step = max(len(frames) // 1000, 1)
    ax.plot(frames[::step], y[::step], lw=0.8, alpha=0.5, color="black")
    for lab in uniq:
        m = labs == lab
        ax.plot(frames[m][::step], y[m][::step], ls="none", marker="o", ms=2.0, alpha=0.7, label=f"C{lab}", color=color_map[lab])

    ax.set_xlabel("Frame")
    ax.set_ylabel("Data")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1), ncols=min(len(uniq), 4), fontsize=12, frameon=False)

    y_min, y_max = np.min(y), np.max(y)
    bins_edges = np.linspace(y_min, y_max, bins + 1)

    counts, edges = np.histogram(y[labs == lab], bins=bins_edges)
    for i in range(len(counts)):
        if counts[i] > 0:
            y0, y1 = edges[i], edges[i+1]
            axh.hlines((y0 + y1)/2, 0, counts[i], color=color_map[lab], lw=1.2)

    axh.yaxis.set_visible(False)
    axh.set_xlabel("")
    axh.grid(False)
    axh.axis("off")
    axh.set_xlim(0, axh.get_xlim()[1])

    ax.set_xlim(frames.min(),frames.max())
    ax.set_ylim(y_min, y_max)
    
    fig.suptitle(os.path.abspath(os.path.dirname(out_pdf)), fontsize=10)
    fig.savefig(out_pdf, bbox_inches="tight", format="pdf")
    if show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)

def create_output_dir(base="clusters"):
    counter = 1
    while os.path.exists(f"{base}_{counter}"):
        counter += 1
    os.makedirs(f"{base}_{counter}")
    return f"{base}_{counter}"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cluster a univariate series and plot with an attached histogram.")
    parser.add_argument("-i", "--input_file", default="forcluster.dat", help="Data file.")
    parser.add_argument("-c", "--col", type=int, default=1, help="0-based column index to cluster.")
    parser.add_argument("-e", "--every", type=int, default=1, help="Subsample stride for initial clustering.")
    parser.add_argument("-m", "--method", default="kmeans", choices=["kmeans", "agglomerative"], help="Clustering method.")
    parser.add_argument("-k", "--n_clusters", type=int, default=None, help="Number of clusters; defaults via elbow.")
    parser.add_argument("-t", "--tol", type=float, default=None, help="KMeans tolerance; default 0.1*σ of subset.")
    parser.add_argument("-a", "--approx_centroids", nargs="+", type=float, default=None, help='Initial KMeans guesses, e.g. "--approx_centroids 1.2 9.3"')
    parser.add_argument("-l", "--linkage", default="ward", choices=["ward", "complete", "average", "single"], help="Agglomerative linkage.")
    parser.add_argument("-b", "--bins", type=int, default=100, help="Histogram bins.")
    parser.add_argument("--no_show", action="store_true", help="Do not display the plot; just save the PDF.")
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help", "help", "h"):
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
    if args.method == "kmeans":
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

    elif args.method == "agglomerative":
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
    with open(f"{output_dir}/cluster.all.dat", "w") as f:
        f.write("#Frame Data Cluster\n")
        for frame, val, lab in zip(frames, values.flatten(), labels):
            f.write(f"{int(frame)} {val:.6f} {lab}\n")

    for unique_label in np.unique(labels):
        with open(f"{output_dir}/cluster.c{unique_label}.dat", "w") as f:
            f.write("#Frame Data Cluster\n")
            for frame, val, lab in zip(frames, values.flatten(), labels):
                if lab == unique_label:
                    f.write(f"{int(frame)} {val:.6f} {lab}\n")

    with open(f"{output_dir}/cluster.sum", "w") as f:
        f.write("#Cluster   Frames     Frac  AvgDist    Stdev  Centroid AvgCDist   CValue \n")
        for new_label, row in enumerate(summary_data):
            f.write(f"{new_label:7d} {row[1]:9d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:8.3f} {row[7]:8.3f}\n")

    # Histograms and plotting
    out_pdf = os.path.join(output_dir, "cluster.pdf")
    plot_timeseries_with_right_hist(
        frames=frames,
        values=values,
        labels=labels,
        out_pdf=out_pdf,
        bins=args.bins,
        show=not args.no_show,
    )

    log_to_file(f"Saved plot: {out_pdf}", log_file)
    log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)


if __name__ == "__main__":
    main()
