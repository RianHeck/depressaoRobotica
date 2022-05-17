#!/bin/bash

cd /root/bots/depressaoRobotica
git pull --quiet
success=$?

if [[ $success -eq 0 ]];
then
	echo "Git Pull para depressaoRobotica retornou igual. Nada alterado"
else
	echo "Atualizando depressaoRobotica"
	# wall <<< "foi"	
	bash /root/bots/depressaoRobotica/email.sh
	systemctl restart bot.service
fi
