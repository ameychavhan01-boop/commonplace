#!/bin/bash
# usage: pv.sh "ids" "times"  -> previews + one contact sheet per scene
S=/tmp/claude-0/-home-user-commonplace/2a93e3af-c23e-527f-844d-2cefa1c641ec/scratchpad/build
cd /home/user/commonplace/videos/ta1
python3 render.py $S preview $1 --t=$2 2>&1 | grep -A12 ERROR
cd $S/preview
for s in $1; do
  files=""; for tt in ${2//,/ }; do [ -s ${s}_$tt.png ] && files="$files ${s}_$tt.png"; done
  python3 /home/user/commonplace/videos/ta1/tools/sheet.py ../sheet_$s.png $files
done
