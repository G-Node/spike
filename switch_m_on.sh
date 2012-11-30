#/bin/bash

echo "switching maintenance mode on"
su www-data -c "git pull"
service apache2 stop
a2dissite spike
a2ensite maintenance
service apache2 start
echo "done."
