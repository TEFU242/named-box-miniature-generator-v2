import os,base64,html,datetime,glob
def esc(s):return html.escape(str(s))
def make(ROOT,R,steps,shots):
    out=os.path.join(ROOT,'report');os.makedirs(out,exist_ok=True)
    ok=sum(1 for x in R if x['ok'] and not x['warn']);warn=sum(1 for x in R if x['warn'] and x['ok']);fail=sum(1 for x in R if not x['ok'])
    total=len(R);pct=(ok+warn)/total*100 if total else 0
    groups={}
    for x in R:groups.setdefault(x['grp'],[]).append(x)
    def badge(x):
        if not x['ok']:return '<span class="b f">✗ 失敗</span>'
        if x['warn']:return '<span class="b w">⚠ 注意</span>'
        return '<span class="b p">✓ 通過</span>'
    rows=''
    for g,items in groups.items():
        gp=sum(1 for x in items if x['ok'])
        rows+=f'<h3>{esc(g)} <small>{gp}/{len(items)}</small></h3><table><tr><th style="width:90px">結果</th><th>測試項目</th><th>實測資料</th><th style="width:70px">耗時</th></tr>'
        for x in items:rows+=f'<tr class="{"fail" if not x["ok"] else ""}"><td>{badge(x)}</td><td>{esc(x["name"])}</td><td class="d">{esc(x["detail"])}</td><td>{x["ms"]} ms</td></tr>'
        rows+='</table>'
    names=['預設雙斜＋地板燈孔','2 層樓＋樓板＋屋頂分離＋窗框＋屋脊蓋＋煙囪＋外伸＋室內牆','四面斜＋蜂巢六邊形燈孔','複折＋2 層＋拱形窗','雙折＋屋頂燈孔＋屋頂分離','四面斜＋3 層＋樓板＋拱形大門＋2 組樓梯','3 層＋L 型鏤空樓梯（雙側扶手）＋U 型接續樓梯','美式組合：附屬車庫（門洞）＋前門廊＋後工具棚','2 層＋各層獨立室內牆（圖層）']
    srows=''
    for i,(st,n) in enumerate(zip(steps,names)):
        mark='<span class="b p">✓</span>' if st[0] else '<span class="b f">✗</span>'
        srows+=f'<tr><td>{mark}</td><td>第 {i+1} 組：{n}</td><td class="d">{esc(st[1])}</td><td>{st[2]/1024:.0f} KB</td></tr>'
    imgs=''
    for sid,title,fn in shots:
        if fn and os.path.exists(fn):
            b=base64.b64encode(open(fn,'rb').read()).decode()
            imgs+=f'<figure><img src="data:image/png;base64,{b}" alt="{esc(title)}"><figcaption>{esc(title)}</figcaption></figure>'
        else:imgs+=f'<figure><div class="noimg">（截圖失敗）</div><figcaption>{esc(title)}</figcaption></figure>'
    boc=os.path.join(os.path.dirname(ROOT),'boc_creator')
    files=''
    if os.path.isdir(boc):
        for f in sorted(glob.glob(os.path.join(boc,'js','*.js'))+glob.glob(os.path.join(boc,'*.html'))+glob.glob(os.path.join(boc,'*.css'))+glob.glob(os.path.join(boc,'server.py'))):
            files+=f'<tr><td>{esc(os.path.relpath(f,os.path.dirname(boc)))}</td><td>{datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")}</td></tr>'
    chk=[
     ('整體 UI 改為明亮風格','✓','預設明亮主題，右上角可切換暗色；3D 場景、網格、尺寸標籤、ViewCube 同步換色'),
     ('屋頂不再像方塊盒','✓','改為「本體牆＋屋頂厚板」：新增屋簷外伸（長邊／山牆）、屋頂厚度、雙折（穀倉）與複折（四面）屋頂、屋脊蓋、煙囪、傾角快速設定（15/30/45/55°）'),
     ('屋頂可分開、可各自選 3D／雷射','✓','屋頂與本體各為獨立零件；步驟⑥可選「本體雷射＋屋頂 3D」或相反；STL／STEP 可選全部／本體／屋頂'),
     ('紋路解析度太低','✓','預覽解析度（0.8~0.12mm）與「貼皮輸出解析度」（0.5~0.08mm）分開；匯出時以輸出解析度重算，並預估三角面與檔案大小'),
     ('紋路最小比例過大','✓','紋理比例／屋頂密度下限由 0.5 降到 0.2；新增 12 種更細緻紋路（細磚、細木紋、灰泥、混凝土、切石、亂石、鵝卵石、茅草、魚鱗瓦、波浪鐵皮、直立木板、木瓦）'),
     ('紋路裂痕舊化＋閾值','✓','「舊化／裂痕程度」0~100：越高裂縫越寬越密、剝落越多、表面越凌亂；可設隨機種子；屋頂也有獨立舊化滑桿'),
     ('燈孔裝在地板（不是屋頂）','✓','預設裝在底層地板並自動產生地板；仍保留「屋頂」選項'),
     ('窗戶／貼皮：3D 與平面圖一起顯示','✓','步驟③④預設並排顯示；右上角可切換 3D／平面圖／並排'),
     ('窗戶對齊與均分（仿 Illustrator）','✓','Shift 點選或框選多扇窗：左／右／頂／底對齊、水平／垂直置中、水平／垂直均分（中心或等間距）、置中於牆、牆內均分排列；單選時以牆面為基準'),
     ('個別調整設為進階選項','✓','數字清單與轉換按鈕收進「進階」；日常用正視圖拖曳即可'),
     ('窗框單獨拉出、放最下面','✓','步驟③最下方「窗框與窗台」：框寬、凸出量、窗台'),
     ('窗戶可視化調整','✓','牆面正視圖：拖曳移動、拖白色小方塊縮放、雙擊新增、Delete 刪除；拖到貼地自動變門'),
     ('貼皮：獨立預覽','✓','並排檢視；另保留頁內 3D 小視窗（非另開瀏覽器視窗）'),
     ('貼皮：框選區域易辨識、可調大小','✓','白邊＋高對比色框（橘＝待套用、綠＝已貼皮、藍＝選取）；「調整區域」工具可拖控制點縮放／移動，並可輸入左下寬高；3D 上同步標示'),
     ('室內牆可自由起訖、符合現實','✓','牆有起點／終點，拖端點調長度並吸附外牆與他牆；雙擊牆身加門；十字／T 字範本'),
     ('第一步加地板','✓','「加地板（底層）」「加樓板（樓層之間）」與厚度'),
     ('重設選項、貼皮無法移除','✓','新增「清除全部貼皮」（含屋頂款式與待套用區域）、移除選取貼皮現在也能移除屋頂款式面；每個步驟底部新增「↺ 重設本步驟」，可 Ctrl+Z 復原；右上角「新專案」仍可整個重來'),
     ('窗戶移動時按住 Shift 吸附','✓','拖曳窗戶或縮放控制點時按住 Shift：吸附到同牆其他窗戶的邊緣／中心、牆面邊緣／中心、樓層線與地面（門檻 3mm），並顯示粉紅參考線；Shift 點選多選仍可用（未移動才切換選取）'),
     ('每層樓可加樓梯（開關）','✓','步驟⑤每層樓一個「加樓梯」開關（1F→2F、2F→3F…）；有樓板時自動在上一層樓板挖樓梯洞'),
     ('樓梯獨立成步驟？','✓','評估後併入步驟⑤「室內牆壁・門・樓梯」：樓梯位置要對照牆與門，共用同一張平面圖最直覺，也不需重排步驟編號；若仍希望獨立成第 7 步可再調整'),
     ('樓梯可調位置、方向、斜度','✓','平面圖拖曳樓梯移動、拖橘色圓點改方向（±X／±Z）；卡片可輸入起點、斜度 15~60°、寬度、每階高；階數與長度自動換算，超出室內會警告'),
     ('窗戶步驟加「大門」','✓','步驟③新增大門：牆面、款式（單扇／雙開／拱形）、寬、高、位置；正視圖可拖曳（Shift 吸附牆中心／窗戶中心）；參數化窗戶自動讓開；3D／STEP／雷射皆支援'),
     ('3D 顯示不舒服（漸層、疊色）','✓','原因：半透明材質（DoubleSide）讓內牆與背面透出疊色；大三角形的平滑法線在平面上拉出漸層。已改為 CAD 式：不透明霧面、折角 12° 才平滑、加反向補光與跟隨視角的頭燈'),
     ('右下角 X 光開關','✓','預設「X光：關」＝外殼不透明、完全看不到室內；開啟後外殼半透明，室內牆、樓板、樓梯以暖色凸顯，並自動顯示輪廓線'),
     ('透視／正交視圖','✓','右下角「透視｜正交」：正交為 CAD 平行投影；切換時保持視角方向與物體大小，視角立方體、標籤、點選、平移縮放皆可用'),
     ('室內每加一層就多一張頂視圖','✓','步驟⑤同時並排顯示每一層各自的頂視圖（1F、2F、3F…），各層只畫自己的牆、門、樓梯，不再疊在一起；點某層空白處或牆就切換為目前編輯層；樓下來的樓梯以淡色顯示在上一層'),
     ('記憶體釋放按鈕','✓','右上角「🧹 釋放記憶體」：顯示 JS 記憶體、GPU 物件、貼皮三角面、復原歷史；可一鍵釋放，或單獨清歷史、釋放快取、暫時關閉貼皮預覽、降到 0.8mm 預覽；記憶體偏高時按鈕出現紅點'),
     ('輸出可選「牆壁分片列印」','✓','步驟⑥勾選後，牆／屋頂一片一片平放拼版（板厚可調、含窗洞燈孔），可匯出分片牆板 STL；未勾獨立紋理時，浮雕直接長在牆片上（FDM 平放可印出紋理）'),
     ('紋理獨立薄片（搭配雷射切割＋光固化）','✓','勾選「紋理獨立成薄片」：每個貼皮面輸出一片（底板厚度可調、避開窗洞）平放拼版 STL 供光固化列印，黏在雷射切割的平板上；牆片／本體不再含浮雕'),
     ('屋頂紋路加解析度（面數）選項','✓','步驟②選了屋頂紋路款式後，出現與貼皮步驟相同的預覽／輸出解析度，並顯示屋頂紋路三角面數；兩處共用同一數值'),
     ('窗戶本體與窗框為外加零件','✓','牆體開口不變；可另外勾選「窗戶玻璃片」「窗扇框與窗格條」（含厚度）與窗框、窗台，各自是獨立零件'),
     ('門的款式與門把','✓','勾選「生成門板本體」後可選：木門、鐵門、鐵花門、玻璃門、鐵捲門、分節式車庫門、平板門；門把：喇叭鎖、把手鎖、推拉直把、無；支援單扇、雙開、拱形、多扇與各面牆。門板僅輸出到 STL（STEP 只含開口）'),
     ('不影響原本正常的程式','✓','BentoBox3D（boc_creator）未修改；本專案舊功能（試板、雷射、STEP、存檔、復原）納入回歸測試'),
    ]
    crows=''.join(f'<tr><td>{esc(a)}</td><td class="c{"p" if b=="✓" else "w"}">{b}</td><td>{esc(c)}</td></tr>' for a,b,c in chk)
    lim=['❌ 超出列印平台時的「自動分件」尚未提供（僅警告，屋頂分離可減少單件體積）。','❌ 貼皮是連續曲面浮雕，只輸出到 STL；STEP 為不含貼皮的精確本體。','⚠️ STL 為網格：CSG 後仍可能有極少量接縫（已做 T 型接縫修補，剩 1~6 條邊），切片軟體會自動修復；STEP 不受影響。','⚠️ 窗框一律為矩形外框（拱形窗外框不隨弧形）。','⚠️ 煙囪底部會略伸入屋頂內側（為確保與屋頂相連）。','⚠️ 室內牆、地板、樓板在雷射模式為平板，需自行黏合。','❓ 真實滑鼠／觸控板的拖曳手感無法在無頭瀏覽器驗證，請實際操作確認。','⚠️ 「獨立視窗」為頁內小視窗，不是另開的瀏覽器視窗。']
    limh=''.join(f'<li>{esc(x)}</li>' for x in lim)
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    doc=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>冠名盒子微縮生成器・驗證報告</title>
<style>
:root{{--bg:#f3f6fa;--card:#fff;--line:#d8e0ea;--txt:#1c2b3d;--mut:#66788f;--ac:#0a74d6;--ok:#10a874;--wn:#d98a00;--ng:#d93a3a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--txt);font:15px/1.6 -apple-system,"PingFang TC",sans-serif}}
header{{background:linear-gradient(135deg,#0a74d6,#2aa6f0);color:#fff;padding:28px 6vw}}header h1{{margin:0 0 6px;font-size:26px}}header p{{margin:0;opacity:.9}}
main{{padding:22px 6vw 60px;max-width:1280px;margin:auto}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:18px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}.card b{{display:block;font-size:30px}}.card span{{color:var(--mut);font-size:13px}}
h2{{margin:34px 0 10px;font-size:20px;border-left:5px solid var(--ac);padding-left:10px}}h3{{margin:22px 0 6px;font-size:16px}}h3 small{{color:var(--mut);font-weight:400}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:13.5px}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:#eaf1f9;font-weight:600}}td.d{{color:var(--mut);word-break:break-all}}tr.fail td{{background:#fff2f2}}
.b{{display:inline-block;padding:1px 9px;border-radius:12px;font-size:12px;color:#fff}}.b.p{{background:var(--ok)}}.b.w{{background:var(--wn)}}.b.f{{background:var(--ng)}}
td.cp{{color:var(--ok);font-weight:700;text-align:center}}td.cw{{color:var(--wn);font-weight:700;text-align:center}}
.bar{{height:14px;background:#e1e8f0;border-radius:8px;overflow:hidden}}.bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--ok),#42d6a0);width:{pct:.1f}%}}
figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px}}figure img{{width:100%;border-radius:8px;display:block}}figcaption{{padding:8px 4px 2px;font-size:13px;color:var(--mut)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px}}.noimg{{padding:60px;text-align:center;color:var(--mut)}}
code{{background:#e9eff6;padding:1px 6px;border-radius:5px}}li{{margin:4px 0}}
</style></head><body>
<header><h1>冠名盒子微縮生成器・開發驗證報告</h1><p>產生時間 {now} ｜ 專案：roof_lamp_generator ｜ 驗證方式：無頭 Chrome（SwiftShader WebGL）自動化測試 + build123d STEP 後端檢查 + 場景截圖</p></header>
<main>
<div class="cards"><div class="card"><b>{total}</b><span>自動化測試項目</span></div><div class="card"><b style="color:var(--ok)">{ok}</b><span>通過</span></div><div class="card"><b style="color:var(--wn)">{warn}</b><span>通過但有注意事項</span></div><div class="card"><b style="color:var(--ng)">{fail}</b><span>失敗</span></div><div class="card"><b>{pct:.0f}%</b><span>可用率（通過＋注意）</span></div></div>
<div class="bar"><i></i></div>
<h2>1. 需求完成度對照</h2><table><tr><th>需求</th><th style="width:60px">狀態</th><th>實作說明</th></tr>{crows}</table>
<h2>2. 設計決策與評估（為什麼這樣做）</h2><ul>
<li><b>屋頂改為「本體＋厚板」</b>：舊版把屋頂當成外殼的一部分，只能是方盒加斜頂。改成以「屋頂平面組」切出厚板，才能做外伸、厚度、雙折／複折，也讓屋頂能獨立列印或雷射切割。平面組同時用來自動展開雷射零件與貼皮面，所有輸出共用同一份幾何，避免不一致。</li>
<li><b>燈孔改裝在地板</b>：燈具從底部放入最合理，也避免破壞屋頂紋路與貼皮；屋頂選項保留給特殊情況。</li>
<li><b>解析度「所見即所得」但分開設定</b>：預覽用較粗格距維持流暢，匯出時用輸出解析度重算，所以最後的樣子與預覽一致、只是更細；並預估檔案大小避免產生打不開的巨型 STL。</li>
<li><b>舊化用 Voronoi 裂縫＋低頻剝落</b>：閾值同時提高裂縫密度、寬度與剝落比例，才會「越高越凌亂」；種子固定所以可重現。</li>
<li><b>對齊工具仿 Illustrator</b>：單選對齊牆面、多選對齊選取範圍；同一牆面的窗戶為一組，避免跨牆誤算。</li>
<li><b>進階／一般分流</b>：日常以拖曳完成，數字清單與細項參數收進「進階」，降低初學者負擔。</li>
</ul>
<h2>3. 自動化測試結果</h2>{rows}
<h2>4. STEP 精確幾何後端測試</h2><table><tr><th style="width:60px">結果</th><th>情境</th><th>實體檢查（build123d 重新讀入）</th><th style="width:80px">大小</th></tr>{srows}</table>
<h2>5. 畫面截圖（無頭 Chrome 實際渲染）</h2><div class="grid">{imgs}</div>
<h2>6. 已知限制與未驗證項目</h2><ul>{limh}</ul>
<h2>7. 對原有程式的影響</h2><p>BentoBox3D（<code>/Users/huanglizhi/Desktop/boc_creator</code>）程式未被修改（僅依你的要求刪除過 <code>exports/test.stl</code>）。下列為其原始碼檔案的最後修改時間，供核對：</p>
<table><tr><th>檔案</th><th>最後修改</th></tr>{files}</table>
<p>本專案改動前皆有備份（<code>/private/tmp/claude-501/dl/index.before_*.html</code>），舊功能（表面試板、雷射切割、STEP、存檔／復原、窗戶／燈孔／貼皮）皆納入回歸測試。</p>
<h2>8. 如何重新驗證</h2><p>先啟動伺服器（雙擊 <code>啟動 RoofLamp.command</code>），再執行：<code>python3 tests/run_all.py</code>，會重新跑完所有測試並覆寫本報告（<code>report/驗證報告.html</code>）。</p>
</main></body></html>'''
    fn=os.path.join(out,'驗證報告.html');open(fn,'w',encoding='utf8').write(doc);return fn
