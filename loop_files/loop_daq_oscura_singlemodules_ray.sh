#!/bin/bash
###
#
#rutine in progress: 
rutine="generic loop"
#
###
timeStart=$(date)
#Vvr=-7; Vvdd=-17; Vvdrain=-22;
#Vvh=5; Vvl=2.5; Vth=4.5; Vtl=2; Vhh=4; Vhl=1; 
#Vsh=3.5; Vsl=-10; Voh=-2.5; Vol=-8; Vdh=4; Vdl=-10;
Vvsub=70
#Vsl=-9;

CLEAR=120
#dtph=200; dtphshort=4; npumps=40000; il_secs=120;		#Variables for trap pumping
#rows=650; cols=700; nsmpls=1; expo=0; binrow=1; bincol=1;				#Variables for images

imgFOLDER=`dirname $BASH_SOURCE`/images/MITLL/09MAR2023/spuriousTest/ #END WITH / please!!!!
runname=module24_MITLL01_externalVr-4_Vv2_T140_
lockfilename=lockfile

clearseq=sequencers/sequencer_microchip_clear_brenda.xml
#initscript=init/init_skp_lta_oscura_singlemodules.sh		#Init script (sequencer and voltages are loaded here)
initscript=init/init_ICN_MM_230208.sh
#-----Acquire raw output data (as seen in the oscilloscope)-----
doRaw(){
	lta startseq
	sleep 0
	lta set bufSel 0	# Select ADC channel to capture (0-3)
	# Transfer raw data
	lta set packSource 4
	lta set packStart 1
	lta getraw
	lta set packSource 9
	lta set packStart 0
	}

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

#-----Set voltages-----
setVoltages(){
#	lta set vsub $Vvsub
#	lta set vr $Vvr
#	lta set vdd $Vvdd
#	lta set vdrain $Vvdrain
#	lta set swal $Vsl
#	lta set swbl $Vsl

#	lta set swah $Vsh
#	lta set swbh $Vsh
#	lta set ogah $Voh
#	lta set ogbh $Voh
#	lta set dgah $Vdh
#	lta set dgbh $Vdh

#	lta set h1ah $vhh
#	lta set h1bh $Vhh
#	lta set h3ah $Vhh
#	lta set h3bh $Vhh
#	lta set h2ch $Vhh	
#	lta set h1al $Vhl
#	lta set h1bl $Vhl
#	lta set h3al $Vhl
#	lta set h3bl $Vhl
#	lta set h2cl $Vhl
	echo "set voltages ok"
	}

#----------To start----------
touch $lockfilename
mkdir -p $imgFOLDER
source $initscript
#cp $BASH_SOURCE ${imgFOLDER}/loop_${runname}.sh        #Copy this script into imgFOLDER

doClear
lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#source eraseANDepurge_microchip_hor.sh 0.125 2

#source eraseANDepurge.sh #comentar
#lta set vsub $Vvsub	#comentar

#doClear
#lta sseq sequencers/sequencer_microchip_binned_brenda.xml #comentar

#doRaw



#----------LOOPS----------

#---Generic loop---

CLEAR=600
#cols=700; rows=10; nsmpls=1; expo=0; binrow=1; bincol=1;

for loop in {1..10}
do
	cols=700; rows=250; nsmpls=324; expo=0; binrow=1; bincol=1;  #Cambiar a Row = 50
	echo "start generic loop"

	if [ ! -f "$lockfilename" ]; then break; fi
	echo "Rutine $rutine"
	source eraseANDepurge.sh
	lta set vsub $Vvsub

	doClear
	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

	setVoltages
	doSettings
	lta name $imgFOLDER/skp_${runname}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
	lta read

	#use skipper to root to process the last image
	lastFileFZ=$(ls $imgFOLDER -rt | tail -1)
	fullPathImg=$imgFOLDER$lastFileFZ
	skp2rB $fullPathImg

	newFitsImg=$(ls -rt | tail -1)
	if [[ $newFitsImg == *.fits ]]
	then
		mv $newFitsImg $imgFOLDER
	else
		echo "is not an image"
		echo $newFitsImg
		sleep 2
	fi

	rows=650; nsmpls=1;
	doSettings
	lta name $imgFOLDER/skp_${runname}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
	lta read
	echo "End of loop $loop in $rutine"
done
end=$(date)

echo "Start="$timeStart
echo "End="$end

#---Test changing voltages---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for Vvdrain in `seq -20.8 0.2 -20.2`
#for Vvdd in -22 -21 -20 -19 -18 -17
#for Vhl in -1 -0.5 0 0.5 1 1.5
#for Voh in -1.5 -0.5 0.5
#for Vdh in -1 4 9
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	setVoltages
#	doSettings
#	lta name $imgFOLDER/skp_${runname}_hl${Vhl}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#----------STANDARD TESTS----------


#---Test Vv1 Vv2 & Vv3 voltages---

# CLEAR=300
# cols=700; binrow=1; bincol=1;
# for j in 3 2 1
# do
# 	if [ ! -f "$lockfilename" ]; then break; fi
# 	#source voltage_skp_lta_v${j}_microchip.sh
# 	source voltage_skp_lta_v${j}_mitll.sh

# 	source eraseANDepurge.sh
# 	lta set vsub $Vvsub

# 	doClear
# 	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

# 	rows=650; nsmpls=1; expo=150;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_Vv${j}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read

# 	rows=50; nsmpls=324; expo=0;
# 	doSettings
# 	lta name $imgFOLDER/skp_${runname}_Vv${j}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
# 	lta read
# done


#---Test inverting clocks (reading half of the sensor through one amplifier)---

#CLEAR=120
#cols=1200; binrow=1; bincol=1;
#for string in HA HB VA VB
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source eraseANDepurge.sh
#	lta set vsub $Vvsub

#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda_${string}.xml

#	rows=1300; nsmpls=1; expo=0;
#	doSettings
#	lta name $imgFOLDER/skp_${runname}_seq${string}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read

#	rows=100; nsmpls=324; expo=0;
#	doSettings
#	lta name $imgFOLDER/skp_${runname}_seq${string}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#---Test changing ssamp/psamp---

#cols=700; rows=650; nsmpls=1; expo=0; binrow=1; bincol=1;
#doSettings

#for smp in `seq 20 20 2500`
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	delay=$(echo ${smp}+50 | bc)
#	delay=$((smp+50))
#	lta set ssamp $smp
#	lta set psamp $smp
#	lta delay_Integ_ped $delay
#	lta delay_Integ_sig $delay
#	lta name $imgFOLDER/skp_${runname}_loopSSAMP_SSAMP${smp}_PSAMP${smp}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#---Test changing NSAMP---

#CLEAR=120
#cols=700; rows=100; expo=0; binrow=1; bincol=1;

#for nsmpls in 1 4 9 16 25 49 100 225 400 625 900 1225
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_loopNSAMP_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#---Test changing EXPOSURE---

#CLEAR=300
#cols=700; rows=100; nsmpls=324; binrow=1; bincol=1;

#for loop in `seq 1 1 10`
#do
#for expo in `seq 0 600 1800`
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source eraseANDepurge.sh
#	lta set vsub $Vvsub

#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_loopEXPOSURE_clear${CLEAR}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


#----------TRAP PUMPING AND LED ILLUMINATION----------


#---Loop dtph---

# CLEAR=120
# dtphshort=4; npumps=40000; il_secs=120;
# rows=50; cols=700; nsmpls=10; expo=0; binrow=1; bincol=1;

#for string in a b c d e f
#do
#for dtph in 75 100 200 500 1000 1500 2000 2500 3500 5000 7500 10000 25000 50000 100000 150000 300000 500000 1000000 2000000
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source voltage_skp_microchip_looptraps_${string}.sh

#	doClear
#	lta sseq sequencers/sequencer_microchip_ppump_horizontal.xml

#	doSettings  
#	lta delay_Tph $dtph
#	lta NPUMPS $npumps
#	lta delay_Tphshort $dtphshort
#	python ard_led_ctrl.py $il_secs
#	lta name $imgFOLDER/skp_${runname}_loopdtph_wledon${il_secs}_npump${npumps}_dtph${dtph}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta name $imgFOLDER/skp_${runname}_Vv${string}_loopdtph_wledon${il_secs}_npump${npumps}_dtph${dtph}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


#---Test LED illumination---

#CLEAR=120                                
#rows=650; cols=700; nsmpls=1; expo=0; binrow=1; bincol=1;

#for il_secs in 0.4
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#	doSettings
#	python ard_led_ctrl.py $il_secs
#	lta name $imgFOLDER/skp_${runname}_wledon${il_secs}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done


#----------EXTRA TESTS----------


#---Test changing delays---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for delay in `seq 150 50 300`
#do  
#	if [ ! -f "$lockfilename" ]; then break; fi
#	doClear
#	lta sseq sequencers/sequencer_microchip_binned_brenda.xml

#       doSettings       
#       lta delay_H_overlap $delay
#	lta delay_V_Overlap $delay
#       lta name $imgFOLDER/skp_${runname}_delayH${delay}_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#       lta read
#done


#---Test of manual eraseANDepurge---

#CLEAR=120
#cols=700; rows=100; nsmpls=324; expo=0; binrow=1; bincol=1;

#for slope in 0.05 0.15 0.25
#do
#for sleep in 0.5 1.5 2.5
#do
#	if [ ! -f "$lockfilename" ]; then break; fi
#	source eraseANDepurge_microchip.sh $slope $sleep

#	doClear
#	lta sseq sequencers/sequencer_microchip_brenda.xml

#	doSettings
#	lta name $imgFOLDER/skp_${runname}_eANDemicrochip_NSAMP${nsmpls}_NROW${rows}_NCOL${cols}_EXPOSURE${expo}_NBINROW${binrow}_NBINCOL${bincol}_img
#	lta read
#done
#done


