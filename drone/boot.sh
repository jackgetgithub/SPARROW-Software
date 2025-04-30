#!/bin/bash

/usr/bin/screen -dmS proxy /bin/bash -c './proxy_no_relay.sh'

/usr/bin/screen -dmS send /bin/bash -c './send.sh'
