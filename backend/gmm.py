from sklearn.mixture import GaussianMixture
import numpy as np
from featureIdentification import spectral_analysis_for_dominant_period
from dataRepresentation import build_feature_trajectories
import math
import json

def trainGMM(feat_traj):

    params = {}

    # iterate over each word feature
    for feature, featureTrajectory in feat_traj.iteritems():

        # derive the number of classes
        T = len(featureTrajectory)
        dominantPeriod = 1  #spectral_analysis_for_dominant_period(featureTrajectory)
        n_classes = int(math.floor(float(T) / dominantPeriod))

        # create the matrix
        matrix = np.array(featureTrajectory)[np.newaxis].T

        # initialize the mixture of Gaussians
        clf = GaussianMixture(n_components=n_classes, covariance_type='full', max_iter=20, random_state=0)

        # train
        clf.fit(matrix)

        # store
        params[feature] = {}
        params[feature]['weights'] = np.copy(clf.weights_)
        params[feature]['means'] = np.copy(clf.means_)
        params[feature]['covariances'] = np.copy(clf.covariances_)

    return params


tweets_as_json = json.dumps([{"lat": "37.548342500000004", "text": "Wish I could spend New Years Eve with my friends and family back in US!", "createdAtAsLong": "1451557495000", "long": "55.7558765"}, {"lat": "-1.284233", "text": "@joeyzed Happy birthday!!!\ud83c\udf89 Have a lovely day  hopefully see you soon\ud83d\udc9c", "createdAtAsLong": "1451557497000", "long": "52.991392499999996"}, {"lat": "-0.213197", "text": "\u2615\ufe0f\ud83c\udf76 (@ boulangerie cafe) https://t.co/OZRoLDe1Do", "createdAtAsLong": "1451557497000", "long": "51.489915"}, {"lat": "-0.8827685", "text": "@Independent things in life are relevant to those in those situations. We can help people and so we should but what about those here?", "createdAtAsLong": "1451557499000", "long": "51.043277"}, {"lat": "35.079862", "text": "Happy New Year to all my colleagues and friends and to all Twitter members. https://t.co/HYGVBrQNfs https://t.co/VGDf6mySi7", "createdAtAsLong": "1451557499000", "long": "31.415447"}, {"lat": "37.548342500000004", "text": "@Marcespley @scfcjase @BenDinnery but Arnie is Marko", "createdAtAsLong": "1451557501000", "long": "55.7558765"}, {"lat": "-0.102162", "text": "@arthurvonnagel Wind Waker way up there  nice. Why so low for Minish though? That\u2019s right up there for me. But then  it was one of my first.", "createdAtAsLong": "1451557503000", "long": "51.5879015"}, {"lat": "-3.2030085", "text": "@sporan1314 @joannahsbyoung @Edinburghchap @MrsCupcake79 Says the bloke who sent pictures of his penis to middle aged bloke Claire Rob LOL", "createdAtAsLong": "1451557504000", "long": "55.9431955"}, {"lat": "4.9040535", "text": "Smoking French rolled cigarettes can turn you into weed smoker pretty quickly in Amsterdam!", "createdAtAsLong": "1451557506000", "long": "52.35472800000001"}, {"lat": "6.7666574", "text": "Half way home :slightly_smiling_face:  \ud83d\udeeb\ud83d\udeec\ud83d\udeeb\ud83d\udeec #\ub3c5\uc77c #\ub4a4\uc140\ub3c4\ub974\ud504 #\uc9d1\uc5d0\uac00\ub294\uae38 #\uc0c8\ud574\ubcf5\ub9ce\uc774\ubc1b\uc73c\uc138\uc694 #germany #dusseldorf #happynewyear\u2026 https://t.co/TUfZE9mcLN", "createdAtAsLong": "1451557507000", "long": "51.2794991"}])
feat_traj = build_feature_trajectories(tweets_as_json, 1451557495000, 1451557507000)

params = trainGMM(feat_traj)