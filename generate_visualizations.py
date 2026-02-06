"""
Cell Division Volume Visualization
Generates research-paper quality figures from the arrangement tab
of the single cell division volume Excel file.

Output: PNG files in /visualization directory
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import os
from itertools import combinations

# Fix random seed so plots are identical across runs
np.random.seed(42)

# ============================================================
# 1. PARSE DATA FROM EXCEL
# ============================================================

df_raw = pd.read_excel(
    'data/single cell division_volume.xlsx',
    sheet_name='arrangement',
    header=None,
)

# Forward-fill sample and tissue type columns
df_raw.columns = ['Sample', 'Tissue', 'CellNumber', 'Vol_0h', 'Vol_12h', 'Vol_14h']
# Drop header rows (rows 0-2)
df = df_raw.iloc[3:].copy().reset_index(drop=True)
df['Sample'] = df['Sample'].ffill()
df['Tissue'] = df['Tissue'].ffill()

# Clean up types
df['CellNumber'] = pd.to_numeric(df['CellNumber'], errors='coerce')
df['Vol_0h'] = pd.to_numeric(df['Vol_0h'], errors='coerce')
df['Vol_12h'] = pd.to_numeric(df['Vol_12h'], errors='coerce')
df['Vol_14h'] = pd.to_numeric(df['Vol_14h'], errors='coerce')

# Drop any rows with NaN cell numbers
df = df.dropna(subset=['CellNumber']).reset_index(drop=True)

# Shorten sample names for plotting
sample_map = {
    'SAMPLE 02 (stage 6-6.5)': 'Sample 02\n(stage 6–6.5)',
    'SAMPLE 08 (stage 6.5-7)': 'Sample 08\n(stage 6.5–7)',
    'SAMPLE 03 (stage 4)': 'Sample 03\n(stage 4)',
}
sample_map_short = {
    'SAMPLE 02 (stage 6-6.5)': 'Sample 02',
    'SAMPLE 08 (stage 6.5-7)': 'Sample 08',
    'SAMPLE 03 (stage 4)': 'Sample 03',
}
df['SampleLabel'] = df['Sample'].map(sample_map)
df['SampleShort'] = df['Sample'].map(sample_map_short)

# Derived metrics
df['Growth_0_12h'] = df['Vol_12h'] - df['Vol_0h']
df['Growth_12_14h'] = df['Vol_14h'] - df['Vol_12h']
df['Growth_0_14h'] = df['Vol_14h'] - df['Vol_0h']
df['GrowthPct_0_12h'] = (df['Growth_0_12h'] / df['Vol_0h']) * 100
df['GrowthPct_0_14h'] = (df['Growth_0_14h'] / df['Vol_0h']) * 100
df['GrowthPct_12_14h'] = (df['Growth_12_14h'] / df['Vol_12h']) * 100

# Melt for time-series plots
df_melt = df.melt(
    id_vars=['Sample', 'SampleLabel', 'SampleShort', 'Tissue', 'CellNumber'],
    value_vars=['Vol_0h', 'Vol_12h', 'Vol_14h'],
    var_name='Timepoint',
    value_name='Volume',
)
time_map = {'Vol_0h': '0 h', 'Vol_12h': '12 h', 'Vol_14h': '14 h'}
df_melt['Timepoint'] = df_melt['Timepoint'].map(time_map)

# Print summary
print("Data parsed successfully!")
print(f"  Total cells: {len(df)}")
for s in df['Sample'].unique():
    sub = df[df['Sample'] == s]
    print(f"  {s}:")
    for t in sub['Tissue'].unique():
        n = len(sub[sub['Tissue'] == t])
        print(f"    {t}: {n} cells")

# ============================================================
# 2. STYLE CONFIGURATION (research-paper quality)
# ============================================================

os.makedirs('visualization', exist_ok=True)

plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'lines.linewidth': 1.2,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

# Color palettes
SAMPLE_COLORS = {
    'SAMPLE 02 (stage 6-6.5)': '#4C72B0',
    'SAMPLE 08 (stage 6.5-7)': '#DD8452',
    'SAMPLE 03 (stage 4)': '#55A868',
}
TISSUE_COLORS = {
    'Locule': '#5B9BD5',
    'Connective tissue': '#ED7D31',
}
TISSUE_HATCHES = {
    'Locule': '',
    'Connective tissue': '',
}

SAMPLE_ORDER = [
    'SAMPLE 03 (stage 4)',
    'SAMPLE 02 (stage 6-6.5)',
    'SAMPLE 08 (stage 6.5-7)',
]
SAMPLE_LABEL_ORDER = [sample_map[s] for s in SAMPLE_ORDER]
SAMPLE_SHORT_ORDER = [sample_map_short[s] for s in SAMPLE_ORDER]


def add_significance_bracket(ax, x1, x2, y, h, text, fontsize=8):
    """Draw a significance bracket between two x-positions."""
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=0.8, c='black')
    ax.text((x1 + x2) / 2, y + h, text, ha='center', va='bottom', fontsize=fontsize)


def save_fig(fig, name):
    path = f'visualization/{name}.png'
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {path}")


# ============================================================
# FIGURE 1: Locule comparison across samples
# (Box + strip plot of volumes at each timepoint)
# ============================================================

def fig1_locule_across_samples():
    data = df_melt[df_melt['Tissue'] == 'Locule'].copy()
    data['Timepoint'] = pd.Categorical(data['Timepoint'], categories=['0 h', '12 h', '14 h'], ordered=True)
    data['SampleShort'] = pd.Categorical(data['SampleShort'], categories=SAMPLE_SHORT_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 3, figsize=(10, 4), sharey=True)
    fig.suptitle('Locule Cell Volume Across Samples', fontweight='bold', y=1.02)

    for i, tp in enumerate(['0 h', '12 h', '14 h']):
        ax = axes[i]
        sub = data[data['Timepoint'] == tp]
        sns.boxplot(
            data=sub, x='SampleShort', y='Volume',
            order=SAMPLE_SHORT_ORDER,
            palette=[SAMPLE_COLORS[s] for s in SAMPLE_ORDER],
            width=0.5, linewidth=0.8, fliersize=0,
            boxprops=dict(alpha=0.4), ax=ax,
        )
        sns.stripplot(
            data=sub, x='SampleShort', y='Volume',
            order=SAMPLE_SHORT_ORDER,
            palette=[SAMPLE_COLORS[s] for s in SAMPLE_ORDER],
            size=5, jitter=0.15, alpha=0.8, edgecolor='white', linewidth=0.4, ax=ax,
        )
        ax.set_title(f't = {tp}', fontsize=11)
        ax.set_xlabel('')
        if i == 0:
            ax.set_ylabel('Volume (μm³)')
        else:
            ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=0)

    fig.tight_layout()
    save_fig(fig, '01_locule_across_samples')


# ============================================================
# FIGURE 2: Connective tissue comparison across samples
# ============================================================

def fig2_ct_across_samples():
    data = df_melt[df_melt['Tissue'] == 'Connective tissue'].copy()
    data['Timepoint'] = pd.Categorical(data['Timepoint'], categories=['0 h', '12 h', '14 h'], ordered=True)
    data['SampleShort'] = pd.Categorical(data['SampleShort'], categories=SAMPLE_SHORT_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 3, figsize=(10, 4), sharey=True)
    fig.suptitle('Connective Tissue Cell Volume Across Samples', fontweight='bold', y=1.02)

    for i, tp in enumerate(['0 h', '12 h', '14 h']):
        ax = axes[i]
        sub = data[data['Timepoint'] == tp]
        sns.boxplot(
            data=sub, x='SampleShort', y='Volume',
            order=SAMPLE_SHORT_ORDER,
            palette=[SAMPLE_COLORS[s] for s in SAMPLE_ORDER],
            width=0.5, linewidth=0.8, fliersize=0,
            boxprops=dict(alpha=0.4), ax=ax,
        )
        sns.stripplot(
            data=sub, x='SampleShort', y='Volume',
            order=SAMPLE_SHORT_ORDER,
            palette=[SAMPLE_COLORS[s] for s in SAMPLE_ORDER],
            size=5, jitter=0.15, alpha=0.8, edgecolor='white', linewidth=0.4, ax=ax,
        )
        ax.set_title(f't = {tp}', fontsize=11)
        ax.set_xlabel('')
        if i == 0:
            ax.set_ylabel('Volume (μm³)')
        else:
            ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=0)

    fig.tight_layout()
    save_fig(fig, '02_connective_tissue_across_samples')


# ============================================================
# FIGURE 3: Locule vs Connective tissue within each sample
# (Paired box+strip at each timepoint, one panel per sample)
# ============================================================

def fig3_tissue_within_sample():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.5), sharey=True)
    fig.suptitle('Locule vs. Connective Tissue Within Each Sample', fontweight='bold', y=1.02)

    for i, sample in enumerate(SAMPLE_ORDER):
        ax = axes[i]
        sub = df_melt[df_melt['Sample'] == sample].copy()
        sub['Timepoint'] = pd.Categorical(sub['Timepoint'], categories=['0 h', '12 h', '14 h'], ordered=True)

        sns.boxplot(
            data=sub, x='Timepoint', y='Volume', hue='Tissue',
            hue_order=['Locule', 'Connective tissue'],
            palette=TISSUE_COLORS,
            width=0.6, linewidth=0.8, fliersize=0,
            boxprops=dict(alpha=0.4), ax=ax,
        )
        sns.stripplot(
            data=sub, x='Timepoint', y='Volume', hue='Tissue',
            hue_order=['Locule', 'Connective tissue'],
            palette=TISSUE_COLORS,
            size=4.5, jitter=0.12, alpha=0.85, edgecolor='white', linewidth=0.3,
            dodge=True, ax=ax, legend=False,
        )
        ax.set_title(sample_map_short[sample], fontsize=11)
        ax.set_xlabel('Timepoint')
        if i == 0:
            ax.set_ylabel('Volume (μm³)')
        else:
            ax.set_ylabel('')

        # Only keep legend on first panel
        if i == 0:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:2], labels[:2], loc='upper left', frameon=True,
                      framealpha=0.9, edgecolor='gray', fontsize=8)
        else:
            ax.get_legend().remove()

    fig.tight_layout()
    save_fig(fig, '03_locule_vs_connective_within_sample')


# ============================================================
# FIGURE 4: Overall Locule vs Connective tissue (all samples pooled)
# ============================================================

def fig4_overall_locule_vs_ct():
    data = df_melt.copy()
    data['Timepoint'] = pd.Categorical(data['Timepoint'], categories=['0 h', '12 h', '14 h'], ordered=True)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    fig.suptitle('Overall Locule vs. Connective Tissue\n(All Samples Pooled)', fontweight='bold', y=1.02)

    sns.boxplot(
        data=data, x='Timepoint', y='Volume', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        width=0.55, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax,
    )
    sns.stripplot(
        data=data, x='Timepoint', y='Volume', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        size=4.5, jitter=0.12, alpha=0.8, edgecolor='white', linewidth=0.3,
        dodge=True, ax=ax, legend=False,
    )
    ax.set_xlabel('Timepoint')
    ax.set_ylabel('Volume (μm³)')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], loc='upper left', frameon=True,
              framealpha=0.9, edgecolor='gray')

    fig.tight_layout()
    save_fig(fig, '04_overall_locule_vs_connective_tissue')


# ============================================================
# FIGURE 5: Growth trajectories — individual cell traces
# (Line plot: each cell as a thin line, mean as bold)
# ============================================================

def fig5_growth_trajectories():
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharey='row')
    fig.suptitle('Individual Cell Volume Trajectories Over Time', fontweight='bold', y=1.02)

    timepoints = [0, 12, 14]

    for col_i, sample in enumerate(SAMPLE_ORDER):
        for row_i, tissue in enumerate(['Locule', 'Connective tissue']):
            ax = axes[row_i, col_i]
            sub = df[(df['Sample'] == sample) & (df['Tissue'] == tissue)]

            if len(sub) == 0:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                        transform=ax.transAxes, fontsize=10, color='gray')
                ax.set_xlim(-1, 16)
                continue

            # Individual traces
            for _, row in sub.iterrows():
                vols = [row['Vol_0h'], row['Vol_12h'], row['Vol_14h']]
                ax.plot(timepoints, vols, color=SAMPLE_COLORS[sample],
                        alpha=0.3, linewidth=0.8, marker='o', markersize=3)

            # Mean trace
            mean_vols = [sub['Vol_0h'].mean(), sub['Vol_12h'].mean(), sub['Vol_14h'].mean()]
            ax.plot(timepoints, mean_vols, color=SAMPLE_COLORS[sample],
                    linewidth=2.2, marker='s', markersize=6, markeredgecolor='white',
                    markeredgewidth=0.8, label='Mean', zorder=5)

            # SEM shading
            for t_i, t in enumerate(timepoints):
                col_name = ['Vol_0h', 'Vol_12h', 'Vol_14h'][t_i]
                sem = sub[col_name].sem()
                ax.fill_between([t - 0.3, t + 0.3],
                                mean_vols[t_i] - sem, mean_vols[t_i] + sem,
                                color=SAMPLE_COLORS[sample], alpha=0.15)

            ax.set_xticks(timepoints)
            ax.set_xticklabels(['0 h', '12 h', '14 h'])
            ax.set_xlim(-1, 16)

            # Division line between 12h and 14h
            ax.axvline(x=13, color='#C0392B', linestyle=':', alpha=0.7, linewidth=1.5)
            if row_i == 0 and col_i == 0:
                ax.text(13.2, ax.get_ylim()[1] * 0.97, 'Division',
                        color='#C0392B', fontsize=7, fontweight='bold',
                        va='top', ha='left')

            if col_i == 0:
                ax.set_ylabel('Volume (μm³)')
            if row_i == 0:
                ax.set_title(f'{sample_map_short[sample]}', fontsize=11)
            if row_i == 1:
                ax.set_xlabel('Timepoint')

            # Tissue label on right
            if col_i == 2:
                ax.annotate(tissue, xy=(1.05, 0.5), xycoords='axes fraction',
                            fontsize=10, rotation=270, va='center', ha='left')

            n = len(sub)
            ax.text(0.97, 0.03, f'n = {n}', transform=ax.transAxes,
                    ha='right', va='bottom', fontsize=8, color='gray')

    fig.tight_layout()
    save_fig(fig, '05_individual_cell_trajectories')


# ============================================================
# FIGURE 5b: Combined Locule trajectory (all samples, one panel)
# ============================================================

def fig5b_locule_combined_trajectory():
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle('Locule Cell Volume Trajectory Through Division\n(All Samples)', fontweight='bold', y=1.04)

    stages = ['0 h\n(Before growth)', '12 h\n(Before division)', '14 h\n(After division)']
    x_pos = [0, 1, 2]

    sub_all = df[df['Tissue'] == 'Locule']

    # Individual traces
    for _, row in sub_all.iterrows():
        color = SAMPLE_COLORS[row['Sample']]
        vols = [row['Vol_0h'], row['Vol_12h'], row['Vol_14h']]
        ax.plot(x_pos, vols, '-o', color=color, alpha=0.25, linewidth=0.8, markersize=3.5)

    # Mean traces per sample
    for sample in SAMPLE_ORDER:
        sub = sub_all[sub_all['Sample'] == sample]
        if len(sub) == 0:
            continue
        means = [sub['Vol_0h'].mean(), sub['Vol_12h'].mean(), sub['Vol_14h'].mean()]
        ax.plot(x_pos, means, '-s', color=SAMPLE_COLORS[sample],
                linewidth=2.5, markersize=10, label=f'{sample_map_short[sample]} (n={len(sub)})',
                markeredgecolor='white', markeredgewidth=1, zorder=5)

    # Division line
    ax.axvline(x=1.5, color='#C0392B', linestyle=':', alpha=0.8, linewidth=1.8)
    ylim = ax.get_ylim()
    ax.text(1.55, ylim[1] - (ylim[1] - ylim[0]) * 0.03, 'DIVISION', color='#C0392B',
            fontsize=9, fontweight='bold', va='top')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(stages)
    ax.set_ylabel('Volume (μm³)')
    ax.set_xlim(-0.3, 2.4)
    ax.legend(frameon=True, framealpha=0.9, edgecolor='gray', fontsize=9, loc='upper left')

    fig.tight_layout()
    save_fig(fig, '05b_locule_combined_trajectory')


# ============================================================
# FIGURE 5c: Combined Connective Tissue trajectory (all samples)
# ============================================================

def fig5c_ct_combined_trajectory():
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle('Connective Tissue Cell Volume Trajectory Through Division\n(All Samples)', fontweight='bold', y=1.04)

    stages = ['0 h\n(Before growth)', '12 h\n(Before division)', '14 h\n(After division)']
    x_pos = [0, 1, 2]

    sub_all = df[df['Tissue'] == 'Connective tissue']

    # Individual traces
    for _, row in sub_all.iterrows():
        color = SAMPLE_COLORS[row['Sample']]
        vols = [row['Vol_0h'], row['Vol_12h'], row['Vol_14h']]
        ax.plot(x_pos, vols, '-o', color=color, alpha=0.25, linewidth=0.8, markersize=3.5)

    # Mean traces per sample
    for sample in SAMPLE_ORDER:
        sub = sub_all[sub_all['Sample'] == sample]
        if len(sub) == 0:
            continue
        means = [sub['Vol_0h'].mean(), sub['Vol_12h'].mean(), sub['Vol_14h'].mean()]
        ax.plot(x_pos, means, '-s', color=SAMPLE_COLORS[sample],
                linewidth=2.5, markersize=10, label=f'{sample_map_short[sample]} (n={len(sub)})',
                markeredgecolor='white', markeredgewidth=1, zorder=5)

    # Division line
    ax.axvline(x=1.5, color='#C0392B', linestyle=':', alpha=0.8, linewidth=1.8)
    ylim = ax.get_ylim()
    ax.text(1.55, ylim[1] - (ylim[1] - ylim[0]) * 0.03, 'DIVISION', color='#C0392B',
            fontsize=9, fontweight='bold', va='top')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(stages)
    ax.set_ylabel('Volume (μm³)')
    ax.set_xlim(-0.3, 2.4)
    ax.legend(frameon=True, framealpha=0.9, edgecolor='gray', fontsize=9, loc='upper left')

    fig.tight_layout()
    save_fig(fig, '05c_connective_tissue_combined_trajectory')


# ============================================================
# FIGURE 6: Percentage growth (0h → 14h) by sample and tissue
# ============================================================

def fig6_percent_growth():
    data = df.copy()
    data['SampleShort'] = pd.Categorical(data['SampleShort'], categories=SAMPLE_SHORT_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5), sharey=True)
    fig.suptitle('Percentage Volume Growth (0 h → 14 h)', fontweight='bold', y=1.02)

    # Panel A: by sample, colored by tissue
    ax = axes[0]
    sns.boxplot(
        data=data, x='SampleShort', y='GrowthPct_0_14h', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        width=0.55, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax,
    )
    sns.stripplot(
        data=data, x='SampleShort', y='GrowthPct_0_14h', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        size=5, jitter=0.1, alpha=0.85, edgecolor='white', linewidth=0.3,
        dodge=True, ax=ax, legend=False,
    )
    ax.set_xlabel('')
    ax.set_ylabel('Volume growth (%)')
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], loc='upper right', frameon=True,
              framealpha=0.9, edgecolor='gray', fontsize=8)
    ax.set_title('By Sample & Tissue', fontsize=11)

    # Panel B: all samples pooled by tissue
    ax = axes[1]
    sns.boxplot(
        data=data, x='Tissue', y='GrowthPct_0_14h',
        order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        width=0.45, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax,
    )
    sns.stripplot(
        data=data, x='Tissue', y='GrowthPct_0_14h',
        order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        size=5, jitter=0.15, alpha=0.85, edgecolor='white', linewidth=0.3,
        ax=ax,
    )
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
    ax.set_title('Overall (Pooled)', fontsize=11)

    fig.tight_layout()
    save_fig(fig, '06_percent_growth_0h_to_14h')


# ============================================================
# FIGURE 7: Mean volume bar chart with error bars
# (Grouped bar: sample x tissue, at each timepoint)
# ============================================================

def fig7_mean_volume_bars():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), sharey=True)
    fig.suptitle('Mean Cell Volume (± SEM) by Sample and Tissue Type', fontweight='bold', y=1.02)

    for i, tp in enumerate(['Vol_0h', 'Vol_12h', 'Vol_14h']):
        ax = axes[i]
        tp_label = {'Vol_0h': '0 h', 'Vol_12h': '12 h', 'Vol_14h': '14 h'}[tp]

        # Calculate means and SEMs
        grouped = df.groupby(['Sample', 'Tissue'])[tp].agg(['mean', 'sem', 'count']).reset_index()
        grouped['SampleShort'] = grouped['Sample'].map(sample_map_short)
        grouped['SampleShort'] = pd.Categorical(grouped['SampleShort'], categories=SAMPLE_SHORT_ORDER, ordered=True)
        grouped = grouped.sort_values('SampleShort')

        x = np.arange(len(SAMPLE_SHORT_ORDER))
        width = 0.3

        for j, tissue in enumerate(['Locule', 'Connective tissue']):
            sub = grouped[grouped['Tissue'] == tissue]
            means = []
            sems = []
            for s in SAMPLE_SHORT_ORDER:
                row = sub[sub['SampleShort'] == s]
                if len(row) > 0:
                    means.append(row['mean'].values[0])
                    sems.append(row['sem'].values[0] if not np.isnan(row['sem'].values[0]) else 0)
                else:
                    means.append(0)
                    sems.append(0)

            offset = -width / 2 + j * width
            bars = ax.bar(x + offset, means, width, yerr=sems,
                          label=tissue if i == 0 else '',
                          color=TISSUE_COLORS[tissue], alpha=0.75,
                          edgecolor='white', linewidth=0.5,
                          capsize=3, error_kw={'linewidth': 0.8})

        ax.set_title(f't = {tp_label}', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(SAMPLE_SHORT_ORDER, fontsize=9)
        ax.set_xlabel('')
        if i == 0:
            ax.set_ylabel('Mean volume (μm³)')
            ax.legend(frameon=True, framealpha=0.9, edgecolor='gray', fontsize=8)

    fig.tight_layout()
    save_fig(fig, '07_mean_volume_bars_with_sem')


# ============================================================
# FIGURE 8: Heatmap of mean volume change (0h→12h, 12h→14h)
# ============================================================

def fig8_growth_heatmap():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    fig.suptitle('Mean Volume Change Heatmap', fontweight='bold', y=1.05)

    for i, (metric, label) in enumerate([
        ('GrowthPct_0_12h', '0 h → 12 h'),
        ('GrowthPct_12_14h', '12 h → 14 h'),
    ]):
        ax = axes[i]
        pivot = df.pivot_table(
            values=metric, index='Tissue',
            columns='SampleShort', aggfunc='mean',
        )
        # Reorder
        pivot = pivot.reindex(index=['Locule', 'Connective tissue'],
                              columns=SAMPLE_SHORT_ORDER)

        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn',
                    center=0, linewidths=0.8, linecolor='white',
                    cbar_kws={'label': 'Growth (%)', 'shrink': 0.8},
                    ax=ax, annot_kws={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_title(f'Growth: {label}', fontsize=11)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=0)
        ax.tick_params(axis='y', rotation=0)

    fig.tight_layout()
    save_fig(fig, '08_growth_heatmap')


# ============================================================
# FIGURE 9: Paired dot plot — volume at 0h vs 14h
# ============================================================

def fig9_paired_dotplot():
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(1, 3, figsize=(12, 5), sharey=True)
    fig.suptitle('Cell Volume Trajectory (0 h → 12 h → 14 h) with Tissue Means',
                 fontweight='bold', y=1.02)

    x_pos = [0, 1, 2]
    stages = ['0 h', '12 h', '14 h']

    for i, sample in enumerate(SAMPLE_ORDER):
        ax = axes[i]
        sub = df[df['Sample'] == sample].copy()

        # Individual cell traces
        for _, row in sub.iterrows():
            color = TISSUE_COLORS[row['Tissue']]
            vols = [row['Vol_0h'], row['Vol_12h'], row['Vol_14h']]
            ax.plot(x_pos, vols, '-o', color=color, alpha=0.3, linewidth=0.8,
                    markersize=4, markeredgecolor='white', markeredgewidth=0.3)

        # Mean traces per tissue type
        for tissue in ['Locule', 'Connective tissue']:
            tsub = sub[sub['Tissue'] == tissue]
            if len(tsub) == 0:
                continue
            means = [tsub['Vol_0h'].mean(), tsub['Vol_12h'].mean(), tsub['Vol_14h'].mean()]
            ax.plot(x_pos, means, '-s', color=TISSUE_COLORS[tissue],
                    linewidth=2.5, markersize=9, zorder=5,
                    markeredgecolor='white', markeredgewidth=1,
                    label=f'{tissue} mean (n={len(tsub)})')

        # Division line
        ax.axvline(x=1.5, color='#C0392B', linestyle=':', alpha=0.7, linewidth=1.5)
        if i == 0:
            ylim = ax.get_ylim()
            ax.text(1.55, ax.get_ylim()[1] * 0.97, 'Division',
                    color='#C0392B', fontsize=8, fontweight='bold', va='top')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(stages)
        ax.set_title(sample_map_short[sample], fontsize=11)
        if i == 0:
            ax.set_ylabel('Volume (μm³)')
        ax.set_xlim(-0.3, 2.4)

        # Legend on first panel
        if i == 0:
            ax.legend(frameon=True, framealpha=0.9, edgecolor='gray', fontsize=7.5,
                      loc='upper left')

    fig.tight_layout()
    save_fig(fig, '09_paired_dotplot_0h_12h_14h')


# ============================================================
# FIGURE 10: Violin plot — volume distribution by tissue, all samples
# ============================================================

def fig10_violin_overall():
    data = df_melt.copy()
    data['Timepoint'] = pd.Categorical(data['Timepoint'], categories=['0 h', '12 h', '14 h'], ordered=True)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.suptitle('Volume Distribution: Locule vs. Connective Tissue\n(All Samples, All Timepoints)',
                 fontweight='bold', y=1.04)

    parts = sns.violinplot(
        data=data, x='Timepoint', y='Volume', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS, split=True, inner=None,
        linewidth=0.8, ax=ax, density_norm='width', alpha=0.5,
    )
    sns.stripplot(
        data=data, x='Timepoint', y='Volume', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        size=3.5, jitter=0.06, alpha=0.7, edgecolor='white', linewidth=0.2,
        dodge=True, ax=ax, legend=False,
    )

    ax.set_xlabel('Timepoint')
    ax.set_ylabel('Volume (μm³)')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], loc='upper left', frameon=True,
              framealpha=0.9, edgecolor='gray')

    fig.tight_layout()
    save_fig(fig, '10_violin_locule_vs_connective_tissue')


# ============================================================
# FIGURE 11: Scatter — Volume at 12h vs 14h (Before vs After Division)
# with identity line, inspired by old v0 analysis
# ============================================================

def fig11_before_vs_after_division_scatter():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.suptitle('Volume Conservation at Cell Division (12 h → 14 h)', fontweight='bold', y=1.02)

    # Panel A: colored by sample
    ax = axes[0]
    for sample in SAMPLE_ORDER:
        sub = df[df['Sample'] == sample]
        ax.scatter(sub['Vol_12h'], sub['Vol_14h'],
                   c=SAMPLE_COLORS[sample], label=sample_map_short[sample],
                   s=50, alpha=0.8, edgecolors='white', linewidth=0.5, zorder=3)
    vmax = max(df['Vol_12h'].max(), df['Vol_14h'].max()) * 1.1
    ax.plot([0, vmax], [0, vmax], 'k--', alpha=0.4, linewidth=0.8, label='No change (y = x)')
    ax.set_xlabel('Volume at 12 h (μm³)')
    ax.set_ylabel('Volume at 14 h (μm³)')
    ax.set_title('By Sample', fontsize=11)
    ax.set_xlim(0, vmax)
    ax.set_ylim(0, vmax)
    ax.set_aspect('equal')
    ax.legend(fontsize=8, frameon=True, framealpha=0.9, edgecolor='gray', loc='lower right')
    ax.text(0.03, 0.97, 'Above line = Volume gained\nBelow line = Volume lost',
            transform=ax.transAxes, fontsize=7, va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', alpha=0.8, edgecolor='gray'))

    # Panel B: colored by tissue
    ax = axes[1]
    for tissue in ['Locule', 'Connective tissue']:
        sub = df[df['Tissue'] == tissue]
        ax.scatter(sub['Vol_12h'], sub['Vol_14h'],
                   c=TISSUE_COLORS[tissue], label=tissue,
                   s=50, alpha=0.8, edgecolors='white', linewidth=0.5, zorder=3)
    ax.plot([0, vmax], [0, vmax], 'k--', alpha=0.4, linewidth=0.8, label='No change (y = x)')
    ax.set_xlabel('Volume at 12 h (μm³)')
    ax.set_ylabel('Volume at 14 h (μm³)')
    ax.set_title('By Tissue', fontsize=11)
    ax.set_xlim(0, vmax)
    ax.set_ylim(0, vmax)
    ax.set_aspect('equal')
    ax.legend(fontsize=8, frameon=True, framealpha=0.9, edgecolor='gray', loc='lower right')

    fig.tight_layout()
    save_fig(fig, '11_volume_before_vs_after_division_scatter')


# ============================================================
# FIGURE 12: Volume change % at division (12h→14h) — box+strip
# ============================================================

def fig12_division_volume_change():
    data = df.copy()
    data['SampleShort'] = pd.Categorical(data['SampleShort'], categories=SAMPLE_SHORT_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    fig.suptitle('Volume Change During Cell Division (12 h → 14 h)', fontweight='bold', y=1.02)

    # Panel A: By sample
    ax = axes[0]
    sns.boxplot(
        data=data, x='SampleShort', y='GrowthPct_12_14h',
        hue='SampleShort', palette={s: SAMPLE_COLORS[k] for s, k in zip(SAMPLE_SHORT_ORDER, SAMPLE_ORDER)},
        width=0.5, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax, legend=False,
    )
    sns.stripplot(
        data=data, x='SampleShort', y='GrowthPct_12_14h',
        hue='SampleShort', palette={s: SAMPLE_COLORS[k] for s, k in zip(SAMPLE_SHORT_ORDER, SAMPLE_ORDER)},
        size=5, jitter=0.15, alpha=0.85, edgecolor='white', linewidth=0.3,
        ax=ax, legend=False,
    )
    ax.axhline(0, color='black', linestyle='--', alpha=0.4, linewidth=0.8)
    ax.set_xlabel('')
    ax.set_ylabel('Volume change at division (%)')
    ax.set_title('By Sample', fontsize=11)
    # Add mean annotations
    for i, s in enumerate(SAMPLE_SHORT_ORDER):
        sub = data[data['SampleShort'] == s]
        mean_val = sub['GrowthPct_12_14h'].mean()
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ = {mean_val:.1f}%',
                ha='center', fontsize=8, color='gray')

    # Panel B: By tissue
    ax = axes[1]
    sns.boxplot(
        data=data, x='Tissue', y='GrowthPct_12_14h',
        order=['Locule', 'Connective tissue'],
        hue='Tissue', palette=TISSUE_COLORS,
        width=0.45, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax, legend=False,
    )
    sns.stripplot(
        data=data, x='Tissue', y='GrowthPct_12_14h',
        order=['Locule', 'Connective tissue'],
        hue='Tissue', palette=TISSUE_COLORS,
        size=5, jitter=0.15, alpha=0.85, edgecolor='white', linewidth=0.3,
        ax=ax, legend=False,
    )
    ax.axhline(0, color='black', linestyle='--', alpha=0.4, linewidth=0.8)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('By Tissue', fontsize=11)
    for i, t in enumerate(['Locule', 'Connective tissue']):
        sub = data[data['Tissue'] == t]
        mean_val = sub['GrowthPct_12_14h'].mean()
        ax.text(i, ax.get_ylim()[1] * 0.95, f'μ = {mean_val:.1f}%',
                ha='center', fontsize=8, color='gray')

    # Panel C: By sample + tissue (grouped)
    ax = axes[2]
    sns.boxplot(
        data=data, x='SampleShort', y='GrowthPct_12_14h', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        width=0.55, linewidth=0.8, fliersize=0,
        boxprops=dict(alpha=0.4), ax=ax,
    )
    sns.stripplot(
        data=data, x='SampleShort', y='GrowthPct_12_14h', hue='Tissue',
        hue_order=['Locule', 'Connective tissue'],
        palette=TISSUE_COLORS,
        size=4, jitter=0.1, alpha=0.85, edgecolor='white', linewidth=0.3,
        dodge=True, ax=ax, legend=False,
    )
    ax.axhline(0, color='black', linestyle='--', alpha=0.4, linewidth=0.8)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title('By Sample & Tissue', fontsize=11)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], fontsize=8, frameon=True,
              framealpha=0.9, edgecolor='gray', loc='lower left')

    fig.tight_layout()
    save_fig(fig, '12_volume_change_at_division')


# ============================================================
# FIGURE 13: Growth phases comparison — bar chart
# (Growth 0→12h vs Change at division 12→14h)
# ============================================================

def fig13_growth_phases():
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle('Comparison of Growth Phases', fontweight='bold', y=1.02)

    # Panel A: by sample
    ax = axes[0]
    samples_short = SAMPLE_SHORT_ORDER
    x = np.arange(len(samples_short))
    width = 0.3

    growth_before = []
    change_at_div = []
    growth_before_sem = []
    change_at_div_sem = []
    for s in SAMPLE_ORDER:
        sub = df[df['Sample'] == s]
        growth_before.append(sub['GrowthPct_0_12h'].mean())
        change_at_div.append(sub['GrowthPct_12_14h'].mean())
        growth_before_sem.append(sub['GrowthPct_0_12h'].sem())
        change_at_div_sem.append(sub['GrowthPct_12_14h'].sem())

    bars1 = ax.bar(x - width/2, growth_before, width, yerr=growth_before_sem,
                   label='Growth (0 h → 12 h)', color='#5B9BD5', alpha=0.8,
                   edgecolor='white', linewidth=0.5, capsize=3, error_kw={'linewidth': 0.8})
    bars2 = ax.bar(x + width/2, change_at_div, width, yerr=change_at_div_sem,
                   label='Change at division (12 h → 14 h)', color='#ED7D31', alpha=0.8,
                   edgecolor='white', linewidth=0.5, capsize=3, error_kw={'linewidth': 0.8})

    ax.set_ylabel('Volume change (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(samples_short, fontsize=9)
    ax.axhline(0, color='black', linestyle='-', alpha=0.2)
    ax.legend(fontsize=8, frameon=True, framealpha=0.9, edgecolor='gray', loc='upper left')
    ax.set_title('By Sample (mean ± SEM)', fontsize=11)

    # Value labels
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1.5, f'{h:.1f}%',
                ha='center', fontsize=7.5, color='gray')
    for bar in bars2:
        h = bar.get_height()
        offset = 1.5 if h >= 0 else -3.5
        ax.text(bar.get_x() + bar.get_width()/2, h + offset, f'{h:.1f}%',
                ha='center', fontsize=7.5, color='gray')

    # Panel B: by tissue (pooled)
    ax = axes[1]
    tissues = ['Locule', 'Connective tissue']
    x2 = np.arange(len(tissues))

    growth_before_t = []
    change_at_div_t = []
    growth_before_t_sem = []
    change_at_div_t_sem = []
    for t in tissues:
        sub = df[df['Tissue'] == t]
        growth_before_t.append(sub['GrowthPct_0_12h'].mean())
        change_at_div_t.append(sub['GrowthPct_12_14h'].mean())
        growth_before_t_sem.append(sub['GrowthPct_0_12h'].sem())
        change_at_div_t_sem.append(sub['GrowthPct_12_14h'].sem())

    bars3 = ax.bar(x2 - width/2, growth_before_t, width, yerr=growth_before_t_sem,
                   label='Growth (0 h → 12 h)', color='#5B9BD5', alpha=0.8,
                   edgecolor='white', linewidth=0.5, capsize=3, error_kw={'linewidth': 0.8})
    bars4 = ax.bar(x2 + width/2, change_at_div_t, width, yerr=change_at_div_t_sem,
                   label='Change at division (12 h → 14 h)', color='#ED7D31', alpha=0.8,
                   edgecolor='white', linewidth=0.5, capsize=3, error_kw={'linewidth': 0.8})

    ax.set_ylabel('Volume change (%)')
    ax.set_xticks(x2)
    ax.set_xticklabels(tissues, fontsize=9)
    ax.axhline(0, color='black', linestyle='-', alpha=0.2)
    ax.legend(fontsize=8, frameon=True, framealpha=0.9, edgecolor='gray', loc='upper left')
    ax.set_title('By Tissue (mean ± SEM)', fontsize=11)

    for bar in bars3:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1.5, f'{h:.1f}%',
                ha='center', fontsize=7.5, color='gray')
    for bar in bars4:
        h = bar.get_height()
        offset = 1.5 if h >= 0 else -3.5
        ax.text(bar.get_x() + bar.get_width()/2, h + offset, f'{h:.1f}%',
                ha='center', fontsize=7.5, color='gray')

    fig.tight_layout()
    save_fig(fig, '13_growth_phases_comparison')


# ============================================================
# FIGURE 14: Cell volume trajectory through division
# (All cells, all samples on one panel — like old v0 style)
# ============================================================

def fig14_combined_trajectory():
    fig, ax = plt.subplots(figsize=(6, 5))
    fig.suptitle('Cell Volume Trajectory Through Division\n(All Cells)', fontweight='bold', y=1.04)

    stages = ['0 h\n(Before growth)', '12 h\n(Before division)', '14 h\n(After division)']
    x_pos = [0, 1, 2]

    # Individual traces
    for _, row in df.iterrows():
        color = SAMPLE_COLORS[row['Sample']]
        vols = [row['Vol_0h'], row['Vol_12h'], row['Vol_14h']]
        ax.plot(x_pos, vols, '-o', color=color, alpha=0.25, linewidth=0.8, markersize=4)

    # Mean traces per sample
    for sample in SAMPLE_ORDER:
        sub = df[df['Sample'] == sample]
        means = [sub['Vol_0h'].mean(), sub['Vol_12h'].mean(), sub['Vol_14h'].mean()]
        ax.plot(x_pos, means, '-s', color=SAMPLE_COLORS[sample],
                linewidth=2.5, markersize=10, label=sample_map_short[sample],
                markeredgecolor='white', markeredgewidth=1, zorder=5)

    # Division line
    ax.axvline(x=1.5, color='#C0392B', linestyle=':', alpha=0.8, linewidth=1.8)
    ax.text(1.55, ax.get_ylim()[1] * 0.97, 'DIVISION', color='#C0392B',
            fontsize=9, fontweight='bold', va='top')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(stages)
    ax.set_ylabel('Volume (μm³)')
    ax.set_xlim(-0.3, 2.4)
    ax.legend(frameon=True, framealpha=0.9, edgecolor='gray', fontsize=9, loc='upper left')

    fig.tight_layout()
    save_fig(fig, '14_combined_trajectory_with_division')


# ============================================================
# RUN ALL FIGURES
# ============================================================

print("\nGenerating visualizations...")
fig1_locule_across_samples()
fig2_ct_across_samples()
fig3_tissue_within_sample()
fig4_overall_locule_vs_ct()
fig5_growth_trajectories()
fig5b_locule_combined_trajectory()
fig5c_ct_combined_trajectory()
fig6_percent_growth()
fig7_mean_volume_bars()
fig8_growth_heatmap()
fig9_paired_dotplot()
fig10_violin_overall()
fig11_before_vs_after_division_scatter()
fig12_division_volume_change()
fig13_growth_phases()
fig14_combined_trajectory()
print("\nDone! All 16 visualizations saved to visualization/")
