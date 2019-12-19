#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2019, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

import logging
from json import loads

import ipykernel.kernelbase
import jupyter_client.session as session
from ipykernel.comm import CommManager

SESSION_KEY = b'ipywidgets_bokeh'

class WebsocketStream(object):
    def __init__(self, session):
        self.session = session

class BytesWrap(object):
    def __init__(self, bytes):
        self.bytes = bytes

class StreamWrapper(object):
    def __init__(self, channel):
        self.channel = channel

    def flush(self, arg):
        pass

class SessionWebsocket(session.Session):

    def send(self, stream, msg_or_type, content=None, parent=None, ident=None, buffers=None, track=False, header=None, metadata=None):
        msg = self.msg(msg_or_type, content=content, parent=parent, header=header, metadata=metadata)
        msg['channel'] = stream.channel

        #from bokeh.io import curdoc
        #from bokeh.document.events import MessageSentEvent
        #doc = curdoc()
        #event = MessageSentEvent(doc, msg)
        #doc._trigger_on_change(event)

        items = list(self.parent._bk_mapping.items())
        if len(items) == 0:
            return

        doc = items[0][1].document
        if doc is not None:
            from bokeh.document.events import MessageSentEvent
            event = MessageSentEvent(doc, msg)
            doc._trigger_on_change(event)

class BokehKernel(ipykernel.kernelbase.Kernel):
    implementation = 'ipython'
    implementation_version = '0.1'
    banner = 'banner'

    def __init__(self):
        super(BokehKernel, self).__init__()
        self._bk_mapping = {}

        self.session = SessionWebsocket(parent=self, key=SESSION_KEY)
        self.stream = self.iopub_socket = WebsocketStream(self.session)

        self.iopub_socket.channel = 'iopub'
        self.session.stream = self.iopub_socket
        self.comm_manager = CommManager(parent=self, kernel=self)
        self.shell = None
        self.log = logging.getLogger('fake')

        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)

    def _bk_register(self, model, widget):
        self._bk_mapping[widget] = model

kernel = BokehKernel.instance()

def receive_message(data):
    msg = loads(data)
    msg_serialized = kernel.session.serialize(msg)
    if msg['channel'] == 'shell':
        stream = StreamWrapper(msg['channel'])
        msg_list = [ BytesWrap(k) for k in msg_serialized ]
        kernel.dispatch_shell(stream, msg_list)
