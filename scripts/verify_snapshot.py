"""Fail closed on changed, invalid or mismatched deployment evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def verify(directory, write_manifest=False):
    directory=Path(directory)
    results=json.loads((directory/'final_results.json').read_text())
    shots=pd.read_parquet(directory/'shots_scored.parquet')
    if shots.empty or shots[['model_p','made','point_value','season','contest_id']].isna().any().any():
        raise ValueError('Empty snapshot or missing required values')
    if not shots.model_p.between(0,1).all() or not shots.made.isin([0,1]).all() or not shots.point_value.isin([2,3]).all():
        raise ValueError('Invalid shot outcome, probability or point value')
    for metric in results['model_comparison']:
        if metric['model']==results['selected_model']:
            f=shots.loc[shots.season==metric['season']]
            if len(f)!=metric['n']:
                raise ValueError('Evaluation count does not match snapshot')
            brier=((f.model_p-f.made)**2).mean()
            if abs(brier-metric['brier'])>1e-6:
                raise ValueError('Snapshot probabilities do not reproduce saved Brier score')
    required=['shots_scored.parquet','final_results.json']
    if (directory/'team_context.parquet').exists():
        context=pd.read_parquet(directory/'team_context.parquet')
        if context.duplicated(['season','team_name','designation']).any() or not (context.possessions>0).all():
            raise ValueError('Invalid team context')
        required+=['team_context.parquet','context_manifest.json']
    manifest={'run_id':results['run_id'],'rows':len(shots),'files':{name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in required}}
    path=directory/'snapshot_manifest.json'
    if write_manifest:
        path.write_text(json.dumps(manifest,indent=2)+'\n')
    elif not path.exists() or json.loads(path.read_text())!=manifest:
        raise ValueError('Snapshot integrity manifest missing or mismatched')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',type=Path,default=ROOT/'data/app')
    parser.add_argument('--write-manifest',action='store_true')
    args=parser.parse_args()
    result=verify(args.directory,args.write_manifest)
    print(f"Verified {result['rows']:,} rows · {result['run_id']}")
