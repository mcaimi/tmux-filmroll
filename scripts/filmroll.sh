#!/bin/bash
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $CURRENT_DIR/variables.sh
source $CURRENT_DIR/helpers.sh

function prepare_filmroll_cmd() {
  FILMROLL_SOURCE_PATH="$(get_tmux_option "$filmroll_source_path")"
  FILMROLL_DESTINATION_PATH="$(get_tmux_option "$filmroll_destination_path")"

  COUNTCMD="$GOPATH/bin/cameraimport count -s $FILMROLL_SOURCE_PATH"
  SHELLCMD="$GOPATH/bin/cameraimport import -s $FILMROLL_SOURCE_PATH -d $FILMROLL_DESTINATION_PATH"

  # confirmation message
  MSG=$($COUNTCMD)

  # execute script
  tmux confirm-before -p "> $MSG. Do you want to proceed [y/n]?" "split-window -h -p 30 $SHELLCMD"
}

function main() {
  prepare_filmroll_cmd
}

main

