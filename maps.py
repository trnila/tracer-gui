import signal

signals = dict([(getattr(signal, i), i) for i in dir(signal) if i.startswith('SIG')])
