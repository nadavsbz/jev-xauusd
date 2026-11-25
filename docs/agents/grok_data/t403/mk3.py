
src=open('/workspace/t400/t400.py').read()
def rep(a,b):
    global src
    assert src.count(a)==1,(a,src.count(a)); src=src.replace(a,b)
rep("    base=100.0; eqc=np.full(n,np.nan); eql=np.full(n,np.nan)","    base=100.0; HW=100.0; eqc=np.full(n,np.nan); eql=np.full(n,np.nan)")
rep("A1[:]=0;A2[:]=0;AC[:]=0; Er=base","A1[:]=0;A2[:]=0;AC[:]=0; Er=base; HW=base")
rep("        fl=0.85*Er; h=np.where(Lw<=fl)[0]","        hwa=np.maximum(HW,np.maximum.accumulate(Cw)); fla=0.85*np.r_[HW,hwa[:-1]]; fl=float(fla[0]); h=np.where(Lw<=fla)[0]")
rep("            j=h[0]; eqc[idx[:j]]","            j=h[0]; fl=float(fla[j]); eqc[idx[:j]]")
rep("        else:\n            eqc[idx]=Cw; eql[idx]=Lw","        else:\n            eqc[idx]=Cw; eql[idx]=Lw; HW=float(hwa[-1])")
rep("    for days,arm in [(7,'A7'),(14,'B14')]:","    for days,arm in [(7,'T7')]:")
src=src.replace("'t400_","'t403_")
open('/workspace/t403/t403.py','w').write(src)
