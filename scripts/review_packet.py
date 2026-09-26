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
    args=parser.parse_args()
    args.config = args.config or default_configs(ROOT)
    sources=required_sources(ROOT,load_config(ROOT,args.config));evidence=json.loads((ROOT/'data/evidence.json').read_text())
    lines=['# Jeff Does Doors review inventory', '', 'This is a generated review inventory, not an approval receipt.', '', f'Configuration: `{args.config}`', '', '| Source | Recorded approval | Current SHA-256 |', '| --- | --- | --- |']
    for name in sources:
        path=ROOT/name
        digest=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
        item=evidence.get(name,{})
        state='approved revision' if not approval_issues(ROOT,[name]) else 'needs review'
        lines.append(f'| `{name}` | {state} | `{digest}` |')
    args.output.write_text('\n'.join(lines)+'\n')
    print(f'Wrote {len(sources)} review items to {args.output}')
