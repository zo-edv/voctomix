import logging
from gi.repository import Gtk

from lib.config import Config
import lib.connection as Connection
import time


class RecordingToolbarController(object):

    def __init__(self, drawing_area, win, uibuilder):
        self.log = logging.getLogger('MiscToolbarController')
        self.recbtn = uibuilder.find_widget_recursive(drawing_area, 'rec_btn')
        self.recbtn.set_visible(Config.getboolean('misc', 'rec'))
        self.recbtn.connect('clicked', self.on_recbtn_clicked)

        self.timelabel = uibuilder.find_widget_recursive(drawing_area, 'rec_time')
        self.sizelabel = uibuilder.find_widget_recursive(drawing_area, 'rec_size')
        self.ratelabel = uibuilder.find_widget_recursive(drawing_area, 'rec_rate')

        self.timelabel.set_text("--:--:--.--")
        self.sizelabel.set_text("")
        self.ratelabel.set_text("")

        Connection.on('message', self.on_message)
        Connection.send('message get_rec')

    def on_message(self, args):
        if "recstatus" in args:
            recstatus = args.split(',')
            self.log.debug(recstatus)
            self.timelabel.set_markup("<span foreground='red'>{}</span>".format(str(recstatus[1])))
            self.ratelabel.set_label(str(recstatus[2]))
            self.sizelabel.set_label(str(recstatus[3]))
            self.recbtn.set_label("Recording")
        elif args == "rec_stop":
            self.recbtn.set_label("Record")
            self.timelabel.set_markup("<span foreground='black'>--:--:--.--</span>")

    def on_recbtn_clicked(self, btn):
        self.log.info('rec-button clicked')
        Connection.send('message', 'rec')

