#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later

case "${DJSDEV_UNIT:-djs1000}" in
    djs1000) APP_NAME=EP113_Main_R; DEFAULT_HOME="$HOME/djs"; SP16=0 ;;
    sp16)    APP_NAME=EP085_Main_R; DEFAULT_HOME="$HOME/sp16"; SP16=1 ;;
    *) echo "Unknown emulator unit: $DJSDEV_UNIT (use djs1000 or sp16)" >&2; exit 1 ;;
esac
APP="/root/pdj/$APP_NAME"
APP_PATTERN="(/root/pdj/|[.]/)$APP_NAME"
DJS="${DJS_HOME:-$DEFAULT_HOME}"
