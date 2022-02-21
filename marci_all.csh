#!/bin/csh

if ($#argv != 2) then
   echo "Usage: $0 maptemplate.map [0|1]"
   echo "0 = keep all files as you go"
   echo "1 = delete old files as you go"
   goto done
endif


set map=$1
set del=$2

##marci2isis 
foreach i (*.IMG)
  set base=`basename $i .IMG`
  set new="$base.cub"
  echo marci2isis "from=$i to=$new"
  marci2isis from=$i to=$new
  if (-e $new && $del) then
    /bin/rm $i
  endif
end

##spiceinit
foreach i (*.cub)
  #echo spiceinit "from=$i"
  echo spiceinit "from=$i web=true"
  #spiceinit from=$i
  spiceinit from=$i web=true
end

##marcical 
foreach i (*.cub)
  set base=`basename $i .cub`
  set new="$base.lev1.cub"
  echo marcical "from=$i to=$new"
  marcical from=$i to=$new
  if (-e $new && $del) then
    /bin/rm $i
  endif
end


 
##cam2map
foreach i (*.lev1.cub)
  set base=`basename $i .lev1.cub`
  set new="$base.lev2.cub"
  echo cam2map "from=$i map=$map to=$new"
  cam2map from=$i map=$map to=$new
  if (-e $new && $del) then
    /bin/rm $i
  endif
end

##isis2std
foreach i (*.lev2.cub)
  set base=`basename $i .lev2.cub`
  set new="$base.png"
  #Only send base name to isis2std to help with extension issue
  echo isis2std "from=$i to=$base"
  isis2std from=$i to=$base
#  if (-e $new && $del) then
#    /bin/rm $i
#  endif
end

echo complete $0

done:
  exit 0

