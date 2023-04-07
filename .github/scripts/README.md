# GitHub Workflow Scripts

To avoid using `wget` in the CI process, the bash shell script to manage the
IOCs has been copied from the vendor repository:

```bash
cd ~/bin
wget https://raw.githubusercontent.com/prjemian/epics-docker/main/resources/iocmgr.sh
chmod +x iocmgr.sh
iocmgr.sh start GP gp
iocmgr.sh start ADSIM ad
```
