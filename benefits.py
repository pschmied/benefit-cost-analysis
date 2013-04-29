"""
Calculates each component of user benefits for each combination of origin zone and destination zone and puts the results in a table
in the alternative scenario's schema.

Takes one parameter, the name of the alternative scenario's schema.
Schema names are of the form 'whatever_YYYY' where YYYY is the year.

Gets base-scenario data from the schema named 'base_YYYY' where YYYY is the year of the alternative scenario.
"""

import sys, datetime
from psycopg2 import connect
connection = connect(database='psrc_lcp', host='localhost', user='postgres',password='BCAdatabase')
cursor = connection.cursor()

alt = sys.argv[1]
base = 'base' + alt[alt.find('_'):]

# drop old benefits table if it exists
try:
	cursor.execute("DROP TABLE %s.benefits;" % alt)
except:
	pass
connection.commit()

# create new benefits table just like the one in the public schema
cursor.execute("CREATE TABLE %s.benefits (LIKE public.benefits, PRIMARY KEY (o_zone, d_zone, tod));" % alt)
connection.commit()

# get parking rates
parking = {base : {}, alt : {}}
cursor.execute("select d_zone, parkda, parksr, parkco, nwhrpk from %s.parking;" % base)
data = cursor.fetchall()
for i in data:
	parking[base][i[0]] = {'parkda' : i[1], 'parksr' : i[2], 'parkco' : i[3], 'nwhrpk' : i[4]}
cursor.execute("select d_zone, parkda, parksr, parkco, nwhrpk from %s.parking;" % alt)
data = cursor.fetchall()
for i in data:
	parking[alt][i[0]] = {'parkda' : i[1], 'parksr' : i[2], 'parkco' : i[3], 'nwhrpk' : i[4]}

start = datetime.datetime.now()

# do atomistic benefits for all destination zones in each origin zone
for o_zone in range(1, 957): #range(1, 957) to do all real zones; range(1, 1201) to do all zones
	data = {base : {}, alt : {}}
	banks = {'bank1' : ('biketm', 'walktm', 'au1dis', 'pnrtim', 'pnrdis', 'aivtau', 'aivtwa', 'atwkau', 'aauxwa', 
		'atwtau', 'atwtwa', 'pkfara', 'pkfarw', 'ahbw1v', 'ahbw2v', 'ahbw3v', 'ahbw4v', 'avehda', 'avehs2', 'avehs3', 
		'avpool', 'alttrk', 'amdtrk', 'ahvtrk', 'alttrk', 'amdtrk', 'ahvtrk', 'ambike', 'amwalk', 'atrnst'), 'bank2' :
		('nwbktm', 'nwwktm', 'off1ds', 'oivtwa', 'oauxwa', 'otwtwa', 'opfarw', 'mhbw1v', 'mhbw2v', 'mhbw3v', 'mhbw4v', 
		'ovehda', 'ovehs2', 'ovehs3', 'olttrk', 'omdtrk', 'ohvtrk', 'olttrk', 'omdtrk', 'ohvtrk', 'opbike', 'opwalk', 'otrnst'),
		'bank3' : ('pbiket', 'pwlktm', 'pau1ds', 'ebiket', 'ewlktm', 'eau1ds', 'nbiket', 'nwlktm', 'nau1ds', 'phbw1v', 'phbw2v', 
		'phbw3v', 'phbw4v', 'pvehda', 'pvehs2', 'pvehs3', 'pvpool', 'plttrk', 'pmdtrk', 'phvtrk', 'plttrk', 'pmdtrk', 'phvtrk', 
		'pmbike', 'pmwalk', 'ehbw1v', 'ehbw2v', 'ehbw3v', 'ehbw4v', 'evehda', 'evehs2', 'evehs3', 'elttrk', 'emdtrk', 'ehvtrk', 
		'elttrk', 'emdtrk', 'ehvtrk', 'evbike', 'evwalk', 'nhbw1v', 'nhbw2v', 'nhbw3v', 'nhbw4v', 'nvehda', 'nvehs2', 'nvehs3', 
		'nlttrk', 'nmdtrk', 'nhvtrk', 'nlttrk', 'nmdtrk', 'nhvtrk', 'nibike', 'niwalk'), 'bank4' : ('am1tm1', 'am1tm2', 'am1tm3', 
		'am1tm4', 'am1tim', 'am2tim', 'am3tim', 'am4tim', 'am1tl1', 'am1tl2', 'am1tl3', 'am1tl4', 'am1tol', 'am2tol', 'am3tol', 
		'am4tol', 'amltim', 'ammtim', 'amhtim', 'amltol', 'ammtol', 'amhtol', 'mm1tm1', 'mm1tm2', 'mm1tm3', 'mm1tm4', 'mm1tim', 
		'mm2tim', 'mm3tim', 'mm1tl1', 'mm1tl2', 'mm1tl3', 'mm1tl4', 'mm1tol', 'mm2tol', 'mm3tol', 'mmltim', 'mmmtim', 'mmhtim', 
		'mmltol', 'mmmtol', 'mmhtol', 'pm1tm1', 'pm1tm2', 'pm1tm3', 'pm1tm4', 'pm1tim', 'pm2tim', 'pm3tim', 'pm4tim', 'pm1tl1', 
		'pm1tl2', 'pm1tl3', 'pm1tl4', 'pm1tol', 'pm2tol', 'pm3tol', 'pm4tol', 'pmltim', 'pmmtim', 'pmhtim', 'pmltol', 'pmmtol', 
		'pmhtol', 'em1tm1', 'em1tm2', 'em1tm3', 'em1tm4', 'em1tim', 'em2tim', 'em3tim', 'em1tl1', 'em1tl2', 'em1tl3', 'em1tl4', 
		'em1tol', 'em2tol', 'em3tol', 'emltim', 'emmtim', 'emhtim', 'emltol', 'emmtol', 'emhtol', 'nm1tm1', 'nm1tm2', 'nm1tm3', 
		'nm1tm4', 'nm1tim', 'nm2tim', 'nm3tim', 'nm1tl1', 'nm1tl2', 'nm1tl3', 'nm1tl4', 'nm1tol', 'nm2tol', 'nm3tol', 'nmltim', 
		'nmmtim', 'nmhtim', 'nmltol', 'nmmtol', 'nmhtol', 'am1unc', 'am2unc', 'am3unc', 'am4unc', 'am1uc1', 'am1uc2', 'am1uc3', 
		'am1uc4', 'amlunc', 'ammunc', 'amhunc', 'mm1unc', 'mm2unc', 'mm3unc', 'mm1uc1', 'mm1uc2', 'mm1uc3', 'mm1uc4', 'mmlunc', 
		'mmmunc', 'mmhunc', 'pm1unc', 'pm2unc', 'pm3unc', 'pm4unc', 'pm1uc1', 'pm1uc2', 'pm1uc3', 'pm1uc4', 'pmlunc', 'pmmunc', 
		'pmhunc', 'em1unc', 'em2unc', 'em3unc', 'em1uc1', 'em1uc2', 'em1uc3', 'em1uc4', 'emlunc', 'emmunc', 'emhunc', 'nm1unc', 
		'nm2unc', 'nm3unc', 'nm1uc1', 'nm1uc2', 'nm1uc3', 'nm1uc4', 'nmlunc', 'nmmunc', 'nmhunc')}
	
	# put full matrices from data banks into data
	for bank in banks.keys():
		query1 = "select d_zone, "
		for field in banks[bank]:
			query1 = query1 + field + ", "
		for alternative in (base, alt):
			query = query1[:-2] + " from %s.%s where o_zone = %i and d_zone < 957;" % (alternative, bank, o_zone)
			cursor.execute(query)
			results = cursor.fetchall()
			for result in results:
				for i in range(0, len(banks[bank])):
					data[alternative].setdefault(result[0], {})
					data[alternative][result[0]][banks[bank][i]] = result[i+1]
				data[alternative][result[0]]['zero'] = 0
	
	# get park-and-ride trips
	pr_trips = {base : {}, alt : {}}
	for alternative in (base, alt):
		cursor.execute("select d_zone, trips from %s.pr_trips where o_zone = %s" % (alternative, str(o_zone)))
		results = cursor.fetchall()
		for i in results:
			pr_trips[alternative][i[0]] = i[1]
	
	# get trips to which parking charges apply
	parking_trips = {base : {}, alt : {}}
	cursor.execute("select d_zone, da, sr, col from %s.parking_trips where o_zone = %s" % (base, str(o_zone)))
	results = cursor.fetchall()
	for i in results:
		parking_trips[base][i[0]] = {'da' : i[1], 'sr' : i[2], 'col' : i[3]}
	cursor.execute("select d_zone, da, sr, col from %s.parking_trips where o_zone = %s" % (alt, str(o_zone)))
	results = cursor.fetchall()
	for i in results:
		parking_trips[alt][i[0]] = {'da' : i[1], 'sr' : i[2], 'col' : i[3]}
	
	# calculate benefits and accounting variables
	variables={'am' : {}, 'md' : {}, 'pm' : {}, 'ev' : {}, 'ni' : {}}
	variables['am']['hbw_da_1'] = ('am1tm1', 'am1tl1', 'au1dis', 'ahbw1v', 'am1uc1')
	variables['am']['hbw_da_2'] = ('am1tm2', 'am1tl2', 'au1dis', 'ahbw2v', 'am1uc2')
	variables['am']['hbw_da_3'] = ('am1tm3', 'am1tl3', 'au1dis', 'ahbw3v', 'am1uc3')
	variables['am']['hbw_da_4'] = ('am1tm4', 'am1tl4', 'au1dis', 'ahbw4v', 'am1uc4')
	variables['am']['nhbw_da'] = ('am1tim', 'am1tol', 'au1dis', 'avehda', 'am1unc')
	variables['am']['all_sr2'] = ('am2tim', 'am2tol', 'au1dis', 'avehs2', 'am2unc')
	variables['am']['all_sr3'] = ('am3tim', 'am3tol', 'au1dis', 'avehs3', 'am3unc')
	variables['am']['vanpool'] = ('am4tim', 'am4tol', 'au1dis', 'avpool', 'am4unc')
	variables['am']['lt_truck'] = ('amltim', 'amltol', 'au1dis', 'alttrk', 'amlunc')
	variables['am']['md_truck'] = ('ammtim', 'ammtol', 'au1dis', 'amdtrk', 'ammunc')
	variables['am']['hv_truck'] = ('amhtim', 'amhtol', 'au1dis', 'ahvtrk', 'amhunc')
	variables['am']['bike'] = ('biketm', 'zero', 'au1dis', 'ambike', 'zero')
	variables['am']['walk'] = ('walktm', 'zero', 'au1dis', 'amwalk', 'zero')
	variables['md']['hbw_da_1'] = ('mm1tm1', 'mm1tl1', 'off1ds', 'mhbw1v', 'mm1uc1')
	variables['md']['hbw_da_2'] = ('mm1tm2', 'mm1tl2', 'off1ds', 'mhbw2v', 'mm1uc2')
	variables['md']['hbw_da_3'] = ('mm1tm3', 'mm1tl3', 'off1ds', 'mhbw3v', 'mm1uc3')
	variables['md']['hbw_da_4'] = ('mm1tm4', 'mm1tl4', 'off1ds', 'mhbw4v', 'mm1uc4')
	variables['md']['nhbw_da'] = ('mm1tim', 'mm1tol', 'off1ds', 'ovehda', 'mm1unc')
	variables['md']['all_sr2'] = ('mm2tim', 'mm2tol', 'off1ds', 'ovehs2', 'mm2unc')
	variables['md']['all_sr3'] = ('mm3tim', 'mm3tol', 'off1ds', 'ovehs3', 'mm3unc')
	variables['md']['vanpool'] = ('zero', 'zero', 'zero', 'zero', 'zero')
	variables['md']['lt_truck'] = ('mmltim', 'mmltol', 'off1ds', 'olttrk', 'mmlunc')
	variables['md']['md_truck'] = ('mmmtim', 'mmmtol', 'off1ds', 'omdtrk', 'mmmunc')
	variables['md']['hv_truck'] = ('mmhtim', 'mmhtol', 'off1ds', 'ohvtrk', 'mmhunc')
	variables['md']['bike'] = ('nwbktm', 'zero', 'off1ds', 'opbike', 'zero')
	variables['md']['walk'] = ('nwwktm', 'zero', 'off1ds', 'opwalk', 'zero')
	variables['pm']['hbw_da_1'] = ('pm1tm1', 'pm1tl1', 'pau1ds', 'phbw1v', 'pm1uc1')
	variables['pm']['hbw_da_2'] = ('pm1tm2', 'pm1tl2', 'pau1ds', 'phbw2v', 'pm1uc2')
	variables['pm']['hbw_da_3'] = ('pm1tm3', 'pm1tl3', 'pau1ds', 'phbw3v', 'pm1uc3')
	variables['pm']['hbw_da_4'] = ('pm1tm4', 'pm1tl4', 'pau1ds', 'phbw4v', 'pm1uc4')
	variables['pm']['nhbw_da'] = ('pm1tim', 'pm1tol', 'pau1ds', 'pvehda', 'pm1unc')
	variables['pm']['all_sr2'] = ('pm2tim', 'pm2tol', 'pau1ds', 'pvehs2', 'pm2unc')
	variables['pm']['all_sr3'] = ('pm3tim', 'pm3tol', 'pau1ds', 'pvehs3', 'pm3unc')
	variables['pm']['vanpool'] = ('pm4tim', 'pm4tol', 'pau1ds', 'pvpool', 'pm4unc')
	variables['pm']['lt_truck'] = ('pmltim', 'pmltol', 'pau1ds', 'plttrk', 'pmlunc')
	variables['pm']['md_truck'] = ('pmmtim', 'pmmtol', 'pau1ds', 'pmdtrk', 'pmmunc')
	variables['pm']['hv_truck'] = ('pmhtim', 'pmhtol', 'pau1ds', 'phvtrk', 'pmhunc')
	variables['pm']['bike'] = ('pbiket', 'zero', 'pau1ds', 'pmbike', 'zero')
	variables['pm']['walk'] = ('pwlktm', 'zero', 'pau1ds', 'pmwalk', 'zero')
	variables['ev']['hbw_da_1'] = ('em1tm1', 'em1tl1', 'eau1ds', 'ehbw1v', 'em1uc1')
	variables['ev']['hbw_da_2'] = ('em1tm2', 'em1tl2', 'eau1ds', 'ehbw2v', 'em1uc2')
	variables['ev']['hbw_da_3'] = ('em1tm3', 'em1tl3', 'eau1ds', 'ehbw3v', 'em1uc3')
	variables['ev']['hbw_da_4'] = ('em1tm4', 'em1tl4', 'eau1ds', 'ehbw4v', 'em1uc4')
	variables['ev']['nhbw_da'] = ('em1tim', 'em1tol', 'eau1ds', 'evehda', 'em1unc')
	variables['ev']['all_sr2'] = ('em2tim', 'em2tol', 'eau1ds', 'evehs2', 'em2unc')
	variables['ev']['all_sr3'] = ('em3tim', 'em3tol', 'eau1ds', 'evehs3', 'em3unc')
	variables['ev']['vanpool'] = ('zero', 'zero', 'zero', 'zero', 'zero')
	variables['ev']['lt_truck'] = ('emltim', 'emltol', 'eau1ds', 'elttrk', 'emlunc')
	variables['ev']['md_truck'] = ('emmtim', 'emmtol', 'eau1ds', 'emdtrk', 'emmunc')
	variables['ev']['hv_truck'] = ('emhtim', 'emhtol', 'eau1ds', 'ehvtrk', 'emhunc')
	variables['ev']['bike'] = ('ebiket', 'zero', 'eau1ds', 'evbike', 'zero')
	variables['ev']['walk'] = ('ewlktm', 'zero', 'eau1ds', 'evwalk', 'zero')
	variables['ni']['hbw_da_1'] = ('nm1tm1', 'nm1tl1', 'nau1ds', 'nhbw1v', 'nm1uc1')
	variables['ni']['hbw_da_2'] = ('nm1tm2', 'nm1tl2', 'nau1ds', 'nhbw2v', 'nm1uc2')
	variables['ni']['hbw_da_3'] = ('nm1tm3', 'nm1tl3', 'nau1ds', 'nhbw3v', 'nm1uc3')
	variables['ni']['hbw_da_4'] = ('nm1tm4', 'nm1tl4', 'nau1ds', 'nhbw4v', 'nm1uc4')
	variables['ni']['nhbw_da'] = ('nm1tim', 'nm1tol', 'nau1ds', 'nvehda', 'nm1unc')
	variables['ni']['all_sr2'] = ('nm2tim', 'nm2tol', 'nau1ds', 'nvehs2', 'nm2unc')
	variables['ni']['all_sr3'] = ('nm3tim', 'nm3tol', 'nau1ds', 'nvehs3', 'nm3unc')
	variables['ni']['vanpool'] = ('zero', 'zero', 'zero', 'zero', 'zero')
	variables['ni']['lt_truck'] = ('nmltim', 'nmltol', 'nau1ds', 'nlttrk', 'nmlunc')
	variables['ni']['md_truck'] = ('nmmtim', 'nmmtol', 'nau1ds', 'nmdtrk', 'nmmunc')
	variables['ni']['hv_truck'] = ('nmhtim', 'nmhtol', 'nau1ds', 'nhvtrk', 'nmhunc')
	variables['ni']['bike'] = ('nbiket', 'zero', 'nau1ds', 'nibike', 'zero')
	variables['ni']['walk'] = ('nwlktm', 'zero', 'nau1ds', 'niwalk', 'zero')
	benefits = {}
	for d_zone in range(1, 957):
		benefits[d_zone] = {'am' : {}, 'md' : {}, 'pm' : {}, 'ev' : {}, 'ni' : {}}
		for tod in benefits[d_zone].keys():
			for user_class in variables[tod].keys():
				benefits[d_zone][tod][user_class + '_base_trips'] = data[base][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_alt_trips'] = data[alt][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_base_vht'] = (data[base][d_zone][variables[tod][user_class][0]] - data[base][d_zone][variables[tod][user_class][4]]) * data[base][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_alt_vht'] = (data[alt][d_zone][variables[tod][user_class][0]] - data[alt][d_zone][variables[tod][user_class][4]]) * data[alt][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_base_vmt'] = data[base][d_zone][variables[tod][user_class][2]] * data[base][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_alt_vmt'] = data[alt][d_zone][variables[tod][user_class][2]] * data[alt][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_base_rev'] = data[base][d_zone][variables[tod][user_class][1]] * data[base][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_alt_rev'] = data[alt][d_zone][variables[tod][user_class][1]] * data[alt][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_base_unrel'] = data[base][d_zone][variables[tod][user_class][4]] * data[base][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_alt_unrel'] = data[alt][d_zone][variables[tod][user_class][4]] * data[alt][d_zone][variables[tod][user_class][3]]
				benefits[d_zone][tod][user_class + '_time'] = ((data[base][d_zone][variables[tod][user_class][0]] - data[base][d_zone][variables[tod][user_class][4]] 
					- (data[alt][d_zone][variables[tod][user_class][0]] - data[alt][d_zone][variables[tod][user_class][4]]))
					* (data[base][d_zone][variables[tod][user_class][3]] + data[alt][d_zone][variables[tod][user_class][3]]) / 2.0)
				benefits[d_zone][tod][user_class + '_dist'] = ((data[base][d_zone][variables[tod][user_class][2]] - data[alt][d_zone][variables[tod][user_class][2]])
					* (data[base][d_zone][variables[tod][user_class][3]] + data[alt][d_zone][variables[tod][user_class][3]]) / 2.0)
				benefits[d_zone][tod][user_class + '_toll'] = ((data[base][d_zone][variables[tod][user_class][1]] - data[alt][d_zone][variables[tod][user_class][1]])
					* (data[base][d_zone][variables[tod][user_class][3]] + data[alt][d_zone][variables[tod][user_class][3]]) / 2.0)
				benefits[d_zone][tod][user_class + '_unrel'] = ((data[base][d_zone][variables[tod][user_class][4]] - data[alt][d_zone][variables[tod][user_class][4]])
					* (data[base][d_zone][variables[tod][user_class][3]] + data[alt][d_zone][variables[tod][user_class][3]]) / 2.0)
				benefits[d_zone]['hbw_dat_time'] = ((data[base][d_zone]['pnrtim'] - data[alt][d_zone]['pnrtim']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_dat_dist'] = ((data[base][d_zone]['pnrdis'] - data[alt][d_zone]['pnrdis']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_dat_ivt'] = ((data[base][d_zone]['aivtau'] - data[alt][d_zone]['aivtau']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_wat_ivt'] = ((data[base][d_zone]['aivtwa'] - data[alt][d_zone]['aivtwa']) * (data[base][d_zone]['atrnst'] + data[alt][d_zone]['atrnst']) / 2.0)
				benefits[d_zone]['nhbw_wat_ivt'] = ((data[base][d_zone]['oivtwa'] - data[alt][d_zone]['oivtwa']) * (data[base][d_zone]['otrnst'] + data[alt][d_zone]['otrnst']) / 2.0)
				benefits[d_zone]['hbw_dat_walk'] = ((data[base][d_zone]['atwkau'] - data[alt][d_zone]['atwkau']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_wat_walk'] = ((data[base][d_zone]['aauxwa'] - data[alt][d_zone]['aauxwa']) * (data[base][d_zone]['atrnst'] + data[alt][d_zone]['atrnst']) / 2.0)
				benefits[d_zone]['nhbw_wat_walk'] = ((data[base][d_zone]['oauxwa'] - data[alt][d_zone]['oauxwa']) * (data[base][d_zone]['otrnst'] + data[alt][d_zone]['otrnst']) / 2.0)
				benefits[d_zone]['hbw_dat_wait'] = ((data[base][d_zone]['atwtau'] - data[alt][d_zone]['atwtau']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_wat_wait'] = ((data[base][d_zone]['atwtwa'] - data[alt][d_zone]['atwtwa']) * (data[base][d_zone]['atrnst'] + data[alt][d_zone]['atrnst']) / 2.0)
				benefits[d_zone]['nhbw_wat_wait'] = ((data[base][d_zone]['otwtwa'] - data[alt][d_zone]['otwtwa']) * (data[base][d_zone]['otrnst'] + data[alt][d_zone]['otrnst']) / 2.0)
				benefits[d_zone]['hbw_dat_fare'] = ((data[base][d_zone]['pkfara'] - data[alt][d_zone]['pkfara']) * (pr_trips[base][d_zone] + pr_trips[alt][d_zone]) / 2.0)
				benefits[d_zone]['hbw_wat_fare'] = ((data[base][d_zone]['pkfarw'] - data[alt][d_zone]['pkfarw']) * (data[base][d_zone]['atrnst'] + data[alt][d_zone]['atrnst']) / 2.0)
				benefits[d_zone]['nhbw_wat_fare'] = ((data[base][d_zone]['opfarw'] - data[alt][d_zone]['opfarw']) * (data[base][d_zone]['otrnst'] + data[alt][d_zone]['otrnst']) / 2.0)
				benefits[d_zone]['parking'] = ((parking[base][d_zone]['parkda'] - parking[alt][d_zone]['parkda']) * (parking_trips[base][d_zone]['da'] + parking_trips[alt][d_zone]['da']) / 2.0 +
					(parking[base][d_zone]['parksr'] - parking[alt][d_zone]['parksr']) * (parking_trips[base][d_zone]['sr'] + parking_trips[alt][d_zone]['sr']) / 2.0 +
					(parking[base][d_zone]['parkco'] - parking[alt][d_zone]['parkco']) * (parking_trips[base][d_zone]['col'] + parking_trips[alt][d_zone]['col']) / 2.0)
		
		for tod in ('am', 'md', 'pm', 'ev', 'ni'):
			query = "INSERT INTO %s.benefits (o_zone, d_zone, tod, " % alt
			user_classes = variables[tod].keys()
			for user_class in user_classes:
				for var in ('_base_trips', '_alt_trips', '_base_vht', '_alt_vht', '_base_vmt', '_alt_vmt', '_base_rev', '_alt_rev', '_base_unrel', '_alt_unrel', '_time', '_dist', '_toll', '_unrel'):
					query = query + user_class + var + ', '
			query = query[:-2] + ") VALUES (%i, %i, '%s', " % (o_zone, d_zone, tod)
			for user_class in user_classes:
				for var in ('_base_trips', '_alt_trips', '_base_vht', '_alt_vht', '_base_vmt', '_alt_vmt', '_base_rev', '_alt_rev', '_base_unrel', '_alt_unrel', '_time', '_dist', '_toll', '_unrel'):
					query = query + "%f, " % benefits[d_zone][tod][user_class + var]
			query = query[:-2] + ");"
			cursor.execute(query)
		
		cursor.execute("""
			INSERT INTO %s.benefits (o_zone, d_zone, tod, hbw_dat_time, hbw_dat_dist, hbw_dat_ivt, hbw_wat_ivt, nhbw_wat_ivt, hbw_dat_walk, hbw_wat_walk, 
			nhbw_wat_walk, hbw_dat_wait, hbw_wat_wait, nhbw_wat_wait, hbw_dat_fare, hbw_wat_fare, nhbw_wat_fare, parking) 
			VALUES (%i, %i, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f);""" % 
			(alt, o_zone, d_zone, "'all'", benefits[d_zone]['hbw_dat_time'], benefits[d_zone]['hbw_dat_dist'], benefits[d_zone]['hbw_dat_ivt'], 
			benefits[d_zone]['hbw_wat_ivt'], benefits[d_zone]['nhbw_wat_ivt'], benefits[d_zone]['hbw_dat_walk'], benefits[d_zone]['hbw_wat_walk'], 
			benefits[d_zone]['nhbw_wat_walk'], benefits[d_zone]['hbw_dat_wait'], benefits[d_zone]['hbw_wat_wait'], benefits[d_zone]['nhbw_wat_wait'], 
			benefits[d_zone]['hbw_dat_fare'], benefits[d_zone]['hbw_wat_fare'], benefits[d_zone]['nhbw_wat_fare'], benefits[d_zone]['parking']))
		connection.commit()
	print "Calculated benefits for origin zone " + str(o_zone)
benefits = None
# add summary rows to benefits table
cursor.execute ("""insert into %s.benefits select 0 as o_zone, 0 as d_zone, tod,
	sum(hbw_da_1_base_vht) as hbw_da_1_base_vht,
	sum(hbw_da_1_alt_vht) as hbw_da_1_alt_vht,
	sum(hbw_da_1_base_vmt) as hbw_da_1_base_vmt,
	sum(hbw_da_1_alt_vmt) as hbw_da_1_alt_vmt,
	sum(hbw_da_1_base_rev) as hbw_da_1_base_rev,
	sum(hbw_da_1_alt_rev) as hbw_da_1_alt_rev,
	sum(hbw_da_1_base_unrel) as hbw_da_1_base_unrel,
	sum(hbw_da_1_alt_unrel) as hbw_da_1_alt_unrel,
	sum(hbw_da_1_time) as hbw_da_1_time,
	sum(hbw_da_1_dist) as hbw_da_1_dist,
	sum(hbw_da_1_toll) as hbw_da_1_toll,
	sum(hbw_da_1_unrel) as hbw_da_1_unrel,

	sum(hbw_da_2_base_vht) as hbw_da_2_base_vht,
	sum(hbw_da_2_alt_vht) as hbw_da_2_alt_vht,
	sum(hbw_da_2_base_vmt) as hbw_da_2_base_vmt,
	sum(hbw_da_2_alt_vmt) as hbw_da_2_alt_vmt,
	sum(hbw_da_2_base_rev) as hbw_da_2_base_rev,
	sum(hbw_da_2_alt_rev) as hbw_da_2_alt_rev,
	sum(hbw_da_2_base_unrel) as hbw_da_2_base_unrel,
	sum(hbw_da_2_alt_unrel) as hbw_da_2_alt_unrel,
	sum(hbw_da_2_time) as hbw_da_2_time,
	sum(hbw_da_2_dist) as hbw_da_2_dist,
	sum(hbw_da_2_toll) as hbw_da_2_toll,
	sum(hbw_da_2_unrel) as hbw_da_2_unrel,

	sum(hbw_da_3_base_vht) as hbw_da_3_base_vht,
	sum(hbw_da_3_alt_vht) as hbw_da_3_alt_vht,
	sum(hbw_da_3_base_vmt) as hbw_da_3_base_vmt,
	sum(hbw_da_3_alt_vmt) as hbw_da_3_alt_vmt,
	sum(hbw_da_3_base_rev) as hbw_da_3_base_rev,
	sum(hbw_da_3_alt_rev) as hbw_da_3_alt_rev,
	sum(hbw_da_3_base_unrel) as hbw_da_3_base_unrel,
	sum(hbw_da_3_alt_unrel) as hbw_da_3_alt_unrel,
	sum(hbw_da_3_time) as hbw_da_3_time,
	sum(hbw_da_3_dist) as hbw_da_3_dist,
	sum(hbw_da_3_toll) as hbw_da_3_toll,
	sum(hbw_da_3_unrel) as hbw_da_3_unrel,

	sum(hbw_da_4_base_vht) as hbw_da_4_base_vht,
	sum(hbw_da_4_alt_vht) as hbw_da_4_alt_vht,
	sum(hbw_da_4_base_vmt) as hbw_da_4_base_vmt,
	sum(hbw_da_4_alt_vmt) as hbw_da_4_alt_vmt,
	sum(hbw_da_4_base_rev) as hbw_da_4_base_rev,
	sum(hbw_da_4_alt_rev) as hbw_da_4_alt_rev,
	sum(hbw_da_4_base_unrel) as hbw_da_4_base_unrel,
	sum(hbw_da_4_alt_unrel) as hbw_da_4_alt_unrel,
	sum(hbw_da_4_time) as hbw_da_4_time,
	sum(hbw_da_4_dist) as hbw_da_4_dist,
	sum(hbw_da_4_toll) as hbw_da_4_toll,
	sum(hbw_da_4_unrel) as hbw_da_4_unrel,

	sum(nhbw_da_base_vht) as nhbw_da_base_vht,
	sum(nhbw_da_alt_vht) as nhbw_da_alt_vht,
	sum(nhbw_da_base_vmt) as nhbw_da_base_vmt,
	sum(nhbw_da_alt_vmt) as nhbw_da_alt_vmt,
	sum(nhbw_da_base_rev) as nhbw_da_base_rev,
	sum(nhbw_da_alt_rev) as nhbw_da_alt_rev,
	sum(nhbw_da_base_unrel) as nhbw_da_base_unrel,
	sum(nhbw_da_alt_unrel) as nhbw_da_alt_unrel,
	sum(nhbw_da_time) as nhbw_da_time,
	sum(nhbw_da_dist) as nhbw_da_dist,
	sum(nhbw_da_toll) as nhbw_da_toll,
	sum(nhbw_da_unrel) as nhbw_da_unrel,

	sum(all_sr2_base_vht) as all_sr2_base_vht,
	sum(all_sr2_alt_vht) as all_sr2_alt_vht,
	sum(all_sr2_base_vmt) as all_sr2_base_vmt,
	sum(all_sr2_alt_vmt) as all_sr2_alt_vmt,
	sum(all_sr2_base_rev) as all_sr2_base_rev,
	sum(all_sr2_alt_rev) as all_sr2_alt_rev,
	sum(all_sr2_base_unrel) as all_sr2_base_unrel,
	sum(all_sr2_alt_unrel) as all_sr2_alt_unrel,
	sum(all_sr2_time) as all_sr2_time,
	sum(all_sr2_dist) as all_sr2_dist,
	sum(all_sr2_toll) as all_sr2_toll,
	sum(all_sr2_unrel) as all_sr2_unrel,

	sum(all_sr3_base_vht) as all_sr3_base_vht,
	sum(all_sr3_alt_vht) as all_sr3_alt_vht,
	sum(all_sr3_base_vmt) as all_sr3_base_vmt,
	sum(all_sr3_alt_vmt) as all_sr3_alt_vmt,
	sum(all_sr3_base_rev) as all_sr3_base_rev,
	sum(all_sr3_alt_rev) as all_sr3_alt_rev,
	sum(all_sr3_base_unrel) as all_sr3_base_unrel,
	sum(all_sr3_alt_unrel) as all_sr3_alt_unrel,
	sum(all_sr3_time) as all_sr3_time,
	sum(all_sr3_dist) as all_sr3_dist,
	sum(all_sr3_toll) as all_sr3_toll,
	sum(all_sr3_unrel) as all_sr3_unrel,

	sum(vanpool_base_vht) as vanpool_base_vht,
	sum(vanpool_alt_vht) as vanpool_alt_vht,
	sum(vanpool_base_vmt) as vanpool_base_vmt,
	sum(vanpool_alt_vmt) as vanpool_alt_vmt,
	sum(vanpool_base_rev) as vanpool_base_rev,
	sum(vanpool_alt_rev) as vanpool_alt_rev,
	sum(vanpool_base_unrel) as vanpool_base_unrel,
	sum(vanpool_alt_unrel) as vanpool_alt_unrel,
	sum(vanpool_time) as vanpool_time,
	sum(vanpool_dist) as vanpool_dist,
	sum(vanpool_toll) as vanpool_toll,
	sum(vanpool_unrel) as vanpool_unrel,

	sum(lt_truck_base_vht) as lt_truck_base_vht,
	sum(lt_truck_alt_vht) as lt_truck_alt_vht,
	sum(lt_truck_base_vmt) as lt_truck_base_vmt,
	sum(lt_truck_alt_vmt) as lt_truck_alt_vmt,
	sum(lt_truck_base_rev) as lt_truck_base_rev,
	sum(lt_truck_alt_rev) as lt_truck_alt_rev,
	sum(lt_truck_base_unrel) as lt_truck_base_unrel,
	sum(lt_truck_alt_unrel) as lt_truck_alt_unrel,
	sum(lt_truck_time) as lt_truck_time,
	sum(lt_truck_dist) as lt_truck_dist,
	sum(lt_truck_toll) as lt_truck_toll,
	sum(lt_truck_unrel) as lt_truck_unrel,

	sum(md_truck_base_vht) as md_truck_base_vht,
	sum(md_truck_alt_vht) as md_truck_alt_vht,
	sum(md_truck_base_vmt) as md_truck_base_vmt,
	sum(md_truck_alt_vmt) as md_truck_alt_vmt,
	sum(md_truck_base_rev) as md_truck_base_rev,
	sum(md_truck_alt_rev) as md_truck_alt_rev,
	sum(md_truck_base_unrel) as md_truck_base_unrel,
	sum(md_truck_alt_unrel) as md_truck_alt_unrel,
	sum(md_truck_time) as md_truck_time,
	sum(md_truck_dist) as md_truck_dist,
	sum(md_truck_toll) as md_truck_toll,
	sum(md_truck_unrel) as md_truck_unrel,

	sum(hv_truck_base_vht) as hv_truck_base_vht,
	sum(hv_truck_alt_vht) as hv_truck_alt_vht,
	sum(hv_truck_base_vmt) as hv_truck_base_vmt,
	sum(hv_truck_alt_vmt) as hv_truck_alt_vmt,
	sum(hv_truck_base_rev) as hv_truck_base_rev,
	sum(hv_truck_alt_rev) as hv_truck_alt_rev,
	sum(hv_truck_base_unrel) as hv_truck_base_unrel,
	sum(hv_truck_alt_unrel) as hv_truck_alt_unrel,
	sum(hv_truck_time) as hv_truck_time,
	sum(hv_truck_dist) as hv_truck_dist,
	sum(hv_truck_toll) as hv_truck_toll,
	sum(hv_truck_unrel) as hv_truck_unrel,

	sum(bike_base_vht) as bike_base_vht,
	sum(bike_alt_vht) as bike_alt_vht,
	sum(bike_base_vmt) as bike_base_vmt,
	sum(bike_alt_vmt) as bike_alt_vmt,
	sum(bike_base_rev) as bike_base_rev,
	sum(bike_alt_rev) as bike_alt_rev,
	sum(bike_base_unrel) as bike_base_unrel,
	sum(bike_alt_unrel) as bike_alt_unrel,
	sum(bike_time) as bike_time,
	sum(bike_dist) as bike_dist,
	sum(bike_toll) as bike_toll,
	sum(bike_unrel) as bike_unrel,

	sum(walk_base_vht) as walk_base_vht,
	sum(walk_alt_vht) as walk_alt_vht,
	sum(walk_base_vmt) as walk_base_vmt,
	sum(walk_alt_vmt) as walk_alt_vmt,
	sum(walk_base_rev) as walk_base_rev,
	sum(walk_alt_rev) as walk_alt_rev,
	sum(walk_base_unrel) as walk_base_unrel,
	sum(walk_alt_unrel) as walk_alt_unrel,
	sum(walk_time) as walk_time,
	sum(walk_dist) as walk_dist,
	sum(walk_toll) as walk_toll,
	sum(walk_unrel) as walk_unrel,

	sum(hbw_dat_time) as hbw_dat_time,
	sum(hbw_dat_dist) as hbw_dat_dist,
	sum(hbw_dat_ivt) as hbw_dat_ivt,
	sum(hbw_wat_ivt) as hbw_wat_ivt,
	sum(nhbw_wat_ivt) as nhbw_wat_ivt,
	sum(hbw_dat_walk) as hbw_dat_walk,
	sum(hbw_wat_walk) as hbw_wat_walk,
	sum(nhbw_wat_walk) as nhbw_wat_walk,
	sum(hbw_dat_wait) as hbw_dat_wait,
	sum(hbw_wat_wait) as hbw_wat_wait,
	sum(nhbw_wat_wait) as nhbw_wat_wait,
	sum(hbw_dat_fare) as hbw_dat_fare,
	sum(hbw_wat_fare) as hbw_wat_fare,
	sum(nhbw_wat_fare) as nhbw_wat_fare,
	sum(parking) as parking,

	sum(hbw_da_1_base_trips) as hbw_da_1_base_trips,
	sum(hbw_da_2_base_trips) as hbw_da_2_base_trips,
	sum(hbw_da_3_base_trips) as hbw_da_3_base_trips,
	sum(hbw_da_4_base_trips) as hbw_da_4_base_trips,
	sum(nhbw_da_base_trips) as nhbw_da_base_trips,
	sum(all_sr2_base_trips) as all_sr2_base_trips,
	sum(all_sr3_base_trips) as all_sr3_base_trips,
	sum(vanpool_base_trips) as vanpool_base_trips,
	sum(lt_truck_base_trips) as lt_truck_base_trips,
	sum(md_truck_base_trips) as md_truck_base_trips,
	sum(hv_truck_base_trips) as hv_truck_base_trips,
	sum(bike_base_trips) as bike_base_trips,
	sum(walk_base_trips) as walk_base_trips,
	sum(hbw_da_1_alt_trips) as hbw_da_1_alt_trips,
	sum(hbw_da_2_alt_trips) as hbw_da_2_alt_trips,
	sum(hbw_da_3_alt_trips) as hbw_da_3_alt_trips,
	sum(hbw_da_4_alt_trips) as hbw_da_4_alt_trips,
	sum(nhbw_da_alt_trips) as nhbw_da_alt_trips,
	sum(all_sr2_alt_trips) as all_sr2_alt_trips,
	sum(all_sr3_alt_trips) as all_sr3_alt_trips,
	sum(vanpool_alt_trips) as vanpool_alt_trips,
	sum(lt_truck_alt_trips) as lt_truck_alt_trips,
	sum(md_truck_alt_trips) as md_truck_alt_trips,
	sum(hv_truck_alt_trips) as hv_truck_alt_trips,
	sum(bike_alt_trips) as bike_alt_trips,
	sum(walk_alt_trips) as walk_alt_trips
	from %s.benefits group by tod;""" % (alt, alt))
connection.commit()
print "added all-zone summary rows"

# do link-level benefits
SR3_OCC = 3.15 # Occupancy of shared-ride three plus vehicles
VP_OCC = 8.0 # Occupancy of vanpool vehicles

SPEED_RANGES = (0, 10, 20, 30, 40, 50, 60)
V_C_RANGES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75)

try:
	cursor.execute("DROP TABLE %s.link_benefits;" % alt)
except:
	pass
connection.commit()
cursor.execute("CREATE TABLE %s.link_benefits (LIKE public.link_benefits);" % alt)
connection.commit()
alternatives = (base, alt)
scenarios = (1002, 1003, 1004, 1005, 1006)
vol_factors = {1002 : 0.35, 1003 : 0.184, 1004 : 0.35, 1005 : 0.354, 1006 : 0.255}
variables = ('length', 'link_type', 'volume_delay_function', 'lanes', 'aux_transit_volume', 'auto_time',
	'additional_volume', 'ul1', 'ul2', 'ul3', 'toll_da', 'toll_2p', 'toll_3plus', 'toll_lt_truck', 'toll_med_truck', 
	'toll_hvy_truck', 'ferry_link', 'bridge_link', 'transit_persons', 'sov_volume', 'hbw1_sov_volume', 'hbw2_sov_volume', 
	'hbw3_sov_volume', 'hbw4_sov_volume', 'hov2_volume', 'hov3plus_volume', 'vanpool_volume', 'lt_truck_volume', 
	'med_truck_volume', 'hvy_truck_volume')
# vmt by speed range for pollution, vmt by fc by v/c range for accidents, unreliability benefits by user class in minutes
data = {}
for scenario in scenarios:
	data[scenario] = {}
	for user in ('hbw_da_1', 'hbw_da_2', 'hbw_da_3', 'hbw_da_4', 'nhbw_da', 'all_sr2', 'all_sr3', 'vanpool', 'lt_truck', 'md_truck', 'hv_truck'):
		data[scenario]['unr_' + user] = 0.0
	for i in range(0, len(SPEED_RANGES)):
		for veh in ('car', 'lt', 'mt', 'ht'):
			data[scenario]['base_' + veh + '_vmt_' + str(i)] = 0.0
			data[scenario]['alt_' + veh + '_vmt_' + str(i)] = 0.0
	for fc in range(1, 7):
		for i in range(0, len(V_C_RANGES)):
			data[scenario]['base_vmt_fc' + str(fc) + '_vc' + str(i)] = 0.0
			data[scenario]['alt_vmt_fc' + str(fc) + '_vc' + str(i)] = 0.0
	print 'Getting data for scenario', scenario, 'at', datetime.datetime.now() - start
	links = {}
	for alternative in alternatives:
		links[alternative] = {}
		query = "select i_node, j_node, "
		for variable in variables:
			query = query + variable + ', '
		query = query[:-2] + " from %s.links where scenario = %s;" % (alternative, scenario)
		cursor.execute(query)
		result = cursor.fetchall()
		for link in result:
			links[alternative][(link[0], link[1])] = {}
			for i in range(0, len(variables)):
				links[alternative][(link[0], link[1])][variables[i]] = link[i + 2]
	print 'Processing data for scenario', scenario, 'at', datetime.datetime.now() - start
	for link in links[alt].keys():
		alt_data = links[alt][link]
		if link in links[base].keys():
			base_data = links[base][link]
		else:
			base_data = {}
			for variable in variables:
				base_data[variable] = 0
		if (alt_data['length'] > 0) and (alt_data['ul3'] > 0):
			base_speed = base_data['length'] / (max(0.1, base_data['auto_time']) / 60.0)
			alt_speed = alt_data['length'] / (max(0.1, alt_data['auto_time']) / 60.0)
			base_volume = ((base_data['sov_volume'] + base_data['hov2_volume'] + base_data['hov3plus_volume'] + base_data['vanpool_volume'] 
				+ base_data['lt_truck_volume'] + base_data['med_truck_volume'] * 1.5 + base_data['hvy_truck_volume'] * 2) * vol_factors[scenario]
				* base_data['lanes'])
			alt_volume = ((alt_data['sov_volume'] + alt_data['hov2_volume'] + alt_data['hov3plus_volume'] + alt_data['vanpool_volume'] 
				+ alt_data['lt_truck_volume'] + alt_data['med_truck_volume'] * 1.5 + alt_data['hvy_truck_volume'] * 2) * vol_factors[scenario]
				* alt_data['lanes'])
			if base_data['ul1'] > 0 and link[0] > 1200 and link[1] > 1200:
				base_vc = base_volume / (base_data['ul1'] * base_data['lanes'])
			else:
				base_vc = 0
			if alt_data['ul1'] > 0 and link[0] > 1200 and link[1] > 1200:
				alt_vc = alt_volume / (alt_data['ul1'] * alt_data['lanes'])
			else:
				alt_vc = 0
			for i in range(0, len(SPEED_RANGES)):
				if base_speed >= SPEED_RANGES[i]:
					base_speed_range = i
				if alt_speed >= SPEED_RANGES[i]:
					alt_speed_range = i
			data[scenario]['base_car_vmt_' + str(base_speed_range)] += base_data['length'] * (base_data['sov_volume'] + base_data['hov2_volume'] 
				+ base_data['hov3plus_volume'] + base_data['vanpool_volume'])
			data[scenario]['base_lt_vmt_' + str(base_speed_range)] += base_data['length'] * base_data['lt_truck_volume']
			data[scenario]['base_mt_vmt_' + str(base_speed_range)] += base_data['length'] * base_data['med_truck_volume']
			data[scenario]['base_ht_vmt_' + str(base_speed_range)] += base_data['length'] * base_data['hvy_truck_volume']
			data[scenario]['alt_car_vmt_' + str(alt_speed_range)] += alt_data['length'] * (alt_data['sov_volume'] + alt_data['hov2_volume'] 
				+ alt_data['hov3plus_volume'] + alt_data['vanpool_volume'])
			data[scenario]['alt_lt_vmt_' + str(alt_speed_range)] += alt_data['length'] * alt_data['lt_truck_volume']
			data[scenario]['alt_mt_vmt_' + str(alt_speed_range)] += alt_data['length'] * alt_data['med_truck_volume']
			data[scenario]['alt_ht_vmt_' + str(alt_speed_range)] += alt_data['length'] * alt_data['hvy_truck_volume']
			for i in range(0, len(V_C_RANGES)):
				if base_vc >= V_C_RANGES[i]:
					base_vc_range = i
				if alt_vc >= V_C_RANGES[i]:
					alt_vc_range = i
			if int(base_data['ul3']) > 0:
				data[scenario]['base_vmt_fc' + str(int(base_data['ul3'])) + '_vc' + str(base_vc_range)] += base_data['length'] * (base_data['sov_volume'] + base_data['hov2_volume'] 
					+ base_data['hov3plus_volume'] + base_data['vanpool_volume'] + base_data['lt_truck_volume'] + base_data['med_truck_volume'] + base_data['hvy_truck_volume'])
			if int(alt_data['ul3']) > 0:
				data[scenario]['alt_vmt_fc' + str(int(alt_data['ul3'])) + '_vc' + str(alt_vc_range)] += alt_data['length'] * (alt_data['sov_volume'] + alt_data['hov2_volume'] 
					+ alt_data['hov3plus_volume'] + alt_data['vanpool_volume'] + alt_data['lt_truck_volume'] + alt_data['med_truck_volume'] + alt_data['hvy_truck_volume'])
print 'Finished at', datetime.datetime.now() - start
tods = {1002 : 'am', 1003 : 'md', 1004 : 'pm', 1005 : 'ev', 1006 : 'ni'}
for scenario in scenarios:
	keys = data[scenario].keys()
	keys.sort()
	for key in keys:
		# print scenario, key, data[scenario][key]
		cursor.execute("INSERT INTO %s.link_benefits (tod, variable, value) VALUES (\'%s\', \'%s\', %f);" % (alt, tods[scenario], key, data[scenario][key]))
	connection.commit()


finish = datetime.datetime.now()
print finish - start
connection.close()
