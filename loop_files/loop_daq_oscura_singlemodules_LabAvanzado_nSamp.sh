#!/bin/bash
##########
#
# Laboratorio Avanzado
# Script para adquisicion de imagenes variando numero de muestras por pixel
#
# Elaboro:
# Mauricio Martinez
# Alexis Aguilar
#
##########
#rutine in progress: 
rutine="Changing NSAMP"

imgFOLDER=`dirname $BASH_SOURCE`/images/LabAvanzado/2025/Images/nSamp_test/ ###END WITH / please!!!!
runname=m-009_microchip_vtested_T_160_    					# Tipo de detector
lockfilename=lockfile
clearseq=sequencers/sequencer_microchip_clear_brenda.xml

initscript=init/init_ICN_LabAvanado.sh

#-----Clear without image-----
doClear(){
	if (( $CLEAR ))
	then
	lta sseq $clearseq
	lta NROW 1000000000	#max 32-bit	#>70 sec for NROW 1e5, so NROW 1e9 should run for >7 days
	lta startseq
	sleep $CLEAR
	lta readoff
	fi
	}

#-----Img settings-----
doSettings(){
	lta NROW $rows
	lta NCOL $cols
	lta NSAMP $nsmpls
	lta EXPOSURE $expo
	lta NBINROW $binrow
	lta NBINCOL $bincol
	}


#----------To start----------
touch $lockfilename							# Variable lockfile, archivo de seguridad.  Ver ANEXO
mkdir -p $imgFOLDER							# Se crea (si no existe) el directorio
source $initscript							# Ejecuta el archivo de inicializacion		Ver ANEXO

timeStart=$(date)
Vvsub=70
CLEAR=120


doClear
lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#---Test changing nsamp---
string=_
CLEAR=120
cols=700; binrow=1; bincol=1;
for loop in  {1..20} 								# Numero de imagenes desde 1 hasta 20
do
	if [ ! -f "$lockfilename" ]; then break; fi     
        echo "Rutine $rutine"
	source eraseANDepurge.sh						# Ver ANEXO
	lta set vsub $Vvsub

	doClear
	lta sseq sequencers/sequencer_microchip_binned_brenda.xml
    

	rows=400; nsmpls=1225; expo=0;  #4 25 49 81 100 225 324 625 900 1225
	doSettings                      #   Ver ANEXO

	# Nombre de la imagen y directorio  Ver ANEXO
	lta name $imgFOLDER/skp_${runname}_seq${string}_NSAMP_${nsmpls}_NROW_${rows}_NCOL_${cols}_EXPOSURE_${expo}_NBINROW_${binrow}_NBINCOL_${bincol}_img_
	lta read #Read the image

	#use skipper to root to process the last image
	# Ver ANEXO
	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
	fullPathImg=$imgFOLDER$lastFileFZ
	skp2rr $fullPathImg

	newFitsImg=$(ls -rt | tail -1)
	if [[ $newFitsImg == *.fits ]]
	then
		mv $newFitsImg $imgFOLDER
	else
		echo "is not an image"
		echo $newFitsImg
		sleep 2
	fi

done

end=$(date)

echo "Start="$timeStart
echo "End="$end
echo "image: "$newFitsImg

###################################
#
# Anexos
#
# lockfile  	Archivo que se crea al inicio del script y que si lo borramos del directorio interrumpe el loop
#				de esta manera no hay que detener ningun script, solo esperar a que termine la adquisicion de
#				la imagen actual
#
# initScript	Inicia comandos lta
#				define archivo de voltajes
#				define archivo sequencer
#				define un path por default para guardar imagenes
#
# eraseANDepurge	limpieza de la CCD
#
# doSettings	Establece los valores definidos de
#				Renglones
#				Columnas
#				nSamps
#				tiempo de Exposicion
#				bining por renglon
#				bining por columna
#
# lta name /path/name_of_image_img_			Se define el directorio y nombre de la imagen
#
# lta read		comando para iniciar la lectura de la CCD
#
# skipper to ROOT procesa lña imagen y nos entrega un archivo fits a partir de nuestra imagen .fz
#
# 
