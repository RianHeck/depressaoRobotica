#!/bin/sh

cd /root/bots/depressaoRobotica
git remote update
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    	echo "Git Pull para depressaoRobotica retornou igual. Nada alterado"
elif [ $LOCAL = $BASE ]; then
	echo "Atualizando depressaoRobotica"
	# wall <<< "foi"
	git pull --quiet
	bash /root/bots/depressaoRobotica/email.sh
	systemctl restart bot.service
elif [ $REMOTE = $BASE ]; then
   	 echo "Need to push"
else
    	echo "Diverged"
fi

