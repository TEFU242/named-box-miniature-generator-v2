#!/usr/bin/env python3
"""由 index.html 產生「測試副本」_harness.html（注入 harness.js），不會改動 index.html。"""
import os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(root,'index.html'),encoding='utf8').read()
h=open(os.path.join(root,'tests','harness.js'),encoding='utf8').read()
i=s.rindex('</script>')
open(os.path.join(root,'_harness.html'),'w',encoding='utf8').write(s[:i]+h+'\n'+s[i:])
print('ok')
