# Transcript video editor skill

A portable Codex skill for selecting transcript words and sentences in chat, then producing a new video with those passages removed. The skill creates a timestamped transcript locally, shows a conversation widget on supported Codex hosts, and renders requested cuts with FFmpeg. It can fall back to a plain transcript and ordinary chat.

## Install

Copy the `transcript-video-editor` directory into the skills directory used by your Codex installation (typically `~/.codex/skills/`), then start a new session. Installation paths and inline-widget support depend on your host. Ask Codex to use `$transcript-video-editor` on a local video.

## Requirements

- Python 3.10 or newer and the `faster-whisper` Python package
- FFmpeg and FFprobe on `PATH`
- A compatible faster-whisper model cached locally, or permission for its initial download
- For interactive selection inside chat: a host that renders the inline visualization format and provides `window.openai.sendFollowUpMessage`. The skill falls back to text when those capabilities are absent.

Example request: “Use $transcript-video-editor to let me remove sentences and filler words from my video in this chat.”

All transcription and editing can run locally. The transcript is machine-generated and may omit or mis-time words and fillers. Preview your source and review the result; the in-chat selector itself does not play video. The cut script re-encodes an MP4 with one video and one audio stream, and does not create a native editing-project timeline. It never overwrites the source.

## Repository contents

`transcript-video-editor/` is the installable skill; it contains the `SKILL.md` instructions, Python scripts and the self-contained in-chat template. No media or transcripts are included.
