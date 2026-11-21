"""Archive old MT5 tester HTML reports from C:\\MT5_JEV_TEST into data/archive/<name>.zip (user request 17.11.2026: free disk).
Kept in place: reports modified in the last 3 days, and the ones the live pipeline reads (in2dst_t_*, demo_cmp_*, bull47*).
The zip is verified (CRC of every member + byte sizes) before a delete list is written; this script deletes nothing.
Writes data/archive/<name>.delete.txt with the archived paths (for the user's own delete command).
Restore one report: py -3.12 -c "import zipfile;zipfile.ZipFile('data/archive/<name>.zip').extract('<file>.htm', r'C:\\MT5_JEV_TEST')"
Usage: py -3.12 tools/archive_test_reports.py"""
import os, time, zipfile, glob
ROOT = r"C:\MT5_JEV_TEST"; OUT = "data/archive"; name = "mt5_test_reports_20261117"
keep_prefix = ("in2dst_t_", "demo_cmp_", "bull47")
cut = time.time() - 3 * 86400
files = [f for f in glob.glob(os.path.join(ROOT, "*.htm"))
         if os.path.getmtime(f) < cut and not os.path.basename(f).startswith(keep_prefix)]
zp = os.path.join(OUT, name + ".zip")
with zipfile.ZipFile(zp, "a", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    have = set(z.namelist())
    for i, f in enumerate(files):
        b = os.path.basename(f)
        if b not in have:
            z.write(f, b)
        if i % 200 == 0: print(f"{i}/{len(files)}", flush=True)
with zipfile.ZipFile(zp) as z:
    bad = z.testzip()
    info = {i.filename: i.file_size for i in z.infolist()}
ok = [f for f in files if info.get(os.path.basename(f)) == os.path.getsize(f)]
if bad: raise SystemExit(f"zip check failed at {bad}")
open(os.path.join(OUT, name + ".delete.txt"), "w", encoding="utf-8").write("\n".join(ok) + "\n")
src = sum(os.path.getsize(f) for f in ok) / 2**30
print(f"archived {len(ok)}/{len(files)} reports, {src:.1f} GB -> zip {os.path.getsize(zp) / 2**30:.2f} GB; delete list written")
