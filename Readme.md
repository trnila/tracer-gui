# tracer-gui
## install
```sh
$ git clone https://github.com/trnila/tracer-gui.git
$ cd tracer-gui
$ virtualenv gui
$ source ./gui/bin/activate
$ pip install -r requirements.txt

```

## usage

```sh
$ ./gui/bin/python app.py /tmp/report
```

## configuration
Configuration file is stored in *~/.tracerguirc*. 
It is plain python.
Example configuration is available in *tracerguirc.example* in this repository.
Your configuration extends configuration set in *tracergui.settings*.

### Editor
#### Add new editor
EDITOR['emacs'] = 'emacs %path%'
#### Disable default editor
del EDITOR['vim']