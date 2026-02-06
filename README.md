# Cell Division Volume Analysis / 细胞分裂体积分析

> **Bilingual README — English below, 中文在后**

---

## 🇬🇧 English

### Overview

This project provides a Python-based data analysis and visualization pipeline for studying **cell volume changes before and after cell division**. It processes single-cell tracking data from multiple biological samples, computes growth metrics, and generates publication-quality figures summarizing the findings.

### Scientific Background

During cell division, a mother cell splits into two daughter cells. Understanding how cell volume is conserved (or changes) during this process is fundamental in cell biology. This script tracks individual cells across multiple timepoints, measuring:

- **Volume at an early timepoint** — baseline cell size before growth
- **Volume immediately before division** — cell size after growth phase
- **Combined daughter-cell volume after division** — total volume of both daughter cells

### Data

The input data file `02 07 08_single cell division_volume.csv` contains volume measurements (in μm³) for individual cells tracked across timepoints from three biological samples:

| Sample | Cells Tracked | Timepoints (Early → Before Division → After Division) |
|--------|--------------|-------------------------------------------------------|
| 02     | 8 cells      | T0→T6→T7, T2→T8→T9                                   |
| 07     | 1 cell       | T1→T7→T8                                              |
| 08     | 21 cells     | T0→T6→T7, T1→T7→T8, T2→T8→T9                        |

### Computed Metrics

The script calculates three key percentage-based metrics for each cell:

| Metric | Description |
|--------|-------------|
| **Growth Before Division** | Percentage volume increase from early timepoint to the timepoint just before division |
| **Division Volume Change** | Percentage volume change at the moment of division (before vs. after) |
| **Total Growth** | Overall percentage volume change from the earliest to the post-division timepoint |

### Output Visualizations

The script produces a 4-panel figure (`cell_division_analysis.png`):

1. **Volume Conservation Scatter Plot** — Before vs. after division volume with an identity line (y = x) to assess conservation
2. **Cell Volume Trajectory Plot** — Paired line plot showing each cell's volume across the three stages, with per-sample mean trajectories
3. **Division Volume Change Box Plot** — Distribution of percentage volume change at division, grouped by sample
4. **Growth Phase Comparison Bar Chart** — Mean percentage change for the growth phase vs. the division event, by sample

### Requirements

- Python 3.8+
- Required packages:

```
pandas
matplotlib
seaborn
numpy
```

### Installation & Usage

1. **Clone the repository**

```bash
git clone <repository-url>
cd DataVisualization
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install pandas matplotlib seaborn numpy
```

4. **Run the script**

```bash
python cell_division_analysis.py
```

5. **Output**
   - Console: Summary statistics and detailed per-sample results
   - File: `cell_division_analysis.png` — the 4-panel figure (150 DPI)

### Project Structure

```
DataVisualization/
├── cell_division_analysis.py                  # Main analysis script
├── 02 07 08_single cell division_volume.csv   # Raw data (volume measurements)
├── cell_division_analysis.png                 # Generated figure (after running)
├── .gitignore
└── README.md                                  # This file
```

---

## 🇨🇳 中文

### 概述

本项目提供了一套基于 Python 的数据分析与可视化流程，用于研究**细胞分裂前后的体积变化**。脚本处理来自多个生物样本的单细胞追踪数据，计算生长指标，并生成适用于学术发表的高质量图表。

### 科学背景

在细胞分裂过程中，一个母细胞分裂为两个子细胞。理解细胞体积在此过程中如何守恒（或变化）是细胞生物学的基本问题。本脚本追踪单个细胞在多个时间点的表现，测量以下指标：

- **早期时间点的体积** — 生长前的基线细胞大小
- **分裂前的体积** — 生长阶段后的细胞大小
- **分裂后子细胞的总体积** — 两个子细胞的合计体积

### 数据说明

输入数据文件 `02 07 08_single cell division_volume.csv` 包含三个生物样本中单个细胞在不同时间点的体积测量值（单位：μm³）：

| 样本 | 追踪细胞数 | 时间点（早期 → 分裂前 → 分裂后） |
|------|-----------|-------------------------------|
| 02   | 8 个细胞   | T0→T6→T7, T2→T8→T9           |
| 07   | 1 个细胞   | T1→T7→T8                      |
| 08   | 21 个细胞  | T0→T6→T7, T1→T7→T8, T2→T8→T9 |

### 计算指标

脚本为每个细胞计算三个基于百分比的关键指标：

| 指标 | 描述 |
|------|------|
| **分裂前生长率** | 从早期时间点到分裂前时间点的体积增长百分比 |
| **分裂时体积变化** | 分裂瞬间的体积变化百分比（分裂前 vs. 分裂后） |
| **总生长率** | 从最早时间点到分裂后时间点的整体体积变化百分比 |

### 输出可视化

脚本生成一张四面板图（`cell_division_analysis.png`）：

1. **体积守恒散点图** — 分裂前 vs. 分裂后体积，附带恒等线（y = x）以评估体积守恒情况
2. **细胞体积轨迹图** — 配对折线图展示每个细胞在三个阶段的体积变化，附带各样本的均值轨迹
3. **分裂体积变化箱线图** — 分裂时体积变化百分比的分布情况，按样本分组
4. **生长阶段对比柱状图** — 生长阶段与分裂事件的平均百分比变化对比，按样本分组

### 环境要求

- Python 3.8+
- 所需依赖包：

```
pandas
matplotlib
seaborn
numpy
```

### 安装与运行

1. **克隆仓库**

```bash
git clone <仓库地址>
cd DataVisualization
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install pandas matplotlib seaborn numpy
```

4. **运行脚本**

```bash
python cell_division_analysis.py
```

5. **输出结果**
   - 控制台：汇总统计信息和各样本的详细分析结果
   - 文件：`cell_division_analysis.png` — 四面板图表（150 DPI）

### 项目结构

```
DataVisualization/
├── cell_division_analysis.py                  # 主分析脚本
├── 02 07 08_single cell division_volume.csv   # 原始数据（体积测量值）
├── cell_division_analysis.png                 # 生成的图表（运行后产生）
├── .gitignore
└── README.md                                  # 本文件
```

---

## License / 许可证

This project is provided for educational and research purposes.

本项目仅供教育和研究用途。
