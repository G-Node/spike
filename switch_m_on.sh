#/bin/bash

echo "switching maintenance mode on"
service apache2 stop
a2dissite spike
a2ensite maintenance
service apache2 start
echo "done."
