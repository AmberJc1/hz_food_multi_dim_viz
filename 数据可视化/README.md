# 杭州餐饮商家地图（高德地图 + FastAPI）

## 启动
在本目录打开 PowerShell：

```powershell
py -m pip install -r requirements.txt
$env:AMAP_KEY="89fea970098d0fa47cbcf93df7705330"
$env:AMAP_JS_KEY="be30e611ac8c7712edf7c28eb0b04d88"
$env:AMAP_SECURITY_CODE="fba72a8d66a2292e60d7cf8b8afc65b4"
py -m uvicorn main:app --host 127.0.0.1 --port 8000
```

然后打开：

`http://127.0.0.1:8000`

注意：高德 JS API 需要联网加载。浏览器首次定位时需要允许网页获取位置权限。
