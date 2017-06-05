#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $CURRENT_DIR/scripts/variables.sh
source $CURRENT_DIR/scripts/helpers.sh

function set_filmroll_invoke_bindings() {
  # bind RTFM command
  tmux bind-key f run-shell "$CURRENT_DIR/filmroll.sh"
}

function main() {
  # set default variables
  set_tmux_option "@filmroll_source_path_default" "$filmroll_source_path_default"
  set_tmux_option "@filmroll_destination_path_default" "$filmroll_destination_path_default"

  set_filmroll_invoke_bindings
}

main

