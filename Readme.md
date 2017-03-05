# tracer-gui
## requirements
- graphviz
- python3
- pyqt5

## install
```sh
pip3 install git+https://github.com/trnila/tracer-gui.git
pip3 install PyQt5 # if doesnt work, install package python3-pyqt5
```

## usage

```sh
$ tracergui /tmp/report
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