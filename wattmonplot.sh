#!/bin/bash
if [[ -z "$DISPLAY" ]]; then
    GNUPLOT_TERMINAL="dumb"
else
    GNUPLOT_TERMINAL="wxt"
fi
python3 wattmon.py "$@" | tee wattmon.log | gnuplot -p -e "set terminal $GNUPLOT_TERMINAL; set nokey; plot '-' using 2 w l"

