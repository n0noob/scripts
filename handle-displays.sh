#!/bin/bash

# Utility function
containsElement () {
  local e match="$1"
  shift
  for e; do [[ "$e" == "$match" ]] && return 0; done
  return 1
}

# Redetect monitor configuration
xrandr --auto

connected_displays=($(xrandr | grep ' connected' | cut -d " " -f 1))
    
dual_disp=false
    
# Check is dual displays are connected
if [[ ${#connected_displays[@]} -gt 2 ]]; then
    dual_disp=true
fi
    
# Initialize few variables
pos=0
primary="--primary"
    
# If HDMI-A-0 is connected 
containsElement "HDMI-A-0" "${connected_displays[@]}"
if [[ $? -eq 0 ]]; then
    xrandr --output HDMI-A-0 ${primary} --mode 1920x1080 --pos ${pos}x0 --rotate normal
    primary=""
    pos=$((pos + 1920))
fi
    
# If DP-1-0 is connected 
containsElement "DP-1-0" "${connected_displays[@]}"
if [[ $? -eq 0 ]]; then
    xrandr --output DP-1-0 ${primary} --mode 1920x1080 --pos ${pos}x0 --rotate normal
    primary=""
    pos=$((pos + 1920))
fi
    
# If eDP is connected   
containsElement "eDP" "${connected_displays[@]}"  
if [[ $? -eq 0 ]]; then
    if [[ "$dual_disp" == true ]]; then
    xrandr --output eDP --off
    else 
    xrandr --output eDP ${primary} --mode 1920x1080 --pos ${pos}x0 --rotate normal
    fi
    primary=""
    pos=$((pos + 1920))
fi

~/.config/polybar/launch.sh
