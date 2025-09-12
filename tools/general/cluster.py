#!/usr/bin/env python3

import numpy as np
import sys
import os 
from datetime import datetime
import argparse

# Moved heavy imports to respective functions 
# from sklearn.cluster import AgglomerativeClustering,KMeans
# from sklearn.neighbors import NearestCentroid

def log_to_file(message, log_file, printmsg=True):
    if printmsg:
        print(message)
    with open(log_file, "a") as f:
        f.write(f"{message}\n")
        
def _parse_approx_centroids(tokens, d):
    import ast
    if tokens is None:
        return None
    # if any token has brackets, parse each; else treat as flat list
    if any(t.strip().startswith(("[", "(")) for t in tokens):
        pts = []
        for t in tokens:
            v = ast.literal_eval(t)
            v = list(v) if isinstance(v, (list, tuple, np.ndarray)) else [float(v)]
            if len(v) != d:
                raise ValueError(f"Centroid {t} has dim={len(v)}; expected d={d}.")
            pts.append([float(x) for x in v])
        return np.asarray(pts, dtype=float)
    # flat list
    vals = [float(x) for x in tokens]
    if d == 1:
        return np.asarray([[v] for v in vals], dtype=float)
    if len(vals) % d != 0:
        raise ValueError(f"Provided {len(vals)} numbers; not divisible by d={d}.")
    return np.asarray(list(map(list, np.array(vals, dtype=float).reshape(-1, d))), dtype=float)

def kmeans(data, k, initial_centroids=None, tol=1e-4, max_iter=100):
    from sklearn.cluster import KMeans
    if initial_centroids is not None:
        if len(initial_centroids) != k:
            raise ValueError("Number of initial centroids must match k")
        init = np.array(initial_centroids, dtype=float)
        n_init = 1
    else:
        init = "k-means++"
        n_init = 20
    model = KMeans(n_clusters=k, init=init, n_init=n_init, tol=tol, max_iter=max_iter, random_state=0)
    model.fit(data)
    return model, model.cluster_centers_, model.labels_, model.inertia_

def agglomerative_clustering(data, n_clusters, linkage):
    from sklearn.cluster import AgglomerativeClustering # heavy import
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    model.fit(data)
    centroids = np.array([data[model.labels_ == i].mean(axis=0) for i in range(n_clusters)])
    inertia = 0.0
    for i in range(n_clusters):
        Xc = data[model.labels_ == i]
        if Xc.size:
            dif = Xc - centroids[i]
            inertia += (dif * dif).sum()
    return model, centroids, model.labels_, inertia

def hdbscan_clustering(data, min_cluster_size, min_samples, cluster_selection_epsilon, max_cluster_size=None, cluster_selection_method="eom", leaf_size=40):
    from sklearn.cluster import HDBSCAN # heavy import
    model = HDBSCAN(min_cluster_size=min_cluster_size, 
                    min_samples=min_samples, 
                    cluster_selection_epsilon=cluster_selection_epsilon, 
                    max_cluster_size=max_cluster_size, 
                    algorithm="auto", 
                    allow_single_cluster=True, 
                    store_centers="centroid", 
                    cluster_selection_method=cluster_selection_method, 
                    leaf_size=leaf_size)
    model.fit(data)
    return model, model.centroids_, model.labels_

def _kneedle(x, y, decreasing=True):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    # normalize to [0,1]
    x_n = (x - x.min()) / (x.max() - x.min() + 1e-12)
    y_n = (y - y.min()) / (y.max() - y.min() + 1e-12)
    if decreasing:
        y_n = 1.0 - y_n  # convert to increasing
    # distance from identity
    diff = y_n - x_n
    return int(np.argmax(diff))

def elbow_method(data, k_range, method="kmeans", initial_centroids=None, linkage="ward", tol=1e-4, max_iter=100, output_dir="."):
    ks = list(k_range)
    inertia = []
    for k in ks:
        if method == "kmeans":
            _, _, _, iner = kmeans(data, k, initial_centroids, tol=tol, max_iter=max_iter)
        elif method == "agglomerative":
            _, _, _, iner = agglomerative_clustering(data, k, linkage)
        inertia.append(float(iner))
    inertia = np.asarray(inertia, dtype=float)
    if inertia.size == 0:
        raise ValueError("Empty k_range for elbow_method.")
    if inertia.size == 1:
        return int(ks[0])
    inertia_log = np.log(np.maximum(inertia, 1e-12))
    idx = _kneedle(np.asarray(ks, dtype=float), inertia_log, decreasing=True)
    plot_elbow_curve(ks, inertia_log, output_dir=output_dir)
    return int(ks[idx])

def plot_elbow_curve(ks, inertias, output_dir):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(ks, inertias, 'bo-')
    plt.xlabel('Number of clusters')
    plt.ylabel('ln(Inertia)')
    plt.savefig(f"{output_dir}/elbow_curve.pdf", bbox_inches="tight", format="pdf")
    plt.close()

def label_full_data(model, method, full_data, subset_data=None, subset_labels=None):
    if method == "kmeans":
        return model.predict(full_data)
    elif method == "hdbscan":
        # Separate valid clusters from noise in the subset
        valid_mask = subset_labels >= 0
        valid_data = subset_data[valid_mask]
        valid_labels = subset_labels[valid_mask]
        
        if len(valid_labels) == 0:
            return np.full(len(full_data), -1)
        
        # distance based
        from sklearn.neighbors import NearestNeighbors
        from scipy.spatial.distance import cdist
        
        cluster_properties = {}
        for label in np.unique(valid_labels):
            cluster_points = valid_data[valid_labels == label]
            centroid = cluster_points.mean(axis=0)
            
            centroid_distances = np.linalg.norm(cluster_points - centroid, axis=1)
            radius = np.percentile(centroid_distances, 95) if len(centroid_distances) > 1 else 0.1
            if len(cluster_points) > 1:
                pairwise_distances = cdist(cluster_points, cluster_points)
                np.fill_diagonal(pairwise_distances, np.inf)
                avg_neighbor_dist = np.mean(np.min(pairwise_distances, axis=1))
            else:
                avg_neighbor_dist = 0.1
            
            cluster_properties[label] = {
                'centroid': centroid,
                'radius': radius,
                'avg_neighbor_dist': avg_neighbor_dist,
                'max_distance': np.max(centroid_distances) if len(centroid_distances) > 0 else 0.1
            }
        
        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(subset_data)
        distances, indices = nn.kneighbors(full_data)
        
        distances = distances.flatten()
        indices = indices.flatten()
        
        full_labels = np.full(len(full_data), -1)
        
        for i, (distance, idx) in enumerate(zip(distances, indices)):
            nearest_label = subset_labels[idx]
            
            if nearest_label >= 0:  # valid cluster
                props = cluster_properties[nearest_label]
                
                # Use multiple criteria for threshold
                threshold1 = props['radius'] * 3.0 
                threshold2 = props['avg_neighbor_dist'] * 10.0 
                threshold3 = props['max_distance'] * 2.0 
                
                # Use the most generous threshold
                threshold = max(threshold1, threshold2, threshold3)
                
                # Also check if point is closer to this cluster than to any other cluster centroid
                if distance <= threshold:
                    full_labels[i] = nearest_label
                else:
                    # Additional check: if this point is closer to this cluster's centroid
                    # than to any other cluster's centroid, assign it anyway
                    centroid_distances = []
                    for other_label, other_props in cluster_properties.items():
                        dist_to_centroid = np.linalg.norm(full_data[i] - other_props['centroid'])
                        centroid_distances.append((other_label, dist_to_centroid))
                    
                    # Find the closest centroid
                    closest_label, min_centroid_dist = min(centroid_distances, key=lambda x: x[1])
                    
                    if closest_label == nearest_label and min_centroid_dist <= threshold1 * 2:
                        full_labels[i] = nearest_label
                    else:
                        full_labels[i] = -1
            else:
                full_labels[i] = nearest_label  # keep noise label
        
        return full_labels
    else:
        unique_labels = np.unique(subset_labels)
        valid_labels = unique_labels[unique_labels >= 0]
        if len(valid_labels) == 1:
            return np.full(len(full_data), valid_labels[0])
        elif len(valid_labels) == 0:
            if len(unique_labels) > 0:
                return np.full(len(full_data), unique_labels[0])
            else:
                return np.full(len(full_data), -1)
        else:
            from sklearn.neighbors import NearestCentroid # heavy import
            clf = NearestCentroid()
            clf.fit(subset_data, subset_labels)
            return clf.predict(full_data)
    
def _pairwise_l1_stats(cluster_data):
    # compute L1 distances to the cluster mean
    if len(cluster_data) <= 1:
        return 0.0, 0.0
    mu = cluster_data.mean(axis=0, keepdims=True)
    d = np.abs(cluster_data - mu).sum(axis=1)
    return float(d.mean()), float(d.std(ddof=1))

def cluster_summary(data, labels, centroids_map, frames):
    """
    Handles special HDBSCAN labels: -1 (noise), -2 (inf), -3 (NaN).
    For negative labels, no centroid is assumed (centroid_frame = -1, CVector = 'NA').
    For non-negative labels, centroid comes from centroids_map[lab] if present;
    otherwise falls back to the cluster mean
    """
    unique_labels = np.unique(labels)
    n_frames = len(data)
    summary = []
    for lab in unique_labels:
        sel = (labels == lab)
        cluster_data = data[sel]
        n_cluster_frames = cluster_data.shape[0]
        fraction = n_cluster_frames / n_frames
        mean_distance, stdev = _pairwise_l1_stats(cluster_data)

        centroid_frame = -1
        centroid_value_str = "NA"
        # centroid_frame: pick the frame whose full vector is closest (squared L2) to the cluster centroid
        if n_cluster_frames > 0:
            if lab >= 0:
                c = centroids_map.get(lab, cluster_data.mean(axis=0))
                d2 = np.einsum("ij,ij->i", cluster_data - c, cluster_data - c)
                idx = int(np.argmin(d2))
                centroid_frame = int(frames[sel][idx])
                centroid_value_str = "[" + " ".join(f"{v:.6f}" for v in cluster_data[idx].ravel()) + "]"
            else:
                centroid_frame = -1
                centroid_value_str = "NA"

        # AvgCDist: mean L1 distance to other clusters mean
        other = data[~sel]
        if other.size:
            avg_cdist = float(np.abs(cluster_data.mean(axis=0) - other.mean(axis=0)).sum())
        else:
            avg_cdist = float("nan")

        summary.append([
            int(lab),                        # Cluster label (can be -1/-2/-3)
            int(n_cluster_frames),           # Frames
            float(fraction),                 # Frac
            float(mean_distance),            # AvgL1
            float(stdev),                    # StdevL1
            int(centroid_frame),             # Centroid frame id or -1
            float(avg_cdist),                # AvgCDist
            centroid_value_str               # CVector
        ])
    return summary

def plot_timeseries_with_right_hist(frames, values, labels, centroids_map, out_pdf, bins=100, show=True):
    import matplotlib
    matplotlib.use("Agg" if not show else matplotlib.get_backend())
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    y = values.flatten()
    labs = np.asarray(labels)
    uniq = np.unique(labs)

    fig = plt.figure(figsize=(10, 4.8), constrained_layout=True)
    gs = GridSpec(nrows=1, ncols=2, width_ratios=[5.0, 1.6], wspace=0.0003, figure=fig)
    ax = fig.add_subplot(gs[0, 0])
    axh = fig.add_subplot(gs[0, 1], sharey=ax)

    palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    color_map = {lab: palette[i % len(palette)] for i, lab in enumerate(uniq)}

    step = max(len(frames) // 10000, 1)
    idx = np.arange(frames.size)[::step]
    ax.plot(frames[idx], y[idx], lw=0.8, alpha=0.3, color="black")
    for lab in uniq:
        m_idx = np.nonzero(labs == lab)[0]
        m_idx = np.intersect1d(m_idx, idx, assume_unique=False)
        ax.plot(frames[m_idx], y[m_idx], ls="none", marker="o", ms=2.5, alpha=1, color=color_map[lab])
        ax.plot([], [], label=f"C{lab}", color=color_map[lab], lw=2)

    ax.set_xlabel("Frame")
    ax.set_ylabel("Data")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1), ncols=min(len(uniq), 4), fontsize=12, frameon=False)

    y_min, y_max = np.min(y), np.max(y)
    bins_edges = np.linspace(y_min, y_max, bins + 1)

    for lab in uniq:
        axh.hist(y[labs == lab], bins=bins_edges, orientation="horizontal",
                 histtype="step", linewidth=1.2, alpha=0.9, color=color_map[lab])

    # centroid lines only for non-negative labels with defined centroids
    for lab in uniq:
        if lab >= 0 and (lab in centroids_map):
            cv = float(centroids_map[lab][0])
            if np.isfinite(cv):
                axh.axhline(y=cv, color=color_map[lab], linestyle="--", linewidth=2, alpha=0.8)

    axh.grid(False)
    axh.axis("off")
    axh.set_xlim(0.1, axh.get_xlim()[1])

    ax.set_xlim(frames.min(), frames.max() - 1)
    ax.set_ylim(y_min, y_max)
    fig.suptitle(os.path.abspath(os.path.dirname(out_pdf)), fontsize=8)
    fig.savefig(out_pdf, bbox_inches="tight", format="pdf")
    if show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)

def _white_to_color_cmap(base_color):
    from matplotlib.colors import LinearSegmentedColormap, to_rgb
    rgb = to_rgb(base_color)
    return LinearSegmentedColormap.from_list("w2c", [(1, 1, 1), rgb], N=256)

def plot_2d_hist_by_cluster(data2d, labels, centroids_map, out_pdf, colx_idx, coly_idx, bins=100, show=True):
    import matplotlib
    matplotlib.use("Agg" if not show else matplotlib.get_backend())
    import matplotlib.pyplot as plt

    x, y = data2d[:, 0], data2d[:, 1]
    labs = np.asarray(labels)
    uniq = np.unique(labs)

    fig, ax = plt.subplots(figsize=(6.2, 5.6), constrained_layout=True)
    palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    x_min, x_max = float(x.min()), float(x.max())
    y_min, y_max = float(y.min()), float(y.max())
    x_edges = np.linspace(x_min, x_max, bins + 1)
    y_edges = np.linspace(y_min, y_max, bins + 1)

    all_hists = []
    for lab in uniq:
        sel = (labs == lab)
        if not np.any(sel):
            all_hists.append(None)
            continue
        H, _, _ = np.histogram2d(x[sel], y[sel], bins=(x_edges, y_edges))
        all_hists.append(H.T)

    all_nonzero = np.concatenate([H[H > 0] for H in all_hists if H is not None]) if any(H is not None for H in all_hists) else np.array([])
    global_max = np.max(all_nonzero) if all_nonzero.size else 1
    log_min = np.min(all_nonzero) if all_nonzero.size else 1

    for i, (lab, H) in enumerate(zip(uniq, all_hists)):
        if H is None:
            continue
        H_log = np.zeros_like(H)
        nz = H > 0
        H_log[nz] = np.log10(H[nz])
        if nz.any():
            log_max = np.log10(global_max)
            log_range = log_max - np.log10(log_min)
            H_norm = (H_log - np.log10(log_min)) / (log_range if log_range > 0 else 1.0)
            H_norm = np.clip(H_norm, 0, 1)
        else:
            H_norm = np.zeros_like(H)
        cmap = _white_to_color_cmap(palette[i % len(palette)])
        ax.pcolormesh(x_edges, y_edges, H_norm, shading="auto", cmap=cmap, vmin=0.0, vmax=1.0, alpha=H_norm**0.5, antialiased=False, zorder=1+i)
        ax.plot([], [], lw=6, color=palette[i % len(palette)], label=f"C{lab}")

    # centroid markers only for non-negative labels with defined centroids
    for i, lab in enumerate(uniq):
        if lab >= 0 and (lab in centroids_map):
            cx, cy = centroids_map[lab][:2]
            ax.scatter(cx, cy, s=100, color=palette[i % len(palette)], edgecolors="black", linewidth=2, zorder=100, marker="o")

    ax.set_xlabel(f"Col {colx_idx}")
    ax.set_ylabel(f"Col {coly_idx}")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend(frameon=False)
    fig.suptitle(os.path.abspath(os.path.dirname(out_pdf)), fontsize=8)
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
    parser.add_argument("-c", "--col", type=int, nargs="+", default=[1], help="0-based column index/indices to cluster. Provide one or more.")
    parser.add_argument("-e", "--every", type=int, default=1, help="Subsample stride for initial clustering.")
    parser.add_argument("-m", "--method", default="kmeans", choices=["kmeans", "agglomerative", "hdbscan"], help="Clustering method.")
    parser.add_argument("-k", "--n_clusters", type=int, default=None, help="Number of clusters; defaults via elbow.")
    parser.add_argument("-t", "--tol", type=float, default=None, help="KMeans tolerance; default 0.1*σ of subset.")
    parser.add_argument("-a", "--approx_centroids", nargs="+", type=str, default=None, help="Initial KMeans guesses; space-separated series of centroids (can be bracketed), eg for 3 2D clusters, `-a [x1,y1] [x2,y2] [x3,y3]` or `-a x1 y1 x2 y2 x3 y3`.")
    parser.add_argument("-l", "--linkage", default="ward", choices=["ward", "complete", "average", "single"], help="Agglomerative linkage.")
    parser.add_argument("-b", "--bins", type=int, default=100, help="Histogram bins.")
    parser.add_argument("-x", "--max_iter", type=int, default=100, help="Max iterations for kmeans algorithm.")
    parser.add_argument("--no_show", action="store_true", help="Do not display the plot; just save the PDF.")
    parser.add_argument("--hdbscan_min_cluster_size", type=int, default=5, help="Minimum cluster size for HDBSCAN.")
    parser.add_argument("--hdbscan_epsilon", type=float, default=0.0, help="Cluster selection epsilon for HDBSCAN.")
    parser.add_argument("--hdbscan_min_samples", type=int, default=None, help="'k' parameter in HDBSCAN. Used to calculate the distance between a point its k-th nearest neighbor; defaults to min_cluster_size if not set.")
    parser.add_argument("--hdbscan_max_cluster_size", type=int, default=None, help="Maximum cluster size for HDBSCAN.")
    parser.add_argument("--hdbscan_cluster_selection_method", type=str, default="eom", choices=["eom", "leaf"], help="Cluster selection method for HDBSCAN.")
    parser.add_argument("--hdbscan_leaf_size", type=int, default=40, help="Leaf size for HDBSCAN.")

    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help", "help", "h"):
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()
        
def main():
    args = parse_arguments()
    
    input_file = args.input_file
    cols = list(args.col)
    d = len(cols)
    n_clusters = args.n_clusters
    tol = args.tol

    output_dir = create_output_dir()
    log_file = f"{output_dir}/cluster.log"
    log_to_file(f"Run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    log_to_file(" ".join(sys.argv), log_file)
    log_to_file(f"Output directory: {output_dir}", log_file)

    values = np.loadtxt(input_file, usecols=tuple(cols), unpack=False, ndmin=2)
    if values.ndim == 1:
        values = values[:, None]
    frames = np.arange(1, len(values) + 1)
    frames_subset = np.arange(1, len(values) + 1, args.every)
    values_subset = values[frames_subset - 1, :]

    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    values_scaled = scaler.fit_transform(values)
    values_subset_scaled = values_scaled[frames_subset - 1, :]
    
    # prepare initial centroid guesses
    approx_centroids = _parse_approx_centroids(args.approx_centroids, d)
    if approx_centroids is not None:
        k_from_init = approx_centroids.shape[0]
        if args.n_clusters is not None and args.n_clusters != k_from_init:
            raise ValueError(f"-k = {args.n_clusters} but {k_from_init} centroids approximated.")
        n_clusters = k_from_init if args.n_clusters is None else args.n_clusters
        approx_centroids_scaled = scaler.transform(approx_centroids) 
        if args.method != "kmeans":
            log_to_file("WARNING: Initial centroids were set but method is not kmeans, so they will be ignored.", log_file)
        else:
            log_to_file(f"Initial centroids (orig units):\n{approx_centroids}", log_file)
            log_to_file(f"Initial centroids (scaled):\n{approx_centroids_scaled}", log_file)
    else:
        approx_centroids_scaled = None

    # tol
    if tol is None:
        tol = 0.1 * float(np.std(values_subset_scaled))
    log_to_file(f"Tolerance set to {tol}", log_file)

    # choose k if unspecified
    if n_clusters is None and args.method != "hdbscan":
        log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Determining optimal clusters via Elbow method (up to 11)", log_file)
        n_clusters = elbow_method(values_subset_scaled, range(1, 11),
                                  method=args.method,
                                  initial_centroids=approx_centroids_scaled,
                                  linkage=args.linkage,
                                  tol=tol,
                                  max_iter=args.max_iter,
                                  output_dir=output_dir)
        log_to_file(f"\tLogged elbow plot to {output_dir}/elbow_curve.pdf", log_file)

    if args.method != "hdbscan":
        log_to_file(f"Using {n_clusters} clusters.", log_file)
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using {args.method} clustering method on every {args.every} datapoints...", log_file)

    # Fit data 
    if args.method == "kmeans":
        model, centroids_scaled, labels_subset, _ = kmeans(
            values_subset_scaled, n_clusters,
            initial_centroids=approx_centroids_scaled, tol=tol, max_iter=args.max_iter
        )

    elif args.method == "agglomerative":
        log_to_file(f"Using {args.linkage} linkage method", log_file)
        model, centroids_scaled, labels_subset, _ = agglomerative_clustering(values_subset_scaled, n_clusters, args.linkage)
        
    elif args.method == "hdbscan":
        model, centroids_scaled, labels_subset  = hdbscan_clustering(values_subset_scaled, args.hdbscan_min_cluster_size, args.hdbscan_min_samples, 
                                                                     args.hdbscan_epsilon, max_cluster_size=args.hdbscan_max_cluster_size, 
                                                                     cluster_selection_method=args.hdbscan_cluster_selection_method, 
                                                                     leaf_size=args.hdbscan_leaf_size)
        log_to_file(f"Found {len(set(labels_subset)) - (1 if -1 in labels_subset else 0)} clusters (+ noise) with HDBSCAN", log_file)

    # Fit labels to full dataset
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fitting labels to the full dataset", log_file)
    if args.every > 1:
        labels = label_full_data(model, args.method, values_scaled, values_subset_scaled, labels_subset)
    else:
        labels = labels_subset
    
    # Bring centroids back to original units
    #centroids = scaler.inverse_transform(centroids_scaled) if scaler is not None else centroids_scaled

    # Summarize clusters
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting centroids, etc.", log_file)
    # 1) initial summary (for counts) regardless of centroids
    summary_data = cluster_summary(values, labels, centroids_map={}, frames=frames)

    # 2) relabel only non-negative clusters by size
    pos_rows = [row for row in summary_data if row[0] >= 0]
    pos_rows.sort(key=lambda x: x[1], reverse=True)
    relabel_map = {old_lab: new_lab for new_lab, (old_lab, *_) in enumerate(pos_rows)}
    labels = np.array([relabel_map.get(int(lab), int(lab)) for lab in labels], dtype=int)

    # 3) build centroids_map only for non-negative labels
    centroids_map = {}
    for lab in np.unique(labels):
        if lab >= 0:
            sel = (labels == lab)
            if np.any(sel):
                centroids_map[lab] = values[sel].mean(axis=0)

    # 4) recompute summary with final labels and centroids_map (gives centroid_frame etc.)
    summary_data = cluster_summary(values, labels, centroids_map, frames)
    summary_data.sort(key=lambda x: (x[0] < 0, -x[1]))  # positives by size desc, then negatives

    # 5) log centroids
    centroids_from_frames = {}
    for lab in np.unique(labels):
        if lab >= 0:
            sel = (labels == lab)
            c = centroids_map[lab]
            d2 = np.einsum("ij,ij->i", values[sel] - c, values[sel] - c)
            idx = int(np.argmin(d2))
            centroids_from_frames[lab] = values[sel][idx]
    log_to_file("Centroids (theory):\n" + "\n".join([f"C{lab}: {centroids_map[lab]}" for lab in sorted(centroids_map)]), log_file)
    log_to_file("Centroids (from frames):\n" + "\n".join([f"C{lab}: {centroids_from_frames[lab]}" for lab in sorted(centroids_from_frames)]), log_file)

    # Write outputs
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Writing outputs.", log_file)
    with open(f"{output_dir}/cluster.all.dat", "w") as f:
        f.write("#Frame " + " ".join([f"Col{j}" for j in range(d)]) + " Cluster\n")
        for frame, row, lab in zip(frames, values, labels):
            f.write(f"{int(frame)} " + " ".join(f"{v:.6f}" for v in row) + f" {int(lab)}\n")

    for unique_label in np.unique(labels):
        with open(f"{output_dir}/cluster.c{int(unique_label)}.dat", "w") as f:
            f.write("#Frame " + " ".join([f"Col{j}" for j in cols]) + " Cluster\n")
            sel = (labels == unique_label)
            for frame, row, lab in zip(frames[sel], values[sel], labels[sel]):
                f.write(f"{int(frame)} " + " ".join(f"{v:.6f}" for v in row) + f" {int(lab)}\n")

    with open(f"{output_dir}/cluster.sum", "w") as f:
        f.write("#Cluster   Frames     Frac    AvgL1  StdevL1  Centroid  AvgCDist CVector\n")
        for row in summary_data:
            f.write(f"{row[0]:4d} {row[1]:12d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:9.3f} {row[7]}\n")

    # Plotting (skip centroid overlays for negative labels automatically)
    out_pdf = os.path.join(output_dir, "cluster.pdf")
    if d == 1:
        plot_timeseries_with_right_hist(frames=frames, values=values[:, 0], labels=labels,
                                        centroids_map=centroids_from_frames, out_pdf=out_pdf,
                                        bins=args.bins, show=not args.no_show)
        log_to_file(f"Saved plot: {out_pdf}", log_file)
    elif d == 2:
        plot_2d_hist_by_cluster(values[:, :2], labels, centroids_from_frames, out_pdf=out_pdf,
                                colx_idx=cols[0], coly_idx=cols[1], bins=args.bins, show=not args.no_show)
        log_to_file(f"Saved 2D histogram: {out_pdf}", log_file)
    else:
        log_to_file("Dimensionality > 2; skipping plotting.", log_file)
    log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)


if __name__ == "__main__":
    main()