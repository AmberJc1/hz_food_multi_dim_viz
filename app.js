const DATA_URLS = {
  merchants: "./数据分析/data/hangzhou_clean.csv",
  ranking: "./数据分析/output/overall_ranking.csv",
  clusters: "./数据分析/output/clustering_result.csv",
  profiles: "./数据分析/output/cluster_profile.csv",
  evaluation: "./数据分析/output/final_evaluation_summary.csv",
  stability: "./数据分析/output/ranking_stability_top10.csv"
};
const AMAP_JS_KEY = "be30e611ac8c7712edf7c28eb0b04d88";
const AMAP_SECURITY_CODE = "fba72a8d66a2292e60d7cf8b8afc65b4";
const DISTRICTS = ["全部行政区", "上城区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "钱塘区", "临平区", "富阳区", "临安区", "淳安县", "桐庐县", "建德市"];
const CUISINES = ["全部菜系", "中餐厅", "外国餐厅", "快餐厅", "咖啡厅", "冷饮店", "休闲餐饮场所"];
const ROUTES = {
  overview: ["01", "总览大盘", "全城餐饮脉搏"],
  ranking: ["02", "商家排行", "筛选与决策"],
  map: ["03", "地图洞察", "餐厅评分分布"],
  ai: ["04", "AI 智能", "预测与推荐"]
};

const app = document.querySelector("#app");
let amapLoader = null;
let activeMap = null;
let activeInfoWindow = null;
let activeRouteService = null;
let startMarker = null;
let destinationMarker = null;
let navigationWatchId = null;
const mapNav = {
  origin: null,
  destination: null,
  pickStart: false,
  navigating: false,
  lastRouteOrigin: null,
  lastRerouteAt: 0,
  rerouteBusy: false
};
const state = {
  route: "overview",
  merchants: [],
  filtered: [],
  filters: { district: "全部行政区", cuisine: "全部菜系", cost: "all", status: "all", chain: false, delivery: false, parking: false },
  ranking: "overall",
  favorites: new Set(JSON.parse(localStorage.getItem("hz-favorites") || "[]")),
  compare: new Set(),
  selectedMerchant: null,
  compareOpen: false,
  showFavorites: false,
  aiTab: "predict",
  aiBusy: false,
  aiNotice: "AI 接口待配置 · 本地模式可用",
  clusterProfiles: [],
  algorithm: { bestK: 3, silhouette: .5361, stabilityMin: 80 },
  recommendations: [],
  recommendationMeta: null,
  history: JSON.parse(localStorage.getItem("hz-prediction-history") || "[]"),
  prediction: null
};

function parseCSV(text) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === '"') {
      if (quoted && text[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (ch === "," && !quoted) { row.push(cell); cell = ""; }
    else if ((ch === "\n" || ch === "\r") && !quoted) {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); cell = "";
      if (row.some(Boolean)) rows.push(row);
      row = [];
    } else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const headers = rows.shift().map(h => h.replace(/^\uFEFF/, ""));
  return rows.map(values => Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""])));
}

function hashNumber(value) {
  let h = 2166136261;
  for (const ch of String(value)) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
  return Math.abs(h >>> 0);
}

function classifyCuisine(name, rawType) {
  // Only infer from the merchant name when the wording is explicit. Tag text often
  // describes ingredients (for example "澳洲牛肉") and is not a reliable cuisine.
  const source = name;
  const namedRules = [
    ["杭帮菜", /杭帮|杭州菜|杭儿风|江南味|楼外楼|外婆家/],
    ["浙江菜", /浙江菜|浙菜|浙宴/],
    ["衢州菜", /衢州|开化|遂昌|衢味/],
    ["桐庐菜", /桐庐/],
    ["绍兴菜", /绍兴/],
    ["宁波菜", /宁波/],
    ["徽菜", /徽菜|安徽|徽地|徽柴/],
    ["湘菜", /湘菜|湖南/],
    ["川菜", /川菜|四川/],
    ["重庆火锅", /重庆.*火锅|老火锅|重庆.*串串/],
    ["潮汕菜", /潮汕|潮州/],
    ["粤菜", /粤菜|广东菜|广式/],
    ["东北菜", /东北菜|东北烧烤|铁锅炖/],
    ["西北菜", /西北菜|新疆菜|新疆.*餐厅/],
    ["陕西菜", /陕西|陕味|秦菜/],
    ["山东菜", /山东菜|鲁菜|单县/],
    ["北京菜", /北京菜|京菜/],
    ["内蒙古菜", /内蒙|蒙古.*(?:菜|羊|餐)/],
    ["闽菜", /福建菜|闽菜/],
    ["贵州菜", /贵州|黔菜/],
    ["云南菜", /云南菜|滇菜/],
    ["泰国菜", /泰式|泰国|Thai/i],
    ["西班牙菜", /西班牙|Spanish|BROWNSTONE/i],
    ["澳洲菜", /澳洲|澳大利亚|Aussie/i],
    ["法国菜", /法式|法国|法餐|南法/i],
    ["意大利菜", /意式|意大利|Pizzeria|披萨|比萨/i],
    ["日本料理", /日本料理|日料|日式|寿司|寿喜|烧鸟|居酒屋|omakase|刺身|鮨/i],
    ["韩国料理", /韩国料理|韩式|韩餐|韩国/i],
    ["美式餐厅", /美式|美国|Shake Shack|BlueFrog|蓝蛙/i],
    ["印度菜", /印度菜|印度餐厅|Indian/i],
    ["东南亚菜", /越南菜|越式|新加坡菜|南洋|马来西亚|东南亚/i],
    ["潮汕牛肉火锅", /潮汕.*牛肉.*火锅/],
    ["北京铜锅涮肉", /铜锅涮肉|老北京.*火锅/],
    ["串串香", /串串香|串串火锅/],
    ["烤肉", /烤肉|烧肉|烤(?:牛|羊|猪)肉/],
    ["烧烤", /烧烤|烤串/],
    ["海鲜酒楼", /海鲜|海产/],
    ["火锅店", /火锅|涮锅|打边炉/]
  ];
  const inferred = namedRules.find(([, pattern]) => pattern.test(source));
  if (inferred) return inferred[0];

  const details = rawType.split("|").map(part => part.split(";").map(x => x.trim())).filter(parts => parts.length >= 3).map(parts => parts[2]);
  const detail = details.find(value => !["餐饮相关", "餐饮服务场所", "外国餐厅", "中餐厅"].includes(value)) || details[0] || "餐饮相关";
  const normalized = {
    "浙江菜": "浙江菜", "湖南菜(湘菜)": "湘菜", "四川菜(川菜)": "川菜", "广东菜(粤菜)": "粤菜",
    "安徽菜(徽菜)": "徽菜", "东北菜": "东北菜", "江苏菜": "苏菜", "清真菜馆": "清真菜",
    "意式菜品餐厅": "意大利菜", "法式菜品餐厅": "法国菜", "韩国料理": "韩国料理", "美式风味": "美式餐厅",
    "日本料理": "日本料理", "西餐厅(综合风味)": "综合西餐", "牛扒店(扒房)": "牛排西餐",
    "外国餐厅": "其他外国餐厅", "中餐厅": "综合中餐", "特色/地方风味餐厅": "地方特色菜", "餐饮相关": "其他餐饮",
    "服装鞋帽皮具店": "其他餐饮", "品牌服装店": "其他餐饮", "购物相关场所": "其他餐饮",
    "村庄级地名": "其他餐饮", "体育休闲服务场所": "其他餐饮", "生活服务场所": "其他餐饮",
    "住宅小区": "其他餐饮", "商务住宅相关": "其他餐饮", "公司": "其他餐饮", "宾馆酒店": "酒店餐厅"
  };
  return normalized[detail] || detail;
}

const analysisKey = row => [row.name, row.adname, row.type].join("\u001f");
const PROFILE_LABELS = { "平价高性价比型":"平价优选", "大众品质型":"日常品质", "高消费高品质型":"品质体验" };
const friendlyProfile = name => PROFILE_LABELS[name] || name || "日常品质";

function enrich(row, index, analysis = {}) {
  const seed = hashNumber(row.id || index);
  const [lng, lat] = (row.location || "120.16,30.25").split(",").map(Number);
  const rating = Number(row.rating) || 0;
  const cost = Number(row.cost) || 0;
  const tags = (row.atag || "").split(",").map(x => x.trim()).filter(Boolean);
  const name = row.name || `杭州商家 ${index + 1}`;
  const cuisine = classifyCuisine(name, row.type || "");
  const chainWords = /店\)|店）|杭州.*店|星巴克|肯德基|麦当劳|必胜客|瑞幸|海底捞|喜茶|奈雪/;
  const valueRatio = Number(analysis.ranking?.["性价比"]) || rating / Math.log1p(cost || 1);
  const ratingIndex = Number(analysis.ranking?.["评分标准化"]) || 0;
  const costFriendliness = Number(analysis.ranking?.["消费友好度"]) || 0;
  const valueIndex = Number(analysis.ranking?.["性价比标准化"]) || 0;
  const overallScore = Number(analysis.ranking?.["综合得分"]) || 0;
  return {
    id: row.id || `merchant-${index}`,
    name,
    address: row.address || "杭州市",
    district: row.adname || "杭州市",
    type: row.cat_level2 || row.type?.split(";")[1] || "餐饮相关场所",
    subtype: row.type?.split(";").at(-1) || row.cat_level2 || "餐饮服务",
    cuisine,
    tags,
    rating,
    cost,
    lng: Number.isFinite(lng) ? lng : 120.16,
    lat: Number.isFinite(lat) ? lat : 30.25,
    tel: row.tel || "暂无电话",
    status: seed % 13 === 0 ? "休息中" : "营业中",
    chain: chainWords.test(name) || seed % 7 === 0,
    delivery: seed % 5 !== 0,
    parking: seed % 3 === 0,
    valueRatio,
    ratingIndex,
    costFriendliness,
    valueIndex,
    overallScore,
    overallRank: Number(analysis.ranking?.["综合排名"]) || index + 1,
    profile: friendlyProfile(analysis.cluster?.["餐厅类型"]),
    profileRaw: analysis.cluster?.["餐厅类型"] || "大众品质型",
    cluster: Number(analysis.cluster?.cluster ?? 1)
  };
}

const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
const fmt = n => new Intl.NumberFormat("zh-CN").format(Math.round(n));
const money = n => n ? `¥${Math.round(n)}` : "暂无";
const esc = value => String(value ?? "").replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[ch]));
const pct = (n, total) => total ? `${(n / total * 100).toFixed(1)}%` : "0%";

async function loadData() {
  try {
    const entries = await Promise.all(Object.entries(DATA_URLS).map(async ([key, url]) => {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`${key} 数据文件读取失败`);
      return [key, parseCSV(await response.text())];
    }));
    const data = Object.fromEntries(entries);
    const ranking = new Map(data.ranking.map(row => [analysisKey(row), row]));
    const clusters = new Map(data.clusters.map(row => [analysisKey(row), row]));
    state.merchants = data.merchants.filter(r => r.valid_for_model !== "False").map((row, index) => enrich(row, index, { ranking: ranking.get(analysisKey(row)), cluster: clusters.get(analysisKey(row)) }));
    state.clusterProfiles = data.profiles.map(row => ({ id:Number(row.cluster), name:friendlyProfile(row["餐厅类型"]), rawName:row["餐厅类型"], count:Number(row["餐厅数量"]), rating:Number(row["平均评分"]), cost:Number(row["平均人均消费"]), value:Number(row["平均性价比"]), share:Number(row["餐厅占比"]) })).sort((a,b)=>b.share-a.share);
    const evaluation = Object.fromEntries(data.evaluation.map(row => [row["评价项目"], row["评价结果"]]));
    const stability = data.stability.slice(1).map(row => Number(row["Top10重合率"])).filter(Number.isFinite);
    state.algorithm = { bestK:Number(evaluation["最佳聚类K值"]) || 3, silhouette:Number(evaluation["最佳轮廓系数"]) || .5361, stabilityMin:stability.length?Math.min(...stability):80 };
    if (!state.merchants.length) throw new Error("数据为空");
  } catch (error) {
    app.innerHTML = `<main class="boot-screen"><div class="boot-mark">DATA<br>ERR</div><p>${esc(error.message)}。请使用 npm run dev 启动。</p></main>`;
    return;
  }
  routeFromHash();
}

function routeFromHash() {
  const route = location.hash.replace("#/", "").split("?")[0];
  state.route = ROUTES[route] ? route : "overview";
  render();
}

function persist() {
  localStorage.setItem("hz-favorites", JSON.stringify([...state.favorites]));
  localStorage.setItem("hz-prediction-history", JSON.stringify(state.history.slice(0, 20)));
}

function shell(content) {
  const current = ROUTES[state.route];
  return `
    <div class="app-shell">
      <aside class="sidebar" aria-label="主导航">
        <a class="brand" href="#/overview" aria-label="杭州味觉图谱首页">
          <span class="brand-mark">HZ<br>FOOD</span><span><strong>杭州味觉图谱</strong><small>URBAN FOOD INDEX</small></span>
        </a>
        <span class="nav-kicker">Workspace</span>
        <nav><ul class="nav-list">
          <li><a href="#top" class="nav-link"><span class="nav-index">00</span><span class="nav-label">回到首页</span></a></li>
          ${Object.entries(ROUTES).map(([key, [num, label]]) => `<li><a href="#/${key}" class="nav-link ${state.route === key ? "active" : ""}" ${state.route === key ? 'aria-current="page"' : ""}><span class="nav-index">${num}</span><span class="nav-label">${label}</span></a></li>`).join("")}
        </ul></nav>
        <div class="sidebar-bottom"><div class="data-stamp"><strong>${fmt(state.merchants.length)} RECORDS</strong><span>综合评分 · K=${state.algorithm.bestK} 消费画像</span></div></div>
      </aside>
      <div class="main-shell">
        <header class="topbar">
          <div class="crumb"><span>杭州餐饮</span><span>/</span><strong>${current[1]}</strong></div>
          <div class="top-actions"><span class="live-dot">DATA READY</span><span class="pill">${current[0]} · ${current[2]}</span></div>
        </header>
        <main id="main" class="page">${content}</main>
      </div>
    </div>
    ${state.selectedMerchant ? detailDrawer(state.selectedMerchant) : ""}
    ${state.compareOpen ? compareModal() : ""}
  `;
}

function render() {
  if(activeMap){
    stopMapNavigation(false);
    clearRouteDrawing();
    activeInfoWindow?.close();activeInfoWindow=null;
    activeMap.destroy();activeMap=null;startMarker=null;destinationMarker=null;
  }
  const pages = { overview: renderOverview, ranking: renderRanking, map: renderMap, ai: renderAI };
  app.innerHTML = shell(pages[state.route]());
  bindGlobal();
  ({ overview: bindOverview, ranking: bindRanking, map: bindMap, ai: bindAI })[state.route]();
}

function summary() {
  const list = state.merchants;
  const rated = list.filter(m => m.rating > 0);
  const priced = list.filter(m => m.cost > 0);
  return {
    count: list.length,
    avgRating: rated.reduce((s, m) => s + m.rating, 0) / rated.length,
    avgCost: priced.reduce((s, m) => s + m.cost, 0) / priced.length,
    high: rated.filter(m => m.rating >= 4.5).length,
    districtCount: new Set(list.map(m => m.district)).size
  };
}

function groupBy(list, key) {
  return list.reduce((map, item) => map.set(item[key], (map.get(item[key]) || []).concat(item)), new Map());
}

function topGroups(key, limit = 8) {
  return [...groupBy(state.merchants, key)].map(([name, list]) => ({ name, count: list.length, rating: average(list.filter(x => x.rating), "rating"), cost: average(list.filter(x => x.cost), "cost") })).sort((a,b) => b.count - a.count).slice(0, limit);
}

function average(list, key) { return list.length ? list.reduce((s, x) => s + Number(x[key] || 0), 0) / list.length : 0; }

function renderOverview() {
  const s = summary();
  const cuisines = topGroups("cuisine", 6);
  const districts = topGroups("district", 8);
  const donutTotal = cuisines.reduce((a, b) => a + b.count, 0);
  const colors = ["#151713", "#215cff", "#0c8a67", "#f37b2b", "#d23c31", "#a4a097"];
  let running = 0;
  const stops = cuisines.map((x, i) => { const from = running; running += x.count / donutTotal * 360; return `${colors[i]} ${from}deg ${running}deg`; }).join(",");
  return `
    <header class="page-head">
      <div><span class="eyebrow">Hangzhou · Urban taste observatory</span><h1>读懂一座城市的<br>吃饭方式。</h1></div>
      <p>从 ${fmt(s.count)} 家杭州餐饮商家的位置、消费与口碑出发，观察区域供给结构，寻找真正值得去的那一家。</p>
    </header>
    <section class="overview-grid" aria-label="杭州餐饮总览">
      <div class="explore-canvas" id="explore-canvas">
        <div class="canvas-grid"></div>
        <div class="canvas-copy"><small>LIVE CITY SAMPLE · 2026</small><h2>味觉，正在发生</h2><p>拖动数据透镜，探索杭州餐饮样本</p></div>
        <div class="food-stage" aria-hidden="true">
          <div class="food-chip">上城<small>${topGroups("district", 13).find(x=>x.name==="上城区")?.count || 0} SHOPS</small></div>
          <div class="food-chip">浙味<small>LOCAL TASTE</small></div>
          <div class="food-chip">¥${s.avgCost.toFixed(0)}<small>AVG COST</small></div>
          <div class="food-chip">${fmt(s.high)} 高分<small>RATING ≥ 4.5</small></div>
          <div class="food-chip">西湖边<small>30.25° N</small></div>
        </div>
        <div class="data-orb" id="data-orb" role="img" aria-label="可拖动的数据透镜，当前平均评分 ${s.avgRating.toFixed(2)}"><div class="orb-center"><strong>${s.avgRating.toFixed(2)}</strong><span>average rating</span></div></div>
      </div>
      <div class="metrics-stack">
        <article class="metric"><span class="metric-label">全城餐饮样本 <b>01</b></span><strong class="metric-value">${fmt(s.count)}</strong><span class="metric-delta">覆盖 ${s.districtCount} 个区县 · 数据已就绪</span></article>
        <article class="metric"><span class="metric-label">平均人均 <b>02</b></span><strong class="metric-value">¥${s.avgCost.toFixed(0)}</strong><span class="metric-delta">有效消费样本</span></article>
        <article class="metric"><span class="metric-label">高分商家 <b>03</b></span><strong class="metric-value">${pct(s.high, s.count)}</strong><span class="metric-delta">评分 ≥ 4.5</span></article>
      </div>
    </section>
    <section class="section profile-section" aria-labelledby="consumer-profiles"><div class="section-title"><div><span class="eyebrow">Algorithm / smart grouping</span><h2 id="consumer-profiles">三种消费类型</h2></div><p>系统根据评分、人均和性价比，把餐厅分成 ${state.algorithm.bestK} 类，帮助你更快找到符合预算与场景的选择。</p></div>
      <div class="profile-strata">${state.clusterProfiles.map((profile,index)=>`<article class="profile-row"><div><span class="profile-index">0${index+1}</span><strong>${esc(profile.name)}</strong></div><div class="profile-measure"><span style="width:${profile.share}%"></span></div><div class="profile-stats"><span>${fmt(profile.count)} 家 · ${profile.share.toFixed(1)}%</span><span>${profile.rating.toFixed(2)} 分 · 人均 ¥${profile.cost.toFixed(0)}</span></div></article>`).join("")}</div>
    </section>
    <section class="section" aria-labelledby="city-structure"><div class="section-title"><div><span class="eyebrow">01 / City structure</span><h2 id="city-structure">城市餐饮结构</h2></div><p>占比与区域供给均来自现有商家数据；辅助服务类指标为平台派生字段。</p></div>
      <div class="chart-grid">
        <article class="panel"><div class="panel-head"><h3>菜系 / 业态占比</h3><span>TOP 6 CATEGORIES</span></div><div class="donut-wrap chart"><div class="donut" style="background:conic-gradient(${stops})"><div class="donut-center"><strong>${cuisines.length}</strong><small>主要业态</small></div></div><div class="legend">${cuisines.map((x,i)=>`<div class="legend-row"><i class="legend-dot" style="background:${colors[i]}"></i><span>${esc(x.name)}</span><span>${pct(x.count, donutTotal)}</span></div>`).join("")}</div></div></article>
        <article class="panel panel-dark"><div class="panel-head"><h3>行政区餐饮供给</h3><span>MERCHANT COUNT</span></div><div class="bars chart">${districts.map(x=>`<div class="bar-row"><span>${esc(x.name.replace("区",""))}</span><div class="bar-track"><div class="bar-fill" style="width:${x.count/districts[0].count*100}%;background:#fff"></div></div><strong>${x.count}</strong></div>`).join("")}</div></article>
      </div>
    </section>`;
}

function bindOverview() {
  const canvas = document.querySelector("#explore-canvas"), orb = document.querySelector("#data-orb");
  if (!canvas || !orb) return;
  let dragging = false, offsetX = 0, offsetY = 0;
  orb.addEventListener("pointerdown", e => { dragging = true; orb.setPointerCapture(e.pointerId); const r=orb.getBoundingClientRect(); offsetX=e.clientX-r.left; offsetY=e.clientY-r.top; });
  orb.addEventListener("pointermove", e => {
    if (!dragging) return;
    const c=canvas.getBoundingClientRect(), o=orb.getBoundingClientRect();
    orb.style.left = `${clamp(e.clientX-c.left-offsetX, 0, c.width-o.width)}px`;
    orb.style.top = `${clamp(e.clientY-c.top-offsetY, 0, c.height-o.height)}px`;
  });
  orb.addEventListener("pointerup", () => dragging=false);
}

function filterMerchants() {
  const f = state.filters;
  return state.merchants.filter(m =>
    (f.district === "全部行政区" || m.district === f.district) &&
    (f.cuisine === "全部菜系" || m.cuisine === f.cuisine) &&
    (f.cost === "all" || (f.cost === "low" && m.cost <= 60) || (f.cost === "mid" && m.cost > 60 && m.cost <= 150) || (f.cost === "high" && m.cost > 150)) &&
    (f.status === "all" || m.status === f.status) && (!f.chain || m.chain) && (!f.delivery || m.delivery) && (!f.parking || m.parking)
  );
}

const rankingMeta = {
  overall: ["综合推荐榜", m => m.overallScore],
  praise: ["高分口碑榜", m => m.rating * 100 + m.overallScore / 100],
  value: ["性价比榜", m => m.valueRatio]
};

function sortedRanking() {
  const list = filterMerchants().filter(m => !state.showFavorites || state.favorites.has(m.id));
  return list.sort((a,b) => rankingMeta[state.ranking][1](b) - rankingMeta[state.ranking][1](a));
}

function renderFilters() {
  const cuisineCounts = [...groupBy(state.merchants, "cuisine")].map(([name, list]) => [name, list.length]).sort((a,b) => b[1] - a[1]);
  const cuisineOptions = [["全部菜系", "全部菜系"], ...cuisineCounts.map(([name, count]) => [name, `${name} · ${count}`])];
  return `<div class="filter-bar" aria-label="排行榜筛选条件"><div class="filter-grid">
    ${selectField("filter-district","行政区",DISTRICTS,state.filters.district)}
    ${selectField("filter-cuisine","具体菜系 / 类型",cuisineOptions,state.filters.cuisine)}
    ${selectField("filter-cost","人均消费",[["all","全部价格"],["low","¥60 以下"],["mid","¥61–150"],["high","¥150 以上"]],state.filters.cost)}
    ${selectField("filter-status","营业状态",[["all","全部状态"],["营业中","营业中"],["休息中","休息中"]],state.filters.status)}
  </div><div class="toggle-row">
    ${checkPill("filter-chain","仅连锁",state.filters.chain)}${checkPill("filter-delivery","支持外卖",state.filters.delivery)}${checkPill("filter-parking","有停车位",state.filters.parking)}
    <button class="btn btn-ghost" id="reset-filters">重置条件</button>
  </div></div>`;
}

function selectField(id, label, options, value) {
  return `<div class="field"><label for="${id}">${label}</label><select class="control" id="${id}">${options.map(o=>{const [v,t]=Array.isArray(o)?o:[o,o];return `<option value="${esc(v)}" ${v===value?"selected":""}>${esc(t)}</option>`}).join("")}</select></div>`;
}
function checkPill(id,label,checked){return `<label class="check-pill"><input id="${id}" type="checkbox" ${checked?"checked":""}><span>${label}</span></label>`}

function renderRanking() {
  const list = sortedRanking();
  state.filtered = list;
  return `<header class="page-head"><div><span class="eyebrow">Rankings · filtered intelligence</span><h1>哪一家，<br>真正值得去？</h1></div><p>用行政区、菜系、消费与服务条件缩小范围。综合榜同时考虑评分、消费友好度与性价比，避免只看单一星级。</p></header>
    ${renderFilters()}
    <div class="ranking-tabs" role="tablist" aria-label="排行榜类型">${Object.entries(rankingMeta).map(([key,[label]])=>`<button class="ranking-tab ${state.ranking===key?"active":""}" data-ranking="${key}" role="tab" aria-selected="${state.ranking===key}">${label}</button>`).join("")}</div>
    <details class="algorithm-disclosure"><summary><span>推荐分怎么算？</span><strong>好吃 45% · 价格友好 25% · 性价比 30%</strong></summary><div class="algorithm-body"><p>推荐分满分 100。评分越高、价格越友好、同价位表现越突出，分数越高；同分时优先评分更高、消费更低的商家。</p><div class="weight-track" aria-label="推荐分权重：评分百分之四十五，价格友好百分之二十五，性价比百分之三十"><span style="width:45%">好吃 45</span><span style="width:25%">价格 25</span><span style="width:30%">性价比 30</span></div><small>技术说明：性价比采用评分与人均消费的对数比值，三个指标标准化后加权；换用其他合理权重时，前十名至少有 ${state.algorithm.stabilityMin.toFixed(0)}% 保持一致。</small></div></details>
    <div class="result-line"><span>${state.showFavorites?"收藏中有":"筛选得到"} <strong>${fmt(list.length)}</strong> 家商户 · 当前显示前 100 家</span><div class="result-actions"><button class="btn ${state.showFavorites?"btn-dark":""}" id="toggle-favorites" aria-pressed="${state.showFavorites}">我的收藏 · ${state.favorites.size}</button><button class="btn" id="open-compare" ${state.compare.size<2?"disabled":""}>并排对比 · ${state.compare.size}/4</button><button class="btn" id="export-csv">导出 CSV</button></div></div>
    <div class="table-wrap"><table class="data-table"><thead><tr><th>排名</th><th>商家</th><th>行政区 / 具体菜系</th><th>评分</th><th>人均</th><th>推荐分</th><th>适合</th><th>操作</th></tr></thead><tbody>
      ${list.slice(0,100).map((m,i)=>rankingRow(m,i)).join("") || `<tr><td colspan="8"><div class="empty-state"><div><strong>${state.showFavorites?"暂未收藏商家":"没有符合条件的商家"}</strong>${state.showFavorites?"返回全部商家后，可将心仪餐厅加入收藏。":"调整筛选条件后再试。"}</div></div></td></tr>`}
    </tbody></table></div>`;
}

function rankingRow(m, i) {
  const favorite=state.favorites.has(m.id), comparing=state.compare.has(m.id);
  return `<tr><td><span class="rank-no ${i<3?"top":""}">${String(i+1).padStart(2,"0")}</span></td>
    <td><button class="merchant-link" data-detail="${esc(m.id)}">${esc(m.name)}<span class="merchant-meta">${esc(m.address)}</span></button></td>
    <td>${esc(m.district)}<span class="merchant-meta">${esc(m.cuisine)}</span></td>
    <td><span class="score-cell"><span class="score-badge"><strong>${m.rating.toFixed(1)}</strong><small>/ 5</small></span>${starRating(m.rating)}</span></td>
    <td>${money(m.cost)}</td><td><strong class="algorithm-score">${m.overallScore.toFixed(1)}</strong><span class="merchant-meta">全城综合 #${m.overallRank}</span></td>
    <td><span class="pill profile-pill">${esc(m.profile)}</span><span class="merchant-meta">性价比 ${m.valueRatio.toFixed(2)}</span></td>
    <td><div class="row-actions"><button class="text-button ${favorite?"active":""}" data-favorite="${esc(m.id)}" aria-pressed="${favorite}">${favorite?"已收藏":"收藏"}</button><button class="text-button ${comparing?"active":""}" data-compare="${esc(m.id)}" aria-pressed="${comparing}">${comparing?"已选对比":"加入对比"}</button></div></td>
    </tr>`;
}

function starRating(rating) {
  const stars = Array.from({length: 5}, (_, index) => {
    const fill = clamp((rating - index) * 100, 0, 100);
    return `<span class="star-unit" style="--fill:${fill}%" aria-hidden="true">★</span>`;
  }).join("");
  return `<span class="stars" role="img" aria-label="${rating.toFixed(1)} 颗星">${stars}</span>`;
}

function bindRanking() {
  [["#filter-district","district"],["#filter-cuisine","cuisine"],["#filter-cost","cost"],["#filter-status","status"]].forEach(([sel,key])=>document.querySelector(sel)?.addEventListener("change",e=>{state.filters[key]=e.target.value;render()}));
  [["#filter-chain","chain"],["#filter-delivery","delivery"],["#filter-parking","parking"]].forEach(([sel,key])=>document.querySelector(sel)?.addEventListener("change",e=>{state.filters[key]=e.target.checked;render()}));
  document.querySelector("#reset-filters")?.addEventListener("click",()=>{state.filters={district:"全部行政区",cuisine:"全部菜系",cost:"all",status:"all",chain:false,delivery:false,parking:false};render()});
  document.querySelector("#toggle-favorites")?.addEventListener("click",()=>{state.showFavorites=!state.showFavorites;render()});
  document.querySelectorAll("[data-ranking]").forEach(btn=>btn.addEventListener("click",()=>{state.ranking=btn.dataset.ranking;render()}));
  document.querySelector("#export-csv")?.addEventListener("click", exportCSV);
}

function exportCSV() {
  const cols = [["当前排名", (_,i)=>i+1],["全城综合排名",m=>m.overallRank],["商家名称",m=>m.name],["行政区",m=>m.district],["具体菜系",m=>m.cuisine],["评分",m=>m.rating],["人均消费",m=>m.cost],["综合得分",m=>m.overallScore],["性价比",m=>m.valueRatio],["消费画像",m=>m.profile],["地址",m=>m.address]];
  const csv = "\uFEFF" + [cols.map(x=>x[0]), ...state.filtered.map((m,i)=>cols.map(x=>x[1](m,i)))].map(row=>row.map(x=>`"${String(x).replaceAll('"','""')}"`).join(",")).join("\n");
  const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"})); const a=document.createElement("a"); a.href=url; a.download=`杭州餐饮-${rankingMeta[state.ranking][0]}.csv`; a.click(); URL.revokeObjectURL(url); toast("榜单 CSV 已导出");
}

function scoreColor(rating) { return rating >= 4.5 ? "#0c8a67" : rating >= 4 ? "#f1a52c" : "#d23c31"; }

function renderMap() {
  const destinations = [...state.merchants].sort((a,b)=>a.name.localeCompare(b.name,"zh-CN")).map(m=>`<option value="${esc(m.id)}" ${mapNav.destination?.id===m.id?"selected":""}>${esc(m.name)} · ${esc(m.district)}</option>`).join("");
  return `<header class="page-head"><div><span class="eyebrow">AMap · Hangzhou</span><h1>把味道，<br>放回街区。</h1></div><p>在高德地图上查看真实评分点位。地图支持缩放、拖拽和商家点选，也可从当前位置规划驾车、步行或骑行路线。</p></header>
    <section class="map-layout map-layout-navigation">
      <div class="map-panel real-map-panel">
        <div id="real-map" role="region" aria-label="杭州餐饮商家评分点位高德地图，可缩放、平移和点击商家" tabindex="0"></div>
        <div class="map-mode-label">评分点位 · ${fmt(state.merchants.length)} 家</div>
        <div class="map-zoom" aria-label="地图缩放"><button type="button" id="map-zoom-in" aria-label="放大地图">＋</button><button type="button" id="map-zoom-out" aria-label="缩小地图">−</button></div>
        <div class="map-legend"><span>低分</span><i class="legend-scale"></i><span>高分</span></div>
        <div class="map-loading" id="map-loading" role="status">正在连接高德地图…</div>
      </div>
      <aside class="map-navigation" aria-labelledby="navigation-title">
        <div class="navigation-heading"><span class="eyebrow">Route planning</span><h2 id="navigation-title">去这家餐厅</h2><p>先点地图上的商家，或从列表选择目的地。</p></div>
        <label class="field"><span class="field-label">目的地</span><select class="control" id="map-destination-select"><option value="">选择一家商家</option>${destinations}</select></label>
        <div class="route-place"><span>起点</span><strong id="map-origin-text">${mapNav.origin?esc(mapNav.origin.label):"尚未设置"}</strong></div>
        <div class="route-place"><span>目的地</span><strong id="map-destination-text">${mapNav.destination?esc(mapNav.destination.name):"尚未选择"}</strong></div>
        <div class="route-mode" role="radiogroup" aria-label="出行方式">
          <label><input type="radio" name="map-mode" value="driving" checked><span>驾车</span></label>
          <label><input type="radio" name="map-mode" value="walking"><span>步行</span></label>
          <label><input type="radio" name="map-mode" value="bicycling"><span>骑行</span></label>
        </div>
        <div class="route-actions secondary-actions"><button class="btn" type="button" id="map-locate">使用我的位置</button><button class="btn" type="button" id="map-pick-start">地图选择起点</button></div>
        <div class="route-actions"><button class="btn btn-blue" type="button" id="map-plan-route">规划路线</button><button class="btn btn-dark" type="button" id="map-start-navigation">开始实时导航</button></div>
        <div class="route-actions quiet-actions"><button class="text-action" type="button" id="map-stop-navigation">结束导航</button><button class="text-action" type="button" id="map-clear-route">清除路线</button></div>
        <div class="route-status" id="map-route-status" role="status" aria-live="polite"><strong>等待选择</strong><span>点击评分点位即可查看商家详情。</span></div>
      </aside>
    </section>`;
}

function loadAMap() {
  if (window.AMap) return Promise.resolve(window.AMap);
  if (amapLoader) return amapLoader;
  window._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_CODE };
  amapLoader = new Promise((resolve,reject)=>{
    const script=document.createElement("script");
    script.src=`https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(AMAP_JS_KEY)}&plugin=AMap.Scale,AMap.Geolocation,AMap.Driving,AMap.Walking,AMap.Riding`;
    script.async=true;
    script.onload=()=>resolve(window.AMap);
    script.onerror=()=>reject(new Error("高德地图资源加载失败"));
    document.head.appendChild(script);
  });
  return amapLoader;
}

function updateRouteStatus(title, detail) {
  const box=document.querySelector("#map-route-status");
  if(!box)return;
  box.innerHTML=`<strong>${esc(title)}</strong><span>${esc(detail||"")}</span>`;
}

function setMapOrigin(lng,lat,label="用户当前位置") {
  mapNav.origin={lng:Number(lng),lat:Number(lat),label};
  const text=document.querySelector("#map-origin-text"); if(text)text.textContent=label;
  if(!activeMap||!window.AMap)return;
  if(startMarker)startMarker.setPosition([mapNav.origin.lng,mapNav.origin.lat]);
  else {startMarker=new AMap.Marker({position:[mapNav.origin.lng,mapNav.origin.lat],content:'<span class="route-pin start-pin">起</span>',offset:new AMap.Pixel(-15,-15)});startMarker.setMap(activeMap);}
}

function setMapDestination(merchant,{openPopup=false}={}) {
  if(!merchant)return;
  mapNav.destination=merchant;
  const select=document.querySelector("#map-destination-select"); if(select)select.value=merchant.id;
  const text=document.querySelector("#map-destination-text"); if(text)text.textContent=merchant.name;
  if(activeMap&&window.AMap){
    if(destinationMarker)destinationMarker.setPosition([merchant.lng,merchant.lat]);
    else {destinationMarker=new AMap.Marker({position:[merchant.lng,merchant.lat],content:'<span class="route-pin destination-pin">终</span>',offset:new AMap.Pixel(-15,-15)});destinationMarker.setMap(activeMap);}
    activeMap.panTo([merchant.lng,merchant.lat]);
    if(activeMap.getZoom()<14)activeMap.setZoom(14);
    if(openPopup)openMerchantPopup(merchant,[merchant.lng,merchant.lat]);
  }
  updateRouteStatus("目的地已选择",merchant.name);
}

function merchantPopupElement(m) {
  const node=document.createElement("article");
  node.className="amap-merchant";
  node.innerHTML=`<button class="popup-close" type="button" aria-label="关闭商家信息">×</button><span class="eyebrow">${esc(m.district)} · ${esc(m.cuisine)}</span><h3>${esc(m.name)}</h3><div class="popup-score"><strong>${m.rating.toFixed(1)}</strong><span>/ 5</span>${starRating(m.rating)}</div><div class="popup-facts"><span>人均 ${money(m.cost)}</span><span>推荐分 ${m.overallScore.toFixed(1)}</span><span>${esc(m.profile)}</span></div><p>${esc(m.address)}</p><button class="btn btn-dark popup-destination" type="button">设为目的地</button>`;
  node.querySelector(".popup-close").addEventListener("click",()=>activeInfoWindow?.close());
  node.querySelector(".popup-destination").addEventListener("click",()=>{setMapDestination(m);activeInfoWindow?.close()});
  return node;
}

function openMerchantPopup(m, position) {
  if(!activeMap||!window.AMap)return;
  activeInfoWindow?.close();
  activeInfoWindow=new AMap.InfoWindow({isCustom:true,offset:new AMap.Pixel(0,-9),content:merchantPopupElement(m)});
  activeInfoWindow.open(activeMap,position);
}

function selectedMapMode() { return document.querySelector('input[name="map-mode"]:checked')?.value||"driving"; }

function clearRouteDrawing() {
  if(activeRouteService?.clear)activeRouteService.clear();
  activeRouteService=null;
}

function makeRouteService(mode) {
  const options={map:activeMap,hideMarkers:true,autoFitView:true};
  if(mode==="walking")return new AMap.Walking(options);
  if(mode==="bicycling")return new AMap.Riding(options);
  return new AMap.Driving({...options,policy:AMap.DrivingPolicy.LEAST_TIME,showTraffic:false});
}

function planMapRoute({quiet=false}={}) {
  if(!mapNav.origin){updateRouteStatus("还缺少起点","使用当前位置，或点击地图选择一个起点。");return;}
  if(!mapNav.destination){updateRouteStatus("还缺少目的地","请先点选一家餐厅。");return;}
  if(!activeMap||!window.AMap)return;
  const mode=selectedMapMode();
  if(!quiet)updateRouteStatus("正在规划路线","高德地图正在计算合适路线…");
  clearRouteDrawing();
  AMap.plugin(["AMap.Driving","AMap.Walking","AMap.Riding"],()=>{
    activeRouteService=makeRouteService(mode);
    activeRouteService.search([mapNav.origin.lng,mapNav.origin.lat],[mapNav.destination.lng,mapNav.destination.lat],(status,data)=>{
      mapNav.rerouteBusy=false;
      if(status!=="complete") {updateRouteStatus("路线规划失败",data?.info||"请稍后重试，或切换出行方式。");return;}
      const route=data?.routes?.[0];
      if(!route){updateRouteStatus("没有可用路线","请检查起点与目的地后重试。");return;}
      const distance=Number(route.distance||0),duration=Number(route.time||route.duration||0);
      mapNav.lastRouteOrigin={lng:mapNav.origin.lng,lat:mapNav.origin.lat};mapNav.lastRerouteAt=Date.now();
      updateRouteStatus(mapNav.navigating?"导航进行中":"路线规划完成",`${(distance/1000).toFixed(2)} 公里 · 预计 ${Math.max(1,Math.ceil(duration/60))} 分钟`);
    });
  });
}

function locateForMap() {
  if(!activeMap||!window.AMap)return;
  updateRouteStatus("正在定位","请在浏览器提示中允许获取位置。");
  AMap.plugin("AMap.Geolocation",()=>{
    const geolocation=new AMap.Geolocation({enableHighAccuracy:true,timeout:12000,convert:true,showButton:false,showMarker:false,showCircle:false});
    geolocation.getCurrentPosition((status,result)=>{
      if(status!=="complete"||!result.position){updateRouteStatus("定位失败","可点击“地图选择起点”手动设置。");return;}
      setMapOrigin(result.position.lng,result.position.lat,"我的当前位置");
      activeMap.panTo([result.position.lng,result.position.lat]);
      updateRouteStatus("定位完成","现在可以选择餐厅并规划路线。");
    });
  });
}

function startMapNavigation() {
  if(!mapNav.destination){updateRouteStatus("还缺少目的地","请先点选一家餐厅。");return;}
  if(!navigator.geolocation){updateRouteStatus("无法实时导航","当前浏览器不支持持续定位。");return;}
  if(mapNav.navigating)return;
  mapNav.navigating=true;
  updateRouteStatus("正在启动实时导航","请保持浏览器定位权限开启。");
  navigationWatchId=navigator.geolocation.watchPosition(position=>{
    const gps=[position.coords.longitude,position.coords.latitude];
    AMap.convertFrom(gps,"gps",(status,result)=>{
      if(status!=="complete"||!result.locations?.[0]){updateRouteStatus("坐标转换失败","暂时无法更新当前位置。");return;}
      const point=result.locations[0];setMapOrigin(point.lng,point.lat,"实时位置");activeMap?.panTo([point.lng,point.lat]);
      const moved=mapNav.lastRouteOrigin?AMap.GeometryUtil.distance([mapNav.lastRouteOrigin.lng,mapNav.lastRouteOrigin.lat],[point.lng,point.lat]):Infinity;
      if(!mapNav.rerouteBusy&&(moved>=50||Date.now()-mapNav.lastRerouteAt>=12000)){mapNav.rerouteBusy=true;planMapRoute({quiet:true});}
    });
  },error=>updateRouteStatus("实时定位失败",error.message||"请检查定位权限。"),{enableHighAccuracy:true,maximumAge:3000,timeout:15000});
}

function stopMapNavigation(message=true) {
  mapNav.navigating=false;mapNav.rerouteBusy=false;
  if(navigationWatchId!==null){navigator.geolocation.clearWatch(navigationWatchId);navigationWatchId=null;}
  if(message)updateRouteStatus("导航已结束","路线仍保留在地图上。");
}

async function bindMap() {
  const target=document.querySelector("#real-map"); if(!target)return;
  try { await loadAMap(); }
  catch(error){document.querySelector("#map-loading").textContent=`${error.message}，请检查网络或高德 Key 配置`;return;}
  if(!document.body.contains(target))return;
  activeMap=new AMap.Map(target,{zoom:11,center:[120.1551,30.2741],viewMode:"2D",mapStyle:"amap://styles/fresh",resizeEnable:true,scrollWheel:true});
  activeMap.addControl(new AMap.Scale({position:{bottom:"18px",right:"18px"}}));
  document.querySelector("#map-loading")?.remove();
  const list=state.merchants.filter(m=>m.lng>119.9&&m.lng<120.6&&m.lat>29.9&&m.lat<30.6);
  list.forEach(m=>{
    const marker=new AMap.CircleMarker({center:[m.lng,m.lat],radius:5,strokeColor:"#fffef9",strokeWeight:1,fillColor:scoreColor(m.rating),fillOpacity:.88,zIndex:10});
    marker.setMap(activeMap);
    marker.on("click",()=>openMerchantPopup(m,marker.getCenter()));
  });
  if(mapNav.origin)setMapOrigin(mapNav.origin.lng,mapNav.origin.lat,mapNav.origin.label);
  if(mapNav.destination)setMapDestination(mapNav.destination);
  activeMap.on("click",event=>{if(!mapNav.pickStart)return;mapNav.pickStart=false;activeMap.setDefaultCursor("default");setMapOrigin(event.lnglat.lng,event.lnglat.lat,"地图选择的起点");updateRouteStatus("起点已设置","请选择目的地并规划路线。");});
  document.querySelector("#map-zoom-in")?.addEventListener("click",()=>activeMap.zoomIn());
  document.querySelector("#map-zoom-out")?.addEventListener("click",()=>activeMap.zoomOut());
  document.querySelector("#map-locate")?.addEventListener("click",locateForMap);
  document.querySelector("#map-pick-start")?.addEventListener("click",()=>{mapNav.pickStart=true;activeMap.setDefaultCursor("crosshair");updateRouteStatus("请选择起点","点击地图上的任意位置。");});
  document.querySelector("#map-destination-select")?.addEventListener("change",event=>setMapDestination(findMerchant(event.target.value),{openPopup:true}));
  document.querySelector("#map-plan-route")?.addEventListener("click",()=>planMapRoute());
  document.querySelector("#map-start-navigation")?.addEventListener("click",startMapNavigation);
  document.querySelector("#map-stop-navigation")?.addEventListener("click",()=>stopMapNavigation());
  document.querySelector("#map-clear-route")?.addEventListener("click",()=>{clearRouteDrawing();updateRouteStatus("路线已清除","起点和目的地仍已保留。");});
}

function renderAI() {
  const tabs = {predict:"评分预测",recommend:"智能推荐"};
  return `<header class="page-head"><div><span class="eyebrow">AI lab · explainable scoring</span><h1>让预测，<br>说得清理由。</h1></div><p>评分预测与自然语言选店集中在一个工作区。配置 AI 服务后优先调用云端模型，接口不可用时自动回退到透明的本地分析。</p></header>
    <div class="ai-service-line"><span class="service-dot ${state.aiNotice.includes("已连接")?"":"local"}"></span><strong>${state.aiNotice||"智能服务已就绪"}</strong><span>API READY · LOCAL FALLBACK</span></div>
    <div class="ai-tabs" role="tablist" aria-label="AI 功能">${Object.entries(tabs).map(([k,v])=>`<button class="ai-tab ${state.aiTab===k?"active":""}" data-ai-tab="${k}" role="tab" aria-selected="${state.aiTab===k}" aria-controls="ai-workspace">${v}</button>`).join("")}</div>
    <div id="ai-workspace" role="tabpanel">
    ${state.aiTab==="predict"?predictView():recommendView()}</div>`;
}

function predictView() {
  const cuisines=[...new Set(state.merchants.map(m=>m.cuisine))].sort((a,b)=>a.localeCompare(b,"zh-CN"));
  return `<section class="ai-layout"><form class="panel form-panel" id="predict-form"><div class="panel-head"><h3>录入商家特征</h3><span>AI + DATA MODEL</span></div><div class="form-grid">
    ${selectField("ai-cuisine","具体菜系 / 业态",cuisines,"杭帮菜")}${selectField("ai-district","所在行政区",DISTRICTS.slice(1),"西湖区")}
    <div class="field field-full"><label for="ai-location">商圈或位置描述</label><input class="control" id="ai-location" name="location" value="西湖景区周边" maxlength="80" placeholder="例如：滨江区星光大道附近"></div>
    <div class="field"><label for="ai-cost">人均消费（元）</label><input class="control" id="ai-cost" name="cost" type="number" min="0" max="2000" value="88" required></div>
    <div class="field"><label for="ai-reviews">评论数量</label><input class="control" id="ai-reviews" name="reviews" type="number" min="0" max="999999" value="680" required></div>
    <fieldset class="service-fieldset field-full"><legend>配套服务</legend><div class="toggle-row"><label class="check-pill"><input name="delivery" type="checkbox" checked><span>支持外卖</span></label><label class="check-pill"><input name="parking" type="checkbox"><span>有停车位</span></label><label class="check-pill"><input name="chain" type="checkbox"><span>连锁品牌</span></label><label class="check-pill"><input name="open" type="checkbox" checked><span>正常营业</span></label></div></fieldset>
    <button class="btn btn-blue wide field-full" type="submit" ${state.aiBusy?"disabled aria-busy=\"true\"":""}>${state.aiBusy?"正在分析…":"生成评分预测"}</button>
  </div></form><div class="panel ai-result" id="prediction-result">${predictionResult()}</div></section>
  <section class="section"><div class="section-title"><div><span class="eyebrow">Prediction history</span><h2>最近的预测</h2></div>${state.history.length?`<button class="btn" id="clear-history">清空本地记录</button>`:""}</div>${state.history.length?`<div class="panel history-list">${state.history.map(h=>`<div class="history-row"><div><strong>${esc(h.cuisine)} · ${esc(h.district)}</strong><p>${esc(h.time)} · ${esc(h.location||"位置未填写")} · 人均 ¥${h.cost} · ${fmt(h.reviews)} 条评论</p></div><span class="history-score">${h.score}</span></div>`).join("")}</div>`:`<div class="history-empty">完成一次预测后，结果会保存在当前浏览器中。</div>`}</section>`;
}

function predictionResult() {
  const p=state.prediction; if(!p)return `<div class="empty-state"><div><strong>等待输入</strong>填写左侧特征，模型将返回预测评分、置信度与关键影响因素。</div></div>`;
  return `<div class="prediction-hero"><div class="score-ring" style="--angle:${p.score/5*360}deg"><div><strong>${p.score.toFixed(2)}</strong><span>PREDICTED / 5</span></div></div><div><span class="eyebrow">Prediction ready · ${esc(p.source||"本地模型")}</span><h2>${p.score>=4.5?"值得重点关注":p.score>=4?"具有良好潜力":"仍有优化空间"}</h2><p class="confidence">模型置信度 <strong>${Math.round(p.confidence)}%</strong> · 基于相似商家 ${fmt(p.samples)} 条</p></div></div><div><div class="panel-head"><h3>关键影响因素</h3><span>EXPLAINABLE OUTPUT</span></div><div class="factor-list">${p.factors.map(f=>`<div class="factor ${f.value<0?"negative":""}"><span>${esc(f.name)}</span><div class="factor-track"><div class="factor-fill" style="width:${Math.min(100,Math.abs(f.value)*100)}%"></div></div><strong>${f.value>0?"+":""}${Number(f.impact??f.value*.5).toFixed(2)}</strong></div>`).join("")}</div></div><p class="model-note">结果用于选店参考，并非平台正式评级。云端不可用时会明确标注“本地模型”。</p>`;
}

function recommendView() {
  return `<section class="recommend-layout"><div class="recommend-query-panel"><span class="eyebrow">Natural language search</span><h2>用一句话，描述你想吃什么。</h2><form id="recommend-form"><div class="recommend-row"><label class="field"><span class="field-label">需求描述</span><input class="control" id="recommend-query" value="帮我找滨江性价比高的浙菜" maxlength="160" placeholder="例如：西湖区适合约会、人均 150 内的餐厅"></label><button class="btn btn-blue" type="submit" ${state.aiBusy?"disabled aria-busy=\"true\"":""}>${state.aiBusy?"正在匹配…":"智能推荐"}</button></div></form><div class="toggle-row"><button class="pill example-query" type="button">西湖区人均 80 以下</button><button class="pill example-query" type="button">滨江高分浙菜</button><button class="pill example-query" type="button">萧山安静的咖啡厅</button></div><p>模型会结合区域、预算、菜系、评分与推荐分，从真实商家数据中选择更合适的餐厅。</p></div><div class="recommend-output"><div class="panel-head"><h3>推荐结果</h3><span>${state.recommendations.length?`${state.recommendations.length} MATCHES · ${esc(state.recommendationMeta?.source||"本地理解")}`:"WAITING FOR QUERY"}</span></div><div class="recommend-results">${state.recommendations.length?state.recommendations.map((m,i)=>`<article class="recommend-card"><div class="number">${String(i+1).padStart(2,"0")}</div><div><h4>${esc(m.name)}</h4><p>${esc(m.district)} · ${esc(m.cuisine)} · ${money(m.cost)} · ${m.rating.toFixed(1)} 分 · 推荐分 ${m.overallScore.toFixed(1)}</p><small>${esc(m._reason||"评分、价格与需求匹配度较高")}</small></div><button class="text-button" data-detail="${esc(m.id)}">查看详情</button></article>`).join(""):`<div class="empty-state"><div><strong>从一句需求开始</strong>系统会从 ${fmt(state.merchants.length)} 家商户中匹配候选。</div></div>`}</div></div></section>`;
}

function bindAI() {
  document.querySelectorAll("[data-ai-tab]").forEach(btn=>btn.addEventListener("click",()=>{state.aiTab=btn.dataset.aiTab;render()}));
  document.querySelector("#predict-form")?.addEventListener("submit",runPrediction);
  document.querySelector("#clear-history")?.addEventListener("click",()=>{if(!confirm("确定清空当前浏览器中的预测历史吗？"))return;state.history=[];persist();render()});
  document.querySelector("#recommend-form")?.addEventListener("submit",e=>{e.preventDefault();runRecommendation(document.querySelector("#recommend-query").value)});
  document.querySelectorAll(".example-query").forEach(btn=>btn.addEventListener("click",()=>runRecommendation(btn.textContent)));
}

async function callAI(task,payload){
  try{const response=await fetch("/api/ai",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task,payload})});if(!response.ok)throw new Error((await response.json().catch(()=>({}))).message||"AI 服务不可用");const data=await response.json();state.aiNotice="AI 接口已连接";return data}catch(error){state.aiNotice="AI 未连接，已使用本地分析";return null}
}

async function runPrediction(event){
  event.preventDefault();const fd=new FormData(event.currentTarget);const features={cuisine:fd.get("ai-cuisine")||document.querySelector("#ai-cuisine").value,district:fd.get("ai-district")||document.querySelector("#ai-district").value,location:String(fd.get("location")||""),cost:Number(fd.get("cost")),reviews:Number(fd.get("reviews")),delivery:fd.has("delivery"),parking:fd.has("parking"),chain:fd.has("chain"),open:fd.has("open")};
  const similar=state.merchants.filter(m=>m.cuisine===features.cuisine||m.district===features.district);const base=similar.length?average(similar.filter(x=>x.rating),"rating"):summary().avgRating;const factors=[{name:"同类口碑",value:clamp((base-4)/1.1,-1,1)},{name:"评论样本",value:clamp(Math.log10(features.reviews+1)/4,0,1)},{name:"价格适配",value:clamp(.75-Math.abs(features.cost-95)/210,-1,1)},{name:"地理位置",value:features.location?.16:.02},{name:"配套服务",value:(features.delivery?.22:0)+(features.parking?.18:0)+(features.open?.12:-.35)}];const localScore=clamp(base+(factors[1].value-.55)*.22+factors[2].value*.11+factors[3].value*.12+factors[4].value*.18,2.5,4.95);const local={score:localScore,confidence:Math.round(clamp(67+Math.log10(similar.length+1)*8+Math.min(features.reviews,2000)/200,65,94)),samples:similar.length,factors,source:"本地模型"};
  state.aiBusy=true;render();const ai=await callAI("predict",{features,baseline:{averageRating:base,similarSamples:similar.length,cityAverage:summary().avgRating}});const result=ai?.result;state.prediction=result&&Number.isFinite(Number(result.score))?{score:clamp(Number(result.score),0,5),confidence:clamp(Number(result.confidence)||75,0,100),samples:similar.length,factors:Array.isArray(result.factors)?result.factors.slice(0,6):factors,source:"AI 模型"}:local;state.history.unshift({...features,score:state.prediction.score.toFixed(2),source:state.prediction.source,time:new Date().toLocaleString("zh-CN",{month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"})});state.history=state.history.slice(0,20);state.aiBusy=false;persist();render();toast("预测完成，结果已保存在本机");
}

async function runRecommendation(query) {
  query=String(query||"").trim();
  if(!query){toast("请先描述你的选店需求");return}
  const district=DISTRICTS.slice(1).find(d=>query.includes(d.replace("区",""))||query.includes(d));
  const cuisines=[...new Set(state.merchants.map(m=>m.cuisine))];
  const cuisineAlias=[["浙菜","浙江菜"],["杭帮","杭帮菜"],["日料","日本料理"],["西餐","综合西餐"],["咖啡","咖啡厅"],["火锅","火锅店"]];
  const aliased=cuisineAlias.find(([word])=>query.includes(word))?.[1];
  const cuisine=aliased||cuisines.find(c=>query.includes(c.replace(/菜|餐厅|料理/g,""))||query.includes(c));
  const priceMatch=query.match(/(?:人均|预算|¥|￥)\s*(\d+)/);
  const maxCost=priceMatch?Number(priceMatch[1]):query.includes("性价比")?120:Infinity;
  const candidates=state.merchants
    .filter(m=>(!district||m.district===district)&&(!cuisine||m.cuisine===cuisine)&&(!m.cost||m.cost<=maxCost))
    .sort((a,b)=>query.includes("高分")?b.rating-a.rating:query.includes("性价比")?b.valueRatio-a.valueRatio:b.overallScore-a.overallScore)
    .slice(0,30);
  const local=candidates.slice(0,5).map(m=>({...m,_reason:`${district||m.district}中${query.includes("高分")?"评分表现":query.includes("性价比")?"性价比表现":"综合推荐分"}靠前，属于${m.profile}`}));
  state.aiBusy=true;render();
  const ai=await callAI("recommend",{query,candidates:candidates.map(m=>({id:m.id,name:m.name,district:m.district,cuisine:m.cuisine,cost:m.cost,rating:m.rating,recommendationScore:m.overallScore,valueIndex:m.valueRatio,profile:m.profile,tags:m.tags.slice(0,5)}))});
  const picks=Array.isArray(ai?.result?.recommendations)?ai.result.recommendations:[];
  const byId=new Map(candidates.map(m=>[m.id,m]));
  const aiList=picks.map(p=>{const m=byId.get(String(p.id));return m?{...m,_reason:String(p.reason||"符合需求")}:null}).filter(Boolean).slice(0,5);
  state.recommendations=aiList.length?aiList:local;
  state.recommendationMeta={source:aiList.length?"AI 理解":"本地理解",district,cuisine,maxCost};
  state.aiBusy=false;render();
  toast(`理解到：${district||"全杭州"} · ${cuisine||"全部菜系"} · ${maxCost===Infinity?"不限价格":`¥${maxCost}内`}`);
}

function detailDrawer(m) {
  const sampleTags=m.tags.slice(0,6); const favorite=state.favorites.has(m.id), comparing=state.compare.has(m.id);
  return `<div class="drawer-backdrop" id="drawer-backdrop"><aside class="drawer" role="dialog" aria-modal="true" aria-labelledby="merchant-title"><div class="drawer-head"><div><span class="eyebrow">Merchant detail · ${esc(m.district)}</span><h2 id="merchant-title">${esc(m.name)}</h2><p class="drawer-address">${esc(m.address)}<br>${esc(m.tel)}</p></div><button class="btn" id="close-drawer">关闭</button></div>
    <div class="drawer-actions"><button class="btn ${favorite?"btn-dark":""}" data-favorite="${esc(m.id)}" aria-pressed="${favorite}">${favorite?"已收藏":"收藏商家"}</button><button class="btn ${comparing?"btn-dark":""}" data-compare="${esc(m.id)}" aria-pressed="${comparing}">${comparing?"已加入对比":"加入并排对比"}</button>${state.compare.size>=2?`<button class="btn btn-blue" id="open-compare">查看对比 · ${state.compare.size}/4</button>`:""}</div>
    <div class="detail-score"><div class="detail-stat"><span>用户评分</span><strong>${m.rating.toFixed(1)}</strong></div><div class="detail-stat"><span>推荐分</span><strong>${m.overallScore.toFixed(1)}</strong></div><div class="detail-stat"><span>人均消费</span><strong>${money(m.cost)}</strong></div><div class="detail-stat"><span>全城排名</span><strong>#${m.overallRank}</strong></div></div>
    <div class="tag-list"><span class="pill pill-blue">${esc(m.profile)}</span><span class="pill">${esc(m.subtype)}</span>${sampleTags.map(t=>`<span class="pill">${esc(t)}</span>`).join("")}<span class="pill">${m.chain?"连锁":"非连锁"}</span><span class="pill">${m.delivery?"支持外卖":"仅堂食"}</span></div>
    <section class="section"><div class="panel-head"><h3>推荐分构成</h3><span>好吃 45 · 价格 25 · 性价比 30</span></div><div class="factor-list"><div class="factor"><span>评分表现</span><div class="factor-track"><div class="factor-fill" style="width:${m.ratingIndex*100}%"></div></div><strong>${Math.round(m.ratingIndex*100)}</strong></div><div class="factor"><span>价格友好</span><div class="factor-track"><div class="factor-fill" style="width:${m.costFriendliness*100}%"></div></div><strong>${Math.round(m.costFriendliness*100)}</strong></div><div class="factor"><span>同价位性价比</span><div class="factor-track"><div class="factor-fill" style="width:${m.valueIndex*100}%"></div></div><strong>${Math.round(m.valueIndex*100)}</strong></div></div><p class="model-note">三项都按全城商家范围换算为 0–100 后加权，便于比较不同价位的餐厅。</p></section>
    <section class="section"><div class="panel-head"><h3>选餐摘要</h3><span>FROM MERCHANT DATA</span></div><blockquote class="review-card">“${sampleTags.slice(0,3).join("、")||m.cuisine}”是这家店的主要特色，当前属于“${esc(m.profile)}”。<small>商家标签与消费画像</small></blockquote><blockquote class="review-card">用户评分 ${m.rating.toFixed(1)}，人均约 ${money(m.cost)}，推荐分 ${m.overallScore.toFixed(1)}，全城综合排名第 ${m.overallRank}。<small>评分与消费数据</small></blockquote></section>
    </aside></div>`;
}

function compareModal() {
  const items=[...state.compare].map(findMerchant).filter(Boolean);
  return `<div class="modal-backdrop" id="modal-backdrop"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="compare-title"><div class="drawer-head"><div><span class="eyebrow">Compare · ${items.length}/4</span><h2 id="compare-title" style="margin:7px 0">商家横向对比</h2></div><button class="btn" id="close-compare">关闭</button></div><div class="compare-grid" style="--cols:${items.length}">${items.map(m=>`<div class="compare-col"><div class="compare-cell head"><span class="eyebrow">${esc(m.district)}</span><h3>${esc(m.name)}</h3><button class="btn" data-compare="${esc(m.id)}">移除</button></div><div class="compare-cell"><span>用户评分</span><strong>${m.rating.toFixed(1)} / 5</strong></div><div class="compare-cell"><span>推荐分</span><strong>${m.overallScore.toFixed(1)} / 100</strong></div><div class="compare-cell"><span>人均消费</span><strong>${money(m.cost)}</strong></div><div class="compare-cell"><span>适合</span><strong>${esc(m.profile)}</strong></div><div class="compare-cell"><span>性价比指数</span><strong>${m.valueRatio.toFixed(2)}</strong></div><div class="compare-cell"><span>服务配套</span><p>${m.delivery?"外卖 · ":""}${m.parking?"停车 · ":""}${m.chain?"连锁":"非连锁"}</p></div></div>`).join("")}</div></section></div>`;
}

function bindGlobal() {
  document.querySelectorAll("[data-detail]").forEach(btn=>btn.addEventListener("click",()=>{state.selectedMerchant=findMerchant(btn.dataset.detail);render()}));
  document.querySelectorAll("[data-favorite]").forEach(btn=>btn.addEventListener("click",()=>{const id=btn.dataset.favorite;state.favorites.has(id)?state.favorites.delete(id):state.favorites.add(id);persist();render();toast(state.favorites.has(id)?"已收藏商家":"已取消收藏")}));
  document.querySelectorAll("[data-compare]").forEach(btn=>btn.addEventListener("click",()=>toggleCompare(btn.dataset.compare)));
  document.querySelector("#close-drawer")?.addEventListener("click",()=>{state.selectedMerchant=null;render()});
  document.querySelector("#drawer-backdrop")?.addEventListener("click",e=>{if(e.target.id==="drawer-backdrop"){state.selectedMerchant=null;render()}});
  document.querySelector("#open-compare")?.addEventListener("click",()=>{state.compareOpen=true;render()});
  document.querySelector("#close-compare")?.addEventListener("click",()=>{state.compareOpen=false;render()});
  document.querySelector("#modal-backdrop")?.addEventListener("click",e=>{if(e.target.id==="modal-backdrop"){state.compareOpen=false;render()}});
  document.querySelector("#open-favorites")?.addEventListener("click",()=>{state.filters={district:"全部行政区",cuisine:"全部菜系",cost:"all",status:"all",chain:false,delivery:false,parking:false};state.route="ranking";location.hash="#/ranking";render();toast(`已收藏 ${state.favorites.size} 家，可在榜单中查看收藏标记`)});
  document.addEventListener("keydown", escapeHandler, {once:true});
}

function escapeHandler(e){if(e.key!=="Escape")return;if(state.selectedMerchant){state.selectedMerchant=null;render()}else if(state.compareOpen){state.compareOpen=false;render()}}
function toggleCompare(id){if(state.compare.has(id))state.compare.delete(id);else if(state.compare.size>=4){toast("最多同时对比 4 家商户");return}else state.compare.add(id);if(state.compareOpen&&state.compare.size<2)state.compareOpen=false;render();toast(`${state.compare.size} 家商户已加入对比`) }
function findMerchant(id){return state.merchants.find(m=>m.id===id)}
function toast(message){document.querySelector(".toast")?.remove();const el=document.createElement("div");el.className="toast";el.setAttribute("role","status");el.textContent=message;document.body.appendChild(el);setTimeout(()=>el.remove(),2400)}

window.addEventListener("hashchange", routeFromHash);
loadData();
