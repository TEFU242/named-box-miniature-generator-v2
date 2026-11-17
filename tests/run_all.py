#!/usr/bin/env python3
"""一鍵驗證：自動化功能測試 + STEP 後端測試 + 場景截圖 → 產生 report/驗證報告.html
前置：本機伺服器 `python3 server.py 8090` 已在執行；Chrome 已安裝。"""
import os,re,sys,json,html,subprocess,base64,datetime,urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T=os.path.join(ROOT,'tests');OUT=os.path.join(ROOT,'report');SH=os.path.join(OUT,'shots')
os.makedirs(SH,exist_ok=True)
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE='http://localhost:8090'
GL=['--headless=new','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--hide-scrollbars']
def build(name,inject):
    s=open(os.path.join(ROOT,'index.html'),encoding='utf8').read();h=open(os.path.join(T,inject),encoding='utf8').read();i=s.rindex('</script>')
    open(os.path.join(ROOT,name),'w',encoding='utf8').write(s[:i]+h+'\n'+s[i:])
def run_tests():
    build('_harness.html','harness.js')
    r=subprocess.run([CH,*GL,'--virtual-time-budget=120000','--dump-dom',BASE+'/_harness.html'],capture_output=True,timeout=500,text=True)
    m=re.search(r'<pre id="RESULT">(.*?)</pre>',r.stdout,re.S)
    if not m: raise SystemExit('測試頁沒有輸出結果')
    return json.loads(html.unescape(m.group(1)))
def step_tests(states):
    sys.path.insert(0,ROOT)
    out=[]
    py=os.path.join(ROOT,'.venv','bin','python')
    chk=os.path.join(T,'step_check.py')
    for i,st in enumerate(states):
        try:
            req=urllib.request.Request(BASE+'/step',data=st.encode('utf8'),method='POST')
            data=urllib.request.urlopen(req,timeout=180).read()
            fn=os.path.join('/tmp',f'rooflamp_step_{i}.step');open(fn,'wb').write(data)
            r=subprocess.run([py,chk,fn],capture_output=True,text=True,timeout=120)
            out.append((True,r.stdout.strip() or r.stderr.strip()[-200:],len(data)))
        except Exception as e:
            out.append((False,'錯誤：'+str(e)[:200],0))
    return out
SCENES=[('1','步驟① 樓層：預設（明亮主題）'),('2','步驟② 屋頂：複折＋陶瓦＋屋簷外伸＋屋脊蓋＋煙囪＋分離拉開'),('8','步驟② 屋頂：雙折（穀倉）＋瀝青瓦'),('3','步驟③ 窗戶：3D＋正視圖並排、多選與對齊'),('4','步驟⑤ 貼皮：磚紋＋舊化裂痕、石板屋頂、框選區域'),('5','步驟⑥ 室內：自由起訖的牆與門（平面圖）'),('6','步驟⑦ 輸出：雷射零件排版'),('7','暗色主題＋四面斜＋金屬屋面'),('9','步驟⑥ 樓梯：三層樓、兩組樓梯與拱形大門（平面圖）'),('10','步驟③ 大門：雙開門＋窗框（3D＋正視圖並排）'),('11','屋頂分離拉開：雙斜屋頂（解析式幾何，無破面）'),('12','步驟① 周邊小型建築：美式組合（附屬車庫＋前門廊＋後工具棚）'),('13','步驟⑥ 2F 圖層：L 型鏤空樓梯（扶手）與接續的 U 型樓梯'),('14','步驟⑤ 材質預覽縮圖（含舊化／比例即時更新）'),('15','步驟③ 吸附參考線、間距標註與參考物件（紫色）'),('17','步驟⑥ 三層樓：每層各一張獨立頂視圖（並排）'),('20','步驟⑦ 戶外樓梯：外掛 U 型鐵梯＋入口台階（3D）'),('21','步驟⑦ 室內 L 型梯：扇形踏階＋斜板＋玻璃欄板（X 光）'),('22','步驟⑦ 旋轉梯：中柱＋扇形踏階＋欄杆（X 光）'),('23','步驟⑧ 地板：錯位磚（平面＋3D）'),('24','步驟④ 法式玻璃雙扇門＋氣窗＋側窗＋斜面雨遮＋門框；後牆穀倉滑門'),('25','步驟④ 上下分開門與其他三面牆的玻璃推拉門'),('28','開啟時詢問場景比例（1:64 為推薦，可跳過）'),('26','步驟④ 美式大鐵捲門（1:64，捲起 30%）'),('27','步驟④ 標準鐵捲門：導軌、捲片、底桿、捲門盒（1:64）'),('19','步驟③ 窗戶玻璃片＋窗格條＋窗框、雙開木門＋喇叭鎖（外加零件）'),('18','X 光開啟：外殼半透明，室內牆與樓梯以暖色凸顯')]
def shots():
    res=[]
    build('_scene.html','scenes.js')
    for sid,title in SCENES:
        fn=os.path.join(SH,f'scene{sid}.png')
        try:
            subprocess.run([CH,*GL,'--window-size=1400,860','--virtual-time-budget=12000',f'--screenshot={fn}',BASE+'/_scene.html#'+sid],capture_output=True,timeout=240)
        except Exception as e: pass
        res.append((sid,title,fn if os.path.exists(fn) else None))
    return res
if __name__=='__main__':
    d=run_tests();R=d['results']
    st=step_tests(d['steps'])
    sh=shots()
    import report_gen
    report_gen.make(ROOT,R,st,sh)
    for n in ('_harness.html','_scene.html','_test.html','_t.html'):
        try: os.remove(os.path.join(ROOT,n))
        except OSError: pass
    print('tests',len(R),'fail',sum(1 for x in R if not x['ok']),'warn',sum(1 for x in R if x['warn']),'step',[s[0] for s in st])
