#!/bin/sh
for i in *.ui; do
	pyuic5 "$i" -o "$(basename $i .ui).py"
done
