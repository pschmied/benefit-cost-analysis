from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from psrc.analysis.models import *
from psrc.analysis.calculations import *
from psrc.analysis.forms import *
from django import newforms as forms
from string import join, replace
from datetime import datetime
import csv

def commify(num, separator=','):
	"""commify(num, separator) -> string

	Return a string representing the number num with separator inserted
	for every power of 1000.   Separator defaults to a comma.
	E.g., commify(1234567) -> '1,234,567'
	"""
	num = '%.0f' %(num)	 # just in case we were passed a numeric value
	more_to_do = 1
	while more_to_do:
		(num, more_to_do) = regex.subn(r'\1%s\2' % separator,num)
	return num

# Create your views here.
def analysis_router(request, next='main', use_function=True):
	"""
	router for the application
	"""
	# sends a redirect back to home if something is wack about the session
	#checksession = _check_session(request)
	#if not checksession[0]: return checksession[1]
	
	views = {
		'main':{'view':main,
			'functions':['_update_analysis','_calculate_results']},
		
		'time':{'view':time,
			'functions':['_edit_time','_update_time']},
			
		'distance':{'view':distance,
			'functions':['_edit_distance','_update_distance']},
		
		'accidents':{'view':accidents,
			'functions':['_edit_safety','_update_safety']},
			
		'emissions':{'view':emissions,
			'functions':['_edit_emissions','_update_emissions']},
			
		'unreliability':{'view':unreliability,
			'functions':['_edit_unreliability','_update_unreliability']},
			
		'main_report':{'view':main_report,
			'functions':['_get_main_report']},
			
		'benefit_type_report':{'view':benefit_type_report,
			'functions':['_get_benefit_type_report']},
		
		'tod_report':{'view':tod_report,
			'functions':['_get_tod_report']},
		
		'user_class_report':{'view':user_class_report,
			'functions':['_get_user_class_report']},
		
		'emissions_report':{'view':emissions_report,
			'functions':['_get_emissions_report']},
		
		'safety_report':{'view':safety_report,
			'functions':['_get_safety_report']},
	}
	
	view = views[next]['view']
	if use_function and request.method == 'POST':
		for v in views:
			for f in views[v]['functions']:
				if f in request.POST:
					view = views[v]['view']

					
	# calls the function specified in the views dict and passes request to it
	#if request.method == 'POST' and 'frompage' in request.POST:
	#	for i in views.keys():
	#		if i in request.POST:
	#			next = views[i]
	#else:
	#	next = 'main'
	
	return view(request)
	
def home(request):
	
	return render_to_response(
		'home.html',{
		
		}
	)
		
def main(request):
	try:
		analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	except:
		# brand new session
		analysis = Analysis()
		#save defaults to analysis
		analysis.region = Region.objects.get(pk=1)
		defaults = {}
		defaults_temp = Default.objects.all().values()
		for i in defaults_temp:
			defaults[i['field']] = i['value']
		for i in Analysis._meta.fields:
			if defaults.has_key(i.name):
				setattr(analysis,i.name, defaults[i.name])
		analysis.save()
		request.session['analysis_id'] = analysis.id
		
		#save tod defaults
		tod_defaults = TODDefault.objects.all().values()
		for i in tod_defaults:
			analysis_tod = AnalysisTOD()
			analysis_tod.analysis = analysis
			for j in TODDefault._meta.fields:
				if j.name != 'id':
					setattr(analysis_tod, j.name, i[j.name])
			analysis_tod.save()
			
		#save accident defaults
		accident_defaults = AccidentDefault.objects.all().values()
		for i in accident_defaults:
			accident_input = AccidentInput()
			accident_input.analysis = analysis
			for j in AccidentDefault._meta.fields:
				if j.name != 'id':
					setattr(accident_input, j.name, i[j.name])
			accident_input.save()
		
		#accident_value_defaults = AccidentValueDefault.objects.all().values()
		#for i in accident_value_defaults:
		#	 accident_value_input = AccidentValueInput()
		#	 accident_value_input.analysis = analysis
		#	 accident_value_input.property_damage_only = 
		#	 accident_value_input.injury = 
		#	 accident_value_input.fatality = 
			
		#save emission defaults
		emission_defaults = EmissionDefault.objects.all().values()
		for i in emission_defaults:
			emission_input = EmissionInput()
			emission_input.analysis = analysis
			for j in EmissionDefault._meta.fields:
				if j.name != 'id':
					if j.name == 'pollutant':
						setattr(emission_input, 'pollutant_id', i['pollutant_id'])
					else:
						setattr(emission_input, j.name, i[j.name])
			emission_input.save()
		
		pollutants = Pollutant.objects.all()
		for i in pollutants:
			emission_cost_input = EmissionCostInput()
			emission_cost_input.analysis = analysis
			emission_cost_input.pollutant = i
			emission_cost_input.cost = i.cost
			emission_cost_input.save()
			
	# get household from session household_id
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	analysis_dict = analysis.__dict__
	if analysis_dict['out_year']:
	    analysis_dict['scenario'] = "%s_%s_%s" %(analysis_dict['scenario'], analysis_dict['scenario'].split('_')[0], analysis_dict['out_year'])
	form = AnalysisFormMain(initial=analysis_dict)
	updated = False
	if (request.method == 'POST' and (
		'_update_analysis' in request.POST or 
		'_calculate_results' in request.POST or
		'_edit_time' in request.POST or
		'_edit_distance' in request.POST or
		'_edit_safety' in request.POST or
		'_edit_emissions' in request.POST)):
		#validate input
		form = AnalysisFormMain(request.POST)
		if form.is_valid():
			user_scenario = form.cleaned_data['scenario']
			user_scenario_spl = user_scenario.split('_')
			if len(user_scenario_spl) > 2:
				analysis.scenario = user_scenario_spl[0] + '_' + user_scenario_spl[1]
				analysis.out_year = int(user_scenario_spl[3][:4])
			else:
				analysis.scenario = user_scenario
				analysis.out_year = None
			#analysis.scenario = form.cleaned_data['scenario']
			analysis.region = form.cleaned_data['region_id']
			analysis.title = form.cleaned_data['title']
			analysis.analyst_name = form.cleaned_data['analyst_name']
			analysis.inflation_rate = form.cleaned_data['inflation_rate']
			analysis.fraction_of_base = form.cleaned_data['fraction_of_base']
			analysis.real_discount_rate = form.cleaned_data['real_discount_rate']
			analysis.growth_rate = form.cleaned_data['growth_rate']
			#analysis.out_year = form.cleaned_data['out_year']
			analysis.end_year = form.cleaned_data['end_year']
			analysis.save()
			updated = True
	
			if '_calculate_results' in request.POST:
					#run calcs
					calc_basic(analysis.id)
					calc_emissions(analysis.id)
					calc_accidents(analysis.id)
					if analysis.out_year:
						calc_basic(analysis.id, dynamic=1)
						calc_emissions(analysis.id, dynamic=1)
						calc_accidents(analysis.id, dynamic=1)
						interpolate(analysis.id)
					if analysis.region.id != 1:
						calc_basic(analysis.id, all_regions = 0)
						if analysis.out_year:
							calc_basic(analysis.id, all_regions = 0)
					return analysis_router(request, next='main_report', use_function=False)
			elif '_edit_time' in request.POST:
				return analysis_router(request, next='time')
			elif '_edit_distance' in request.POST:
				return analysis_router(request, next='distance')
			elif '_edit_safety' in request.POST:
				return analysis_router(request, next='accidents')
			elif '_edit_emissions' in request.POST:
				return analysis_router(request, next='emissions')
		
	return render_to_response(
		'main.html',{
			'form':form,
			'updated':updated,
		}
	)

def time(request):
	#analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	#form = TimeForm(initial=analysis.__dict__)
	#updated = False
	#if (request.method == 'POST' and ('_update_time' in request.POST)):
	#	#validate input
	#	form = TimeForm(request.POST)
	#	if form.is_valid():
	#		analysis.hbw_drive_income_1 = form.cleaned_data['hbw_drive_income_1']
	#		analysis.hbw_drive_income_2 = form.cleaned_data['hbw_drive_income_2']
	#		analysis.hbw_drive_income_3 = form.cleaned_data['hbw_drive_income_3']
	#		analysis.hbw_drive_income_4 = form.cleaned_data['hbw_drive_income_4']
	#		analysis.other_driving = form.cleaned_data['other_driving']
	#		analysis.sr2_income_am = form.cleaned_data['sr2_income_am']
	#		analysis.sr2_income_md = form.cleaned_data['sr2_income_md']
	#		analysis.sr2_income_pm = form.cleaned_data['sr2_income_pm']
	#		analysis.sr2_income_ev = form.cleaned_data['sr2_income_ev']
	#		analysis.sr2_income_nt = form.cleaned_data['sr2_income_nt']
	#		analysis.sr3_income_am = form.cleaned_data['sr3_income_am']
	#		analysis.sr3_income_md = form.cleaned_data['sr3_income_md']
	#		analysis.sr3_income_pm = form.cleaned_data['sr3_income_pm']
	#		analysis.sr3_income_ev = form.cleaned_data['sr3_income_ev']
	#		analysis.sr3_income_nt = form.cleaned_data['sr3_income_nt']
	#		analysis.vanpool_income_am = form.cleaned_data['vanpool_income_am']
	#		analysis.vanpool_income_md = form.cleaned_data['vanpool_income_md']
	#		analysis.vanpool_income_pm = form.cleaned_data['vanpool_income_pm']
	#		analysis.vanpool_income_ev = form.cleaned_data['vanpool_income_ev']
	#		analysis.vanpool_income_nt = form.cleaned_data['vanpool_income_nt']
	#		analysis.hbw_transit_ivt_income_1 = form.cleaned_data['hbw_transit_ivt_income_1']
	#		analysis.hbw_transit_ivt_income_2 = form.cleaned_data['hbw_transit_ivt_income_2']
	#		analysis.hbw_transit_ivt_income_3 = form.cleaned_data['hbw_transit_ivt_income_3']
	#		analysis.hbw_transit_ivt_income_4 = form.cleaned_data['hbw_transit_ivt_income_4']
	#		analysis.hbw_transit_walk_income_1 =  form.cleaned_data['hbw_transit_walk_income_1']
	#		analysis.hbw_transit_walk_income_2 =  form.cleaned_data['hbw_transit_walk_income_2']
	#		analysis.hbw_transit_walk_income_3 =  form.cleaned_data['hbw_transit_walk_income_3']
	#		analysis.hbw_transit_walk_income_4 =  form.cleaned_data['hbw_transit_walk_income_4']
	#		analysis.hbw_transit_wait_income_1 =  form.cleaned_data['hbw_transit_wait_income_1']
	#		analysis.hbw_transit_wait_income_2 =  form.cleaned_data['hbw_transit_wait_income_2']
	#		analysis.hbw_transit_wait_income_3 =  form.cleaned_data['hbw_transit_wait_income_3']
	#		analysis.hbw_transit_wait_income_4 =  form.cleaned_data['hbw_transit_wait_income_4']
	#		analysis.other_transit_ivt = form.cleaned_data['other_transit_ivt']
	#		analysis.other_transit_walk = form.cleaned_data['other_transit_walk']
	#		analysis.other_transit_wait = form.cleaned_data['other_transit_wait']
	#		analysis.light_trucks_time = form.cleaned_data['light_trucks_time']
	#		analysis.medium_trucks_time = form.cleaned_data['medium_trucks_time']
	#		analysis.heavy_trucks_time = form.cleaned_data['heavy_trucks_time']
	#		analysis.bike_time = form.cleaned_data['bike_time']
	#		analysis.walk_time = form.cleaned_data['walk_time']
	#		analysis.save()
	#		updated = True
	#		return analysis_router(request, next='main', use_function=False)
	#		
	#return render_to_response(
	#	'time.html',{
	#		'form':form,
	#		'updated':updated,
	#	}
	#)
	
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	toddefaults = TODDefault.objects.all()
	toddefault_dict = {}
	for i in toddefaults.values():
		toddefault_dict[i['field']] = i
	field_list = toddefault_dict.keys()
		
	analysis_tod = AnalysisTOD.objects.filter(analysis=analysis)
	analysis_tod_dict = {}
	for result in analysis_tod.values():
		analysis_tod_dict[result['field']] = result
		
	
	dynamic_fields = {}
	for field in analysis_tod_dict.keys():
		for tod in analysis_tod_dict[field].keys():
			if tod not in ('id','field','analysis_id'):
				dynamic_fields['%s_%s' %(field,tod)] = analysis_tod_dict[field][tod]
				
	form = TimeForm(obj=dynamic_fields, field_list=field_list)
	updated = False
	
			
	if (request.method == 'POST' and ('_update_time' in request.POST)):
		#validate input
		form = TimeForm(obj=request.POST, field_list=field_list)
		if form.is_valid():
			#save changes
						
			for i in analysis_tod:
				for tod in analysis_tod_dict[i.field].keys():
					if tod not in ('id','field','analysis_id'):
						setattr(i, tod, form.cleaned_data['%s_%s' %(i.field, tod)])
				i.save()
			return analysis_router(request, next='main', use_function=False)
	
	form_rows = []
	fields = analysis_tod_dict.keys()
	fields.sort()
	for field in fields:
		temp = {}
		temp['field'] = toddefault_dict[field]['name']
		for tod in analysis_tod_dict[field].keys():
			if tod not in ('id','field','analysis_id'):
				temp[tod] = form['%s_%s' %(field, tod)]
		form_rows.append(temp)
		

			
	return render_to_response(
		'time.html',{
		'form':form,
		'form_rows': form_rows,
		'updated':updated,
		}
	)

def distance(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	form = DistanceForm(initial=analysis.__dict__)
	updated = False
	if (request.method == 'POST' and ('_update_distance' in request.POST)):
		#validate input
		form = DistanceForm(request.POST)
		if form.is_valid():
			analysis.auto_cost = form.cleaned_data['auto_cost']
			analysis.light_trucks_cost = form.cleaned_data['light_trucks_cost']
			analysis.medium_trucks_cost = form.cleaned_data['medium_trucks_cost']
			analysis.heavy_trucks_cost = form.cleaned_data['heavy_trucks_cost']
			analysis.save()
			updated = True
			return analysis_router(request, next='main', use_function=False)
			
	return render_to_response(
		'distance.html',{
			'form':form,
			'updated':updated,
		}
	)

def unreliability(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	form = UnreliabilityForm(initial=analysis.__dict__)
	updated = False
	if (request.method == 'POST' and ('_update_unreliability' in request.POST)):
		#validate input
		form = UnreliabilityForm(request.POST)
		if form.is_valid():
			analysis.i_ratio = form.cleaned_data['i_ratio']
			analysis.personal_discount_rate = form.cleaned_data['personal_discount_rate']
			analysis.prob_not_meet_guar = form.cleaned_data['prob_not_meet_guar']
			analysis.alpha = form.cleaned_data['alpha']
			analysis.beta_1 = form.cleaned_data['beta_1']
			analysis.beta_2 = form.cleaned_data['beta_2']
			analysis.save()
			updated = True
			return analysis_router(request, next='main', use_function=False)
			
	return render_to_response(
		'unreliability.html',{
			'form':form,
			'updated':updated,
		}
	)
	
def accidents(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	accidents = AccidentInput.objects.filter(analysis=analysis)
	acc_dict = {}
	for result in accidents.values():
		if not acc_dict.has_key(result['vc_range']):
			acc_dict[result['vc_range']] = {}
		acc_dict[result['vc_range']][result['functional_class']] = {}
		acc_dict[result['vc_range']][result['functional_class']]['property_damage_only'] = result['property_damage_only']
		acc_dict[result['vc_range']][result['functional_class']]['injury'] = result['injury']
		acc_dict[result['vc_range']][result['functional_class']]['fatality'] = result['fatality']
	
	dynamic_fields = {}
	for vc in vc_range_choices:
		for fc in functional_class_choices:
			dynamic_fields['property_damage_only_%s_%s' %(vc[0],fc[0])] = acc_dict[vc[0]][fc[0]]['property_damage_only']
			dynamic_fields['injury_%s_%s' %(vc[0],fc[0])] = acc_dict[vc[0]][fc[0]]['injury']
			dynamic_fields['fatality_%s_%s' %(vc[0],fc[0])] = acc_dict[vc[0]][fc[0]]['fatality']
				
	form = AccidentsForm(obj=dynamic_fields)
	updated = False
	vc_range = vc_range_choices
	fc_classes = functional_class_choices
	cost_form = AccidentCostForm(initial=analysis.__dict__)
	
			
	if (request.method == 'POST' and ('_update_safety' in request.POST)):
		#validate input
		form = AccidentsForm(obj=request.POST)
		cost_form = AccidentCostForm(request.POST)
		if form.is_valid() and cost_form.is_valid():
			#save changes
			for i in accidents:
				setattr(i, 'property_damage_only', form.cleaned_data['property_damage_only_%s_%s' %(i.vc_range, i.functional_class)])
				setattr(i, 'injury', form.cleaned_data['injury_%s_%s' %(i.vc_range, i.functional_class)])
				setattr(i, 'fatality', form.cleaned_data['fatality_%s_%s' %(i.vc_range, i.functional_class)])
				i.save()
				
			analysis.property_damage_only = cost_form.cleaned_data['property_damage_only']
			analysis.injury = cost_form.cleaned_data['injury']
			analysis.fatality = cost_form.cleaned_data['fatality']
			analysis.save()
			
			return analysis_router(request, next='main', use_function=False)
			
	
	form_rows = []
	for vc in vc_range:
		for fc in fc_classes:
			temp = {}
			temp['vc'] = vc[0]
			temp['fc'] = fc[0]
			temp['property_damage_only'] = form['property_damage_only_%s_%s' %(vc[0],fc[0])]
			temp['injury'] = form['injury_%s_%s' %(vc[0],fc[0])]
			temp['fatality'] = form['fatality_%s_%s' %(vc[0],fc[0])]
			form_rows.append(temp)
			
	return render_to_response(
		'accidents.html',{
		'form':form,
		'vc_range':vc_range,
		'fc_classes':fc_classes,
		'form_rows': form_rows,
		'cost_form':cost_form,
		'updated':updated,
		}
	)

def emissions(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	emmissions = EmissionInput.objects.filter(analysis=analysis)
	emissions_cost = EmissionCostInput.objects.filter(analysis=analysis)
	emm_dict = {}
	for result in emmissions.values():
		if not emm_dict.has_key(result['pollutant_id']):
			emm_dict[result['pollutant_id']] = {}
		emm_dict[result['pollutant_id']][result['speed_class']] = result
	
	emm_cost_dict = {}
	for result in emissions_cost.values():
		emm_cost_dict[result['pollutant_id']] = result
	
	dynamic_fields = {}
	for p in emm_dict.keys():
		for speed in speed_class_choices:
			dynamic_fields['car_%s_%s' %(p,speed[0])] = emm_dict[p][speed[0]]['car']
			dynamic_fields['light_truck_%s_%s' %(p,speed[0])] = emm_dict[p][speed[0]]['light_truck']
			dynamic_fields['medium_truck_%s_%s' %(p,speed[0])] = emm_dict[p][speed[0]]['medium_truck']
			dynamic_fields['heavy_truck_%s_%s' %(p,speed[0])] = emm_dict[p][speed[0]]['heavy_truck']
	
	dynamic_cost_fields = {}
	for p in emm_cost_dict.keys():
		dynamic_cost_fields['pollutant_%s' %(p)] = emm_cost_dict[p]['cost']
	
	form = EmissionsForm(obj=dynamic_fields)
	cost_form = EmissionsCostForm(obj=dynamic_cost_fields)
	
	if (request.method == 'POST' and ('_update_emissions' in request.POST)):
		#validate input
		form = EmissionsForm(obj=request.POST)
		cost_form = EmissionsCostForm(obj=request.POST)
		if form.is_valid() and cost_form.is_valid():
			#save changes
			for i in emmissions:
				setattr(i, 'car', form.cleaned_data['car_%s_%s' %(i.pollutant_id, i.speed_class)])
				setattr(i, 'light_truck', form.cleaned_data['light_truck_%s_%s' %(i.pollutant_id, i.speed_class)])
				setattr(i, 'medium_truck', form.cleaned_data['medium_truck_%s_%s' %(i.pollutant_id, i.speed_class)])
				setattr(i, 'heavy_truck', form.cleaned_data['heavy_truck_%s_%s' %(i.pollutant_id, i.speed_class)])
				i.save()
			for i in emissions_cost:
				setattr(i, 'cost', cost_form.cleaned_data['pollutant_%s' %(i.pollutant_id)])
				i.save()
			return analysis_router(request, next='main', use_function=False)
		
	form_rows = []
	for p in emm_dict.keys():
		for speed in speed_class_choices:
			temp = {}
			temp['p'] = Pollutant.objects.get(pk=p).name
			temp['speed'] = speed[0]
			temp['car'] = form['car_%s_%s' %(p,speed[0])]
			temp['light_truck'] = form['light_truck_%s_%s' %(p,speed[0])]
			temp['medium_truck'] = form['medium_truck_%s_%s' %(p,speed[0])]
			temp['heavy_truck'] = form['heavy_truck_%s_%s' %(p,speed[0])]
			form_rows.append(temp)
	
	cost_form_rows = []
	for p in emm_cost_dict.keys():
		temp = {}
		temp['p'] = Pollutant.objects.get(pk=p).name
		temp['cost'] = cost_form['pollutant_%s' %(p)]
		cost_form_rows.append(temp)
					
	return render_to_response(
		'emissions.html',{
		'form_rows': form_rows,
		'form':form,
		'cost_form_rows': cost_form_rows,
		'cost_form': cost_form
		}
	)



def add_region(request):
	form = RegionForm()
	if request.method == 'POST':
		form = RegionForm(request.POST)
		if form.is_valid():
			newregion = form.save()
			newregion.save()
			form = 0
			return HttpResponseRedirect('/')
	return render_to_response(
		'region/add.html',{
			'form':form
		}
	)

def main_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	benefit_results = BenefitResult.objects.filter(analysis=analysis)
	acct_results = AccountingResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = benefit_results.filter(region=1, tod='all', user_class='all').order_by('year').values()
	full_region_results_dict = {}
	for result in full_region_benefits_raw:
		full_region_results_dict[result['year']] = {'year':result['year']}
		full_region_results_dict[result['year']]['user_benefit'] = result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']
	
	full_region_acct_raw = acct_results.filter(region=1, tod='all', user_class='all').order_by('year').values()
	for result in full_region_acct_raw:
		if result['variable'] == 'rev':
			full_region_results_dict[result['year']]['toll_revenue'] = result['difference']
		elif result['variable'] == 'vmt':
			full_region_results_dict[result['year']]['change_vmt'] = result['difference']
		elif result['variable'] == 'vht':
			full_region_results_dict[result['year']]['change_vht'] = result['difference']
	
	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		full_region_results.append(full_region_results_dict[year])
		
	#calculate full region NPV
	full_region_benefit_npv = 0
	#full_region_toll_npv = 0
	for year in years:
		full_region_benefit_npv += full_region_results_dict[year]['user_benefit'] / (1 + analysis.real_discount_rate)**(year - current_year)
		#full_region_toll_npv += full_region_results_dict[year]['toll_revenue'] / (1 + analysis.real_discount_rate)**(year - current_year)
	#if subregion calculate results and NPV
	if analysis.region.id != 1:
		subregion_benefits_raw = benefit_results.filter(region=analysis.region.id, tod='all', user_class='all').order_by('year').values()
		subregion_results_dict = {}
		for result in subregion_benefits_raw:
			subregion_results_dict[result['year']] = {'year':result['year']}
			subregion_results_dict[result['year']]['user_benefit'] = result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']

		subregion_acct_raw = acct_results.filter(region=analysis.region.id, tod='all', user_class='all').order_by('year').values()
		for result in subregion_acct_raw:
			if result['variable'] == 'rev':
				subregion_results_dict[result['year']]['toll_revenue'] = result['difference']
			elif result['variable'] == 'vmt':
				subregion_results_dict[result['year']]['change_vmt'] = result['difference']
			elif result['variable'] == 'vht':
				subregion_results_dict[result['year']]['change_vht'] = result['difference']

		subregion_results = []
		years = subregion_results_dict.keys()
		years.sort()
		for year in years:
			subregion_results.append(subregion_results_dict[year])

		#calculate full region NPV
		subregion_benefit_npv = 0
		#subregion_toll_npv = 0
		for year in years:
			subregion_benefit_npv += subregion_results_dict[year]['user_benefit'] / (1 + analysis.real_discount_rate)**(year - current_year)
			#full_region_toll_npv += full_region_results_dict[year]['toll_revenue'] / (1 + analysis.real_discount_rate)**(year - current_year)
	else:
		subregion_results=None
		subregion_benefit_npv=0
	
	#get overrides
	overrides=[]
	defaults = {}
	defaults_temp = Default.objects.all().values()
	for i in defaults_temp:
		defaults[i['field']] = i['value']
	for i in Analysis._meta.fields:
		if defaults.has_key(i.name):
			if analysis.__dict__[i.name] != defaults[i.name]:
				overrides.append({'parameter':i.name, 'default':defaults[i.name],'override': analysis.__dict__[i.name]})
				
	return render_to_response(
		'main_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
			'full_region_benefit_npv': full_region_benefit_npv,
			'subregion_results': subregion_results,
			'subregion_benefit_npv': subregion_benefit_npv,
			'overrides': overrides
		}
	)

def benefit_type_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	benefit_results = BenefitResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = benefit_results.filter(region=1, tod='all', user_class='all').order_by('year').values()
	full_region_results_dict = {}
	for result in full_region_benefits_raw:
		full_region_results_dict[result['year']] = {'year':result['year']}
		full_region_results_dict[result['year']]['time_benefit'] = result['time_benefit']
		full_region_results_dict[result['year']]['operating_cost_benefit'] = result['operating_cost_benefit']
		full_region_results_dict[result['year']]['toll_benefit'] = result['toll_benefit']
		full_region_results_dict[result['year']]['fare_benefit'] = result['fare_benefit']
		full_region_results_dict[result['year']]['parking_benefit'] = result['parking_benefit']
		full_region_results_dict[result['year']]['unreliability_benefit'] = result['unreliability_benefit']
	
	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		full_region_results.append(full_region_results_dict[year])
		
	#calculate full region NPV
	full_region_benefit_npv = {}
	#full_region_toll_npv = 0
	for year in years:
		for key in full_region_results_dict[year].keys():
			if not full_region_benefit_npv.has_key(key):
				full_region_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				full_region_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
	
	full_region_results.append(full_region_benefit_npv)
	
	if analysis.region.id != 1:
		subregion_benefits_raw = benefit_results.filter(region=analysis.region.id, tod='all', user_class='all').order_by('year').values()
		subregion_results_dict = {}
		for result in subregion_benefits_raw:
			subregion_results_dict[result['year']] = {'year':result['year']}
			subregion_results_dict[result['year']]['time_benefit'] = result['time_benefit']
			subregion_results_dict[result['year']]['operating_cost_benefit'] = result['operating_cost_benefit']
			subregion_results_dict[result['year']]['toll_benefit'] = result['toll_benefit']
			subregion_results_dict[result['year']]['fare_benefit'] = result['fare_benefit']
			subregion_results_dict[result['year']]['parking_benefit'] = result['parking_benefit']
			subregion_results_dict[result['year']]['unreliability_benefit'] = result['unreliability_benefit']

		subregion_results = []
		years = subregion_results_dict.keys()
		years.sort()
		for year in years:
			subregion_results.append(subregion_results_dict[year])
			
		#calculate full region NPV
		subregion_benefit_npv = {}
		#subregion_toll_npv = 0
		for year in years:
			if not subregion_benefit_npv.has_key(key):
				subregion_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				subregion_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
				
	else:
		subregion_results=None
		subregion_benefit_npv=0
	
				
	return render_to_response(
		'benefit_type_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
			'full_region_benefit_npv': full_region_benefit_npv,
			'subregion_results': subregion_results,
			'subregion_benefit_npv': subregion_benefit_npv
		}
	)
	
def tod_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	benefit_results = BenefitResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = benefit_results.filter(region=1, user_class='all').order_by('year').values()
	full_region_results_dict = {}
	for result in full_region_benefits_raw:
		if not full_region_results_dict.has_key(result['year']):
			full_region_results_dict[result['year']] = {'year':result['year']}
		if not full_region_results_dict[result['year']].has_key(result['tod']):
			full_region_results_dict[result['year']][result['tod']] = 0
		full_region_results_dict[result['year']][result['tod']] += result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']
	
		
	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		full_region_results.append(full_region_results_dict[year])
		
	#calculate full region NPV
	full_region_benefit_npv = {}
	#full_region_toll_npv = 0
	for year in years:
		for key in full_region_results_dict[year].keys():
			if not full_region_benefit_npv.has_key(key):
				full_region_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				full_region_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
				
	full_region_results.append(full_region_benefit_npv)
	
	if analysis.region.id != 1:
		subregion_benefits_raw = benefit_results.filter(region=analysis.region.id, user_class='all').order_by('year').values()
		subregion_results_dict = {}
		for result in subregion_results_dict:
			if not subregion_results_dict.has_key(result['year']):
				subregion_results_dict[result['year']] = {'year':result['year']}
			if not subregion_results_dict[result['year']].has_key(result['tod']):
				subregion_results_dict[result['year']][result['tod']] = 0
			full_region_results_dict[result['year']][result['tod']] += result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']
			
		subregion_results = []
		years = subregion_results_dict.keys()
		years.sort()
		for year in years:
			subregion_results.append(subregion_results_dict[year])
			
		#calculate full region NPV
		subregion_benefit_npv = {}
		#subregion_toll_npv = 0
		for year in years:
			if not full_region_benefit_npv.has_key(key):
				subregion_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				subregion_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
				
	else:
		subregion_results=None
		subregion_benefit_npv=0
		
		
	return render_to_response(
		'tod_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
			'full_region_benefit_npv': full_region_benefit_npv,
			'subregion_results': subregion_results,
			'subregion_benefit_npv': subregion_benefit_npv
		}
	)



def user_class_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	benefit_results = BenefitResult.objects.filter(analysis=analysis)
	acct_results = AccountingResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = benefit_results.filter(region=1, tod='all').order_by('year').values()
	full_region_results_dict = {}
	for result in full_region_benefits_raw:
		if not full_region_results_dict.has_key(result['year']):
			full_region_results_dict[result['year']] = {'year':result['year']}
		if not full_region_results_dict[result['year']].has_key(result['user_class']):
			full_region_results_dict[result['year']][result['user_class']] = 0
		full_region_results_dict[result['year']][result['user_class']] += result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']
		
	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		full_region_results.append(full_region_results_dict[year])

	#calculate full region NPV
	full_region_benefit_npv = {}
	#full_region_toll_npv = 0
	for year in years:
		for key in full_region_results_dict[year].keys():
			if not full_region_benefit_npv.has_key(key):
				full_region_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				full_region_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
				
	full_region_results.append(full_region_benefit_npv)
	
	if analysis.region.id != 1:
		subregion_results_raw = benefit_results.filter(region=analysis.region.id, tod='all').order_by('year').values()
		subregion_results_dict = {}
		for result in subregion_results_raw:
			if not subregion_results_dict.has_key(result['year']):
				subregion_results_dict[result['year']] = {'year':result['year']}
			if not subregion_results_dict[result['year']].has_key(result['user_class']):
				subregion_results_dict[result['year']][result['user_class']] = 0
			subregion_results_dict[result['year']][result['user_class']] += result['time_benefit'] + result['operating_cost_benefit'] + result['toll_benefit'] + result['fare_benefit'] + result['parking_benefit'] + result['unreliability_benefit']
			
		subregion_results = []
		years = subregion_results_dict.keys()
		years.sort()
		for year in years:
			subregion_results.append(subregion_results_dict[year])
			
		#calculate full region NPV
		subregion_benefit_npv = {}
		#subregion_toll_npv = 0
		for year in years:
			if not full_region_benefit_npv.has_key(key):
				subregion_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
			else:
				subregion_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
				
	else:
		subregion_results=None
		subregion_benefit_npv=0
		
		
	return render_to_response(
		'user_class_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
			'full_region_benefit_npv': full_region_benefit_npv,
			'subregion_results': subregion_results,
			'subregion_benefit_npv': subregion_benefit_npv
		}
	)

def emissions_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	emission_results = EmissionResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = emission_results.order_by('year').values()
	full_region_results_dict = {}
	vehicle_types={'heavy_truck':'Heavy Truck', 'medium_truck':'Medium Truck', 'light_truck':'Light Truck', 'car':'Car'}
	for result in full_region_benefits_raw:
		pollutant_name = Pollutant.objects.get(pk=result['pollutant_id']).name
		if not full_region_results_dict.has_key(result['year']):
			full_region_results_dict[result['year']] = {}  #'year':result['year']
		if not full_region_results_dict[result['year']].has_key(pollutant_name):
			full_region_results_dict[result['year']][pollutant_name] = {'pollutant_name': pollutant_name, 'year': result['year']}
		if not full_region_results_dict[result['year']][pollutant_name].has_key(result['vehicle_type']):
			full_region_results_dict[result['year']][pollutant_name][result['vehicle_type']] = 0
		full_region_results_dict[result['year']][pollutant_name][result['vehicle_type']] += result['difference']

	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		pollutants = full_region_results_dict[year].keys()
		pollutants.sort()
		for p in pollutants:
			full_region_results.append(full_region_results_dict[year][p])

	##calculate full region NPV
	#full_region_benefit_npv = {}
	##full_region_toll_npv = 0
	#for year in years:
	#	for key in full_region_results_dict[year].keys():
	#		if not full_region_benefit_npv.has_key(key):
	#			full_region_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
	#		else:
	#			full_region_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
	#			
	#full_region_results.append(full_region_benefit_npv)

	return render_to_response(
		'emissions_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
		}
	)
	
	
def safety_report(request):
	analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	base_year = int(analysis.scenario.split('_')[1][:4])
	current_year = datetime.now().year
	safety_results = AccidentResult.objects.filter(analysis=analysis)
	date_prepared = datetime.now()
	#create full region results
	full_region_benefits_raw = safety_results.order_by('year').values()
	full_region_results_dict = {}
	for result in full_region_benefits_raw:
		if not full_region_results_dict.has_key(result['year']):
			full_region_results_dict[result['year']] = {'year':result['year'], 'property_damage_only':0, 'injury':0, 'fatality': 0, 'total':0}
		full_region_results_dict[result['year']]['property_damage_only'] += result['property_damage_only_benefit']
		full_region_results_dict[result['year']]['injury'] += result['injury_benefit']
		full_region_results_dict[result['year']]['fatality'] += result['fatality_benefit']
		full_region_results_dict[result['year']]['total'] += result['fatality_benefit'] + result['injury_benefit'] + result['property_damage_only_benefit']

	full_region_results = []
	years = full_region_results_dict.keys()
	years.sort()
	for year in years:
		full_region_results.append(full_region_results_dict[year])

	##calculate full region NPV
	#full_region_benefit_npv = {}
	##full_region_toll_npv = 0
	#for year in years:
	#	for key in full_region_results_dict[year].keys():
	#		if not full_region_benefit_npv.has_key(key):
	#			full_region_benefit_npv[key] = full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
	#		else:
	#			full_region_benefit_npv[key] += full_region_results_dict[year][key] / (1 + analysis.real_discount_rate)**(year - current_year)
	#			
	#full_region_results.append(full_region_benefit_npv)

	return render_to_response(
		'safety_report.html',{
			'analysis': analysis,
			'full_region_results': full_region_results,
		}
	)
		

def benefits_csv(request):
	try:
		analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	except:
		return HttpResponseRedirect('/')
	
	benefit_results = BenefitResult.objects.filter(analysis=analysis.id).values()
	if not len(benefit_results) > 0:
		return HttpResponseRedirect('/')
	
	data = []
	header = []
	for field in BenefitResult._meta.fields:
		if field.name not in ('id','analysis'):
			header.append(field.name)
	data.append(header)
	for result in benefit_results:
		row = []
		for field in header:
			if field == 'region':
				row.append(Region.objects.get(id=result['region_id']).name)
			else:
				row.append(result[field])
		data.append(row)
	
	#	 return HttpResponseRedirect('/')
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s_benefit_results.csv' %(replace(analysis.title,' ','_'))

	writer = csv.writer(response)
	for row in data:
		writer.writerow(row)
	
	return response

def accounting_csv(request):
	try:
		analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	except:
		return HttpResponseRedirect('/')
	
	accounting_results = AccountingResult.objects.filter(analysis=analysis.id).values()
	if not len(accounting_results) > 0:
		return HttpResponseRedirect('/')

	data = []
	header = []
	for field in AccountingResult._meta.fields:
		if field.name not in ('id','analysis'):
			header.append(field.name)
	data.append(header)
	for result in accounting_results:
		row = []
		for field in header:
			if field == 'region':
				row.append(Region.objects.get(id=result['region_id']).name)
			else:
				row.append(result[field])
		data.append(row)

	#	 return HttpResponseRedirect('/')
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s_accounting_results.csv' %(replace(analysis.title,' ','_'))

	writer = csv.writer(response)
	for row in data:
		writer.writerow(row)

	return response
	
def safety_csv(request):
	try:
		analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	except:
		return HttpResponseRedirect('/')
	
	accidents_results = AccidentResult.objects.filter(analysis=analysis.id).values()
	if not len(accidents_results) > 0:
		return HttpResponseRedirect('/')

	data = []
	header = []
	for field in AccidentResult._meta.fields:
		if field.name not in ('id','analysis'):
			header.append(field.name)
	data.append(header)
	for result in accidents_results:
		row = []
		for field in header:
			row.append(result[field])
		data.append(row)

	#	 return HttpResponseRedirect('/')
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s_safety_results.csv' %(replace(analysis.title,' ','_'))

	writer = csv.writer(response)
	for row in data:
		writer.writerow(row)

	return response

def emissions_csv(request):
	try:
		analysis = Analysis.objects.get(id=request.session.get('analysis_id'))
	except:
		return HttpResponseRedirect('/')
	
	emissions_results = EmissionResult.objects.filter(analysis=analysis.id).values()
	if not len(emissions_results) > 0:
		return HttpResponseRedirect('/')
	
	data = []
	header = []
	for field in EmissionResult._meta.fields:
		if field.name not in ('id','analysis'):
			header.append(field.name)
	data.append(header)
	for result in emissions_results:
		row = []
		for field in header:
			if field == 'pollutant':
				row.append(Pollutant.objects.get(id=result['pollutant_id']).short_name)
			else:
				row.append(result[field])
		data.append(row)

	#	 return HttpResponseRedirect('/')
	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s_emissions_results.csv' %(replace(analysis.title,' ','_'))

	writer = csv.writer(response)
	for row in data:
		writer.writerow(row)

	return response

def restart(request):
	"""
	Clears the session and send them back home
	"""
	for key in request.session.keys():
		request.session.__delitem__(key)

	return HttpResponseRedirect('/')