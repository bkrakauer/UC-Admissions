import os
import numpy as np
import pandas as pd
import re
import json
import urllib2

API_KEY = ""  #redacted for github 
BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?type=school&query="


def get_zip_code(hsname, city):
	query = hsname + " in " + city + " California"
	query = re.sub(r" ", "+", query)
	
	try:
		response = urllib2.urlopen(BASE_URL + query + "&key=" + API_KEY).read()
		first_result = json.loads(response)['results'][0]
		address = first_result['formatted_address']
		match = re.search(r"CA [0-9]{5}", address)
		zipc = match.group()
		zipc = int(zipc[3:])
	except Exception as e:
		#print type(e)
		zipc = 0
	
	return zipc
	
def simulate_hs(row):

	df = pd.DataFrame({'School': row["School Name"], 'City': row.City, 'County': row.County, 'Income': row.Income, 'Admitted': 0, 'Student GPA': 0}, \
	index=range(row.Applied))
	# This produces somewhat believable GPAs in a normal distribution around the avg GPA.	 
	gpa_raw = np.random.randn(row.Applied) / 6 + row["App GPA"] 
	gpas = [round(element, 2) for element in gpa_raw]
	# Sort list of GPAs and find the GPA cutoff for admission.
	cutoff = (sorted(gpas)[0 - row.Admitted] if row.Admitted != 0 else 10)
	
	# Now, assign the student a gpa from the list...
	for i in range(row.Applied):
		gpa = gpas.pop()
		df.loc[i, "Student GPA"] = gpa
		# ... and if it's at or above the cutoff, admit them!
		if gpa >= cutoff:
			df.loc[i, "Admitted"] = 1
	return df
	