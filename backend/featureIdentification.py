import numpy as np

def spectral_analysis_for_dominant_period(feature, featureTrajectory):
	ft = np.array(featureTrajectory)
	DFT = np.fft.fft(ft)
	try:
		periodogram = np.square(np.absolute(np.split(DFT,2)))
	except ValueError:
		DFT = np.delete(DFT, DFT.size)
		periodogram = np.square(np.absolute(np.split(DFT,2)))
	
	dominantPeriod = len(featureTrajectory)/np.argmax(periodogram)
	dominantPowerSpectrum = np.amax(periodogram)
	return dominantPeriod, dominantPowerSpectrum

def average_dfidf(featureTrajectory):
	return np.mean(featureTrajectory)

def heuristic_stop_word_detection(features, stopwords):
	#Find max DPS, DFIDF, and min DFIDF from stopwords seed	
	init_trajectory = features[stopwords[0]]
	_,UDPS = spectral_analysis_for_dominant_period(sw,trajectory)
	UDFIDF = average_dfidf(trajectory)
	LDFIDF = UDFIDF
	for sw in stopwords:
		trajectory = features.pop(sw, None)
		_,dps = spectral_analysis_for_dominant_period(sw,trajectory)
		average_dfidf = average_dfidf(trajectory)
		if dps>UDPS:
			UDPS=dps
		if average_dfidf>UDFIDF:
			UDFIDF=average_dfidf
		elif LDFIDF<average_dfidf:
			LDFIDF=average_dfidf

	for f, featureTrajectory in features.items():
		_,s_f = spectral_analysis_for_dominant_period(f,featureTrajectory)
		average_dfidf_f = average_dfidf(featureTrajectory)
		if (s_f < UDPS) and (average_dfidf_f<=UDFIDF and average_dfidf_f>=LDFIDF):
			stopwords.append(f)
			features.pop(f, None)
	return features, stopwords, UDPS

def categorizing_features(features):
	HH = []
	HL = []
	LH = []
	LL = []
	SW = ["I","a","about","an","are","as","at","be","by","com","for","from","how","in","is","it","of","on","or","that","the","this","to","was","what","when","where","who","will","with","the","www"]
	features, SW, UDPS = heuristic_stop_word_detection(features, SW)
	for f, featureTrajectory in features.items():
		p_f,s_f = spectral_analysis_for_dominant_period(f,featureTrajectory)
		if p_f > len(featureTrajectory)/2 and s_f > UDPS:
			HH.append(f)
		elif p_f > len(featureTrajectory)/2 and s_f <= UDPS:
			LH.append(f)
		elif p_f <= len(featureTrajectory)/2 and s_f > UDPS:
			HL.append(f)
		elif p_f <= len(featureTrajectory)/2 and s_f <= UDPS:
			LL.append(f)
	