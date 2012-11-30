#/bin/bash

echo "switching maintenance mode off"
service apache2 stop
a2dissite maintenance
a2ensite spike
service apache2 start
echo "done."
