import os
import pandas as pd

def accessFile(dirName):
	count=0
	idDF=pd.DataFrame(columns=['id','filename'])
	for file in os.listdir(dirName):
		if 'csv' in file:
				listcsv=pd.read_csv(os.path.join(dirName,file))
				idList=listcsv['id'].tolist()
				for item in idList:
					idDF.loc[len(idDF)]=[str(item),str(file)]

	idDF.to_csv('idList.csv')

				

DIR_NAME="./videosBySearchDB"
accessFile(DIR_NAME)