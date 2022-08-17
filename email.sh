#!/bin/sh

MAILFILE=/email_test.txt
BRANCH=$(git branch --show-current)

echo "Subject: Aviso de Atualização Bot" > $MAILFILE
echo "To: augustobarthminecraft@gmail.com" >> $MAILFILE
echo "From: viradaoserver@gmail.com" >> $MAILFILE

echo "" >> $MAILFILE
echo "Git Pull executado em $(date "+%d/%m/%Y as %H:%M:%S")." >> $MAILFILE
echo "Bot foi atualizado na branch atual dele ($BRANCH). Serviço sendo reiniciado." >> $MAILFILE

cat $MAILFILE | ssmtp augustobarthminecraft@gmail.com
rm $MAILFILE
