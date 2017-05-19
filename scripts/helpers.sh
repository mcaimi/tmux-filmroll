#!/bin/bash
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $CURRENT_DIR/variables.sh

function get_tmux_option() {
  local option=${1}
  local value=$(tmux show-option -gqv "${option}")
  local default_value=$(tmux show-option -gqv "${option}_default")

  # check if option is set..
  if [ -z "$value" ]; then
    echo "$default_value"
  else
    echo $value
  fi
}

function set_tmux_option() {
  local option=${1}
  local value=${2}

  # set value
  tmux set-option -gq "$option" "$value"
}

