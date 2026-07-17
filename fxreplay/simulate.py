from __future__ import annotations
import json, math, os, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('MARKET_DATA_DIR',ROOT/'marketdata'))/'XAUUSD_csv'
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
BE=[.5,1,1.5,2,3,5]
PLEVEL=[2,3,5]
PFRAC=[.20,.25,.50]

def trades():
 d=pd.read_csv(ROOT/'analytics.csv')
 for c in ['dateStart','dateEnd']: d[c]=pd.to_datetime(d[c],errors='coerce')
 for c in ['entryPrice','initalSL','avgClosePrice','avgRiskReward','rPnL']:
  d[c]=pd.to_numeric(d[c],errors='coerce')
 d['side']=d.side.astype(str).str.lower(); d['status']=d.status.astype(str).str.lower()
 return d.sort_values('dateStart').reset_index(drop=True)

def needed(d):
 s=set()
 for r in d.itertuples():
  a=r.dateStart; b=r.dateEnd if pd.notna(r.dateEnd) else a
  if pd.isna(a): continue
  for x in pd.date_range(a.normalize()-pd.Timedelta(days=2),b.normalize()+pd.Timedelta(days=2)): s.add(x.strftime('%Y-%m-%d'))
 return sorted(s)

def parse_time(s):
 if pd.api.types.is_numeric_dtype(s):
  x=pd.to_numeric(s,errors='coerce'); m=x.dropna().median()
  u='ns' if m>1e17 else 'us' if m>1e14 else 'ms' if m>1e11 else 's'
  return pd.to_datetime(x,unit=u,errors='coerce',utc=True)
 return pd.to_datetime(s,errors='coerce',utc=True,format='mixed')

def load_one(p):
 q=pd.read_csv(p,compression='gzip',low_memory=False)
 if len(q.columns)==1: q=pd.read_csv(p,compression='gzip',sep=None,engine='python')
 cols=list(q.columns); norm={str(c).strip().lower().replace(' ','_'):c for c in cols}
 tc=next((norm[x] for x in ['timestamp','time','datetime','date_time','date','datetime_utc','utc_time'] if x in norm),None)
 if tc is None:
  for c in cols[:3]:
   if pd.to_datetime(q[c].head(100),errors='coerce',utc=True).notna().mean()>.8: tc=c; break
 if tc is None: raise ValueError(f'no time column: {cols}')
 bc=next((norm[x] for x in ['bid','bid_price','bidprice'] if x in norm),None)
 ac=next((norm[x] for x in ['ask','ask_price','askprice'] if x in norm),None)
 pc=next((norm[x] for x in ['price','mid','close','last','last_price'] if x in norm),None)
 if not (bc and ac) and pc is None:
  nums=[]
  for c in cols:
   if c==tc: continue
   if pd.to_numeric(q[c].head(200),errors='coerce').notna().mean()>.8: nums.append(c)
  if len(nums)>=2: bc,ac=nums[:2]
  elif nums: pc=nums[0]
  else: raise ValueError(f'no price columns: {cols}')
 z=pd.DataFrame({'ts':parse_time(q[tc])})
 if bc and ac:
  z['bid']=pd.to_numeric(q[bc],errors='coerce'); z['ask']=pd.to_numeric(q[ac],errors='coerce')
 else:
  z['bid']=z['ask']=pd.to_numeric(q[pc],errors='coerce')
 z['mid']=(z.bid+z.ask)/2
 return z.dropna(subset=['ts','mid']), {'time':str(tc),'bid':str(bc),'ask':str(ac),'price':str(pc)}

def load_ticks(ds):
 fs=[]; diag=[]; schema=None
 for day in ds:
  p=DATA/f'{day}.csv.gz'
  if not p.exists(): continue
  try:
   z,s=load_one(p); fs.append(z); schema=schema or s; diag.append({'file':p.name,'rows':len(z),'min':str(z.ts.min()),'max':str(z.ts.max())})
  except Exception as e: diag.append({'file':p.name,'error':repr(e)})
 if not fs: raise RuntimeError(f'No readable tick files in {DATA}')
 x=pd.concat(fs,ignore_index=True).sort_values('ts').drop_duplicates(['ts','bid','ask']).reset_index(drop=True)
 pd.DataFrame(diag).to_csv(OUT/'parse_diagnostics.csv',index=False)
 return x,schema

def nearest(ticks,tt,col='mid'):
 a=pd.DataFrame({'target':pd.to_datetime(tt,utc=True)}); a['_i']=np.arange(len(a)); a=a.sort_values('target')
 b=pd.merge_asof(a,ticks[['ts',col]],left_on='target',right_on='ts',direction='nearest',tolerance=pd.Timedelta('10min'))
 return b.sort_values('_i')[col].to_numpy()

def calibrate(t,d):
 c=[]; s=d[(d.status=='closed')&d.dateStart.notna()&d.entryPrice.notna()]
 for scale in [1,.1,.01,.001,10,100]:
  for off in range(-720,721,30):
   tt=s.dateStart.dt.tz_localize('UTC')-pd.to_timedelta(off,unit='m'); v=nearest(t,tt)*scale; ok=np.isfinite(v)
   if ok.sum()<max(5,len(s)//2): continue
   e=np.abs(v[ok]-s.loc[ok,'entryPrice'].to_numpy())
   c.append((np.median(e),np.mean(e),np.quantile(e,.95),scale,off,int(ok.sum())))
 if not c: raise RuntimeError('calibration failed')
 c.sort(); best=c[0]
 pd.DataFrame(c,columns=['median_error','mean_error','p95_error','scale','offset_minutes','n']).to_csv(OUT/'calibration.csv',index=False)
 return best[3],best[4]

def path(row,ticks,off):
 st=pd.Timestamp(row.dateStart,tz='UTC')-pd.Timedelta(minutes=off); en=pd.Timestamp(row.dateEnd,tz='UTC')-pd.Timedelta(minutes=off)
 lo=ticks.ts.searchsorted(st-pd.Timedelta(minutes=2)); hi=ticks.ts.searchsorted(en+pd.Timedelta(seconds=1),'right'); w=ticks.iloc[lo:hi]
 if w.empty:return {'matched':False,'reason':'no ticks'}
 j=(w.ts-st).abs().to_numpy().argmin(); e=w.iloc[j]
 if abs(e.ts-st)>pd.Timedelta('10min'):return {'matched':False,'reason':'entry too far'}
 col='bid' if row.side=='buy' else 'ask'; p=w.iloc[j:][col].dropna().to_numpy(float)
 if not len(p): return {'matched':False,'reason':'no prices'}
 risk=abs(row.entryPrice-row.initalSL)
 if not np.isfinite(risk) or risk<=0:return {'matched':False,'reason':'bad risk'}
 sr=(p-p[0])/risk if row.side=='buy' else (p[0]-p)/risk
 rec={'matched':True,'mfe_r':float(sr.max()),'mae_r':float(sr.min()),'tick_count':len(p)}
 actual=row.avgClosePrice-row.entryPrice; rec['exit_move_error_r']=float(abs((p[-1]-p[0])-actual)/risk) if np.isfinite(actual) else np.nan
 for lv in BE:
  hit=np.flatnonzero(sr>=lv)
  rec[f'hit_{lv:g}r']=bool(len(hit))
  rec[f'return_{lv:g}r']=bool(len(hit) and np.any(sr[hit[0]+1:]<=0))
 return rec

def met(v):
 v=np.asarray(v,float); pos=v[v>.05]; neg=v[v<-.05]; be=v[(v>=-.05)&(v<=.05)]
 cu=np.cumsum(v); pk=np.maximum.accumulate(np.r_[0,cu])[1:]; dd=pk-cu
 return dict(trades=len(v),total_r=v.sum(),expectancy_r=v.mean(),profit_factor=pos.sum()/(-neg.sum()) if len(neg) else np.nan,wins=len(pos),losses=len(neg),breakevens=len(be),win_rate_pct=len(pos)/len(v)*100,average_winner_r=pos.mean() if len(pos) else np.nan,average_loser_r=neg.mean() if len(neg) else np.nan,max_drawdown_r=dd.max() if len(dd) else 0)

def scenarios(det,high=False):
 w=det[det.matched].copy()
 if high:w=w[w.high_confidence]
 base=w.baseline_r.to_numpy(float); dic={'Baseline':base}
 for lv in BE: dic[f'BE@{lv:g}R']=np.where(w[f'hit_{lv:g}r']&w[f'return_{lv:g}r'],0,base)
 for lv in PLEVEL:
  hit=w[f'hit_{lv:g}r'].to_numpy(bool); ret=w[f'return_{lv:g}r'].to_numpy(bool)
  for f in PFRAC:
   n=int(f*100); dic[f'Partial {n}%@{lv:g}R']=np.where(hit,f*lv+(1-f)*base,base)
   dic[f'Partial {n}%@{lv:g}R + BE']=np.where(hit,f*lv+(1-f)*np.where(ret,0,base),base)
 rows=[]
 for n,v in dic.items():
  m=met(v); m.update(scenario=n,losses_saved=int(((base<-.05)&(v>=-.05)).sum()),baseline_winners_reduced=int(((base>.05)&(v<base-1e-9)).sum()),baseline_winners_to_be_or_loss=int(((base>.05)&(v<=.05)).sum())) ; rows.append(m)
 return pd.DataFrame(rows)

def main():
 d=trades(); ticks,schema=load_ticks(needed(d)); scale,off=calibrate(ticks,d); ticks[['bid','ask','mid']]*=scale
 rows=[]
 for _,r in d[d.status=='closed'].iterrows():
  x=path(r,ticks,off); z={'id':r.id,'dateStart':r.dateStart,'dateEnd':r.dateEnd,'side':r.side,'entryPrice':r.entryPrice,'initialSL':r.initalSL,'avgClosePrice':r.avgClosePrice,'baseline_r':r.avgRiskReward,'rPnL':r.rPnL}; z.update(x)
  for lv in BE:
   z.setdefault(f'hit_{lv:g}r',False);z.setdefault(f'return_{lv:g}r',False)
  rows.append(z)
 det=pd.DataFrame(rows); det['high_confidence']=det.matched&det.exit_move_error_r.fillna(np.inf).le(.5)
 a=scenarios(det);a['sample']='all_matched';h=scenarios(det,True);h['sample']='high_confidence_le_0.5R';summ=pd.concat([a,h],ignore_index=True)
 dist=[]
 for name,w in [('losses',det[det.matched&(det.baseline_r<-.05)]),('winners',det[det.matched&(det.baseline_r>.05)]),('all',det[det.matched])]:
  for lv in BE:dist.append({'group':name,'rr_level':lv,'trades':len(w),'reached':int(w[f'hit_{lv:g}r'].sum()),'returned_to_entry':int(w[f'return_{lv:g}r'].sum())})
 det.to_csv(OUT/'trade_path_analysis.csv',index=False);summ.to_csv(OUT/'scenario_summary.csv',index=False);pd.DataFrame(dist).to_csv(OUT/'mfe_distribution.csv',index=False)
 q={'source':'noobshow/ai-trading-simulator-data','source_commit':'1e60ef7b92fd79aa467d66b85a5ca590cea9e59e','schema':schema,'scale':scale,'fxreplay_offset_minutes_from_utc':off,'ticks':len(ticks),'closed_trades':len(det),'matched':int(det.matched.sum()),'high_confidence':int(det.high_confidence.sum()),'median_exit_error_r':float(det.loc[det.matched,'exit_move_error_r'].median()),'p90_exit_error_r':float(det.loc[det.matched,'exit_move_error_r'].quantile(.9))}
 (OUT/'data_quality.json').write_text(json.dumps(q,indent=2))
 rank=a.sort_values(['expectancy_r','max_drawdown_r'],ascending=[False,True]); lines=[]
 for _,r in rank.head(15).iterrows():lines.append(f"| {r.scenario} | {r.total_r:.2f} | {r.expectancy_r:.3f} | {r.profit_factor:.2f} | {r.max_drawdown_r:.2f} | {int(r.losses_saved)} | {int(r.baseline_winners_reduced)} |")
 report=f'''# FX Replay management simulation\n\nMatched **{q['matched']} / {q['closed_trades']}** closed trades. High-confidence exit-path matches: **{q['high_confidence']}**. Calibrated timestamp offset: **UTC{off/60:+g}**. Median exit-path mismatch: **{q['median_exit_error_r']:.3f}R**.\n\nPublic XAUUSD tick data is not the exact OANDA feed. Each path is anchored to the public quote at the FX Replay entry time, and low-confidence mismatches are flagged.\n\n| Scenario | Total R | Expectancy | Profit factor | Max DD | Losses saved | Winners reduced |\n|---|---:|---:|---:|---:|---:|---:|\n{chr(10).join(lines)}\n\nTested BE at **0.5R, 1R, 1.5R, 2R, 3R and 5R**. Tested **20%, 25% and 50% partials at 2R, 3R and 5R**, both partial-only and partial-plus-BE. Full results are in `scenario_summary.csv`; trade-level paths are in `trade_path_analysis.csv`.\n'''
 (OUT/'REPORT.md').write_text(report);print(report)
if __name__=='__main__':main()
