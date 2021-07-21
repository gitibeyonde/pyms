#!/bin/bash
### BEGIN INIT INFO
# Provides:          pyms.sh
# Required-Start:    $network
# Required-Stop:     $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: micro services
# Description:       
### END INIT INFO

#set -x

# PATH should only include /usr/* if it runs after the mountnfs.sh script
PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="micro services"
NAME=pyms
DAEMON=/srv/www/pyms/server.py
DAEMON_ARGS="--options args"
PIDFILE=/var/run/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME

# Exit if the package is not installed
[ -x "$DAEMON" ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.2-14) to ensure that this file is present
# and status_of_proc is working.
. /lib/lsb/init-functions

#


f_message(){
        echo "[+] $1"
}
# Carry out specific functions when asked to by the system
case "$1" in
        start)
                f_message "Starting pyms_server"
                python /srv/www/pyms/pyms_server.py
                f_message "pyms_server started"
        ;;
        stop)
                f_message "Stopping pyms_server"
                pid=`ps -ef | grep "pyms_server.py" | grep -v "grep" | awk '{print $2}' | head -n 1`
                [ "$pid" != "" ] && kill -9 $pid
                f_message "pyms_server stopped"
                ;;
        restart)
                f_message "Restarting daemon: pyms_server"
                pid=`ps -ef | grep "pyms_server.py" | grep -v "grep" | awk '{print $2}' | head -n 1`
                [ "$pid" != "" ] && kill -9 $pid
                python /srv/www/pyms/pyms_server.py
                f_message "Restarted daemon: pyms_server"
                ;;
        status)
                pid=`ps -ef | grep "pyms_server.py" | grep -v "grep" | awk '{print $2}' | head -n 1`
                if [ -n "$pid" ];
                then
                        f_message "pyms_server is running with pid ${pid}"
                        f_message "pyms_server was started with the following command line"
                        cat /proc/${pid}/cmdline ; echo ""
                else
                        f_message "Could not find pyms running"
                fi
                ;;
        *)
                f_message "Usage: $0 {start|stop|status|restart}"
                exit 1
                ;;
esac
exit 0
