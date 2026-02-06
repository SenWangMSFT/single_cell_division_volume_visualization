"""
Cell Division Volume Analysis
Analyzes cell volume changes before and after cell division.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.facecolor'] = 'white'

# Data structure: each record contains before-division timepoints and after-division volume
# Format: (Sample, CellID, T_early, T_late_before, T_after, Vol_early, Vol_late_before, Vol_after)

division_data = [
    # Sample 02 - Group 1 (T0, T6 before; T7 after)
    ('02', 133, 'T0', 'T6', 'T7', 204.125, 292.149, 298.939),
    ('02', 685, 'T0', 'T6', 'T7', 249.743, 302.508, 316.800),
    ('02', 804, 'T0', 'T6', 'T7', 150.404, 228.660, 236.844),
    ('02', 834, 'T0', 'T6', 'T7', 90.3997, 114.711, 120.213),
    ('02', 906, 'T0', 'T6', 'T7', 156.344, 236.889, 254.419),
    
    # Sample 02 - Group 2 (T2, T8 before; T9 after)
    ('02', 30, 'T2', 'T8', 'T9', 250.472, 376.866, 370.492),
    ('02', 397, 'T2', 'T8', 'T9', 251.927, 348.183, 338.907),
    ('02', 560, 'T2', 'T8', 'T9', 241.223, 278.363, 268.710),
    
    # Sample 07 (T1, T7 before; T8 after)
    ('07', 469, 'T1', 'T7', 'T8', 149.429, 161.975, 164.710),
    
    # Sample 08 - Group 1 (T0, T6 before; T7 after)
    ('08', 116, 'T0', 'T6', 'T7', 259.878, 436.156, 426.096),
    ('08', 122, 'T0', 'T6', 'T7', 287.476, 494.405, 475.833),
    ('08', 205, 'T0', 'T6', 'T7', 247.637, 402.548, 386.412),
    ('08', 296, 'T0', 'T6', 'T7', 298.170, 488.539, 481.321),
    ('08', 361, 'T0', 'T6', 'T7', 137.681, 212.203, 193.203),
    ('08', 378, 'T0', 'T6', 'T7', 237.936, 361.965, 341.727),
    ('08', 441, 'T0', 'T6', 'T7', 126.829, 191.700, 186.570),
    ('08', 956, 'T0', 'T6', 'T7', 192.350, 292.473, 281.895),
    ('08', 1070, 'T0', 'T6', 'T7', 137.411, 210.628, 204.949),
    
    # Sample 08 - Group 2 (T1, T7 before; T8 after)
    ('08', 67, 'T1', 'T7', 'T8', 315.646, 355.999, 350.377),
    ('08', 272, 'T1', 'T7', 'T8', 349.553, 415.675, 414.493),
    ('08', 544, 'T1', 'T7', 'T8', 238.440, 251.436, 243.213),
    ('08', 608, 'T1', 'T7', 'T8', 379.682, 428.555, 403.001),
    ('08', 745, 'T1', 'T7', 'T8', 293.986, 336.325, 321.133),
    ('08', 1102, 'T1', 'T7', 'T8', 228.794, 264.711, 264.507),
    
    # Sample 08 - Group 3 (T2, T8 before; T9 after)
    ('08', 110, 'T2', 'T8', 'T9', 412.022, 535.442, 560.946),
    ('08', 408, 'T2', 'T8', 'T9', 331.541, 380.966, 365.163),
    ('08', 662, 'T2', 'T8', 'T9', 362.667, 414.365, 390.654),
    ('08', 942, 'T2', 'T8', 'T9', 215.300, 227.087, 219.918),
    ('08', 1180, 'T2', 'T8', 'T9', 261.091, 305.081, 291.848),
    ('08', 1228, 'T2', 'T8', 'T9', 259.209, 289.222, 290.703),
]

# Create DataFrame
df = pd.DataFrame(division_data, columns=[
    'Sample', 'CellID', 'T_early', 'T_late_before', 'T_after',
    'Vol_early', 'Vol_before_division', 'Vol_after_division'
])

# Calculate metrics
df['Growth_before_division'] = ((df['Vol_before_division'] - df['Vol_early']) / df['Vol_early']) * 100
df['Division_volume_change'] = ((df['Vol_after_division'] - df['Vol_before_division']) / df['Vol_before_division']) * 100
df['Total_growth'] = ((df['Vol_after_division'] - df['Vol_early']) / df['Vol_early']) * 100

# Print summary
print("=" * 60)
print("CELL DIVISION VOLUME ANALYSIS")
print("=" * 60)
print(f"\nTotal cells analyzed: {len(df)}")
print(f"  Sample 02: {len(df[df['Sample'] == '02'])} cells")
print(f"  Sample 07: {len(df[df['Sample'] == '07'])} cells")
print(f"  Sample 08: {len(df[df['Sample'] == '08'])} cells")

print("\n--- Volume Change Summary ---")
print(f"Mean growth before division: {df['Growth_before_division'].mean():.1f}%")
print(f"Mean volume change at division: {df['Division_volume_change'].mean():.1f}%")
print(f"Mean total growth (early -> after): {df['Total_growth'].mean():.1f}%")

# ============================================
# VISUALIZATION
# ============================================

fig = plt.figure(figsize=(16, 12))

# Color palette for samples
sample_colors = {'02': '#E74C3C', '07': '#3498DB', '08': '#2ECC71'}

# ----------------------------------------
# Plot 1: Before vs After Division Volume (Scatter with identity line)
# ----------------------------------------
ax1 = fig.add_subplot(2, 2, 1)

for sample in ['02', '07', '08']:
    subset = df[df['Sample'] == sample]
    ax1.scatter(subset['Vol_before_division'], subset['Vol_after_division'], 
                c=sample_colors[sample], label=f'Sample {sample}', 
                s=80, alpha=0.7, edgecolors='white', linewidth=1)

# Add identity line (y = x)
max_vol = max(df['Vol_before_division'].max(), df['Vol_after_division'].max()) * 1.1
ax1.plot([0, max_vol], [0, max_vol], 'k--', alpha=0.5, label='No change line (y=x)')

ax1.set_xlabel('Volume Before Division (um3)', fontsize=11)
ax1.set_ylabel('Volume After Division (um3)\n(Combined daughter cells)', fontsize=11)
ax1.set_title('Volume Conservation at Cell Division', fontsize=13, fontweight='bold')
ax1.legend(loc='lower right')
ax1.set_xlim(0, max_vol)
ax1.set_ylim(0, max_vol)

# Add annotation
ax1.text(0.05, 0.95, 'Points above line = Volume gained\nPoints below line = Volume lost',
         transform=ax1.transAxes, fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# ----------------------------------------
# Plot 2: Paired line plot showing cell trajectory
# ----------------------------------------
ax2 = fig.add_subplot(2, 2, 2)

stages = ['Early\n(Before growth)', 'Late\n(Before division)', 'After\nDivision']
x_positions = [0, 1, 2]

for idx, row in df.iterrows():
    volumes = [row['Vol_early'], row['Vol_before_division'], row['Vol_after_division']]
    ax2.plot(x_positions, volumes, '-o', color=sample_colors[row['Sample']], 
             alpha=0.4, linewidth=1.5, markersize=6)

# Add mean lines for each sample
for sample in ['02', '07', '08']:  # Include all samples
    subset = df[df['Sample'] == sample]
    means = [subset['Vol_early'].mean(), 
             subset['Vol_before_division'].mean(), 
             subset['Vol_after_division'].mean()]
    ax2.plot(x_positions, means, '-s', color=sample_colors[sample], 
             linewidth=3, markersize=12, label=f'Sample {sample} (mean)',
             markeredgecolor='black', markeredgewidth=2)

ax2.set_xticks(x_positions)
ax2.set_xticklabels(stages)
ax2.set_ylabel('Cell Volume (um3)', fontsize=11)
ax2.set_title('Cell Volume Trajectory Through Division', fontsize=13, fontweight='bold')
ax2.legend(loc='upper left')
ax2.set_xlim(-0.3, 2.3)

# Add division marker
ax2.axvline(x=1.5, color='red', linestyle=':', alpha=0.7, linewidth=2)
ax2.text(1.55, ax2.get_ylim()[1] * 0.95, 'DIVISION', color='red', fontsize=10, fontweight='bold')

# ----------------------------------------
# Plot 3: Volume change percentage at division
# ----------------------------------------
ax3 = fig.add_subplot(2, 2, 3)

# Box plot of division volume change by sample
box_data = [df[df['Sample'] == '02']['Division_volume_change'].values,
            df[df['Sample'] == '07']['Division_volume_change'].values,
            df[df['Sample'] == '08']['Division_volume_change'].values]

bp = ax3.boxplot(box_data, labels=['Sample 02', 'Sample 07', 'Sample 08'], patch_artist=True)

colors_box = ['#E74C3C', '#3498DB', '#2ECC71']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

# Add individual points
for i, sample in enumerate(['02', '07', '08']):
    subset = df[df['Sample'] == sample]
    x = np.random.normal(i + 1, 0.04, size=len(subset))
    ax3.scatter(x, subset['Division_volume_change'], c=sample_colors[sample], 
                alpha=0.8, s=50, edgecolors='black', linewidth=0.5, zorder=3)

ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1.5)
ax3.set_ylabel('Volume Change at Division (%)', fontsize=11)
ax3.set_title('Volume Change During Cell Division\n(Positive = Volume gained, Negative = Volume lost)', 
              fontsize=13, fontweight='bold')

# Add stats annotation
for i, sample in enumerate(['02', '07', '08']):
    subset = df[df['Sample'] == sample]
    mean_val = subset['Division_volume_change'].mean()
    ax3.text(i + 1, ax3.get_ylim()[1] * 0.9, f'Mean: {mean_val:.1f}%', 
             ha='center', fontsize=10, fontweight='bold')

# ----------------------------------------
# Plot 4: Growth phases comparison
# ----------------------------------------
ax4 = fig.add_subplot(2, 2, 4)

# Prepare data for grouped bar chart
samples = ['02', '07', '08']
growth_before = [df[df['Sample'] == s]['Growth_before_division'].mean() for s in samples]
growth_at_division = [df[df['Sample'] == s]['Division_volume_change'].mean() for s in samples]

x = np.arange(len(samples))
width = 0.35

bars1 = ax4.bar(x - width/2, growth_before, width, label='Growth Before Division', 
                color='#3498DB', alpha=0.8, edgecolor='black')
bars2 = ax4.bar(x + width/2, growth_at_division, width, label='Change at Division', 
                color='#E74C3C', alpha=0.8, edgecolor='black')

ax4.set_ylabel('Volume Change (%)', fontsize=11)
ax4.set_title('Comparison of Growth Phases (Mean % Change)', fontsize=13, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels([f'Sample {s}' for s in samples])
ax4.legend(loc='upper right')
ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax4.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)

for bar in bars2:
    height = bar.get_height()
    ax4.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3 if height >= 0 else -12), textcoords="offset points", 
                 ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('cell_division_analysis.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.show()

print("\n" + "=" * 60)
print("Saved: cell_division_analysis.png")
print("=" * 60)

# ============================================
# Additional: Detailed summary table
# ============================================
print("\n" + "=" * 60)
print("DETAILED RESULTS BY SAMPLE")
print("=" * 60)

for sample in ['02', '07', '08']:
    subset = df[df['Sample'] == sample]
    print(f"\n--- Sample {sample} (n={len(subset)}) ---")
    print(f"  Volume before division: {subset['Vol_before_division'].mean():.1f} +/- {subset['Vol_before_division'].std():.1f} um3")
    print(f"  Volume after division:  {subset['Vol_after_division'].mean():.1f} +/- {subset['Vol_after_division'].std():.1f} um3")
    print(f"  Growth before division: {subset['Growth_before_division'].mean():.1f} +/- {subset['Growth_before_division'].std():.1f}%")
    print(f"  Change at division:     {subset['Division_volume_change'].mean():.1f} +/- {subset['Division_volume_change'].std():.1f}%")
