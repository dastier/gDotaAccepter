#!/usr/bin/env bash





DotaWindowActivate() {

	xdotool search --desktop 0 --maxdepth 1 --class dota windowactivate --sync sleep 1
	verboseLog "DotA window is focused and ready"
}


RunFindMatchButton() {

	eval "$(xdotool getmouselocation --shell)"
	# prevWindow=$(xdotool getactivewindow)
	DotaWindowActivate
	sleep 2
	xdotool mousemove --sync -polar 123 1220 sleep 1 mousedown 1 sleep 1 mouseup 1 sleep 1 mousedown 1 sleep 1 mouseup 1
	# xdotool sleep 1 windowactivate "$prevWindow"
	# xdotool mousemove --sync "$X" "$Y"
}



FocusDotaWindow() {

	DotaWindowActivate

	[ "$(xdotool getwindowfocus getwindowname)" != "Dota 2" ] && FocusDotaWindow
	[ "$GAMEISREADY" == true ] && xdotool key Return && verboseLog "Match Accepted!"  # press Accept button
}


activateOnPick() {

	# if [ -f "$PID" ]; then
		# verboseLog "already running ($PID exists)"
		rm -f "$PID"
		# exit 0
	# else
		[ ! -f "$PID" ] && writePID
	# fi
	

	verboseLog "Waiting for dbus events..."
	echo "Waiting for dbus events..."

	# dbus-monitor "eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'"
	dbus-monitor "eavesdrop=true, interface='$interface', member='$member'" |
	while read -r line; do
		if [ "$line" == 'string "The hero picking phase has begun"' ]; then
			verboseLog "Picking!"
			echo "Picking!"
			FocusDotaWindow
		elif [ "$line" == 'string "Your game is ready"' ]; then
			verboseLog "Your game is ready!"
			echo "Your game is ready!"
			GAMEISREADY=true  # this flag is needed only for FocusDotaWindow() to press Return
			prevWindow=$(xdotool getactivewindow)
			FocusDotaWindow
			xdotool sleep 1 windowactivate --sync "$prevWindow"
			GAMEISREADY=false

		elif [ "$line" == 'string "The game is unpausing..."' ]; then
			verboseLog "The game is unpausing..."
			# prevWindow=$(xdotool getactivewindow)
			FocusDotaWindow
			#xdotool sleep 1 windowactivate --sync "$prevWindow"
		
		elif [ "$line" == 'string "exit monitor"' ]; then
			verboseLog "EXIT signal received from dbus"
			break
		fi
	done
}





writePID() {

	[ -f "$PID" ] && rm "$PID"
	echo $$ > "$PID"
}

exitMonitor() {

	dbus-send --type=method_call --dest='org.freedesktop.Notifications' \
	/org/freedesktop/Notifications org.freedesktop.Notifications.Notify \
	string:'exit monitor' \
	array:string:''
	cleanUp
}

cleanUp() {

	verboseLog "clean up!"
	killall --quiet dbus-monitor
	#pkill -09 -f "bash.*dotaAccepter.sh -p"
	rm -f "$PID"
	exit $?
}


isDotaRunning() {

	# check if Dota2 is running
	if xdotool search --maxdepth 1 --class dota2 > /dev/null; then
		verboseLog "Dota2 is running"
		return 0
	else
		verboseLog "Dota2 is not running!"
		return 1
	fi
}

function verboseLog () {
    if [[ $verbose -eq 1 ]]; then
        echo "$@"
    fi
}




# main execution starts here:
# requires libnotify-bin package
interface=org.freedesktop.Notifications
member=Notify
PID=/var/run/user/$UID/dotaAcc.pid
verbose=0

isDotaRunning

trap cleanUp SIGTERM


while getopts "rpvsc" opt; do
	case $opt in
		v)
			verbose=1
			;;
		r)
			RunFindMatchButton
			exit 0
			;;
		p)
			activateOnPick
			exit 0
			;;
		s)
			exitMonitor
			# cleanUp
			;;
		c)
			isDotaRunning
			exit 0
			;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			;;
	esac
done

exit 0
