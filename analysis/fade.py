#!/usr/bin/env python3
"""How fast do Nikolauslauf runners start? Measured from the official 10 km split and finish time.

For every finisher: the share of the finish time reached at 10 km is compared with the share expected at
even effort on this course (gradient rule after Daniels, +3.3 % / −1.8 % per 1 %, gain capped at −8 %).
A runner who is ahead of that at 10 km slowed down later. The fade is expressed like the "Einbruch" dial
on the pacing page: a linear drift over the distance, given as seconds the 2nd half was slower than at
even effort.

Model: piece pace = base × f(g) × (1 + k·(x/D − ½))  →  share at 10 km  p(k) = (A + k·B) / (C + k·E),
solved exactly for k; fade [s] = T·k/4.  Years 2021–2025 (course since 2021).
Input: anonymised times (no names) `nll_results_anon.json`; course profile `course.json`.
usage: fade.py RESULTS.json COURSE.json OUT.json
"""
import json, sys, statistics as st

UP, DOWN, CAP = 3.3, 1.8, -0.08
MAT = 10000.0  # 10 km mat at 10.0 km (own official splits vs GPS put it at 10.006 / 10.024 / 10.023 km, i.e. within ~20 m)
f = lambda g: 1 + UP * g if g > 0 else 1 + DOWN * max(g, CAP)


def main():
    res, course, out = sys.argv[1], sys.argv[2], sys.argv[3]
    c = json.load(open(course)); d, alt = c["d"], c["alt"]; D = d[-1]
    A = B = C = E = 0.0
    for i in range(len(d) - 1):
        L = d[i + 1] - d[i]; g = (alt[i + 1] - alt[i]) / L; w = L * f(g); x = ((d[i] + d[i + 1]) / 2) / D - 0.5
        C += w; E += w * x
        frac = max(0.0, min(1.0, (MAT - d[i]) / L))   # part of this 20 m piece before the mat
        A += w * frac; B += w * x * frac
    p0 = A / C
    rows = [r for r in json.load(open(res)) if 2021 <= r["year"] <= 2025 and r["t10"] and r["finish"] and 3600 < r["finish"] < 4 * 3600]
    runners = []
    for r in rows:
        p = r["t10"] / r["finish"]
        if not 0.30 < p < 0.60: continue                   # timing glitches
        # seconds ahead at 10 km of an even-effort run with the same finish time (positive = started too fast)
        runners.append({"year": r["year"], "sex": r.get("sex", "?"), "finish": r["finish"], "p": round(p, 4), "ahead_s": round(r["finish"] * p0 - r["t10"], 1)})
    groups = [(3600, 5100, "< 1:25"), (5100, 5700, "1:25–1:35"), (5700, 6300, "1:35–1:45"), (6300, 6900, "1:45–1:55"), (6900, 7500, "1:55–2:05"), (7500, 14400, "> 2:05")]
    summ = []
    for lo, hi, lab in groups:
        v = sorted(x["ahead_s"] for x in runners if lo <= x["finish"] < hi)
        if len(v) < 20: continue
        q = lambda a: v[int(a * (len(v) - 1))]
        summ.append({"group": lab, "n": len(v), "median": q(.5), "p25": q(.25), "p75": q(.75), "share_neg": round(sum(1 for x in v if x < 0) / len(v), 3)})  # share_neg: started slower than even
    by_sex = []  # same per group and sex (2022–2025: 2021 has no sex column)
    for lo, hi, lab in groups:
        for sx in ("M", "W"):
            v = sorted(x["ahead_s"] for x in runners if lo <= x["finish"] < hi and x["sex"] == sx)
            if len(v) < 5: continue                 # shown with its n; small groups are marked on the page
            q = lambda a: v[int(a * (len(v) - 1))]
            by_sex.append({"group": lab, "sex": sx, "n": len(v), "median": q(.5), "p25": q(.25), "p75": q(.75),
                           "share_neg": round(sum(1 for x in v if x < 0) / len(v), 3)})
    hist = []  # per finish-time group, 15 s bins, clipped to −180…+300 s
    for lo, hi, lab in groups:
        h = {}
        for x in runners:
            if lo <= x["finish"] < hi:
                b = max(-180, min(300, int(x["ahead_s"] // 15) * 15)); h[b] = h.get(b, 0) + 1
        hist += [{"group": lab, "bin": b, "n": n} for b, n in sorted(h.items())]
    json.dump({"p_even": round(p0, 4), "n": len(runners), "summary": summ, "by_sex": by_sex, "hist": hist,
               "years": sorted({x["year"] for x in runners})}, open(out, "w"), indent=1)
    print(f"Anteil bei gleichmäßiger Anstrengung nach 10 km: {p0:.4f} · {len(runners)} Läufer 2021–2025")
    print(f"{'Zielzeit':10s} {'n':>5} {'Median zu schnell':>18} {'25–75 %':>14} {'langsamer':>10}")
    for s in summ:
        print(f"{s['group']:10s} {s['n']:5d} {s['median']:+7.0f}s {s['p25']:+6.0f}…{s['p75']:+5.0f}s {s['share_neg']:9.0%}")


if __name__ == "__main__":
    main()
