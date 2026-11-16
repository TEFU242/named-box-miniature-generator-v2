import sys
from build123d import import_step
s=import_step(sys.argv[1]);bb=s.bounding_box()
print(f"有效={s.is_valid} 實體數={len(s.solids())} 體積={s.volume:.0f}mm³ 外形={bb.size.X:.1f}×{bb.size.Y:.1f}×{bb.size.Z:.1f}")
