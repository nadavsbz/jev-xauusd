import re
src=open('/workspace/t418/t418.py').read()
src=src.replace("W='/workspace/t418/'","W='/workspace/t422/'")
src=re.sub(r"FILES=\{[^\n]*\}","FILES={'B1_brake':'t422_B1_deals.csv.gz'}",src,count=1)
src=re.sub(r"TESTER_DD=\{[^\n]*\}","TESTER_DD={'B1_brake':'n/a (not reported)'}",src,count=1)
src=src.replace("RESULTS_t418.md","RESULTS_t422_B1_core.md").replace("bars_t418_","bars_t422_")
exec(compile(src,'t418_unchanged_core','exec'))
