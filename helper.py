import os
import numpy as np
import pandas as pd

def read_admissions():
	df = pd.read_table('admit.csv', encoding='utf-16')
	# Tidy up the data -- remove unneeded columns and rename some mangled ones.
	df = df.fillna(0)
	df.drop(["Calculation1"], axis = 1, inplace=True)
	df.rename(columns = {'All': 'Students', 'County/State/ Territory' : 'County', 'American Indian': 'AmIndian', \
	'Hispanic/ Latino' : 'Hispanic', 'Domestic Unknown' : 'Unknown',  'African American' : 'Black', 'Inter- national': \
	'International', 'Unnamed: 4' : 'Status'}, inplace=True)
	df[["Students", "AmIndian", "Hispanic", "White", "Asian", "Unknown", "Black", "International"]] = \
	df[["Students", "AmIndian", "Hispanic", "White", "Asian", "Unknown", "Black", "International"]].astype('int', inplace=True)
	return df

def read_county_income():
	df = pd.read_csv('county_income.csv', names = ["County", "Income"])
	df = df.set_index("County")
	# Strip away the dollar sign, comma , make it an int
	df.Income = df.Income.str.replace('$','')
	df.Income = df.Income.str.replace(',','')
	df.Income.astype('int', inplace=True)
	return df

def read_gpas():
	return pd.read_table('frgpabyyear.csv', encoding='utf-16')

def read_zips():
	df = pd.read_csv("ca_zip_codes.csv")
	# Clean up to remove " County" (so as to make data consistent)
	df.county = df.county.str.replace(' County','')
	return df

def read_income_city():
	df = pd.read_csv("MedianZIP-3.csv")
	# Clean up to remove comma and make int.
	df.Median = df.Median.str.replace(',','')
	df.Median = df.Median.astype('int')
	return df[["Zip", "Median"]]
	
def simulate_hs(admits, admgpa, schooln, city, county, applicants, afram, amind, hispanic, asian, white, unk, intl, income, appgpa):
	
	df = pd.DataFrame({'School Name' : schooln, 'City' : city, 'County' : county, 'Applicants' : 1, 'Black' : 0, 'AmIndian' : 0, \
	'Hispanic' : 0, 'Asian' : 0, 'White' : 0, 'Unknown' : 0, 'International': 0, 'Income' : income, 'Student GPA' : 0, 'Admitted' : 0}, \
	index=range(applicants))
	
	# This produces somewhat believable GPAs in a normal distribution around the avg GPA.	 
	gpa_raw = np.random.randn(applicants) / 6 + appgpa 
	gpas = [round(element, 2) for element in gpa_raw]
	# Sort list of GPAs and find the GPA cutoff for admission.
	cutoff = sorted(gpas)[0 - admits]
	
	# Now step through our applicants: first, assign them an ethnicity from the pool...
	for i in range(applicants):
		if afram > 0:
			df.loc[i, "Black"] = 1
			afram -= 1
		elif amind > 0:
			df.loc[i, "AmIndian"] = 1
			amind -= 1
		elif hispanic > 0:
			df.loc[i, "Hispanic"] = 1
			hispanic -= 1
		elif asian > 0:
			df.loc[i, "Asian"] = 1
			asian -= 1
		elif white > 0:
			df.loc[i, "White"] = 1
			white -= 1
		elif intl > 0:
			df.loc[i, "International"] = 1
			intl -= 1
		else:
			df.loc[i, "Unknown"] = 1
			unk -= 1 # technically unecessary, but may be nice for debugging
			
		# Now, assign the student a gpa from the list...
		gpa = gpas.pop()
		df.loc[i, "Student GPA"] = gpa
		# ... and if it's at or above the cutoff, admit them!
		if gpa >= cutoff:
			df.loc[i, "Admitted"] = 1
		
	# Note that we've essentially randomized the ethnicities of those admitted from the sample!
	return df