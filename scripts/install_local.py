#!/usr/bin/env python3
"""Copy this skill locally without overwriting an existing installation."""
import argparse
from pathlib import Path
import shutil

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=Path.home()/'.agents/skills/lafiteskill')
    args=parser.parse_args()
    source=Path(__file__).resolve().parents[1]
    target=args.target.expanduser().resolve()
    if target==source or target.is_relative_to(source):
        parser.error('Target must be outside the source directory')
    if target.exists():
        parser.error('Target already exists; review or back it up before replacing it')
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('.git','__pycache__','.DS_Store','input','output','.env','.env.*'))
    print('Installed: '+str(target))
    print('Restart or reload skills in your agent if needed. No image generation was invoked.')

if __name__=='__main__':
    main()
