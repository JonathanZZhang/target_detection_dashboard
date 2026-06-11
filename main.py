"""FastAPI 后端 —— 只做数据聚合，返回纯数组/字典。前端负责 ECharts option 构造。"""

from pathlib import Path
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ECharts 可行性验证 API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/public", StaticFiles(directory="frontend", html=True), name="frontend")

DATA_PATH = Path(__file__).parent / "data" / "sample_data.csv"


def _load():
    return pd.read_csv(DATA_PATH)


def _filter(df, targets, time_start, time_end):
    if targets:
        df = df[df["target"].isin(targets)]
    if time_start:
        df = df[df["time_stamp"] >= time_start]
    if time_end:
        df = df[df["time_stamp"] <= time_end]
    return df


def _bin_time(df, bucket):
    df["time_bin"] = (
        pd.to_datetime(df["time_stamp"], format="%H:%M:%S")
        .dt.floor(bucket)
        .dt.strftime("%H:%M:%S")
    )
    return df


@app.get("/api/filters")
def get_filters():
    df = _load()
    return {
        "targets": sorted(df["target"].unique().tolist()),
        "time_min": df["time_stamp"].min(),
        "time_max": df["time_stamp"].max(),
    }


@app.get("/api/heatmap")
def api_heatmap(
    targets: list[str] = Query(None),
    time_start: str | None = Query(None),
    time_end: str | None = Query(None),
    time_bucket: str = Query("1s"),
):
    df = (_bin_time(_filter(_load(), targets, time_start, time_end), time_bucket)
          .groupby("time_bin")
          .size()
          .sort_index())
    return JSONResponse({
        "times": df.index.tolist(),
        "counts": df.values.tolist(),
    })


@app.get("/api/scatter")
def api_scatter(
    targets: list[str] = Query(None),
    time_start: str | None = Query(None),
    time_end: str | None = Query(None),
    time_bucket: str = Query("1s"),
):
    df = (_bin_time(_filter(_load(), targets, time_start, time_end), time_bucket)
          .groupby("time_bin")
          .size()
          .sort_index())
    return JSONResponse({
        "times": df.index.tolist(),
        "counts": df.values.tolist(),
    })


@app.get("/api/scatter_density")
def api_scatter_density(
    targets: list[str] = Query(None),
    time_start: str | None = Query(None),
    time_end: str | None = Query(None),
    time_bucket: str = Query("1s"),
):
    df = (
        _bin_time(_filter(_load(), targets, time_start, time_end), time_bucket)
        .groupby("time_bin")
        ["target"]
        .agg(total="count", unique="nunique")
        .reset_index()
    )
    points = [[int(r.total), int(r.unique), int(r.total), r.time_bin] for r in df.itertuples()]
    return JSONResponse({"points": points})


@app.get("/api/bbox_heatmap")
def api_bbox_heatmap(
    targets: list[str] = Query(None),
    time_start: str | None = Query(None),
    time_end: str | None = Query(None),
):
    df = _filter(_load(), targets, time_start, time_end)
    rects = [[int(r.x1), int(r.y1), int(r.x2), int(r.y2), r.target, r.time_stamp] for r in df.itertuples()]
    return JSONResponse({"rects": rects})
