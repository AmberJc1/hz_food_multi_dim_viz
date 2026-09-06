# -*- coding: utf-8 -*-
"""杭州餐饮商家地图 + 高德 JS 地图 + FastAPI 路径规划后端"""
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "hangzhou_clean.csv"
INDEX_FILE = BASE_DIR / "static" / "index.html"
AMAP_KEY = os.getenv("AMAP_KEY", "").strip()                 # Web 服务 Key：后端使用
AMAP_JS_KEY = os.getenv("AMAP_JS_KEY", "").strip()         # JS API Key：前端使用
AMAP_SECURITY_CODE = os.getenv("AMAP_SECURITY_CODE", "").strip()

app = FastAPI(title="杭州餐饮商家地图", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def clean(v):
    if v is None or pd.isna(v):
        return None
    s = str(v).strip()
    return s if s and s.lower() not in {"nan", "none", "[]"} else None


def num(v):
    if v is None or pd.isna(v):
        return None
    try:
        return float(v)
    except Exception:
        return None


def load_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"找不到数据文件：{CSV_FILE}")
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if "cat_level1" in df.columns:
        mask = df["cat_level1"].astype(str).str.strip() == "餐饮服务"
        if mask.any():
            df = df[mask].copy()
    if "location" not in df.columns:
        raise ValueError("CSV 缺少 location 字段")
    loc = df["location"].astype(str).str.strip().str.split(",", expand=True)
    df["lng"] = pd.to_numeric(loc[0], errors="coerce")
    df["lat"] = pd.to_numeric(loc[1], errors="coerce")
    return df.dropna(subset=["lng", "lat"]).reset_index(drop=True)


try:
    DF = load_data()
    LOAD_ERROR = None
except Exception as e:
    DF = pd.DataFrame()
    LOAD_ERROR = str(e)


def shop_dict(row, idx):
    return {
        "id": idx,
        "name": clean(row.get("name")),
        "lng": float(row["lng"]), "lat": float(row["lat"]),
        "cost": num(row.get("cost")), "rating": num(row.get("rating")),
        "category": clean(row.get("keytag")) or clean(row.get("cat_level2")),
        "district": clean(row.get("adname")), "address": clean(row.get("address")),
        "tel": clean(row.get("tel")), "cluster": num(row.get("cluster")),
        "cost_level": clean(row.get("cost_level")), "score_level": clean(row.get("score_level")),
    }


class RouteRequest(BaseModel):
    origin_lng: float = Field(...)
    origin_lat: float = Field(...)
    dest_lng: float = Field(...)
    dest_lat: float = Field(...)
    mode: str = Field("driving", pattern="^(driving|walking|bicycling)$")


@app.get("/")
def index():
    return FileResponse(INDEX_FILE)


@app.get("/api/config")
def config():
    if not AMAP_JS_KEY:
        raise HTTPException(status_code=500, detail="未配置 AMAP_JS_KEY")
    return {"js_key": AMAP_JS_KEY, "security_code": AMAP_SECURITY_CODE, "shops": len(DF)}


@app.get("/api/health")
def health():
    return {"status": "ok", "shops": len(DF), "web_service_key_configured": bool(AMAP_KEY),
            "js_key_configured": bool(AMAP_JS_KEY), "load_error": LOAD_ERROR}


@app.get("/api/shops")
def shops():
    if LOAD_ERROR:
        raise HTTPException(status_code=500, detail=LOAD_ERROR)
    return [shop_dict(row, i) for i, row in DF.iterrows()]


@app.post("/api/route")
def route(req: RouteRequest):
    if not AMAP_KEY:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY（高德 Web 服务 Key）")
    endpoints = {
        "driving": "https://restapi.amap.com/v5/direction/driving",
        "walking": "https://restapi.amap.com/v5/direction/walking",
        "bicycling": "https://restapi.amap.com/v5/direction/bicycling",
    }
    params = {
        "key": AMAP_KEY,
        "origin": f"{req.origin_lng:.6f},{req.origin_lat:.6f}",
        "destination": f"{req.dest_lng:.6f},{req.dest_lat:.6f}",
        "show_fields": "cost,polyline",
    }
    if req.mode == "driving":
        params["strategy"] = "32"
    try:
        r = requests.get(endpoints[req.mode], params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"高德接口请求失败：{e}")
    if str(data.get("status")) != "1":
        raise HTTPException(status_code=400, detail=f"高德路径规划失败：{data.get('info', '未知错误')}")
    paths = (data.get("route") or {}).get("paths") or []
    if not paths:
        raise HTTPException(status_code=404, detail="没有找到可用路线")
    path = paths[0]
    points = []
    for p in str(path.get("polyline", "")).split(";"):
        if "," not in p: continue
        try:
            lng, lat = map(float, p.split(",")[:2])
            points.append([lng, lat])
        except ValueError:
            pass
    duration = float((path.get("cost") or {}).get("duration", 0) or 0)
    distance = float(path.get("distance", 0) or 0)
    return {"status": 1, "mode": req.mode, "distance_m": distance, "duration_s": duration, "points": points}
