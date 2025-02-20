#!/bin/bash

URL1="file:///home/pi/menuboard/remote_control_service/technical_break/technical_break.html"
URL2="file:///home/pi/menuboard/remote_control_service/technical_break/technical_break.html"

export DISPLAY=:0

if xrandr --current | grep -q "^HDMI-1 connected"; then
	HDMI1=True
else
	HDMI1=False
fi

if xrandr --current | grep -q "^HDMI-2 connected"; then
	HDMI2=True
else
	HDMI2=False
fi

if [ "$HDMI1" = "True" ] && [ "$HDMI2" = "True" ]; then
	chromium-browser --new-window --incognito --user-data-dir="$HOME/menuboard/browser_data/browser-1" --window-position="0,0" --start-fullscreen --kiosk --noerrdialogs --disable-session-crashed-bubble --disable-component-update --disable-translate --disable-infobars --hide-scrollbars --disable-features=TranslateUI --disk-cache-dir=/dev/null --app="$URL1" --remote-debugging-port=8989 --remote-allow-origins='*' &
	chromium-browser --new-window --incognito --user-data-dir="$HOME/menuboard/browser_data/browser-2" --window-position="3840,0" --start-fullscreen --kiosk --noerrdialogs --disable-session-crashed-bubble --disable-component-update --disable-translate --disable-infobars --hide-scrollbars --disable-features=TranslateUI --disk-cache-dir=/dev/null --app="$URL2" --remote-debugging-port=8990 --remote-allow-origins='*' &
elif [ "$HDMI1" = "True" ] || [ "$HDMI2" = "True" ]; then
	chromium-browser --new-window --incognito --user-data-dir="$HOME/menuboard/browser_data/browser-1" --window-position="0,0" --start-fullscreen --kiosk --noerrdialogs --disable-session-crashed-bubble --disable-component-update --disable-translate --disable-infobars --hide-scrollbars --disable-features=TranslateUI --disk-cache-dir=/dev/null --app="$URL1" --remote-debugging-port=8989 --remote-allow-origins='*' &
else
	echo "Screen not found"
fi

/usr/bin/python3 /home/pi/menuboard/remote_control_service/app.py "$HDMI1" "$HDMI2"

exit;
