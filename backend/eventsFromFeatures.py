import numpy as numpy

def unsupervised_greedy_event_detection(HH, HH_docs):
	#HH = [{"name": "name", "Sf":"sf", "Pf":"pf", "trajectory":"ft"}...]
	sorted_HH = sorted(HH, key=lambda k: k['Sf'])
	k = 0
	for f_i in sorted_HH:
		k+= 1
		R_i = f_i
		Cost_Ri = 1/f_i["Sf"]
		sorted_HH.pop(0)
		while len(sorted_HH)>0:
			m = 

