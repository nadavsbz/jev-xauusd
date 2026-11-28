import re
src=open('/workspace/t418/t418.py').read()
src=src.replace("W='/workspace/t418/'","W='/workspace/t419/'")
src=re.sub(r"FILES=\{[^\n]*\}","FILES={'A2_VB20':'t419_A2_vb20_deals.csv.gz'}",src,count=1)
src=re.sub(r"TESTER_DD=\{[^\n]*\}","TESTER_DD={'A2_VB20':float('nan')}",src,count=1)
src=src.replace("RESULTS_t418.md","RESULTS_t419_A2.md").replace("bars_t418_","bars_t419_")
exec(compile(src,'t418_unchanged_core','exec'))
