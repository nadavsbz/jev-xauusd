import re
src=open('/workspace/t418/t418.py').read()
src=src.replace("W='/workspace/t418/'","W='/workspace/t420/'")
src=re.sub(r"FILES=\{[^\n]*\}","FILES={'A4_MG0.5_drift':'t420_A4_deals.csv.gz'}",src,count=1)
src=re.sub(r"TESTER_DD=\{[^\n]*\}","TESTER_DD={'A4_MG0.5_drift':'n/a (not reported by Claude)'}",src,count=1)
src=src.replace("RESULTS_t418.md","RESULTS_t420_A4.md").replace("bars_t418_","bars_t420_")
exec(compile(src,'t418_unchanged_core','exec'))
