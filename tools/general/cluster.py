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
        else:
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

def cluster_summary(data, labels, centroids, frames):
    unique_labels = np.unique(labels)
    n_frames = len(data)
    summary = []
    for label in unique_labels:
        cluster_data = data[labels == label]
        n_cluster_frames = len(cluster_data)
        fraction = n_cluster_frames / n_frames
        # avg_dist: mean L1 distance of each point to its cluster mean
        mu = cluster_data.mean(axis=0, keepdims=True) if n_cluster_frames else np.zeros((1, data.shape[1]))
        avg_dist = float(np.abs(cluster_data - mu).sum(axis=1).mean()) if n_cluster_frames else 0.0
        mean_distance, stdev = _pairwise_l1_stats(cluster_data)

        # centroid_frame: pick point closest to mean in L1
        if n_cluster_frames:
            d_to_mu = np.abs(cluster_data - mu).sum(axis=1)
            centroid_idx = int(np.argmin(d_to_mu))
            centroid_frame = int(frames[labels == label][centroid_idx])
            print(frames[centroid_idx],frames[labels == label][centroid_idx])
        else:
            centroid_frame = -1
        # AvgCDist: mean L1 distance to other clusters mean
        other_clusters = [data[labels == other_label] for other_label in unique_labels if other_label != label]
        if other_clusters:
            other = np.concatenate(other_clusters, axis=0)
            avg_cdist = float(np.abs(cluster_data.mean(axis=0) - other.mean(axis=0)).sum())
        else:
            avg_cdist = float("nan")

        centroid_value = "[" + " ".join(f"{v:.6f}" for v in centroids[label].ravel()) + "]"
        summary.append([int(label), int(n_cluster_frames), float(fraction), float(avg_dist), float(stdev),
                        int(centroid_frame), float(avg_cdist), centroid_value])
    return summary

def plot_timeseries_with_right_hist(frames, values, labels, centroids, out_pdf, bins=100, show=True):
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

    color_map = {}
    for i, lab in enumerate(uniq):
        color_map[lab] = plt.rcParams["axes.prop_cycle"].by_key()["color"][i % len(plt.rcParams["axes.prop_cycle"].by_key()["color"])]

    step = max(len(frames) // 10000, 1)
    idx = np.arange(frames.size)[::step]
    ax.plot(frames[idx], y[idx], lw=0.8, alpha=0.3, color="black")
    for lab in uniq:
        m_idx = np.nonzero(labs == lab)[0]
        m_idx = np.intersect1d(m_idx, idx, assume_unique=False)
        ax.plot(frames[m_idx], y[m_idx], ls="none", marker="o", ms=2.5, alpha=1, color=color_map[lab])
        ax.plot([], [], label=f"C{lab}", color=color_map[lab], lw=2) # for legend

    ax.set_xlabel("Frame")
    ax.set_ylabel("Data")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1), ncols=min(len(uniq), 4), fontsize=12, frameon=False)

    y_min, y_max = np.min(y), np.max(y)
    bins_edges = np.linspace(y_min, y_max, bins + 1)

    for lab in uniq: 
        axh.hist(y[labs == lab], bins=bins_edges, orientation="horizontal", 
                 histtype="step", linewidth=1.2, alpha=0.9, color=color_map[lab], label=None)
        
    # Add centroid lines to histogram
    for lab in uniq:
        centroid_value = centroids[lab][0]  # For 1D data, centroid is a single value
        axh.axhline(y=centroid_value, color=color_map[lab], linestyle='--', linewidth=2, alpha=0.8)

    axh.grid(False)
    axh.axis("off")
    axh.set_xlim(0.1, axh.get_xlim()[1])

    ax.set_xlim(frames.min(),frames.max()-1)
    ax.set_ylim(y_min, y_max)
    
    fig.suptitle(os.path.abspath(os.path.dirname(out_pdf)), fontsize=10)
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

def plot_2d_hist_by_cluster(data2d, labels, centroids, out_pdf, colx_idx, coly_idx, bins=100, show=True):
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

    # Precompute all histograms first to get global normalization
    all_hists = []
    for lab in uniq:
        sel = (labs == lab)
        if not np.any(sel):
            all_hists.append(None)
            continue
        H, _, _ = np.histogram2d(x[sel], y[sel], bins=(x_edges, y_edges))
        H = H.T  # (Ny, Nx) for pcolormesh
        all_hists.append(H)
    
    # Get global maximum for normalization (excluding zeros for log scale)
    all_nonzero = np.concatenate([H[H > 0] for H in all_hists if H is not None])
    if len(all_nonzero) > 0:
        global_max = np.max(all_nonzero)
        # For log scale, we need to handle zeros and set a reasonable minimum
        log_min = np.min(all_nonzero) if len(all_nonzero) > 0 else 1
    else:
        global_max = 1
        log_min = 1
    
    # Draw histograms with global normalization and logarithmic scaling
    for i, (lab, H) in enumerate(zip(uniq, all_hists)):
        if H is None:
            continue
        
        # Apply logarithmic scaling to the histogram values
        H_log = np.zeros_like(H)
        non_zero_mask = H > 0
        H_log[non_zero_mask] = np.log10(H[non_zero_mask])
        
        # Normalize to [0, 1] range for coloring
        if np.any(non_zero_mask):
            log_max = np.log10(global_max)
            log_range = log_max - np.log10(log_min)
            if log_range > 0:
                H_norm = (H_log - np.log10(log_min)) / log_range
            else:
                H_norm = np.ones_like(H_log)
            H_norm = np.clip(H_norm, 0, 1)
        else:
            H_norm = np.zeros_like(H)
        
        cmap = _white_to_color_cmap(palette[i % len(palette)])
        
        # Use normalized values for both color and alpha, but with different scaling
        qm = ax.pcolormesh(
            x_edges, y_edges, H_norm,
            shading="auto", cmap=cmap, 
            vmin=0.0, vmax=1.0,
            # Use a nonlinear alpha scaling to make low values more visible
            alpha=H_norm**0.5,  # Square root scaling for better visibility
            antialiased=False, 
            zorder=1+i
        )
        ax.plot([], [], lw=6, color=palette[i % len(palette)], label=f"C{lab}")

    # Add centroid markers with black borders
    for i, lab in enumerate(uniq):
        centroid_x, centroid_y = centroids[lab]
        ax.scatter(centroid_x, centroid_y, s=100, color=palette[i % len(palette)], 
                  edgecolors='black', linewidth=2, zorder=100, marker='o')

    ax.set_xlabel(f"Col {colx_idx}")
    ax.set_ylabel(f"Col {coly_idx}")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend(loc="upper right", frameon=False)
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
    parser.add_argument("-m", "--method", default="kmeans", choices=["kmeans", "agglomerative"], help="Clustering method.")
    parser.add_argument("-k", "--n_clusters", type=int, default=None, help="Number of clusters; defaults via elbow.")
    parser.add_argument("-t", "--tol", type=float, default=None, help="KMeans tolerance; default 0.1*σ of subset.")
    parser.add_argument("-a", "--approx_centroids", nargs="+", type=float, default=None, help="Initial KMeans guesses flattened; length must be k*d (row-major).")
    parser.add_argument("-l", "--linkage", default="ward", choices=["ward", "complete", "average", "single"], help="Agglomerative linkage.")
    parser.add_argument("-b", "--bins", type=int, default=100, help="Histogram bins.")
    parser.add_argument("-x", "--max_iter", type=int, default=100, help="Max iterations for kmeans algorithm.")
    parser.add_argument("--no_show", action="store_true", help="Do not display the plot; just save the PDF.")
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
    approx_centroids = args.approx_centroids

    log_to_file(f"Run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)
    log_to_file(" ".join(sys.argv), log_file)
    output_dir = create_output_dir()
    log_file = f"{output_dir}/cluster.log"
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
    
    # prepare initial centroid guesses if provided: expect k*d floats; reshape to (k,d)
    if approx_centroids is not None:
        approx_centroids = np.array(approx_centroids, dtype=float)
        if n_clusters is None:
            if approx_centroids.size % d != 0:
                raise ValueError("Length of --approx_centroids must be a multiple of dimensionality d=len(--col).")
            n_clusters = approx_centroids.size // d
        if approx_centroids.size != n_clusters * d:
            raise ValueError("Length of --approx_centroids must equal n_clusters * d.")
        approx_centroids = approx_centroids.reshape(n_clusters, d)
        if args.method != "kmeans":
            log_to_file("WARNING: Initial centroids were set but method is not kmeans, so they will not be used.", log_file)
        log_to_file(f"Initial centroids:\n{approx_centroids}", log_file)

    # tol
    if tol is None:
        tol = 0.1 * float(np.std(values_subset_scaled))
    log_to_file(f"Tolerance set to {tol}", log_file)

    # choose k if unspecified
    if n_clusters is None:
        log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Determining optimal clusters via Elbow method (up to 11)", log_file)
        n_clusters = elbow_method(values_subset_scaled, range(1, 11),
                                  method=args.method,
                                  initial_centroids=approx_centroids,
                                  linkage=args.linkage,
                                  tol=tol,
                                  max_iter=args.max_iter,
                                  output_dir=output_dir)

    log_to_file(f"\tUsing {n_clusters} clusters.", log_file)
    log_to_file(f"\tLogged elbow plot to {output_dir}/elbow_curve.pdf", log_file)
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Using {args.method} clustering method on every {args.every} datapoints...", log_file)

    # Fit data 
    if args.method == "kmeans":
        model, centroids_scaled, labels_subset, _ = kmeans(values_subset_scaled, n_clusters, initial_centroids=approx_centroids, tol=tol, max_iter=args.max_iter)

    elif args.method == "agglomerative":
        log_to_file(f"Using {args.linkage} linkage method", log_file)
        model, centroids_scaled, labels_subset, _ = agglomerative_clustering(values_subset_scaled, n_clusters, args.linkage)

    # Fit labels to full dataset
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fitting labels to the full dataset", log_file)
    if args.every > 1:
        labels = label_full_data(model, args.method, values_scaled, values_subset_scaled, labels_subset)
    else:
        labels = labels_subset
    
    # Bring centroids back to original units
    centroids = scaler.inverse_transform(centroids_scaled) if scaler is not None else centroids_scaled

    # Summarize clusters
    log_to_file(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Getting centroids, etc.", log_file)
    summary_data = cluster_summary(values, labels, centroids, frames)
    summary_data.sort(key=lambda x: x[1], reverse=True)
    relabel_map = {old: new for new, (old, *_) in enumerate(summary_data)}
    labels = np.array([relabel_map[int(l)] for l in labels], dtype=int)
    
    # Reorder centroids to match the new labeling
    new_centroids = np.zeros_like(centroids)
    for old_label, new_label in relabel_map.items():
        new_centroids[new_label] = centroids[old_label]
    centroids = new_centroids
    log_to_file(f"Centroids:\n{centroids}", log_file)

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
        f.write("#Cluster   Frames     Frac  AvgL1     StdevL1  Centroid  AvgCDist   CVector\n")
        for new_label, row in enumerate(summary_data):
            f.write(f"{new_label:7d} {row[1]:9d} {row[2]:8.3f} {row[3]:8.3f} {row[4]:8.3f} {row[5]:9d} {row[6]:9.3f} {row[7]}\n")

    # Plotting
    out_pdf = os.path.join(output_dir, "cluster.pdf")
    if d == 1:
        plot_timeseries_with_right_hist(frames=frames, values=values[:, 0], labels=labels, centroids=centroids,
                                        out_pdf=out_pdf, bins=args.bins, show=not args.no_show)
        log_to_file(f"Saved plot: {out_pdf}", log_file)
    elif d == 2:
        plot_2d_hist_by_cluster(values[:, :2], labels, centroids, out_pdf=out_pdf, colx_idx=cols[0], coly_idx=cols[1], bins=args.bins, show=not args.no_show)
        log_to_file(f"Saved 2D histogram: {out_pdf}", log_file)
    else:
        log_to_file("Dimensionality > 2; skipping plotting.", log_file)
    log_to_file(f"Run ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", log_file)


if __name__ == "__main__":
    main()