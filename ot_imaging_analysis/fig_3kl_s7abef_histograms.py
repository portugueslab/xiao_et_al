import flammkuchen as fl
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import ranksums

from xiao_et_al_utils.defaults import IMAGING_DATA_MASTER_PATH, REL_SCORE_THR
from xiao_et_al_utils.plotting_utils import despine, save_figure

sns.set(palette="deep", style="ticks")
cols = sns.color_palette()


stim_thetas = np.array(fl.load(IMAGING_DATA_MASTER_PATH / "stim_pos.h5"))
pooled_data_df = fl.load(IMAGING_DATA_MASTER_PATH / "pooled_dfs.h5", "/all_cells_df")
exp_df = fl.load(IMAGING_DATA_MASTER_PATH / "pooled_dfs.h5", "/exp_df")

popt = fl.load(IMAGING_DATA_MASTER_PATH / "gaussian_fit.h5", "/popt")

fit_params = np.array(popt)

for i, par_name in enumerate(["fit_amp", "fit_mn", "fit_sigma"]):
    pooled_data_df[par_name] = fit_params[:, i]

pooled_data_df["fit_sigma"] = np.abs(pooled_data_df["fit_sigma"])

pooled_data_df["mean_sigma"] = np.nan
for f in exp_df.index:
    s = pooled_data_df.loc[
        (pooled_data_df["fid"] == f)
        & (pooled_data_df["max_rel"] > REL_SCORE_THR)
        & pooled_data_df["in_tectum"],
        "fit_sigma",
    ]
    exp_df.loc[f, "mean_sigma"] = np.nanmean(s)


HIST_FIG_SIZE = (4.0, 3)
group_colors = [(0.2,) * 3, cols[2]]


def hist_and_scatter(
    fig,
    hist_key,
    hist_range=None,
    hist_label=None,
    scatter_key=None,
    scatter_coef=1.0,
    scatter_label=None,
    ylim=None,
):
    SCAT_DISP = 5  # scatter dispersion
    hist_box = (0.12, 0.25, 0.4, 0.5)
    scat_box = (0.72, 0.25, 0.28, 0.5)
    p_val_size = 12

    gen_groups = ["MTZ-cnt", "OPC-abl"]

    axs = fig.add_axes(hist_box)

    rel_histograms = dict()
    for i, g in enumerate(gen_groups):
        sel_fids = pooled_data_df.loc[pooled_data_df["gen"] == g, "fid"].unique()
        all_hists = []
        for f in sel_fids:
            h, bins = np.histogram(
                pooled_data_df.loc[
                    (pooled_data_df["fid"] == f) & pooled_data_df["in_tectum"], hist_key
                ],
                hist_range,
                density=True,
            )
            all_hists.append(h)
        rel_histograms[g] = np.array(all_hists)

        x_bins = (bins[1:] + bins[:-1]) / 2

        axs.plot(x_bins, rel_histograms[g].T, c=group_colors[i], lw=0.2)
        axs.plot(x_bins, rel_histograms[g].mean(0), c=group_colors[i], lw=2, label=g)
    plt.legend(frameon=False)
    axs.set(yscale="log", xlabel=hist_label)
    axs.set_ylabel("log(p)", loc="top", rotation=0, labelpad=-15)
    despine(axs)

    scat_axs = fig.add_axes(scat_box)
    percentiles = dict()
    for i, g in enumerate(gen_groups):
        sel = exp_df.loc[exp_df["gen"] == g, scatter_key]
        scat_axs.scatter(
            (np.random.rand(len(sel)) - 0.5) / SCAT_DISP + i,
            sel * scatter_coef,
            c=group_colors[i],
            s=8,
            lw=0.3,
            ec=(1,) * 3,
        )
        percentiles[g] = np.percentile(sel, [50, 25, 75])

        l_dict = dict(lw=1, c=group_colors[i])
        scat_axs.boxplot(
            sel,
            showcaps=False,
            whis=0,
            sym="",
            widths=0.2,
            positions=[i],
            boxprops=l_dict,
            medianprops=l_dict,
            zorder=-100,
        )
    diff_p = ranksums(
        *[exp_df.loc[exp_df["gen"] == g, scatter_key] for g in gen_groups]
    )
    scat_axs.set(
        xlim=[-0.5, 1.5], xticks=[0, 1], xticklabels=gen_groups, ylabel=scatter_label
    )

    if ylim is not None:
        scat_axs.set_ylim(ylim)

    percent_str = (
        "median[quartiles]= "
        + str(percentiles["MTZ-cnt"])
        + " (MTZ-cnt); "
        + str(percentiles["OPC-abl"])
        + " (OPC-abl)"
    )
    print(f"p={diff_p.pvalue:0.4f}, U={diff_p.statistic:0.4f}, {percent_str}")
    pval = "n.s."
    if diff_p.pvalue < 0.05:
        pval = "*"
    if diff_p.pvalue < 0.01:
        pval = "**"
    if diff_p.pvalue < 0.001:
        pval = "***"
    pval_pos = np.percentile(exp_df.loc[:, scatter_key] * scatter_coef, 75)
    scat_axs.text(0.5, pval_pos, pval, fontsize=p_val_size, ha="center")
    despine(scat_axs)

    return axs, scat_axs


figsize = (6, 3.5)
fig_d = plt.figure(figsize=figsize)
axs, scat_axs = hist_and_scatter(
    fig_d,
    hist_key="max_rel",
    hist_range=np.arange(0, 1, 0.02),
    hist_label="reliability score",
    scatter_key="above_rel_thr",
    scatter_coef=1,
    scatter_label="responsive rois (n)",
)
axs.axvline(0.5, lw=0.5, c=(0.4,) * 3)
save_figure("fig_3k_s7a_hist")

fig_e = plt.figure(figsize=figsize)
axs, scat_axs = hist_and_scatter(
    fig_e,
    hist_key="max_amp",
    hist_range=np.arange(0, 5, 0.2),
    hist_label="response ampl.  ($\Delta F/F$)",
    scatter_key="mn_amplitude",
    scatter_label="average ampl. ($\Delta F/F$)",
    ylim=(0, 1.0),
)
save_figure("fig_3l_s7b_hist")

fig_g = plt.figure(figsize=figsize)
axs, scat_axs = hist_and_scatter(
    fig_g,
    hist_key="fit_sigma",
    hist_range=np.arange(0, 8, 0.2),
    hist_label="$\sigma$",
    scatter_key="mean_sigma",
    scatter_label="average $\sigma$",
    ylim=(0, 3.5),
)

save_figure("fig_s7ef_hist")
