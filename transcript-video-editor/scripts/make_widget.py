#!/usr/bin/env python3
"""Build an inline transcript selector from a word-timed transcript."""
import argparse, json, math
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('transcript', type=Path);p.add_argument('--video',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();data=json.loads(a.transcript.read_text(encoding='utf-8'))
    if not a.video.is_file():p.error('The source video does not exist')
    if a.output.resolve() in {a.video.resolve(),a.transcript.resolve()}:p.error('Output must not replace the source or transcript')
    if Path(data.get('source','')).resolve()!=a.video.resolve():p.error('Transcript source does not match --video')
    words=[]
    for segment in data['segments']:
        for w in segment.get('words',[]):
            start,end=float(w['start']),float(w['end']);text=str(w['word']).strip()
            if text and math.isfinite(start) and math.isfinite(end) and 0<=start<end:words.append({'s':round(start,3),'e':round(end,3),'t':text})
    if not words:p.error('No valid word timestamps')
    payload={'source':str(a.video.resolve()),'words':words}
    template=(Path(__file__).resolve().parent.parent/'assets/editor.html').read_text(encoding='utf-8')
    encoded=json.dumps(payload,ensure_ascii=True,separators=(',',':')).replace('</','<\\/')
    html=template.replace('__PAYLOAD__',encoded)
    if len(html.encode())>1000000:p.error('Transcript exceeds the host widget size limit; split into smaller parts')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html,encoding='utf-8');print(f'Widget written to {a.output}')
if __name__=='__main__':main()
