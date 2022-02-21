# marci_isis
This is a c shell script which is used for the processing of MRO-MARCI images. 
The software used for processing the images is ISIS (Integrated Software for Imagers and Spectrometers) from USGS. 

The workflow is described below:

1.First install ISIS as given here : https://github.com/USGS-Astrogeology/ISIS3/blob/dev/README.md#Installation

2.Download ISIS base data from the rsync server using the command:
```
cd $ISISDATA
rsync -azv --delete --partial isisdist.astrogeology.usgs.gov::isisdata/data/base .
```
and check that ISIS is working properly or not.

3.Download MRO SPICE data from the rsync server using the command:
```
cd $ISISDATA
rsync -azv --exclude='kernels' --delete --partial isisdist.astrogeology.usgs.gov::isisdata/data/mro .
```
No need to download the kernels as they are too big in size. So, it takes a lot of time to download and it also takes a lot of storage space. The kernels can be attached later through SPICE WEB service later.

4.Now, download the images from PDS Cartography and Imaging Sciences Node and save them in a local folder. One can use commands like the one below for downloading the images:
```
wget -nd https://pds-imaging.jpl.nasa.gov/data/mro/mars_reconnaissance_orbiter/marci/mrom_1319/data/N18_069571_0520_MA_00N200W.IMG
```

5.Download the shell script using the command:
```
wget https://raw.githubusercontent.com/Anirbanm0101/marci_isis/main/marci_all.csh
```
Now use the following command to allow the system to execute the shell script 
```
chmod +x marci_all.csh
```

6.Now, create a map template file like the one here (https://raw.githubusercontent.com/Anirbanm0101/marci_isis/main/sample.csh). A sample command line is:
```
printf "Group=Mapping\n TargetName=Mars\n LongitudeDomain=360\n ProjectionName=SimpleCylindrical\n CenterLongitude=0.0\n CenterLatitude=0.0\nEnd_Group\nEnd" > try1.map
```

7.Now, execute the shell script:
```
./marci_all.csh try1.map 0
```
The last argument 0 means during the execution, all files are kept but if it is 1, the old files are deleted. 
