# -*- coding: utf-8 -*-
""""""
from math import sqrt

critics = {
	'Lisa Rose': {
		'Lady in the Water': 2.5,
		'Snakes on a Plane': 3.5,
	 	'Just My Luck': 3.0,
		'Superman Returns': 3.5,
		'You, Me and Dupree': 2.5,
	 	'The Night Listener': 3.0
	},
	'Gene Seymour': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 3.5,
	 	'Just My Luck': 1.5,
		'Superman Returns': 5.0,
		'The Night Listener': 3.0,
	 	'You, Me and Dupree': 3.5
	},
	'Michael Phillips': {
		'Lady in the Water': 2.5,
		'Snakes on a Plane': 3.0,
		'Superman Returns': 3.5,
		'The Night Listener': 4.0
	},
	'Claudia Puig': {
		'Snakes on a Plane': 3.5,
		'Just My Luck': 3.0,
		'The Night Listener': 4.5,
		'Superman Returns': 4.0,
		'You, Me and Dupree': 2.5
	},
	'Mick LaSalle': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 4.0,
		'Just My Luck': 2.0,
		'Superman Returns': 3.0,
		'The Night Listener': 3.0,
		'You, Me and Dupree': 2.0
	},
	'Jack Matthews': {
		'Lady in the Water': 3.0,
		'Snakes on a Plane': 4.0,
		'The Night Listener': 3.0,
		'Superman Returns': 5.0,
		'You, Me and Dupree': 3.5
	},
	'Toby': {
		'Snakes on a Plane':4.5,
		'You, Me and Dupree':1.0,
		'Superman Returns':4.0
	}
}


def sim_distance(prefs, p1, p2):
	"""欧几里得距离"""
	si = dict()
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	if 0 == len(si):
		return 0

	sum_of_squares = sum([pow(prefs[p1][item] - prefs[p2][item], 2)
						  for item in prefs[p1] if item in prefs[p2]])
	return 1 / (1 + sqrt(sum_of_squares))


def pr_sim_pearson(prefs, p1, p2):
	"""皮尔逊相关系数"""
	si = dict()
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	n = len(si)
	if 0 == n:
		return 1

	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])

	sum1sq = sum([pow(prefs[p1][it], 2) for it in si])
	sum2sq = sum([pow(prefs[p2][it], 2) for it in si])

	psum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

	num = psum - (sum1 * sum2 / n)
	den = sqrt((sum1sq - pow(sum1, 2)/n)*(sum2sq-pow(sum2, 2)/n))
	if den == 0:
		return 0
	return num / den

def main():
	""""""
	og = sim_distance(critics, 'Mick LaSalle', 'Jack Matthews')
	print(og)
	ogr = pr_sim_pearson(critics, 'Mick LaSalle', 'Jack Matthews')
	print(og)

if __name__ == '__main__':
	print('Running ... ')
	main()
