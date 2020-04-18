#!/bin/bash

main()
{
clear

    read -p "Please Press 1 to Install or 2 to Uninstall --> : " INPUT
    if [[ "$INPUT" == 1 ]]; then
	          sudo cp ./shellMen /bin/
	          sudo chown root:root /bin/shellMen
	          sudo chmod +x /bin/shellMen
    elif [[ "$INPUT" == 2 ]]; then
          	sudo rm /bin/shellMen
    elif [[ "$INPUT" != 1 || "$INPUT" != 2 ]] ; then
           echo "Please type 1 or 2."
           sleep 2
           main
    fi
}
main
