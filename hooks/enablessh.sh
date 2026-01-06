

bash ./vbox.sh  pauseVNC

vncdo key right
vncdo key right

sleep 60;

vncdo key right
vncdo key right

vncdotool key super-alt-t
sleep 5;

while ! bash ./vbox.sh screenText haiku | grep "Welcome to the Haiku shell"; do
  vncdotool key super-alt-t
  sleep 3;
done


sleep 30;

./vbox.sh inputFile $VM_OS_NAME enablessh.local

sleep 30;


