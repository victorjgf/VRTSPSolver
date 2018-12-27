import yaml
import pickle
import inputData
import numpy as np
from tsp_runGA import tsp_runGA
import tsp_crossoverMethods, tsp_mutationMethods, tsp_selectionMethods, tsp_stopCriteria
from concurrent.futures import ProcessPoolExecutor

# CONSTANTS
N_CORES = 4
REPETITIONS = 5

# MAPPING
mutation_mappings = tsp_mutationMethods.mapping()
crossover_mappings = tsp_crossoverMethods.mapping('REP_ADJACENCY')
selection_mappings = tsp_selectionMethods.mapping('REP_ADJACENCY')
stopCriteria_mapping = tsp_stopCriteria.mapping()

# PATHS
pathCnf = '../resources/'
pathData = '../resources/datasets/'

# FUNCTIONS
def runGAByProccess(argsTSP):
	REPRESENTATION,x, y, NIND, MAXGEN, NVAR, ELITIST, STOP_PERCENTAGE, PR_CROSS, PR_MUT, CROSSOVER, MUTATION, SELECTION,STOPCRITERIA ,LOCALLOOP = argsTSP
	res = tsp_runGA(REPRESENTATION, x, y, NIND, MAXGEN, NVAR, ELITIST, STOP_PERCENTAGE, PR_CROSS, PR_MUT, CROSSOVER, MUTATION, SELECTION,STOPCRITERIA, LOCALLOOP)
	return res

def mp(func, args, cores, currentConfig):
	with ProcessPoolExecutor(max_workers=cores) as executor:
		res = executor.map(func, args)
	return list(res)


# MAIN SCRIPT
with open(pathCnf+"config.yml") as ymlfile:
		cfg = yaml.load(ymlfile)


keys = list(cfg.keys())
dataFiles = ['rondrit023.tsp','rondrit048.tsp']

for currentConfig in keys:
	for fileName in dataFiles:

		outputFileName = '../resources/out/'+currentConfig+'_'+fileName.split('.')[0]+'.pkl'


		##SET PARAMETERS
		############################################################
		REPRESENTATION = cfg[currentConfig]['REPRESENTATION']
		NIND = cfg[currentConfig]['NIND']
		MAXGEN = cfg[currentConfig]['MAXGEN']
		ELITIST = cfg[currentConfig]['ELITIST']
		#GGAP = 1-ELITIST
		STOP_PERCENTAGE = cfg[currentConfig]['STOP_PERCENTAGE']
		PR_CROSS = cfg[currentConfig]['PR_CROSS']
		PR_MUT = cfg[currentConfig]['PR_MUT']
		LOCALLOOP = cfg[currentConfig]['LOCALLOOP']
		CROSSOVER = cfg[currentConfig]['CROSSOVER']
		CROSSOVER = crossover_mappings[CROSSOVER]
		MUTATION = cfg[currentConfig]['MUTATION']
		MUTATION = mutation_mappings[MUTATION]
		SELECTION = cfg[currentConfig]['SELECTION']
		SELECTION = selection_mappings[SELECTION]
		STOPCRITERIA = cfg[currentConfig]['STOPCRITERIA']

		if STOPCRITERIA=='bestWorst':
			tsp_stopCriteria.setThreshold((10**-1))
		elif STOPCRITERIA=='stdDev':
			tsp_stopCriteria.setThreshold((10**-1.7))
		elif STOPCRITERIA=='phi':
			tsp_stopCriteria.setThreshold((0.14))
		elif STOPCRITERIA=='runingMean':
			tsp_stopCriteria.setThreshold((10**-6))
		else:
			tsp_stopCriteria.setThreshold(0)

		STOPCRITERIA = stopCriteria_mapping[STOPCRITERIA]

		x,y = inputData.inputData(pathData+fileName)
		NVAR = len(x)
		############################################################

		##Multiprocess GA Run
		argsTSP = [REPRESENTATION,x, y, NIND, MAXGEN, NVAR, ELITIST, STOP_PERCENTAGE, PR_CROSS, PR_MUT, CROSSOVER, MUTATION, SELECTION,STOPCRITERIA, LOCALLOOP]
		print (argsTSP)
		res = mp(runGAByProccess, [argsTSP for i in range(REPETITIONS)], N_CORES, currentConfig)
		#print (res)
		## Write to File Output res
		##########################
			
		configObj = {}
		configObj['NODES']={
			'X':x,
			'Y':y
		}
		configObj['PARAMETERS']={
			'REPRESENTATION':REPRESENTATION,
			'NIND':NIND,
			'MAXGEN':MAXGEN,
			'NVAR':len(x),
			'ELITIST':ELITIST,
			'STOP_PERCENTAGE':STOP_PERCENTAGE,
			'PR_CROSS':PR_CROSS,
			'PR_MUT':PR_MUT,
			'STOPCRITERIA':STOPCRITERIA,
			'LOCALLOOP':LOCALLOOP
		}
		configObj['RUNS']=res
		outFile = open(outputFileName,'wb')
		pickle.dump(configObj,outFile)
		outFile.close()
