import psutil
import logging
logging.info(psutil.virtual_memory())
# WRITE EXPORT FILE FOR EACH RUN
#90% of available meomry in MB
TOTmem=psutil.virtual_memory()[1]/1024/1024*0.9

def writeExport(outputFile_ExportAster,aster_root,outputFile_Comm,outputFile_Messages,namemess,nameexport):
    #lectura de parametros
    lines=[]
    lines=(
"""P actions make_etude
P aster_root """+aster_root+"""
P version stable
P consbtc oui
P corefilesize unlimited
P cpresok RESNOOK
P debug nodebug
P follow_output yes
P facmtps 1
P lang en
P mpi_nbcpu 1
P mpi_nbnoeud 1
P mode interactif
P memjob """+str(TOTmem*208)+"""
P memory_limit """+str(TOTmem*2)+"""
P time_limit 72000.0
P tpsjob 1201

A memjeveux """+str(TOTmem)+"""
A tpmax 72000.0
F comm """+outputFile_Comm+""" D  1
F mess """+outputFile_Messages+namemess+""".mess R  6
""").split("\n") 
    
    try:
       f = open(outputFile_ExportAster+nameexport+'.export', 'w')
       f.write('\n'.join(lines))
       f.close()
    except:
        logging.error("Error while writing the ExportAster-File")        