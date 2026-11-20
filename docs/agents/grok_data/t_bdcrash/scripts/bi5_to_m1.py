# Decode Dukascopy bi5 tick hours (public datafeed) into 1-min bid/ask OHLC + tick counts. UTC.
import lzma,struct,os,sys,datetime as dt
import pandas as pd
def decode(path, base, point):
    raw=open(path,'rb').read()
    if len(raw)<=109: return None
    d=lzma.decompress(raw); n=len(d)//20
    rows=[struct.unpack('>3I2f',d[i*20:(i+1)*20]) for i in range(n)]
    df=pd.DataFrame(rows,columns=['ms','ask','bid','av','bv'])
    df['t']=base+pd.to_timedelta(df.ms,unit='ms'); df['ask']/=point; df['bid']/=point
    return df
if __name__=='__main__':
    ins=sys.argv[1]; point=float(sys.argv[2]); day=pd.Timestamp(sys.argv[3],tz='UTC')
    out=[]
    for h in range(24):
        p=f'data/ticks/{ins}/{h:02d}h.bi5'
        if not os.path.exists(p): continue
        df=decode(p, day+pd.Timedelta(hours=h), point)
        if df is not None: out.append(df)
    t=pd.concat(out).set_index('t')
    t.to_csv(f'data/{ins}_ticks_{sys.argv[3]}.csv.gz')
    m=t.bid.resample('1min').ohlc(); m['ask_close']=t.ask.resample('1min').last(); m['ticks']=t.bid.resample('1min').count()
    m=m.dropna(subset=['open']); m.to_csv(f'data/{ins}_m1_{sys.argv[3]}.csv')
    print(ins, len(t),'ticks', m.index.min(), m.index.max(), 'hours:', sorted(set(m.index.hour)))
