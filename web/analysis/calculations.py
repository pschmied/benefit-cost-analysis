from psrc.analysis.models import *
import datetime
from string import join

def calc_basic(analysis_id, dynamic=0, all_regions=1):
	#get analysis object
	analysis = Analysis.objects.get(pk=analysis_id)
	temp = AnalysisTOD.objects.filter(analysis=analysis_id).values()
	analysis_tod = {}
	tods = ['am', 'md', 'pm', 'ev', 'ni', 'all']
	for i in temp:
		analysis_tod[i['field']] = i
		total = 0
		for tod in i.keys():
			if tod != 'field':
				total += i[tod]
		#use average for all tod
		analysis_tod[i['field']]['all'] = total/5
		
	#query benefits for scenario and region
	if dynamic:
		scenario_name = analysis.out_year
		year = analysis.out_year.split('_')[1][:4]
	else:
		scenario_name = analysis.scenario
		year = analysis.scenario.split('_')[1][:4]
		
	if all_regions:
		benefits = get_benefits(scenario_name, 1)
		region_id = 1
	else:
		benefits = get_benefits(scenario_name, analysis.region_id)
		region_id = analysis.region_id
		
	results = {}
	benefit_results = {}
	accounting_results = {}
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.datetime.now().year
	real_year = 2000
	
	nhbw_wat = {'am':0.2424, 'md':0.6756, 'pm':0.3910, 'ev':0.2237, 'ni':0.0328, 'all':1.5655}
	hbw_wat = {'am':0.9275, 'md':0.1372, 'pm':0.8179, 'ev':0.2543, 'ni':0.0960, 'all':2.2329}
	hbw_dat = {'am':0.7143, 'md':0.1483, 'pm':0.7102, 'ev':0.2308, 'ni':0.1954, 'all':2.0000}
	
	for tod in benefits.keys():
		benefit_results[tod] = {}
		accounting_results[tod] = {}
		for i in benefits[tod].keys():
			spl = i.split('_')
			if i != 'parking':
				acct_user_class = join(spl[:-2],'_')
				ben_user_class = join(spl[:-1],'_')
			else:
				acct_user_class = 'all'
				ben_user_class = 'all'
	
			#convert minutes to hours to dollars 
			if spl[-1] in ['vht', 'time', 'unrel', 'ivt', 'walk', 'wait', 'toll', 'rev']:
				if spl[-1] == 'vht':
					if not accounting_results[tod].has_key(acct_user_class):
						accounting_results[tod][acct_user_class] = {}
					if not accounting_results[tod][acct_user_class].has_key(spl[-1]):
						accounting_results[tod][acct_user_class][spl[-1]] = {}
					accounting_results[tod][acct_user_class][spl[-1]][spl[-2]] = (benefits[tod][i] / 60.0)
				
				else:
					if spl[0] == 'hbw' and spl[1] == 'da':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['hbw_drive_income_%s' %(spl[2])][tod]
					#	if spl[2] == '1':
					#		benefit = (benefits[tod][i] / 60.0) * analysis_tod[i][tod] #* analysis.hbw_drive_income_1
					#	elif spl[2] == '2':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.hbw_drive_income_2
					#	elif spl[2] == '3':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.hbw_drive_income_3
					#	elif spl[2] == '4':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.hbw_drive_income_4
					elif spl[0] == 'nhbw' and spl[1] == 'da':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['other_driving'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.other_driving
					elif spl[0] == 'all' and spl[1] == 'sr2':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['sr2_income'][tod]
					#	if tod == 'am':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr2_income_am
					#	elif tod == 'md':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr2_income_md
					#	elif tod == 'pm':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr2_income_pm
					#	elif tod == 'ev':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr2_income_ev
					#	elif tod == 'ni':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr2_income_ni
					#	#if spl[-1] == 'time':
					#	#	 benefit *= 2.0
					elif spl[0] == 'all' and spl[1] == 'sr3':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['sr3_income'][tod]
					#	if tod == 'am':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr3_income_am
					#	elif tod == 'md':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr3_income_md
					#	elif tod == 'pm':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr3_income_pm
					#	elif tod == 'ev':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr3_income_ev
					#	elif tod == 'ni':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.sr3_income_ni
					#	#if spl[-1] == 'time':
					#	#	 benefit *= 3.15
					elif spl[0] == 'vanpool':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['vanpool_income'][tod]
					#	if tod == 'am':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.vanpool_income_am
					#	elif tod == 'md':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.vanpool_income_md
					#	elif tod == 'pm':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.vanpool_income_pm
					#	elif tod == 'ev':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.vanpool_income_ev
					#	elif tod == 'ni':
					#		benefit = (benefits[tod][i] / 60.0) * analysis.vanpool_income_ni
					#	#if spl[-1] == 'time':
					#	#	 benefit *= 8.0
					elif spl[0] == 'lt' and spl[1] == 'truck':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['light_trucks_time'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.light_trucks_time
					elif spl[0] == 'md' and spl[1] == 'truck':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['medium_trucks_time'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.medium_trucks_time
					elif spl[0] == 'hv' and spl[1] == 'truck':
						benefit = (benefits[tod][i] / 60.0) * analysis_tod['heavy_trucks_time'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.heavy_trucks_time
					elif spl[0] == 'bike':
						 benefit = (benefits[tod][i] / 60.0) * analysis_tod['bike_time'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.bike_time
					elif spl[0] == 'walk':
						 benefit = (benefits[tod][i] / 60.0) * analysis_tod['walk_time'][tod]
					#	benefit = (benefits[tod][i] / 60.0) * analysis.walk_time
					elif spl[0] == 'hbw' and spl[1] == 'wat' and tod != 'all':
						if spl[2] == 'ivt':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_ivt'][tod] * hbw_wat[tod]
						elif spl[2] == 'walk':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_walk'][tod] * hbw_wat[tod]
						elif spl[2] == 'wait':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_wait'][tod] * hbw_wat[tod]
					elif spl[0] == 'nhbw' and spl[1] == 'wat' and tod != 'all':
						if spl[2] == 'ivt':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_ivt'][tod] * nhbw_wat[tod]
						elif spl[2] == 'walk':						
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_walk'][tod] * nhbw_wat[tod]
						elif spl[2] == 'wait':						
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_wait'][tod] * nhbw_wat[tod]
					elif spl[0] == 'hbw' and spl[1] == 'dat' and tod != 'all':
						if spl[2] == 'ivt':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_ivt'][tod] * hbw_dat[tod]
						elif spl[2] == 'walk':						
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_walk'][tod] * hbw_dat[tod]
						elif spl[2] == 'wait':						
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_wait'][tod] * hbw_dat[tod]
						elif spl[2] == 'time':
							benefit = (benefits['all'][i] / 60.0) * analysis_tod['other_transit_ivt'][tod] * hbw_dat[tod]
					
					#debug stuff
					#try:
					#	spl2 = spl[2]
					#except:
					#	spl2 = 'n/a'
					#print '%s, %s, %s, %s, %s, %s, %s, %s, %s' %(tod, i, spl[0], spl[1], spl2, spl[-1], ben_user_class, benefits[tod][i], benefit)
					
					if spl[-1] == 'toll':
						if not benefit_results[tod].has_key(ben_user_class):
							benefit_results[tod][ben_user_class] = {}
						if not benefit_results[tod][ben_user_class].has_key('toll_benefit'):
							benefit_results[tod][ben_user_class]['toll_benefit'] = benefit
						else:
							benefit_results[tod][ben_user_class]['toll_benefit'] += benefit
					elif spl[-1] == 'rev':
						if not accounting_results[tod].has_key(acct_user_class):
							accounting_results[tod][acct_user_class] = {}
						if not accounting_results[tod][acct_user_class].has_key(spl[-1]):
							accounting_results[tod][acct_user_class][spl[-1]] = {}
						accounting_results[tod][acct_user_class][spl[-1]][spl[-2]] = benefit
					elif spl[-1] == 'unrel':
						if spl[-2] in ('base', 'alt'):
							if not accounting_results[tod].has_key(acct_user_class):
								accounting_results[tod][acct_user_class] = {}
							if not accounting_results[tod][acct_user_class].has_key(spl[-1]):
								accounting_results[tod][acct_user_class][spl[-1]] = {}
							accounting_results[tod][acct_user_class][spl[-1]][spl[-2]] = benefit
						else:
							if not benefit_results[tod].has_key(ben_user_class):
								benefit_results[tod][ben_user_class] = {}
							if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
								benefit_results[tod][ben_user_class]['unreliability_benefit'] = benefit
							else:
								benefit_results[tod][ben_user_class]['unreliability_benefit'] += benefit
					else:
						if not benefit_results[tod].has_key(ben_user_class):
							benefit_results[tod][ben_user_class] = {}
						if not benefit_results[tod][ben_user_class].has_key('time_benefit'):
							benefit_results[tod][ben_user_class]['time_benefit'] = benefit
						else:
							benefit_results[tod][ben_user_class]['time_benefit'] += benefit
						#if spl[0] == 'hbw' and spl[1] == 'da':
						#	print '%s, %s, %s, %s, %s, %s, %s, %s, %s' %(tod, i, spl[0], spl[1], spl2, spl[-1], ben_user_class, benefits[tod][i], benefit)
			
			#convert miles to dollars
			elif spl[-1] in ['vmt', 'dist']:
				if spl[-1] == 'vmt':
					if not accounting_results[tod].has_key(acct_user_class):
						accounting_results[tod][acct_user_class] = {}
					if not accounting_results[tod][acct_user_class].has_key(spl[-1]):
						accounting_results[tod][acct_user_class][spl[-1]] = {}
					accounting_results[tod][acct_user_class][spl[-1]][spl[-2]] = benefits[tod][i]
				else:
					if spl[0] == 'lt' and spl[1] == 'truck':
						operating_cost_benefit= benefits[tod][i] * analysis.light_trucks_cost
					elif spl[0] == 'md' and spl[1] == 'truck':
						operating_cost_benefit = benefits[tod][i] * analysis.medium_trucks_cost
					elif spl[0] == 'hv' and spl[1] == 'truck':
						operating_cost_benefit = benefits[tod][i] * analysis.heavy_trucks_cost
					elif spl[0] == 'bike':
						operating_cost_benefit = benefits[tod][i] * 0.0
					elif spl[0] == 'walk':
						operating_cost_benefit = benefits[tod][i] * 0.0
					else:
						operating_cost_benefit = benefits[tod][i] * analysis.auto_cost
					
					
					if not benefit_results[tod].has_key(ben_user_class):
						benefit_results[tod][ben_user_class] = {}
					if not benefit_results[tod][ben_user_class].has_key('operating_cost_benefit'):
						benefit_results[tod][ben_user_class]['operating_cost_benefit'] = operating_cost_benefit
					else:
						benefit_results[tod][ben_user_class]['operating_cost_benefit'] += operating_cost_benefit
			
			#convert cents to dollars
			elif spl[-1] in ['fare', 'parking']:
				if spl[-1] == 'fare':
					if not benefit_results[tod].has_key(ben_user_class):
						benefit_results[tod][ben_user_class] = {}
					if not benefit_results[tod][ben_user_class].has_key('fare_benefit'):
						benefit_results[tod][ben_user_class]['fare_benefit'] = (benefits[tod][i] / 100.0)
					else:
						benefit_results[tod][ben_user_class]['fare_benefit'] += (benefits[tod][i] / 100.0)
				
				elif spl[-1] == 'parking':
					if not benefit_results[tod].has_key(ben_user_class):
						benefit_results[tod][ben_user_class] = {}
					if not benefit_results[tod][ben_user_class].has_key('parking_benefit'):
						benefit_results[tod][ben_user_class]['parking_benefit'] = (benefits[tod][i] / 100.0)
					else:
						benefit_results[tod][ben_user_class]['parking_benefit'] += (benefits[tod][i] / 100.0)
						
			
			elif spl[-1] in ['trips']:
				if not accounting_results[tod].has_key(acct_user_class):
					accounting_results[tod][acct_user_class] = {}
				if not accounting_results[tod][acct_user_class].has_key(spl[-1]):
					accounting_results[tod][acct_user_class][spl[-1]] = {}
				accounting_results[tod][acct_user_class][spl[-1]][spl[-2]] = benefits[tod][i]
	#print 'just after calcs:'
	#print benefit_results['am']
	
	
	##Old unreliability code from when in link_benefits table
	##unreliability benefits
	#if dynamic:
	#	alt = analysis.out_year
	#else:
	#	alt = analysis.scenario
	#base = 'base_' + alt[-4:]
	#data = get_unreliability(alt,base)
	#tod_convert = {1002:'am',1003:'md',1004:'pm',1005:'ev',1006:'ni',1007:'all'}
	#
	##convert and save
	#for scenario in data.keys():
	#	tod = tod_convert[scenario]
	#	if not results.has_key(tod):
	#		results[tod] = {}
	#	for i in data[scenario].keys():
	#		spl = i.split('_')
	#		ben_user_class = join(spl[1:],'_')
	#		if not benefit_results[tod].has_key(ben_user_class):
	#			benefit_results[tod][ben_user_class] = {}
	#		if spl[1] == 'hbw' and spl[2] == 'da':
	#			if spl[3] == '1':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.hbw_drive_income_1
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.hbw_drive_income_1
	#			elif spl[3] == '2':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.hbw_drive_income_2
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.hbw_drive_income_2
	#			elif spl[3] == '3':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.hbw_drive_income_3
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.hbw_drive_income_3
	#			elif spl[3] == '4':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.hbw_drive_income_4
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.hbw_drive_income_4
	#		elif spl[1] == 'nhbw' and spl[2] == 'da':
	#			if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.other_driving
	#			else:
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.other_driving
	#		elif spl[1] == 'all' and spl[2] == 'sr2':
	#			if tod == 'am':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr2_income_am
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr2_income_am
	#			elif tod == 'md':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr2_income_md
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr2_income_md
	#			elif tod == 'pm':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr2_income_pm
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr2_income_pm
	#			elif tod == 'ev':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr2_income_ev
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr2_income_ev
	#			elif tod == 'ni':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr2_income_nt
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr2_income_nt
	#		elif spl[1] == 'all' and spl[2] == 'sr3':
	#			if tod == 'am':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr3_income_am
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr3_income_am
	#			elif tod == 'md':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr3_income_md
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr3_income_md
	#			elif tod == 'pm':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr3_income_pm
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr3_income_pm
	#			elif tod == 'ev':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr3_income_ev
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr3_income_ev
	#			elif tod == 'ni':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.sr3_income_nt
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.sr3_income_nt
	#		elif spl[1] == 'vanpool':
	#			if tod == 'am':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.vanpool_income_am
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.vanpool_income_am
	#			elif tod == 'md':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.vanpool_income_md
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.vanpool_income_md
	#			elif tod == 'pm':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.vanpool_income_pm
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.vanpool_income_pm
	#			elif tod == 'ev':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.vanpool_income_ev
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.vanpool_income_ev
	#			elif tod == 'ni':
	#				if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.vanpool_income_nt
	#				else:
	#					benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.vanpool_income_nt
	#		elif spl[1] == 'lt' and spl[2] == 'truck':
	#			if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.light_trucks_time
	#			else:
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.light_trucks_time
	#		elif spl[1] == 'md' and spl[2] == 'truck':
	#			if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.medium_trucks_time
	#			else:
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.medium_trucks_time
	#		elif spl[1] == 'hv' and spl[2] == 'truck':
	#			if not benefit_results[tod][ben_user_class].has_key('unreliability_benefit'):
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] = (data[scenario][i]) * analysis.heavy_trucks_time
	#			else:
	#				benefit_results[tod][ben_user_class]['unreliability_benefit'] += (data[scenario][i]) * analysis.heavy_trucks_time
	
	#calculate 'all' tod
	for uc in benefit_results['all'].keys():
		for tod in benefit_results.keys():
			if tod != 'all':
				for field in BenefitResult._meta.fields:
					if field.name[-7:] == 'benefit':
						#if not benefit_results['all'].has_key(uc):
						#	benefit_results['all'][uc] = {}
						if not benefit_results['all'][uc].has_key(field.name):
							benefit_results['all'][uc][field.name] = benefit_results[tod][uc].get(field.name, 0.0)
						else:
							benefit_results['all'][uc][field.name] += benefit_results[tod][uc].get(field.name, 0.0)
			
	for uc in accounting_results['all'].keys():
		for var in accounting_results['all'][uc].keys():
			for tod in accounting_results.keys():
				if tod != 'all':
					accounting_results['all'][uc][var]['base'] += accounting_results[tod][uc][var]['base']
					accounting_results['all'][uc][var]['alt'] += accounting_results[tod][uc][var]['alt']
	
	#calculate 'all' user class
	for tod in benefit_results.keys():
		for uc in benefit_results[tod].keys():
			if uc != 'all':
				for field in BenefitResult._meta.fields:
					if field.name[-7:] == 'benefit':
						if not benefit_results[tod]['all'].has_key(field.name):
							benefit_results[tod]['all'][field.name] = benefit_results[tod][uc].get(field.name, 0.0)
						else:
							benefit_results[tod]['all'][field.name] += benefit_results[tod][uc].get(field.name, 0.0)
	
	for tod in accounting_results.keys():
		if not accounting_results[tod].has_key('all'):
			accounting_results[tod]['all'] = {}
		for uc in accounting_results[tod].keys():
			if uc != 'all':
				for var in accounting_results[tod][uc].keys():
					if not accounting_results[tod]['all'].has_key(var):
						accounting_results[tod]['all'][var] = {'base':0.0,'alt':0.0}
					accounting_results[tod]['all'][var]['base'] += accounting_results[tod][uc][var]['base']
					accounting_results[tod]['all'][var]['alt'] += accounting_results[tod][uc][var]['alt']
				
	#print 'just before save:'
	#print benefit_results['all'] 
	#convert all benefits to base year dollars and save
	if not dynamic and all_regions:
		BenefitResult.objects.filter(analysis=analysis_id).delete()
	for tod in benefit_results.keys():
		for uc in benefit_results[tod].keys():
			benefit_result = BenefitResult()
			benefit_result.analysis = analysis
			benefit_result.year = year
			benefit_result.tod = tod
			benefit_result.user_class = uc
			benefit_result.region = Region.objects.get(pk=region_id)
			for field in BenefitResult._meta.fields:
				if field.name[-7:] == 'benefit':
					#value = benefit_results[tod][uc].get(field.name, 0.0)
					if field.name.split('_')[0] in ['time', 'toll']:
						value = benefit_results[tod][uc].get(field.name, 0.0)*((1 + analysis.inflation_rate)*(1 + analysis.growth_rate))**(base_year-2000)
					else:
						value = benefit_results[tod][uc].get(field.name, 0.0)*(1 + analysis.inflation_rate)**(base_year-2000)
					setattr(benefit_result, field.name, value)
					
			benefit_result.save()
	
	
	if not dynamic and all_regions:
		AccountingResult.objects.filter(analysis=analysis_id).delete()
	for tod in accounting_results.keys():
		for uc in accounting_results[tod].keys():
			for var in accounting_results[tod][uc].keys():
				accounting_result = AccountingResult()
				accounting_result.analysis = analysis
				accounting_result.year = year
				accounting_result.tod = tod
				accounting_result.user_class = uc
				accounting_result.region = Region.objects.get(pk=region_id)
				accounting_result.variable = var
				accounting_result.base = accounting_results[tod][uc][var]['base']
				accounting_result.alt = accounting_results[tod][uc][var]['alt']
				if var == 'rev':
					accounting_result.base *= ((1 + analysis.inflation_rate)*(1 + analysis.growth_rate))**(base_year-real_year)
					accounting_result.alt *= ((1 + analysis.inflation_rate)*(1 + analysis.growth_rate))**(base_year-real_year)
				accounting_result.difference = accounting_result.alt - accounting_result.base
				if accounting_result.base > 0.0:
					accounting_result.percent_different = (accounting_result.difference / accounting_result.base)
				else:
					accounting_result.percent_different = 0.0
				
				accounting_result.save()
	return None

def calc_emissions(analysis_id, dynamic=0):
	#get analysis object
	analysis = Analysis.objects.get(pk=analysis_id)
	#get emission inputs
	emission_inputs_objects = EmissionInput.objects.filter(analysis=analysis_id).values()
	emission_cost_inputs_objects = EmissionCostInput.objects.filter(analysis=analysis_id).values()
	#query link benefits for scenario
	if dynamic:
		scenario_name = analysis.out_year
		year = analysis.out_year.split('_')[1][:4]
	else:
		scenario_name = analysis.scenario
		year = analysis.scenario.split('_')[1][:4]
	link_benefits = get_link_benefits(scenario_name)
	results = {}
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.datetime.now().year
	real_year = 2000
	
	emission_inputs = {}
	for p in emission_inputs_objects:
		if not emission_inputs.has_key(p['pollutant_id']):
			emission_inputs[p['pollutant_id']] = {}
		emission_inputs[p['pollutant_id']][p['speed_class']] = p
	
	emission_cost_inputs = {}
	for p in emission_cost_inputs_objects:
		emission_cost_inputs[p['pollutant_id']] = p['cost']
		
	
	speed_classes = [0,10,20,30,40,50,60]
	vehicle_types = {'car':'car','lt':'light_truck','mt':'medium_truck','ht':'heavy_truck'}
	
	for tod in link_benefits.keys():
		for i in link_benefits[tod].keys():
			spl = i.split('_')
			if len(spl) > 2 and spl[2] == 'vmt':
				vt = vehicle_types[spl[1]]
				sc = speed_classes[int(spl[3])]
				if not results.has_key(vt):
					results[vt] = {}
				if not results[vt].has_key(sc):
					results[vt][sc] = {}
				
				for p in emission_inputs.keys():
					if not results[vt][sc].has_key(p):
						results[vt][sc][p] = {'base_tons':0.0, 'alt_tons':0.0}
					if spl[0] == 'base':
						results[vt][sc][p]['base_tons'] += (link_benefits[tod][i] * emission_inputs[p][sc][vt]) / 1000000
					elif spl[0] == 'alt':
						results[vt][sc][p]['alt_tons'] += (link_benefits[tod][i] * emission_inputs[p][sc][vt]) / 1000000
				
	if not dynamic:
		EmissionResult.objects.filter(analysis=analysis_id).delete()
	for vt in results.keys():
		for sc in results[vt].keys():
			for p in results[vt][sc].keys():
				result = EmissionResult()
				result.analysis = analysis
				result.year = year
				result.vehicle_type = vt
				result.speed_class = sc
				result.pollutant_id = p
				result.base_tons = results[vt][sc][p]['base_tons']
				result.alt_tons = results[vt][sc][p]['alt_tons']
				base_cost = results[vt][sc][p]['base_tons'] * emission_cost_inputs[p] * (1 + analysis.inflation_rate)**(base_year-real_year)
				alt_cost = results[vt][sc][p]['alt_tons'] * emission_cost_inputs[p] * (1 + analysis.inflation_rate)**(base_year-real_year)
				result.base_cost = base_cost
				result.alt_cost = alt_cost
				result.difference = alt_cost - base_cost
				if base_cost > 0:
					result.percent_different = result.difference / base_cost
				else:
					result.percent_different = 0.0
				result.save()
	
	return None

def calc_accidents(analysis_id, dynamic=0):
	#get analysis object
	analysis = Analysis.objects.get(pk=analysis_id)
	#get accident inputs
	accident_inputs_objects = AccidentInput.objects.filter(analysis=analysis_id).values()
	#query link benefits for scenario
	if dynamic:
		scenario_name = analysis.out_year
		year = analysis.out_year.split('_')[1][:4]
	else:
		scenario_name = analysis.scenario
		year = analysis.scenario.split('_')[1][:4]
	link_benefits = get_link_benefits(scenario_name)
	results = {}
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.datetime.now().year
	real_year = 2000
	
	accident_inputs = {}
	for vc in accident_inputs_objects:
		if not accident_inputs.has_key(vc['vc_range']):
			accident_inputs[vc['vc_range']] = {}
		accident_inputs[vc['vc_range']][vc['functional_class']] = vc

	accident_types = ['property_damage_only','injury','fatality']
		
	functional_classes = {'fc1':1,'fc2':2,'fc3':3,'fc4':4,'fc6':6}
	vc_range = {'vc0':'0.0','vc1':'0.25','vc2':'0.5','vc3':'0.75','vc4':'1.0','vc5':'1.25','vc6':'1.5','vc7':'1.75'}
	
	for tod in link_benefits.keys():
		results[tod] = {}
		for i in link_benefits[tod].keys():
			spl = i.split('_')
			if spl[1] == 'vmt' and spl[2] != 'fc5':
				fc = functional_classes[spl[2]]
				vc = vc_range[spl[3]]
				#vc = spl[3]
				if not results[tod].has_key(fc):
					results[tod][fc] = {}
				if not results[tod][fc].has_key(vc):
					results[tod][fc][vc] = {}
				for at in accident_types:
					if not results[tod][fc][vc].has_key(at):
						results[tod][fc][vc][at] = {'alt':0.0, 'base':0.0, 'net':0.0}
					if spl[0] == 'alt':
						results[tod][fc][vc][at]['alt'] += (link_benefits[tod][i] * accident_inputs[vc][fc][at])
					elif spl[0] == 'base':
						results[tod][fc][vc][at]['base'] += (link_benefits[tod][i] * accident_inputs[vc][fc][at])
				
	if not dynamic:
		AccidentResult.objects.filter(analysis=analysis_id).delete()
	for tod in results.keys():
		for fc in results[tod].keys():
			for vc in results[tod][fc].keys():
				result = AccidentResult()
				result.analysis = analysis
				result.year = year
				result.tod = tod
				result.functional_class = fc
				result.vc_range = vc
				result.property_damage_only_benefit = (results[tod][fc][vc]['property_damage_only']['base'] - results[tod][fc][vc]['property_damage_only']['alt']) / 1000000 * analysis.property_damage_only * (1 + analysis.inflation_rate)**(base_year-real_year)
				result.property_damage_only_quantity_base = results[tod][fc][vc]['property_damage_only']['base'] / 1000000
				result.property_damage_only_quantity_alt = results[tod][fc][vc]['property_damage_only']['alt'] / 1000000
				
				result.injury_benefit = (results[tod][fc][vc]['injury']['base'] - results[tod][fc][vc]['injury']['alt']) / 1000000 * analysis.injury * (1 + analysis.inflation_rate)**(base_year-real_year)
				result.injury_quantity_base = results[tod][fc][vc]['injury']['base'] / 1000000
				result.injury_quantity_alt = results[tod][fc][vc]['injury']['alt'] / 1000000
				
				result.fatality_benefit = (results[tod][fc][vc]['fatality']['base'] - results[tod][fc][vc]['fatality']['alt']) * (1 + analysis.inflation_rate)**(base_year-real_year)
				result.fatality_quantity_base = results[tod][fc][vc]['fatality']['base'] / 1000000
				result.fatality_quantity_alt = results[tod][fc][vc]['fatality']['alt'] / 1000000
				result.save()
				
	return None 

def interpolate(analysis_id):
	#get analysis object
	analysis = Analysis.objects.get(pk=analysis_id)
	out_year = int(analysis.out_year.split('_')[1][:4])
	base_year = int(analysis.scenario.split('_')[1][:4])
	end_year = analysis.end_year
	benefits = {}
	benefits[base_year] = {}
	benefits[out_year] = {}
	# fill benefits for base year and out year benefits[year][region][tod][user_class][benefit]
	benefit_results = BenefitResult.objects.filter(analysis=analysis.id).values()
	for results in benefit_results:
		if not benefits[results['year']].has_key(results['region_id']):
			benefits[results['year']][results['region_id']] = {}
		if not benefits[results['year']][results['region_id']].has_key(results['tod']):
			benefits[results['year']][results['region_id']][results['tod']] = {}
		if not benefits[results['year']][results['region_id']][results['tod']].has_key(results['user_class']):
			benefits[results['year']][results['region_id']][results['tod']][results['user_class']] = {}
		for benefit in ('time_benefit', 'operating_cost_benefit', 'toll_benefit', 'fare_benefit', 'parking_benefit', 'unreliability_benefit'):
			benefits[results['year']][results['region_id']][results['tod']][results['user_class']][benefit] = results[benefit]
	#print benefits
	
	accounting = {}
	accounting[base_year] = {}
	accounting[out_year] = {}
	# fill accounting for base year and out year accounting[year][region][tod][user_class][account][run]
	accounting_results = AccountingResult.objects.filter(analysis=analysis.id).values()
	for results in accounting_results:
		if not accounting[results['year']].has_key(results['region_id']):
			accounting[results['year']][results['region_id']] = {}
		if not accounting[results['year']][results['region_id']].has_key(results['tod']):
			accounting[results['year']][results['region_id']][results['tod']] = {}
		if not accounting[results['year']][results['region_id']][results['tod']].has_key(results['user_class']):
			accounting[results['year']][results['region_id']][results['tod']][results['user_class']] = {}
		if not accounting[results['year']][results['region_id']][results['tod']][results['user_class']].has_key('variable'):
			accounting[results['year']][results['region_id']][results['tod']][results['user_class']][results['variable']] = {}
		accounting[results['year']][results['region_id']][results['tod']][results['user_class']][results['variable']]['base'] = results['base']
		accounting[results['year']][results['region_id']][results['tod']][results['user_class']][results['variable']]['alt'] = results['alt']
		
	growth_rates = {}
	regions = benefits[base_year].keys()
	import math
	for region in regions:
		growth_rates[region] = {}
		for tod in ('am', 'md', 'pm', 'ev', 'ni', 'all'):
			growth_rates[region][tod] = {}
			for user_class in ('all_sr2', 'all_sr3', 'bike', 'hbw_da_1', 'hbw_da_2', 'hbw_da_3', 'hbw_da_4', 'hbw_dat', 'hbw_wat', 'hv_truck', 'lt_truck', 'md_truck', 'nhbw_da', 'nhbw_wat', 'vanpool', 'walk', 'all'):
				growth_rates[region][tod][user_class] = {}
				for benefit in ('time_benefit', 'operating_cost_benefit', 'toll_benefit', 'fare_benefit', 'parking_benefit', 'unreliability_benefit'):
					if benefits[base_year][region][tod][user_class][benefit] == 0:
						benefits[base_year][region][tod][user_class][benefit] = 1.0
					if benefits[out_year][region][tod][user_class][benefit] == 0:
						benefits[out_year][region][tod][user_class][benefit] = 1.0
					if benefits[out_year][region][tod][user_class][benefit] > 0 and benefits[base_year][region][tod][user_class][benefit] > 0:
						growth_rates[region][tod][user_class][benefit] = (math.log(benefits[out_year][region][tod][user_class][benefit]) - math.log(benefits[base_year][region][tod][user_class][benefit])) / (out_year - base_year)
					else:
						growth_rates[region][tod][user_class][benefit] = 0.0
				if user_class not in ('hbw_dat', 'hbw_wat', 'nhbw_wat'):
					for account in ('rev', 'trips', 'vht', 'vmt'):
						growth_rates[region][tod][user_class][account] = {}
						for run in ('alt', 'base'):
							if accounting[base_year][region][tod][user_class][account][run] == 0:
								accounting[base_year][region][tod][user_class][account][run] = 1.0
							if accounting[out_year][region][tod][user_class][account][run] == 0:
								accounting[out_year][region][tod][user_class][account][run] = 1.0
							if accounting[out_year][region][tod][user_class][account][run] > 0 and accounting[base_year][region][tod][user_class][account][run] > 0:
								growth_rates[region][tod][user_class][account][run] = (math.log(accounting[out_year][region][tod][user_class][account][run]) - math.log(accounting[base_year][region][tod][user_class][account][run])) / (out_year - base_year)
							else:
								growth_rates[region][tod][user_class][account][run] = 0.0
	#print benefits
	for year in range(base_year + 1, end_year + 1):
		if not benefits.has_key(year):
			benefits[year] = {}
		if not accounting.has_key(year):
			accounting[year] = {}
		for region in regions:
			if not benefits[year].has_key(region):
				benefits[year][region] = {}
			if not accounting[year].has_key(region):
				accounting[year][region] = {}
			for tod in ('am', 'md', 'pm', 'ev', 'ni', 'all'):
				if not benefits[year][region].has_key(tod):
					benefits[year][region][tod] = {}
				if not accounting[year][region].has_key(tod):
					accounting[year][region][tod] = {}
				for user_class in ('all_sr2', 'all_sr3', 'bike', 'hbw_da_1', 'hbw_da_2', 'hbw_da_3', 'hbw_da_4', 'hbw_dat', 'hbw_wat', 'hv_truck', 'lt_truck', 'md_truck', 'nhbw_da', 'nhbw_wat', 'vanpool', 'walk', 'all'):
					if not benefits[year][region][tod].has_key(user_class):
						benefits[year][region][tod][user_class] = {}
					for benefit in ('time_benefit', 'operating_cost_benefit', 'toll_benefit', 'fare_benefit', 'parking_benefit', 'unreliability_benefit'):
						benefits[year][region][tod][user_class][benefit] = benefits[base_year][region][tod][user_class][benefit] * math.exp(growth_rates[region][tod][user_class][benefit] * (year - base_year))
						#print 'benefit, %s, %s, %s, %s, %s' %(year, region, tod, user_class, benefit)
						#print '%s = %s * %s^(%s * (%s - %s))' %(benefits[year][region][tod][user_class][benefit], benefits[base_year][region][tod][user_class][benefit], math.exp(1), growth_rates[region][tod][user_class][benefit], year, base_year)
						#benefits[year][region][tod][user_class][benefit] = growth_rates[region][tod][user_class][benefit]
						if abs(benefits[year][region][tod][user_class][benefit]) <= 1.0:
							benefits[year][region][tod][user_class][benefit] = 0.0
					if user_class not in ('hbw_dat', 'hbw_wat', 'nhbw_wat'):
						if not accounting[year][region][tod].has_key(user_class):
							accounting[year][region][tod][user_class] = {}
						for account in ('rev', 'trips', 'vht', 'vmt'):
							if not accounting[year][region][tod][user_class].has_key(account):
								accounting[year][region][tod][user_class][account] = {}
							for run in ('alt', 'base'):
								accounting[year][region][tod][user_class][account][run] = accounting[base_year][region][tod][user_class][account][run] * math.exp(growth_rates[region][tod][user_class][account][run] * (year - base_year))
								#print 'accounting, %s, %s, %s, %s, %s, %s' %(year, region, tod, user_class, account, run)
								#print '%s = %s * %s^(%s * (%s - %s))' %(accounting[year][region][tod][user_class][account][run], accounting[base_year][region][tod][user_class][account][run], math.exp(1), growth_rates[region][tod][user_class][account][run], year, base_year)
								#accounting[year][region][tod][user_class][account][run] = growth_rates[region][tod][user_class][account][run]
								if abs(accounting[year][region][tod][user_class][account][run]) <= 1.0:
									accounting[year][region][tod][user_class][account][run] = 0.0
								
	#save back to database
	for year in benefits.keys():
		if year not in (base_year, out_year):
			for region in benefits[year].keys():
				for tod in benefits[year][region].keys():
					for uc in benefits[year][region][tod].keys():
						benefit_result = BenefitResult()
						benefit_result.analysis = analysis
						benefit_result.year = year
						benefit_result.region_id = region
						benefit_result.tod = tod
						benefit_result.user_class = uc
						for benefit in benefits[year][region][tod][uc].keys():
							value = benefits[year][region][tod][uc][benefit]
							print '%s, %s, %s' %(benefit_result, benefit, value)
							setattr(benefit_result, benefit, value)
						benefit_result.save()
	
	for year in accounting.keys():
		if year not in (base_year, out_year):
			for region in accounting[year].keys():
				for tod in accounting[year][region].keys():
					for uc in accounting[year][region][tod].keys():
						for account in accounting[year][region][tod][uc].keys():
							accounting_result = AccountingResult()
							accounting_result.analysis = analysis
							accounting_result.year = year
							accounting_result.region_id = region
							accounting_result.tod = tod
							accounting_result.user_class = uc
							accounting_result.variable = account
							accounting_result.base = accounting[year][region][tod][uc][account]['base']
							accounting_result.alt = accounting[year][region][tod][uc][account]['alt']
							accounting_result.difference = accounting_result.alt - accounting_result.base
							if accounting_result.base > 0.0:
								accounting_result.percent_different = (accounting_result.difference / accounting_result.base)
							else:
								accounting_result.percent_different = 0.0
							accounting_result.save()
