#!/bin/sh
ffmpeg \
	-y -nostdin \
	-i tcp://localhost:11000 -i tcp://localhost:13000 -i tcp://localhost:13001 \
	-ac 2 -channel_layout 2 -aspect 16:9 \
	-map 0:v -c:v:0 mpeg2video -pix_fmt:v:0 yuv422p -qscale:v:0 2 -qmin:v:0 2 -qmax:v:0 7 -keyint_min 0 -bf:0 0 -g:0 0 -intra:0 -maxrate:0 90M \
	-map 1:v -c:v:1 mpeg2video -pix_fmt:v:1 yuv422p -qscale:v:1 2 -qmin:v:1 2 -qmax:v:1 7 -keyint_min 0 -bf:1 0 -g:1 0 -intra:1 -maxrate:1 90M \
	-map 2:v -c:v:2 mpeg2video -pix_fmt:v:2 yuv422p -qscale:v:2 2 -qmin:v:2 2 -qmax:v:2 7 -keyint_min 0 -bf:2 0 -g:2 0 -intra:2 -maxrate:2 90M \
	-map 0:a -c:a:0 mp2 -b:a:0 192k -ac:a:0 2 -ar:a:0 48000 \
	-map 1:a -c:a:1 mp2 -b:a:1 192k -ac:a:1 2 -ar:a:1 48000 \
	-flags +global_header -flags +ilme+ildct \
	-f mpegts output.ts
