# PREREG §7/§8/§8א gate table on DEV (primary: conservative entry bar, s=2+1c). No new trials.
import json
from cfg import P
R=json.load(open(P+'results_t318A_DEV.json'))
out={}
for n,r in R.items():
    s=r['s2']; yrs=s['years']
    g=dict(G0=r['G0']['p']<0.05, G1=s['R_net']>0, G2=s['monthly_geo']>=0.035, G3=s['MDD']<=0.25, G4=s['sharpe']>=1.5,
           G5='UNKNOWN (N_company unknown; DSR N=6 upper bound %.3f)'%r['G5_DSR_N6_upperbound'],
           G6=r['G6']['holm_pass'], G7=s['worst_day']>=-0.05, G8=s['median_hold']>=15, G9=r['s3']['R_net']>0,
           G10=(s['H1_total']>0 and s['H2_total']>0 and sum(v>0 for v in yrs.values())>=4))
    out[n]=dict(gates=g, PASS=all(v is True for k,v in g.items() if k!='G5') and False, variant_kill=s['R_net']<=0,
                gross_R=r['gross']['R_gross'], G0_p=r['G0']['p'])
a0=R['OR5m_a10']['gross']['R_gross']
fam=dict(kill_8a_A0_gross_le0=a0<=0, kill_8_G0_fail_all6=all(R[n]['G0']['p']>=0.10 for n in R),
         note='PASS requires G5 (DSR with company N), which is UNKNOWN -> no variant can be declared PASS from this run.')
json.dump(dict(variants=out,family=fam),open(P+'gates_DEV.json','w'),indent=1,default=str)
print('GATES',json.dumps(fam),flush=True)
for n,o in out.items(): print(n,{k:v for k,v in o['gates'].items()},'gross_R=%.3f'%o['gross_R'],flush=True)
print('ALL_DONE',flush=True)
