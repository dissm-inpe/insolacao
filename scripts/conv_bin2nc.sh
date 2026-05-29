#!/bin/bash -x

  # This function returns the file size.
  function getsize() {
    if [ "$#" -ne 1 ]; then
      echo 'Inform the file path'
      exit 1
    fi

    # Get the given file path
    path=$1

    # Extract file size
    size=`ls -l ${path} | awk '{print int($5/1024)}'`

    # Return the value
    echo ${size}
  }

  # Get parameters
  timestamp=$1
  bin_id=$2

  # Separate date and time
  year=`echo ${timestamp} | cut -c 1-4`
  month=`echo ${timestamp} | cut -c 5-6`

  # Configure source id
  src_id="1116"
  prod_id="XXXX"

  if [ ${bin_id} == "7051" ]; then

    input_file="/dados/goes/goes19_produtos/rad_solar/insol_diaria_bin/${year}/${month}/S11167051_${timestamp}.bin"
    output_dir="/dados/goes/goes19_produtos/rad_solar/insol_diaria_nc/${year}/${month}"
    prod_id="7067"

  elif [ ${bin_id} == "7053" ]; then
   
    input_file="/dados/goes/goes19_produtos/rad_solar/insol_quinzenal_bin/${year}/${month}/S11167053_${timestamp}.bin"
    output_dir="/dados/goes/goes19_produtos/rad_solar/insol_quinzenal_nc/${year}/${month}"
    prod_id="7068"

  elif [ ${bin_id} == "7055" ]; then
   
    input_file="/dados/goes/goes19_produtos/rad_solar/insol_mensal_bin/${year}/${month}/S11167055_${timestamp}.bin"
    output_dir="/dados/goes/goes19_produtos/rad_solar/insol_mensal_nc/${year}/${month}"
    prod_id="7069"

  fi

  if [ ${prod_id} == "XXXX" ]; then

    echo "Codigo ${bin_id} não configurado"
    exit 1

  else

    output_file="S${src_id}${prod_id}_${timestamp}.nc"

    mkdir -p ${output_dir}

    ##------Geographic area of regular grid-------##
    beginLat="-50.0"
    endLat="21.96" #"22.0"
    beginLon="-100.0"
    endLon="-28.04" #"-28.0"

    ##--Resolution---##
    degree="0.04"

    ### Convert binary to netcdf
    tmp_dir="/dados/goes/goes19/rad_solar/tmp"; mkdir -p ${tmp_dir}

    rm -f ${tmp_dir}/${output_file}
    /usr/bin/gmt xyz2grd ${input_file} -ZTLh -R${beginLon}/${endLon}/${beginLat}/${endLat} -I${degree} -G${tmp_dir}/${output_file}

    rm -f ${output_dir}/${output_file}
    /usr/bin/gdalwarp ${tmp_dir}/${output_file} -of netCDF -co compress=DEFLATE -co FORMAT=NC4C ${output_dir}/${output_file}

    rm -f ${tmp_dir}/${output_file}

    ### Create BDI log ##
    bdi_log_dir="/dados/bdi"

    size=`getsize ${output_dir}/${output_file}`
    touch ${bdi_log_dir}/${prod_id}_${timestamp}_${size}

  fi

exit 0
