"""生成样本数据：模拟广告检测 bbox 数据，输出 CSV。

坐标系：原点 = 画布左下角 (0, 0)，X 向右 [0, 1920]，Y 向上 [0, 1080]。
bbox 字段: x1(左), y1(下), x2(右), y2(上)
"""

import random
import csv
from pathlib import Path

# ── 参数 ──────────────────────────────────────────
NUM_POINTS = 36000
CANVAS_W, CANVAS_H = 1920, 1080
TIME_START_H, TIME_START_M, TIME_START_S = 0, 0, 0
DURATION_MINUTES = 60
TARGETS = ["Target_A", "Target_B", "Target_C", "Target_D", "Target_E", "Target_F", "Target_G"]
TARGET_WEIGHTS = [0.30, 0.22, 0.18, 0.12, 0.08, 0.06, 0.04]

# 热点区域 (x_min, y_min, x_max, y_max, ratio) — 左下角原点
HOT_ZONES = [
    (1400, 700, 1800, 1000, 0.40),   # 右上区域，高频
    (600, 400, 900, 700, 0.30),       # 中间区域，中频
    (50, 50, 350, 300, 0.15),         # 左下区域，低频
]
SCATTER_RATIO = 0.15
BBOX_MIN, BBOX_MAX = 30, 200  # bbox 边长范围 (px)
# ──────────────────────────────────────────────────

OUTPUT = Path(__file__).parent / "sample_data.csv"


def make_bbox(x, y, rand):
    """以 (x,y) 为左下角生成轴对齐矩形，返回 (x1, y1, x2, y2) 标量。"""
    w = rand.randint(BBOX_MIN, BBOX_MAX)
    h = rand.randint(BBOX_MIN, BBOX_MAX)
    w = min(w, CANVAS_W - x)
    h = min(h, CANVAS_H - y)
    return x, y, x + w, y + h


def gen_timestamp(seconds_offset):
    total = TIME_START_H * 3600 + TIME_START_M * 60 + TIME_START_S + seconds_offset
    h = (total // 3600) % 24
    m = (total // 60) % 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    rand = random.Random(42)
    rows = []

    zone_ratios = [z[4] for z in HOT_ZONES] + [SCATTER_RATIO]
    total_zone_weight = sum(zone_ratios)
    zone_counts = [int(NUM_POINTS * r / total_zone_weight) for r in zone_ratios]
    zone_counts[-1] += NUM_POINTS - sum(zone_counts)
    zone_counts[-1] = max(0, zone_counts[-1])

    target_cum_weights = []
    acc = 0
    for w in TARGET_WEIGHTS:
        acc += w
        target_cum_weights.append(acc)

    zones_params = []
    for x_min, y_min, x_max, y_max, _ in HOT_ZONES:
        zones_params.append(("zone", x_min, y_min, x_max, y_max))
    zones_params.append(("scatter", 0, 0, CANVAS_W, CANVAS_H))

    # zip counts with params
    all_params = list(zip(zones_params, zone_counts))

    for (zone_type, x_min, y_min, x_max, y_max), count in all_params:
        for _ in range(count):
            sec = rand.randint(0, DURATION_MINUTES * 60 - 1)
            ts = gen_timestamp(sec)

            r = rand.random()
            target_idx = next(i for i, c in enumerate(target_cum_weights) if r <= c)
            target = TARGETS[target_idx]

            x = rand.randint(x_min, max(x_min, x_max - BBOX_MIN))
            y = rand.randint(y_min, max(y_min, y_max - BBOX_MIN))

            x1, y1, x2, y2 = make_bbox(x, y, rand)
            rows.append({
                "time_stamp": ts,
                "target": target,
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
            })

    rows.sort(key=lambda r: r["time_stamp"])

    fieldnames = ["time_stamp", "target", "x1", "y1", "x2", "y2"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done: {len(rows)} rows -> {OUTPUT}")


if __name__ == "__main__":
    main()
