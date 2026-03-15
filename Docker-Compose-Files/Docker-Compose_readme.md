## Using docker compose for instalation.
More information can be found at [Yacht.sh](https://yacht.sh/docs/Installation/Install)

For Windows please use the docker-compose_windows.yml file. 

For MacOS, Linux, WSL2 host please use docker-compose-MAC-LINUX.yml

Because WSL2 is a Linux VM, your need to add your user account in WSL2 as a member of the docker security group. 
Follow instructions below

Notes for installing Docker and Yacht on WSL2 platform under Windows
If you’re running under WSL2 inside Windows, because of the difference in how permissions are handled. Your essentially inside of a Linux machine accessing a Windows file system. You will need to run after installation before adding the Yacht container:
```
$ sudo usermod -aG docker $USER
```
Additional information about this can be found in the [Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/)