#!/usr/bin/env python3
"""Generate an approximate word-timed transcript of a local video."""
import argparse, json, sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--model', default='base')
    p.add_argument('--language', default=None)
    p.add_argument('--local-only', action='store_true')
    args = p.parse_args()
    if not args.input.is_file(): p.error('Input video does not exist')
    if args.input.resolve() == args.output.resolve(): p.error('Output cannot be the input file')
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit('Install faster-whisper in the permitted Python environment before transcribing.')
    model = WhisperModel(args.model, device='cpu', compute_type='int8', local_files_only=args.local_only)
    segments, info = model.transcribe(str(args.input), language=args.language, word_timestamps=True, beam_size=5)
    rows = []
    for s in segments:
        rows.append({'start': round(s.start, 3), 'end': round(s.end, 3), 'text': s.text,
                     'words': [{'start': round(w.start, 3), 'end': round(w.end, 3), 'word': w.word} for w in (s.words or [])]})
    if not any(s['words'] for s in rows): sys.exit('No word-timed speech found; use another transcription method or inspect the media.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'version': 1, 'source': str(args.input.resolve()), 'language': info.language, 'segments': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Transcribed {len(rows)} segments to {args.output}')
if __name__ == '__main__': main()
