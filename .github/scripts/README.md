# GitHub Workflow Scripts

To avoid using `wget` in the CI process, the bash shell scripts to start the
IOCs have been copied from the vendor repository:

https://github.com/prjemian/epics-docker

starter script | subdirectory
--- | ---
`start_xxx.sh` | `v1.1/n5_custom_synApps/start_xxx.sh`
`start_adsim.sh` | `v1.1/n6_custom_areaDetector/start_adsim.sh`
