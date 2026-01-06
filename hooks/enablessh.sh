

bash ./vbox.sh  pauseVNC

vncdo key right
vncdo key right

sleep 60;

vncdo key right
vncdo key right

vncdotool key super-alt-t
sleep 2;

vncdotool key super-alt-t

sleep 30;

./vbox.sh inputFile $VM_OS_NAME enablessh.local

sleep 30;


