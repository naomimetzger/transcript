#!/usr/bin/env python3
"""Cut specified time intervals from a video without changing the source."""
import argparse, json, math, shutil, subprocess, sys
from pathlib import Path

def fail(message): sys.exit(message)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('cuts',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    if not a.input.is_file() or not a.cuts.is_file():p.error('Input video and cuts JSON must exist')
    if a.input.resolve()==a.output.resolve():p.error('Output must not overwrite the input')
    if a.output.exists():p.error('Output already exists; choose a new file name')
    if a.output.suffix.lower()!='.mp4':p.error('Choose an .mp4 output file')
    for tool in ('ffmpeg','ffprobe'):
        if not shutil.which(tool):fail(f'{tool} is required on PATH')
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(a.input)],capture_output=True,text=True,check=True)
    meta=json.loads(probe.stdout);streams=meta['streams']
    if sum(s['codec_type']=='video' for s in streams)!=1 or sum(s['codec_type']=='audio' for s in streams)!=1:fail('This script needs exactly one video and one audio stream.')
    duration=float(meta['format']['duration']);data=json.loads(a.cuts.read_text(encoding='utf-8'));cuts=[]
    for c in data['cuts']:
        start,end=float(c['start']),float(c['end'])
        if not math.isfinite(start) or not math.isfinite(end) or start<0 or start>=end or end>duration+0.03:fail(f'Invalid cut: {c}')
        cuts.append((start,min(end,duration)))
    if not cuts:fail('No cuts specified')
    cuts.sort();merged=[]
    for x,y in cuts:
        if merged and x<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],y)
        else:merged.append([x,y])
    keep=[];start=0.0
    for x,y in merged:
        if x-start>=0.04:keep.append((start,x))
        start=y
    if duration-start>=0.04:keep.append((start,duration))
    if not keep:fail('Cuts remove the entire video')
    if len(keep)>300:fail('Too many separate cuts; split the edit into batches')
    filters=[]
    for i,(x,y) in enumerate(keep):
        filters.append(f'[0:v:0]trim=start={x:.6f}:end={y:.6f},setpts=PTS-STARTPTS[v{i}]')
        filters.append(f'[0:a:0]atrim=start={x:.6f}:end={y:.6f},asetpts=PTS-STARTPTS[a{i}]')
    inputs=''.join(f'[v{i}][a{i}]' for i in range(len(keep)))
    filters.append(f'{inputs}concat=n={len(keep)}:v=1:a=1[v][a]')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-nostdin','-n','-v','error','-i',str(a.input),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',str(a.output)]
    result=subprocess.run(cmd)
    if result.returncode:fail('FFmpeg failed. An incomplete output may need to be removed; the source was not modified.')
    print(f'Created {a.output}; {len(merged)} merged cut(s).')
if __name__=='__main__':main()
