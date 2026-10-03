#!/usr/bin/env python3
"""Create a review inventory. Does not approve content or contact anyone."""
import argparse,hashlib,json
from pathlib import Path
from content_policy import load_config,required_sources,approval_issues,default_configs
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default=None)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--pending-only',action='store_true',help='Omit sources whose recorded approval still matches')
    args=parser.parse_args()
    args.config = args.config or default_configs(ROOT)
    sources=required_sources(ROOT,load_config(ROOT,args.config));evidence=json.loads((ROOT/'data/evidence.json').read_text())
    lines=['# Jeff Does Doors review inventory', '', 'This inventory records hashes, not signatures or independent approval. Technical and business reviewers must inspect the relevant source and supporting evidence.', '', f'Configuration: `{args.config}`', '', '| Review area | Source | Recorded approval | Current SHA-256 |', '| --- | --- | --- | --- |']
    count=0
    for name in sources:
        path=ROOT/name
        digest=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
        item=evidence.get(name,{})
        state='approved revision' if not approval_issues(ROOT,[name]) else 'needs review'
        if args.pending_only and state == 'approved revision': continue
        area='Technical' if name.startswith(('assets/','layouts/','functions/','lib/','migrations/','scripts/','.github/','static/_')) or name == 'requirements.txt' else 'Business / content'
        lines.append(f'| {area} | `{name}` | {state} | `{digest}` |')
        count+=1
    args.output.write_text('\n'.join(lines)+'\n')
    print(f'Wrote {count} review items to {args.output}')
