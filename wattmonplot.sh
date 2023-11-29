#!/bin/bash
if [[ -z "$DISPLAY" ]]; then
    GNUPLOT_TERMINAL="dumb"
else
    GNUPLOT_TERMINAL="x11"
fi
python3 util/wattmon.py "$@" | tee wattmon.log | gnuplot -p -e "set terminal $GNUPLOT_TERMINAL; set nokey; plot '-' using 2 w l"

