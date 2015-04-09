#!/bin/bash

main(){
clear
read -p "Please Press 1 to Install or 2 to Uninstall --> : " INPUT
if [ "$INPUT" == 1 ]; then
	sudo cp shellMen.sh /bin/
	sudo chown root:root /bin/shellMen.sh 
	sudo chmod +x /bin/shellMen.sh 
elif [ "$INPUT" == 2 ]; then
	sudo rm /bin/shellMen.sh
elif [ "$INPUT" !== 1 ] || [ "$INPUT" !== 2 ] ; then
echo "Please type 1 or 2."
main
fi	
}
main
