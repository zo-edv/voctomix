#!/usr/bin/python3
import logging, socket
from gi.repository import GObject, Gst

from lib.config import Config

class AVPreviewOutput(object):
	log = logging.getLogger('AVPreviewOutput')

	name = None
	port = None
	caps = None

	boundSocket = None
	receiverPipeline = None

	currentConnections = []

	def __init__(self, channel, port):
		self.log = logging.getLogger('AVPreviewOutput['+channel+']')

		self.channel = channel
		self.port = port

		if Config.has_option('previews', 'videocaps'):
			vcaps_out = Config.get('previews', 'videocaps')
		else:
			vcaps_out = Config.get('mix', 'videocaps')

		pipeline = """
			interaudiosrc channel=audio_{channel} !
			{acaps} !
			queue !
			mux.

			intervideosrc channel=video_{channel} !
			{vcaps_in} !
			textoverlay halignment=left valignment=top ypad=75 text=AVPreviewOutput !
			timeoverlay halignment=left valignment=top ypad=75 xpad=400 !
			videorate !
			videoscale !
			{vcaps_out} !
			jpegenc !
			queue !
			mux.

			matroskamux
				name=mux
				streamable=true
				writing-app=Voctomix-AVPreviewOutput !

			multifdsink
				sync-method=next-keyframe
				name=fd
		""".format(
			channel=self.channel,
			acaps=Config.get('mix', 'audiocaps'),
			vcaps_in=Config.get('mix', 'videocaps'),
			vcaps_out=vcaps_out
		)

		self.log.debug('Launching Output-Pipeline:\n%s', pipeline)
		self.receiverPipeline = Gst.parse_launch(pipeline)
		self.receiverPipeline.set_state(Gst.State.PLAYING)

		self.log.debug('Binding to Output-Socket on [::]:%u', port)
		self.boundSocket = socket.socket(socket.AF_INET6)
		self.boundSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.boundSocket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)
		self.boundSocket.bind(('::', port))
		self.boundSocket.listen(1)

		self.log.debug('Setting GObject io-watch on Socket')
		GObject.io_add_watch(self.boundSocket, GObject.IO_IN, self.on_connect)

	def on_connect(self, sock, *args):
		conn, addr = sock.accept()
		self.log.info("Incomming Connection from %s", addr)

		def on_disconnect(multifdsink, fileno):
			if fileno == conn.fileno():
				self.log.debug('fd %u removed from multifdsink', fileno)

				self.currentConnections.remove(conn)
				self.log.info('Disconnected Receiver %s', addr)
				self.log.info('Now %u Receiver connected', len(self.currentConnections))

		self.log.debug('Adding fd %u to multifdsink', conn.fileno())
		fdsink = self.receiverPipeline.get_by_name('fd')
		fdsink.emit('add', conn.fileno())
		fdsink.connect('client-fd-removed', on_disconnect)

		self.currentConnections.append(conn)
		self.log.info('Now %u Receiver connected', len(self.currentConnections))

		return True