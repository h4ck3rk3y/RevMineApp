kill -9 `ps -ef | grep cyclone.py | grep -v grep | awk '{print $2}'`
python cyclone.py &
disown
