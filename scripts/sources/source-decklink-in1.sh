#!/bin/sh
ffmpeg -y -nostdin -f decklink -video_input hdmi -i 'DeckLink Mini Recorder (1)@10' \
	-c:v rawvideo -c:a pcm_s16le \
	-pix_fmt yuv420p \
	-vf yadif,framerate=fps=25 \
	-f matroska \
	tcp://localhost:10000
