#!/bin/sh
ffmpeg -y -nostdin \
	-f decklink -video_input hdmi \
	-i 'DeckLink Mini Recorder (2)@15' \
	-c:v rawvideo -c:a pcm_s16le \
	-vf yadif,framerate=25,scale=1920x1080 \
	-pix_fmt yuv420p \
	-f matroska \
	tcp://localhost:10001
