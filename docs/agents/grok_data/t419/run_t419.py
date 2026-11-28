import re
src=open('/workspace/t418/t418.py').read()
src=src.replace("W='/workspace/t418/'","W='/workspace/t419/'")
src=re.sub(r"FILES=\{[^\n]*\}","FILES={'A1_MG0.6':'t419_A1_mg06_deals.csv.gz'}",src,count=1)
src=re.sub(r"TESTER_DD=\{[^\n]*\}","TESTER_DD={'A1_MG0.6':14.17}",src,count=1)
src=src.replace("RESULTS_t418.md","RESULTS_t419_A1.md").replace("bars_t418_","bars_t419_")
exec(compile(src,'t418_unchanged_core','exec'))
