#!/usr/bin/env python3
"""Compare CI logs between two directories.

Usage: python3 scripts/ci/compare_ci_logs.py before_dir after_dir

Prints per-file durations and counts of cache hits, cache misses, downloads and wheel builds,
and a short before->after delta summary.
"""
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta

TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?)")
DUR_RE = re.compile(r"duration=([0-9:.]+)")

PATTERNS = {
    'cache_restored': re.compile(r"Cache restored successfully", re.I),
    'cache_not_found': re.compile(r"Cache not found", re.I),
    'downloading': re.compile(r"Downloading\b", re.I),
    'building_wheel': re.compile(r"Building wheel for", re.I),
}


def parse_timestamps(text):
    ts = [m.group(1) for m in TS_RE.finditer(text)]
    datetimes = []
    for s in ts:
        s2 = s
        if s2.endswith('Z'):
            s2 = s2[:-1] + '+00:00'
        # normalize timezone like +0000 -> +00:00
        if re.match(r".*[+\-]\d{4}$", s2):
            s2 = s2[:-2] + ':' + s2[-2:]
        try:
            dt = datetime.fromisoformat(s2)
            datetimes.append(dt)
        except Exception:
            continue
    return datetimes


def parse_duration_from_line(text):
    m = DUR_RE.search(text)
    if not m:
        return None
    s = m.group(1)
    try:
        # format H:MM:SS(.micro)
        parts = s.split(':')
        if len(parts) == 3:
            h, m, rest = parts
            sec = float(rest)
            return timedelta(hours=int(h), minutes=int(m), seconds=sec)
    except Exception:
        return None
    return None


def analyze_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    d = {}
    # counts
    for k, rx in PATTERNS.items():
        d[k] = len(rx.findall(text))
    # duration: prefer explicit duration=... line
    dur = parse_duration_from_line(text)
    if dur is None:
        dts = parse_timestamps(text)
        if dts:
            dur = max(dts) - min(dts)
    d['duration'] = dur
    return d


def find_files(root: Path):
    files: dict[str, Path] = {}
    if not root.exists():
        return files
    for p in root.rglob('*.txt'):
        rel = p.relative_to(root)
        files[str(rel)] = p
    # include top-level text logs too
    for p in root.glob('*.txt'):
        rel = p.relative_to(root)
        files[str(rel)] = p
    return files


def fmt_td(td: timedelta):
    if td is None:
        return '-'
    total = int(td.total_seconds())
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h:
        return f"{h}h{m}m{s}s"
    if m:
        return f"{m}m{s}s"
    return f"{s}s"


def main(before_dir, after_dir):
    broot = Path(before_dir)
    aroot = Path(after_dir)
    bfiles = find_files(broot)
    afiles = find_files(aroot)
    all_keys = sorted(set(bfiles) | set(afiles))

    rows = []
    totals = {'before': {'duration': timedelta(0), 'count': 0}, 'after': {'duration': timedelta(0), 'count': 0}}

    print(f"Comparing\n  before: {broot}\n  after:  {aroot}\n")

    for key in all_keys:
        bpath = bfiles.get(key)
        apath = afiles.get(key)
        b = analyze_file(bpath) if bpath else None
        a = analyze_file(apath) if apath else None
        rows.append((key, b, a))

    # Print per-file summary
    print(f"{'file':70}  {'before':30}  {'after':30}  delta")
    print('-' * 140)
    for key, b, a in rows:
        bdur = b['duration'] if b else None
        adur = a['duration'] if a else None
        bvals = f"dur={fmt_td(bdur)} cr={b['cache_restored']} cnf={b['cache_not_found']} dl={b['downloading']} bw={b['building_wheel']}" if b else 'MISSING'
        avals = f"dur={fmt_td(adur)} cr={a['cache_restored']} cnf={a['cache_not_found']} dl={a['downloading']} bw={a['building_wheel']}" if a else 'MISSING'
        # delta simple: durations
        delta = None
        if bdur and adur:
            delta = adur - bdur
        elif bdur and not adur:
            delta = None
        elif adur and not bdur:
            delta = None

        dstr = fmt_td(delta) if isinstance(delta, timedelta) else '-'
        print(f"{key:70}  {bvals:30}  {avals:30}  {dstr}")

    # Aggregate totals for Windows files
    def agg(rows, which):
        total_dur = timedelta(0)
        count = 0
        for _, b, a in rows:
            item = b if which == 'before' else a
            if not item:
                continue
            if item['duration']:
                total_dur += item['duration']
            count += 1
        return total_dur, count

    btot, bcnt = agg(rows, 'before')
    atot, acnt = agg(rows, 'after')
    print('\nAggregate:')
    print(f"  before files: {bcnt}, total duration {fmt_td(btot)}")
    print(f"  after  files: {acnt}, total duration {fmt_td(atot)}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: compare_ci_logs.py before_dir after_dir')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
