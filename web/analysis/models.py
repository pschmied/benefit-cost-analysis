from django.db import models
import sys, datetime
from math import *

#support functions
def last(seq, pred=None):
	"""Return the last item in seq for which the predicate is true.
	
	If the predicate is None, return the last item regardless of value.
	
	If no items satisfy the predicate, return None.
	"""
	if pred is None:
		pred = lambda x: True
	for item in reversed(seq):
		if pred(item):
			return item
	return None

def norminv(p, mean, stddev):
	xp=0.0
	lim = 1.e-20
	p0 = -0.322232431088
	p1 = -1.0
	p2 = -0.342242088547
	p3 = -0.0204231210245
	p4 = -0.453642210148e-4
	q0 = 0.0993484626060
	q1 = 0.588581570495
	q2 = 0.531103462366
	q3 = 0.103537752850
	q4 = 0.38560700634e-2
	if p < lim or p == 1.:
		return -1.0 / lim
	if p == 0.5:
		return mean
	if p > 0.5:
		p = 1.0 - p
		sign = 1.0
	else:
		sign = -1.0
	y = sqrt(log(1.0 / p**2))
	xp = y + ((((y * p4 + p3) * y + p2) * y + p1) * y + p0) / ((((y * q4 + q3) * y + q2) * y + q1) * y + q0)
	return sign * xp * stddev + mean

def normcdf(x, mean, stddev):
	y = abs((x - mean) / stddev)
	def R1(x):
		N = 0.0
		D = 0.0
		p = [2.4266795523053175e2, 2.1979261618294152e1, 6.9963834886191355, -3.5609843701815385e-2]
		q = [2.1505887586986120e2, 9.1164905404514901e1, 1.5082797630407787e1, 1.0]
		for i in range(0, 4):
			N = N + p[i] * x ** (2.0 * i)
			D = D + q[i] * x ** (2.0 * i)
		return N / D
	def R2(x):
		N = 0.0
		D = 0.0
		p = [3.004592610201616005e2, 4.519189537118729422e2, 3.393208167343436870e2, 1.529892850469404039e2,
			4.316222722205673530e1, 7.211758250883093659, 5.641955174789739711e-1, -1.368648573827167067e-7]
		q = [3.004592609569832933e2, 7.909509253278980272e2, 9.313540948506096211e2, 6.389802644656311665e2,
			2.775854447439876434e2, 7.700015293522947295e1, 1.278272731962942351e1, 1.0]
		for i in range(0, 8):
			N = N + p[i] * x ** (-2.0 * i)
			D = D + q[i] * x ** (-2.0 * i)
		return N / D
	def R3(x):
		N = 0.0
		D = 0.0
		p = [-2.99610707703542174e-3, -4.94730910623250734e-2, -2.26956593539686930e-1, 
			-2.78661308609647788e-1, -2.23192459734184686e-2]
		q = [1.06209230528467918e-2, 1.91308926107829841e-1, 1.05167510706793207,
			1.98733201817135256, 1.0]
		for i in range(0, 5):
			N = N + p[i] * x ** (-2.0 * i)
			D = D + q[i] * x ** (-2.0 * i)
		return N / D
	if y < pi:
		p = (1.0 + (y / sqrt(2.0)) * R1(y / sqrt(2.0))) / 2.0
	else:
		p = 1.0 - (exp(-(y/sqrt(2.0))**2.0)/(y/sqrt(2.0)))*(1.0/sqrt(pi)+R3((y/sqrt(2.0))**-2.0)/((y/sqrt(2.0))**2.0)) / 2.0
	if x > 0:
		return p
	else:
		return 1.0 - p

def opt_val(v, length):
	"""Function to compute option value in minutes from expected speed on a freeway link of a given length"""
	# default parameter values
	i_ratio = 1.0	 # ratio of speed guarantee to speed
	r = 0.05		 # discount rate
	p = 0.01		 # probability of not completing traversal of link when contract expires
	alpha = -2.562	 # standard deviation of ln(v) estimated as alpha + beta1 * ln(v) + beta2 * ln(v)^2
	beta1 = 2.037
	beta2 = -0.339
	# need to get user overrides for parameters
	if (v > 6) and (v < 68):
		lnv = log(v)													# ln(speed)
		i = v * i_ratio													# speed guarantee
		s = max(0.01, alpha + beta1 * lnv + beta2 * lnv**2)				# standard deviation of ln(speed)
		t = (60.0 / exp(norminv(p, lnv, s))) / (60 * 24 * 365)			# contract term in years
		sigma = s / sqrt(t)												# volatility of underlying asset value
		d1 = (log(v/i) + (r + sigma**2 / 2.0) * t) / (sigma * sqrt(t))	# d1 from Black-Shoales
		d2 = (log(v/i) + (r - sigma**2 / 2.0) * t) / (sigma * sqrt(t))	# d2 from Black-Shoales
		opt = i * exp(-r * t) * normcdf(-d2, 0.0, 1.0) - v * normcdf(-d1, 0.0, 1.0)			# option value in miles per hour
	else:
		opt = 0
	return length / (v - opt) - length / v

#custom sql
def scenario_sql():
	from django.db import connection
	cursor = connection.cursor()
	cursor.execute("select nspname from pg_namespace", [])
	scenarios = []
	for i in cursor.fetchall():
		scenarios.append(i[0])
	return scenarios
	
def static_scenario_dict():
	#make dictionary of lists of scenarios for a year
	scenarios = {}
	temp = []
	for i in scenario_sql():
		temp.append(i.split('_'))
	for i in temp:
		if not len(i) > 2:
			try:
				test = int(i[1][0:4])
			except:
				continue
			if scenarios.has_key(i[1]):
				scenarios[i[1]].append(i[0])
			else:
				scenarios[i[1]] = [i[0]]
	return scenarios
	
def dynamic_scenario_dict():
	#make dictionary of lists of scenarios for a year
	dynamic_scenarios = {}
	for i in scenario_sql():
		base = i.split('_')
		try:
			#weed out schemas without a year
			int(base[1][0:4])
		except:
			continue
		for j in scenario_sql():
			end = j.split('_')
			try:
				#weed out schemas without a year
				int(end[1][0:4])
			except:
				continue
			#make sure schema is not a base
			if base[0] != 'base':
				#schema names must match
				if base[0] == end[0]:
					# end year must be greater than base year
					if int(end[1][0:4]) > int(base[1][0:4]):
						#year types must be the same
						if end[1][4:] == base[1][4:]:
							if dynamic_scenarios.has_key(base[1]):
								dynamic_scenarios[base[1]].append(i + '_' + j)
							else:
								dynamic_scenarios[base[1]] = [i + '_' + j]
	return dynamic_scenarios
	
def scenario_choices():
	#make scenario choice set (only get alternative scenarios with corresponding base years)
	dynamic_scenarios = dynamic_scenario_dict()
	static_scenarios = static_scenario_dict()
	scenario_choices = (('','-------'),)
	dynamic_keys = dynamic_scenarios.keys()
	dynamic_keys.sort()
	for year in dynamic_keys:
		for i in dynamic_scenarios[year]:
			spl = i.split('_')
			scenario_choices += ((i, 'Dynamic Analysis %s-%s %s' %(spl[1], spl[3], spl[0].title())),)
	
	static_keys = static_scenarios.keys()
	static_keys.sort()
	for year in static_keys:
		if 'base' in static_scenarios[year]:
			static_scenarios[year].sort()
			for i in static_scenarios[year]:
				if i != 'base':
					scenario_choices += (('%s_%s' %(i,year), 'Static Analysis %s %s' %(year,i.title())),)
	return scenario_choices

def get_benefits(scenario, region):
	from django.db import connection
	cursor = connection.cursor()
	fields = [
	'hbw_da_1_base_vht',
	'hbw_da_1_alt_vht',
	'hbw_da_1_base_vmt',
	'hbw_da_1_alt_vmt',
	'hbw_da_1_base_rev',
	'hbw_da_1_alt_rev',
	'hbw_da_1_base_unrel',
	'hbw_da_1_alt_unrel',
	'hbw_da_1_time',
	'hbw_da_1_dist',
	'hbw_da_1_toll',
	'hbw_da_1_unrel',
	'hbw_da_2_base_vht',
	'hbw_da_2_alt_vht',
	'hbw_da_2_base_vmt',
	'hbw_da_2_alt_vmt',
	'hbw_da_2_base_rev',
	'hbw_da_2_alt_rev',
	'hbw_da_2_base_unrel',
	'hbw_da_2_alt_unrel',
	'hbw_da_2_time',
	'hbw_da_2_dist',
	'hbw_da_2_toll',
	'hbw_da_2_unrel',
	'hbw_da_3_base_vht',
	'hbw_da_3_alt_vht',
	'hbw_da_3_base_vmt',
	'hbw_da_3_alt_vmt',
	'hbw_da_3_base_rev',
	'hbw_da_3_alt_rev',
	'hbw_da_3_base_unrel',
	'hbw_da_3_alt_unrel',
	'hbw_da_3_time',
	'hbw_da_3_dist',
	'hbw_da_3_toll',
	'hbw_da_3_unrel',
	'hbw_da_4_base_vht',
	'hbw_da_4_alt_vht',
	'hbw_da_4_base_vmt',
	'hbw_da_4_alt_vmt',
	'hbw_da_4_base_rev',
	'hbw_da_4_alt_rev',
	'hbw_da_4_base_unrel',
	'hbw_da_4_alt_unrel',
	'hbw_da_4_time',
	'hbw_da_4_dist',
	'hbw_da_4_toll',
	'hbw_da_4_unrel',
	'nhbw_da_base_vht',
	'nhbw_da_alt_vht',
	'nhbw_da_base_vmt',
	'nhbw_da_alt_vmt',
	'nhbw_da_base_rev',
	'nhbw_da_alt_rev',
	'nhbw_da_base_unrel',
	'nhbw_da_alt_unrel',
	'nhbw_da_time',
	'nhbw_da_dist',
	'nhbw_da_toll',
	'nhbw_da_unrel',
	'all_sr2_base_vht',
	'all_sr2_alt_vht',
	'all_sr2_base_vmt',
	'all_sr2_alt_vmt',
	'all_sr2_base_rev',
	'all_sr2_alt_rev',
	'all_sr2_base_unrel',
	'all_sr2_alt_unrel',
	'all_sr2_time',
	'all_sr2_dist',
	'all_sr2_toll',
	'all_sr2_unrel',
	'all_sr3_base_vht',
	'all_sr3_alt_vht',
	'all_sr3_base_vmt',
	'all_sr3_alt_vmt',
	'all_sr3_base_rev',
	'all_sr3_alt_rev',
	'all_sr3_base_unrel',
	'all_sr3_alt_unrel',
	'all_sr3_time',
	'all_sr3_dist',
	'all_sr3_toll',
	'all_sr3_unrel',
	'vanpool_base_vht',
	'vanpool_alt_vht',
	'vanpool_base_vmt',
	'vanpool_alt_vmt',
	'vanpool_base_rev',
	'vanpool_alt_rev',
	'vanpool_base_unrel',
	'vanpool_alt_unrel',
	'vanpool_time',
	'vanpool_dist',
	'vanpool_toll',
	'vanpool_unrel',
	'lt_truck_base_vht',
	'lt_truck_alt_vht',
	'lt_truck_base_vmt',
	'lt_truck_alt_vmt',
	'lt_truck_base_rev',
	'lt_truck_alt_rev',
	'lt_truck_base_unrel',
	'lt_truck_alt_unrel',
	'lt_truck_time',
	'lt_truck_dist',
	'lt_truck_toll',
	'lt_truck_unrel',
	'md_truck_base_vht',
	'md_truck_alt_vht',
	'md_truck_base_vmt',
	'md_truck_alt_vmt',
	'md_truck_base_rev',
	'md_truck_alt_rev',
	'md_truck_base_unrel',
	'md_truck_alt_unrel',
	'md_truck_time',
	'md_truck_dist',
	'md_truck_toll',
	'md_truck_unrel',
	'hv_truck_base_vht',
	'hv_truck_alt_vht',
	'hv_truck_base_vmt',
	'hv_truck_alt_vmt',
	'hv_truck_base_rev',
	'hv_truck_alt_rev',
	'hv_truck_base_unrel',
	'hv_truck_alt_unrel',
	'hv_truck_time',
	'hv_truck_dist',
	'hv_truck_toll',
	'hv_truck_unrel',
	'bike_base_vht',
	'bike_alt_vht',
	'bike_base_vmt',
	'bike_alt_vmt',
	'bike_base_rev',
	'bike_alt_rev',
	'bike_base_unrel',
	'bike_alt_unrel',
	'bike_time',
	'bike_dist',
	'bike_toll',
	'bike_unrel',
	'walk_base_vht',
	'walk_alt_vht',
	'walk_base_vmt',
	'walk_alt_vmt',
	'walk_base_rev',
	'walk_alt_rev',
	'walk_base_unrel',
	'walk_alt_unrel',
	'walk_time',
	'walk_dist',
	'walk_toll',
	'walk_unrel',
	'hbw_dat_time',
	'hbw_dat_dist',
	'hbw_dat_ivt',
	'hbw_wat_ivt',
	'nhbw_wat_ivt',
	'hbw_dat_walk',
	'hbw_wat_walk',
	'nhbw_wat_walk',
	'hbw_dat_wait',
	'hbw_wat_wait',
	'nhbw_wat_wait',
	'hbw_dat_fare',
	'hbw_wat_fare',
	'nhbw_wat_fare',
	'parking',
	'hbw_da_1_base_trips',
	'hbw_da_2_base_trips',
	'hbw_da_3_base_trips',
	'hbw_da_4_base_trips',
	'nhbw_da_base_trips',
	'all_sr2_base_trips',
	'all_sr3_base_trips',
	'vanpool_base_trips',
	'lt_truck_base_trips',
	'md_truck_base_trips',
	'hv_truck_base_trips',
	'bike_base_trips',
	'walk_base_trips',
	'hbw_da_1_alt_trips',
	'hbw_da_2_alt_trips',
	'hbw_da_3_alt_trips',
	'hbw_da_4_alt_trips',
	'nhbw_da_alt_trips',
	'all_sr2_alt_trips',
	'all_sr3_alt_trips',
	'vanpool_alt_trips',
	'lt_truck_alt_trips',
	'md_truck_alt_trips',
	'hv_truck_alt_trips',
	'bike_alt_trips',
	'walk_alt_trips'
	]
	if region == 1:
		sql = "select tod"
		for i in fields:
			sql += ', %s' %(i)
		sql += ' from %s.benefits' %(scenario)
		sql += ' where o_zone=0 and d_zone=0'
	else:
		sql = "select tod"
		for i in fields:
			sql += ', sum(%s) as %s' %(i,i)
		sql += ' from %s.benefits as b, public.analysis_region_zones as z' %(scenario) 
		sql += ' where z.region_id = %s and' %(region)
		sql += ' (b.o_zone = z.zone_id or b.d_zone = z.zone_id)'
		sql += ' group by b.tod' 
	
	cursor.execute(sql, [])
	benefits = {}
	for i in cursor.fetchall():
		tod = str(i[0]).replace(' ','')
		benefits[tod] = {}
		k = 0
		for j in i:
			if j != i[0]:
				if j is None:
					benefits[tod][fields[k]] = 0.0
				else:
					benefits[tod][fields[k]] = j
				k += 1
	return benefits

def get_link_benefits(scenario):
	from django.db import connection
	cursor = connection.cursor()
	sql = "select * from %s.link_benefits" %(scenario)
	cursor.execute(sql,[])
	link_benefits = {}
	for i in cursor.fetchall():
		tod = str(i[0]).replace(' ','')
		if not link_benefits.has_key(tod):
			link_benefits[tod] = {}
		link_benefits[tod][str(i[1])] = i[2]
	return link_benefits

def get_unreliability(alt,base):
	from django.db import connection
	cursor = connection.cursor()
	SR3_OCC = 3.15 # Occupancy of shared-ride three plus vehicles
	VP_OCC = 8.0 # Occupancy of vanpool vehicles
	start = datetime.datetime.now()
	alternatives = (base, alt)
	scenarios = (1002, 1003, 1004, 1005, 1006)
	variables = ('length', 'auto_time', 'sov_volume', 'hbw1_sov_volume', 'hbw2_sov_volume', 
		'hbw3_sov_volume', 'hbw4_sov_volume', 'hov2_volume', 'hov3plus_volume', 'vanpool_volume', 'lt_truck_volume', 
		'med_truck_volume', 'hvy_truck_volume')

	data = {}
	for scenario in scenarios:
		data[scenario] = {}
		for user in ('hbw_da_1', 'hbw_da_2', 'hbw_da_3', 'hbw_da_4', 'nhbw_da', 'all_sr2', 'all_sr3', 'vanpool', 'lt_truck', 'md_truck', 'hv_truck'):
			data[scenario]['unr_' + user] = 0.0
		links = {}
		for alternative in alternatives:
			links[alternative] = {}
			query = "select i_node, j_node, "
			for variable in variables:
				query = query + variable + ', '
			query = query[:-2] + " from %s.links where scenario = %s and ul3 > 0 and ul3 < 3 and length > 0;" % (alternative, scenario)
			cursor.execute(query, [])
			result = cursor.fetchall()
			for link in result:
				links[alternative][(link[0], link[1])] = {}
				for i in range(0, len(variables)):
					links[alternative][(link[0], link[1])][variables[i]] = link[i + 2]
		for link in links[alt].keys():
			alt_data = links[alt][link]
			if link in links[base].keys():
				base_data = links[base][link]
			else:
				base_data = {}
				for variable in variables:
					base_data[variable] = 0
			base_speed = base_data['length'] / (max(0.1, base_data['auto_time']) / 60.0)
			alt_speed = alt_data['length'] / (max(0.1, alt_data['auto_time']) / 60.0)
			base_opt = opt_val(base_speed, base_data['length'])
			alt_opt = opt_val(alt_speed, alt_data['length'])
			data[scenario]['unr_hbw_da_1'] += (base_opt - alt_opt) * (base_data['hbw1_sov_volume'] + alt_data['hbw1_sov_volume']) / 2.0
			data[scenario]['unr_hbw_da_2'] += (base_opt - alt_opt) * (base_data['hbw2_sov_volume'] + alt_data['hbw2_sov_volume']) / 2.0
			data[scenario]['unr_hbw_da_3'] += (base_opt - alt_opt) * (base_data['hbw3_sov_volume'] + alt_data['hbw3_sov_volume']) / 2.0
			data[scenario]['unr_hbw_da_4'] += (base_opt - alt_opt) * (base_data['hbw4_sov_volume'] + alt_data['hbw4_sov_volume']) / 2.0
			data[scenario]['unr_nhbw_da'] += (base_opt - alt_opt) * (base_data['sov_volume'] - base_data['hbw1_sov_volume'] - base_data['hbw2_sov_volume'] 
				- base_data['hbw3_sov_volume'] - base_data['hbw4_sov_volume'] + alt_data['sov_volume'] - alt_data['hbw1_sov_volume'] - alt_data['hbw1_sov_volume'] 
				- alt_data['hbw1_sov_volume'] - alt_data['hbw1_sov_volume']) / 2.0
			data[scenario]['unr_all_sr2'] += (base_opt - alt_opt) * (base_data['hov2_volume'] + alt_data['hov2_volume']) / 2.0
			data[scenario]['unr_all_sr3'] += (base_opt - alt_opt) * (base_data['hov3plus_volume'] + alt_data['hov3plus_volume']) / 2.0
			data[scenario]['unr_vanpool'] += (base_opt - alt_opt) * (base_data['vanpool_volume'] + alt_data['vanpool_volume']) / 2.0
			data[scenario]['unr_lt_truck'] += (base_opt - alt_opt) * (base_data['lt_truck_volume'] + alt_data['lt_truck_volume']) / 2.0
			data[scenario]['unr_md_truck'] += (base_opt - alt_opt) * (base_data['med_truck_volume'] + alt_data['med_truck_volume']) / 2.0
			data[scenario]['unr_hv_truck'] += (base_opt - alt_opt) * (base_data['hvy_truck_volume'] + alt_data['hvy_truck_volume']) / 2.0
	connection.close()
	#print 'Finished in', datetime.datetime.now() - start
	#for scenario in scenarios:
	#	keys = data[scenario].keys()
	#	keys.sort()
	#	for key in keys:
	#		print scenario, key, data[scenario][key]
	return data

def region_choices():
	region_choices = ()
	for i in Region.objects.all():
		region_choices += ((i.id, i.name),)
	return region_choices

	
# Create your models here.
class Zone(models.Model):
	pass
	
	def __str__(self):
		return str(self.id)

class Region(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	zones = models.ManyToManyField(Zone, blank=False, null=False)
	
	def __str__(self):
		return self.name
	
	class Admin:
		pass

class Default(models.Model):
	field = models.CharField(max_length=255, null=False, blank=False)
	value = models.FloatField(null=False, blank=False)
	description = models.TextField(null=True, blank=True)
	
	def __str__(self):
		return self.field
		
	class Admin:
		pass
		
	
class Analysis(models.Model):
	scenario = models.CharField(max_length=255, null=False, blank=False)
	region = models.ForeignKey(Region, null=False, blank=False)
	title = models.CharField(max_length=255, null=False, blank=False)
	analyst_name = models.CharField(max_length=255, null=False, blank=False)
	inflation_rate = models.FloatField(null=False, blank=False)
	fraction_of_base = models.FloatField(null=False, blank=False)
	"""
	#values of time
	#all values of time are now broken out by TOD
	#hbw_drive_income_1 = models.FloatField(null=False, blank=False)
	#hbw_drive_income_2 = models.FloatField(null=False, blank=False)
	#hbw_drive_income_3 = models.FloatField(null=False, blank=False)
	#hbw_drive_income_4 = models.FloatField(null=False, blank=False)
	#other_driving = models.FloatField(null=False, blank=False)
	#sr2_income_am = models.FloatField(null=False, blank=False)
	#sr2_income_md = models.FloatField(null=False, blank=False)
	#sr2_income_pm = models.FloatField(null=False, blank=False)
	#sr2_income_ev = models.FloatField(null=False, blank=False)
	#sr2_income_nt = models.FloatField(null=False, blank=False)
	#sr3_income_am = models.FloatField(null=False, blank=False)
	#sr3_income_md = models.FloatField(null=False, blank=False)
	#sr3_income_pm = models.FloatField(null=False, blank=False)
	#sr3_income_ev = models.FloatField(null=False, blank=False)
	#sr3_income_nt = models.FloatField(null=False, blank=False)
	#vanpool_income_am = models.FloatField(null=False, blank=False)
	#vanpool_income_md = models.FloatField(null=False, blank=False)
	#vanpool_income_pm = models.FloatField(null=False, blank=False)
	#vanpool_income_ev = models.FloatField(null=False, blank=False)
	#vanpool_income_nt = models.FloatField(null=False, blank=False)
	#hbw_transit_ivt_income_1 = models.FloatField(null=False, blank=False)
	#hbw_transit_ivt_income_2 = models.FloatField(null=False, blank=False)
	#hbw_transit_ivt_income_3 = models.FloatField(null=False, blank=False)
	#hbw_transit_ivt_income_4 = models.FloatField(null=False, blank=False)
	#hbw_transit_walk_income_1 = models.FloatField(null=False, blank=False)
	#hbw_transit_walk_income_2 = models.FloatField(null=False, blank=False)
	#hbw_transit_walk_income_3 = models.FloatField(null=False, blank=False)
	#hbw_transit_walk_income_4 = models.FloatField(null=False, blank=False)
	#hbw_transit_wait_income_1 = models.FloatField(null=False, blank=False)
	#hbw_transit_wait_income_2 = models.FloatField(null=False, blank=False)
	#hbw_transit_wait_income_3 = models.FloatField(null=False, blank=False)
	#hbw_transit_wait_income_4 = models.FloatField(null=False, blank=False)
	#other_transit_ivt = models.FloatField(null=False, blank=False)
	#other_transit_walk = models.FloatField(null=False, blank=False)
	#other_transit_wait = models.FloatField(null=False, blank=False)
	#light_trucks_time = models.FloatField(null=False, blank=False)
	#medium_trucks_time = models.FloatField(null=False, blank=False)
	#heavy_trucks_time = models.FloatField(null=False, blank=False)
	#bike_time = models.FloatField(null=False, blank=False)
	#walk_time = models.FloatField(null=False, blank=False)
	"""
	#values of distance
	auto_cost = models.FloatField(null=False, blank=False)
	light_trucks_cost = models.FloatField(null=False, blank=False)
	medium_trucks_cost = models.FloatField(null=False, blank=False)
	heavy_trucks_cost = models.FloatField(null=False, blank=False)
	
	#unreliability
	i_ratio = models.FloatField(null=False, blank=False)
	personal_discount_rate = models.FloatField(null=False, blank=False)
	prob_not_meet_guar = models.FloatField(null=False, blank=False)
	alpha = models.FloatField(null=False, blank=False)
	beta_1 = models.FloatField(null=False, blank=False)
	beta_2 = models.FloatField(null=False, blank=False)
	
	#Dynamic Analysis
	out_year = models.CharField(max_length=255, null=False, blank=False)
	end_year = models.PositiveIntegerField(null=True, blank=True)
	real_discount_rate = models.FloatField(null=False, blank=False)
	growth_rate = models.FloatField(null=False, blank=False)
	
	#Accident costs
	property_damage_only = models.FloatField(null=False, blank=False)
	injury = models.FloatField(null=False, blank=False)
	fatality = models.FloatField(null=False, blank=False)

class TODDefault(models.Model):
	field = models.CharField(max_length=255, null=False, blank=False)
	name = models.CharField(max_length=255, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	am = models.FloatField(null=False, blank=False)
	md = models.FloatField(null=False, blank=False)
	pm = models.FloatField(null=False, blank=False)
	ev = models.FloatField(null=False, blank=False)
	ni = models.FloatField(null=False, blank=False)
	
	def __str__(self):
		return self.field
		
	class Admin:
		pass

class AnalysisTOD(models.Model):
	analysis = models.ForeignKey(Analysis)
	field = models.CharField(max_length=255, null=False, blank=False)
	am = models.FloatField(null=False, blank=False)
	md = models.FloatField(null=False, blank=False)
	pm = models.FloatField(null=False, blank=False)
	ev = models.FloatField(null=False, blank=False)
	ni = models.FloatField(null=False, blank=False)
	
	class Admin:
		pass

vc_range_choices = (
	('0.0','0.0'), 
	('0.25','0.25'),
	('0.5','0.5'),
	('0.75','0.75'),
	('1.0','1.0'),
	('1.25','1.25'),
	('1.5','1.5'),
	('1.75','1.75')
)
type_choices = (
	(1,'Property Damage Only'), 
	(2,'Injury'), 
	(3,'Fatality'), 
)
functional_class_choices = (
	(1,'Freeway'),
	(2,'Expressway'),
	(3,'Urban Arterial 1'),
	(4, 'Urban Arterial 2'),
	(6, 'Rural Arterial')
)

class AccidentDefault(models.Model):
	vc_range = models.CharField(max_length=5, blank=False, choices=vc_range_choices)
	functional_class = models.PositiveSmallIntegerField(blank=False, choices=functional_class_choices)
	property_damage_only = models.FloatField(null=False, blank=False)
	injury = models.FloatField(null=False, blank=False)
	fatality = models.FloatField(null=False, blank=False)
	
	class Admin:
		pass

#class AccidentValueDefault(models.Model):
#	property_damage_only = models.FloatField(null=False, blank=False)
#	injury = models.FloatField(null=False, blank=False)
#	fatality = models.FloatField(null=False, blank=False)
	
	
class AccidentInput(models.Model):
	analysis = models.ForeignKey(Analysis)
	vc_range = models.CharField(max_length=5, blank=False, choices=vc_range_choices)
	functional_class = models.PositiveSmallIntegerField(blank=False, choices=functional_class_choices)
	property_damage_only = models.FloatField(null=False, blank=False)
	injury = models.FloatField(null=False, blank=False)
	fatality = models.FloatField(null=False, blank=False)

#class AccidentValueInput(models.Model):
#	analysis = models.ForeignKey(Analysis)
#	property_damage_only = models.FloatField(null=False, blank=False)
#	injury = models.FloatField(null=False, blank=False)
#	fatality = models.FloatField(null=False, blank=False)

class AccidentResult(models.Model):
	analysis = models.ForeignKey(Analysis)
	year = models.IntegerField(null=False,blank=False)
	tod = models.CharField(null=False, blank=False, max_length=3)
	functional_class = models.PositiveSmallIntegerField(blank=False, choices=functional_class_choices)
	vc_range = models.CharField(max_length=5, blank=False, choices=vc_range_choices)
	property_damage_only_benefit = models.FloatField(null=False, blank=False)
	property_damage_only_quantity_alt = models.FloatField(null=False, blank=False)
	property_damage_only_quantity_base = models.FloatField(null=False, blank=False)
	injury_benefit = models.FloatField(null=False, blank=False)
	injury_quantity_alt = models.FloatField(null=False, blank=False)
	injury_quantity_base = models.FloatField(null=False, blank=False)
	fatality_benefit = models.FloatField(null=False, blank=False)
	fatality_quantity_alt = models.FloatField(null=False, blank=False)
	fatality_quantity_base = models.FloatField(null=False, blank=False)

class Pollutant(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	short_name = models.CharField(max_length=10, null=False, blank=False)
	cost = models.FloatField(null=False, blank=False)
	
	def __str__(self):
		return "%s, %s" %(self.name, self.short_name)
	
	class Admin:
		pass

speed_class_choices = (
	(0,'0'), 
	(10,'10'), 
	(20,'20'), 
	(30,'30'), 
	(40,'40'), 
	(50,'50'), 
	(60,'60')
)
class EmissionDefault(models.Model):
	pollutant = models.ForeignKey(Pollutant)
	speed_class = models.PositiveSmallIntegerField(blank=False, choices=speed_class_choices)
	car = models.FloatField(null=False, blank=False)
	light_truck = models.FloatField(null=False, blank=False)
	medium_truck = models.FloatField(null=False, blank=False)
	heavy_truck = models.FloatField(null=False, blank=False)
	
	class Admin:
		pass
	
class EmissionInput(models.Model):
	analysis = models.ForeignKey(Analysis)
	pollutant = models.ForeignKey(Pollutant)
	speed_class= models.PositiveSmallIntegerField(blank=False, choices=speed_class_choices)
	car = models.FloatField(null=False, blank=False)
	light_truck = models.FloatField(null=False, blank=False)
	medium_truck = models.FloatField(null=False, blank=False)
	heavy_truck = models.FloatField(null=False, blank=False)

class EmissionCostInput(models.Model):
	analysis = models.ForeignKey(Analysis)
	pollutant = models.ForeignKey(Pollutant)
	cost = models.FloatField(null=False, blank=False)
	
class EmissionResult(models.Model):
	analysis = models.ForeignKey(Analysis)
	year = models.IntegerField(null=False,blank=False)
	vehicle_type = models.CharField(null=False, blank=False, max_length=20)
	speed_class= models.PositiveSmallIntegerField(blank=False, choices=speed_class_choices)
	pollutant = models.ForeignKey(Pollutant)
	base_tons = models.FloatField(null=False, blank=False)
	alt_tons = models.FloatField(null=False, blank=False)
	base_cost = models.FloatField(null=False, blank=False)
	alt_cost = models.FloatField(null=False, blank=False)
	difference = models.FloatField(null=False, blank=False)
	percent_different = models.FloatField(null=False, blank=False)

	
class BenefitResult(models.Model):
	analysis = models.ForeignKey(Analysis)
	region = models.ForeignKey(Region, null=False, blank=False)
	year = models.IntegerField(null=False,blank=False)
	tod = models.CharField(null=False, blank=False, max_length=3)
	user_class = models.CharField(null=False, blank=False, max_length=20)
	time_benefit = models.FloatField(null=False, blank=False)
	operating_cost_benefit = models.FloatField(null=False, blank=False)
	toll_benefit = models.FloatField(null=False, blank=False)
	fare_benefit = models.FloatField(null=False, blank=False)
	parking_benefit = models.FloatField(null=False, blank=False)
	unreliability_benefit = models.FloatField(null=False, blank=False)
	
	class Admin:
		pass
	
class AccountingResult(models.Model):
	analysis = models.ForeignKey(Analysis)
	region = models.ForeignKey(Region, null=False, blank=False)
	year = models.IntegerField(null=False,blank=False)
	tod = models.CharField(null=False, blank=False, max_length=3)
	user_class = models.CharField(null=False, blank=False, max_length=10)
	variable = models.CharField(null=False, blank=False, max_length=255)
	base = models.FloatField(null=False, blank=False)
	alt = models.FloatField(null=False, blank=False)
	difference = models.FloatField(null=False, blank=False)
	percent_different = models.FloatField(null=False, blank=False)
	
	
	
class Result(models.Model):
	analysis = models.ForeignKey(Analysis)
	scenario = models.CharField(max_length=255, null=False, blank=False)
	tod = models.CharField(null=False, blank=False, max_length=3)
	hbw_da_1_base_vht = models.FloatField(null=False, blank=False)
	hbw_da_1_alt_vht = models.FloatField(null=False, blank=False)
	hbw_da_1_base_vmt = models.FloatField(null=False, blank=False)
	hbw_da_1_alt_vmt = models.FloatField(null=False, blank=False)
	hbw_da_1_base_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_1_alt_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_1_time_amt = models.FloatField(null=False, blank=False)
	hbw_da_1_dist_amt = models.FloatField(null=False, blank=False)
	hbw_da_1_toll_amt = models.FloatField(null=False, blank=False)
	hbw_da_2_base_vht = models.FloatField(null=False, blank=False)
	hbw_da_2_alt_vht = models.FloatField(null=False, blank=False)
	hbw_da_2_base_vmt = models.FloatField(null=False, blank=False)
	hbw_da_2_alt_vmt = models.FloatField(null=False, blank=False)
	hbw_da_2_base_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_2_alt_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_2_time_amt = models.FloatField(null=False, blank=False)
	hbw_da_2_dist_amt = models.FloatField(null=False, blank=False)
	hbw_da_2_toll_amt = models.FloatField(null=False, blank=False)
	hbw_da_3_base_vht = models.FloatField(null=False, blank=False)
	hbw_da_3_alt_vht = models.FloatField(null=False, blank=False)
	hbw_da_3_base_vmt = models.FloatField(null=False, blank=False)
	hbw_da_3_alt_vmt = models.FloatField(null=False, blank=False)
	hbw_da_3_base_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_3_alt_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_3_time_amt = models.FloatField(null=False, blank=False)
	hbw_da_3_dist_amt = models.FloatField(null=False, blank=False)
	hbw_da_3_toll_amt = models.FloatField(null=False, blank=False)
	hbw_da_4_base_vht = models.FloatField(null=False, blank=False)
	hbw_da_4_alt_vht = models.FloatField(null=False, blank=False)
	hbw_da_4_base_vmt = models.FloatField(null=False, blank=False)
	hbw_da_4_alt_vmt = models.FloatField(null=False, blank=False)
	hbw_da_4_base_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_4_alt_rev_amt = models.FloatField(null=False, blank=False)
	hbw_da_4_time_amt = models.FloatField(null=False, blank=False)
	hbw_da_4_dist_amt = models.FloatField(null=False, blank=False)
	hbw_da_4_toll_amt = models.FloatField(null=False, blank=False)
	nhbw_da_base_vht = models.FloatField(null=False, blank=False)
	nhbw_da_alt_vht = models.FloatField(null=False, blank=False)
	nhbw_da_base_vmt = models.FloatField(null=False, blank=False)
	nhbw_da_alt_vmt = models.FloatField(null=False, blank=False)
	nhbw_da_base_rev_amt = models.FloatField(null=False, blank=False)
	nhbw_da_alt_rev_amt = models.FloatField(null=False, blank=False)
	nhbw_da_time_amt = models.FloatField(null=False, blank=False)
	nhbw_da_dist_amt = models.FloatField(null=False, blank=False)
	nhbw_da_toll_amt = models.FloatField(null=False, blank=False)
	all_sr2_base_vht = models.FloatField(null=False, blank=False)
	all_sr2_alt_vht = models.FloatField(null=False, blank=False)
	all_sr2_base_vmt = models.FloatField(null=False, blank=False)
	all_sr2_alt_vmt = models.FloatField(null=False, blank=False)
	all_sr2_base_rev_amt = models.FloatField(null=False, blank=False)
	all_sr2_alt_rev_amt = models.FloatField(null=False, blank=False)
	all_sr2_time_amt = models.FloatField(null=False, blank=False)
	all_sr2_dist_amt = models.FloatField(null=False, blank=False)
	all_sr2_toll_amt = models.FloatField(null=False, blank=False)
	all_sr3_base_vht = models.FloatField(null=False, blank=False)
	all_sr3_alt_vht = models.FloatField(null=False, blank=False)
	all_sr3_base_vmt = models.FloatField(null=False, blank=False)
	all_sr3_alt_vmt = models.FloatField(null=False, blank=False)
	all_sr3_base_rev_amt = models.FloatField(null=False, blank=False)
	all_sr3_alt_rev_amt = models.FloatField(null=False, blank=False)
	all_sr3_time_amt = models.FloatField(null=False, blank=False)
	all_sr3_dist_amt = models.FloatField(null=False, blank=False)
	all_sr3_toll_amt = models.FloatField(null=False, blank=False)
	vanpool_base_vht = models.FloatField(null=False, blank=False)
	vanpool_alt_vht = models.FloatField(null=False, blank=False)
	vanpool_base_vmt = models.FloatField(null=False, blank=False)
	vanpool_alt_vmt = models.FloatField(null=False, blank=False)
	vanpool_base_rev_amt = models.FloatField(null=False, blank=False)
	vanpool_alt_rev_amt = models.FloatField(null=False, blank=False)
	vanpool_time_amt = models.FloatField(null=False, blank=False)
	vanpool_dist_amt = models.FloatField(null=False, blank=False)
	vanpool_toll_amt = models.FloatField(null=False, blank=False)
	lt_truck_base_vht = models.FloatField(null=False, blank=False)
	lt_truck_alt_vht = models.FloatField(null=False, blank=False)
	lt_truck_base_vmt = models.FloatField(null=False, blank=False)
	lt_truck_alt_vmt = models.FloatField(null=False, blank=False)
	lt_truck_base_rev_amt = models.FloatField(null=False, blank=False)
	lt_truck_alt_rev_amt = models.FloatField(null=False, blank=False)
	lt_truck_time_amt = models.FloatField(null=False, blank=False)
	lt_truck_dist_amt = models.FloatField(null=False, blank=False)
	lt_truck_toll_amt = models.FloatField(null=False, blank=False)
	md_truck_base_vht = models.FloatField(null=False, blank=False)
	md_truck_alt_vht = models.FloatField(null=False, blank=False)
	md_truck_base_vmt = models.FloatField(null=False, blank=False)
	md_truck_alt_vmt = models.FloatField(null=False, blank=False)
	md_truck_base_rev_amt = models.FloatField(null=False, blank=False)
	md_truck_alt_rev_amt = models.FloatField(null=False, blank=False)
	md_truck_time_amt = models.FloatField(null=False, blank=False)
	md_truck_dist_amt = models.FloatField(null=False, blank=False)
	md_truck_toll_amt = models.FloatField(null=False, blank=False)
	hv_truck_base_vht = models.FloatField(null=False, blank=False)
	hv_truck_alt_vht = models.FloatField(null=False, blank=False)
	hv_truck_base_vmt = models.FloatField(null=False, blank=False)
	hv_truck_alt_vmt = models.FloatField(null=False, blank=False)
	hv_truck_base_rev_amt = models.FloatField(null=False, blank=False)
	hv_truck_alt_rev_amt = models.FloatField(null=False, blank=False)
	hv_truck_time_amt = models.FloatField(null=False, blank=False)
	hv_truck_dist_amt = models.FloatField(null=False, blank=False)
	hv_truck_toll_amt = models.FloatField(null=False, blank=False)
	bike_base_vht = models.FloatField(null=False, blank=False)
	bike_alt_vht = models.FloatField(null=False, blank=False)
	bike_base_vmt = models.FloatField(null=False, blank=False)
	bike_alt_vmt = models.FloatField(null=False, blank=False)
	bike_base_rev_amt = models.FloatField(null=False, blank=False)
	bike_alt_rev_amt = models.FloatField(null=False, blank=False)
	bike_time_amt = models.FloatField(null=False, blank=False)
	bike_dist_amt = models.FloatField(null=False, blank=False)
	bike_toll_amt = models.FloatField(null=False, blank=False)
	walk_base_vht = models.FloatField(null=False, blank=False)
	walk_alt_vht = models.FloatField(null=False, blank=False)
	walk_base_vmt = models.FloatField(null=False, blank=False)
	walk_alt_vmt = models.FloatField(null=False, blank=False)
	walk_base_rev_amt = models.FloatField(null=False, blank=False)
	walk_alt_rev_amt = models.FloatField(null=False, blank=False)
	walk_time_amt = models.FloatField(null=False, blank=False)
	walk_dist_amt = models.FloatField(null=False, blank=False)
	walk_toll_amt = models.FloatField(null=False, blank=False)
	hbw_dat_time_amt = models.FloatField(null=False, blank=False)
	hbw_dat_dist_amt = models.FloatField(null=False, blank=False)
	hbw_dat_ivt_amt = models.FloatField(null=False, blank=False)
	hbw_wat_ivt_amt = models.FloatField(null=False, blank=False)
	nhbw_wat_ivt_amt = models.FloatField(null=False, blank=False)
	hbw_dat_walk_amt = models.FloatField(null=False, blank=False)
	hbw_wat_walk_amt = models.FloatField(null=False, blank=False)
	nhbw_wat_walk_amt = models.FloatField(null=False, blank=False)
	hbw_dat_wait_amt = models.FloatField(null=False, blank=False)
	hbw_wat_wait_amt = models.FloatField(null=False, blank=False)
	nhbw_wat_wait_amt = models.FloatField(null=False, blank=False)
	hbw_dat_fare_amt = models.FloatField(null=False, blank=False)
	hbw_wat_fare_amt = models.FloatField(null=False, blank=False)
	nhbw_wat_fare_amt = models.FloatField(null=False, blank=False)
	parking_amt = models.FloatField(null=False, blank=False)
	hbw_da_1_base_trips = models.FloatField(null=False, blank=False)
	hbw_da_2_base_trips = models.FloatField(null=False, blank=False)
	hbw_da_3_base_trips = models.FloatField(null=False, blank=False)
	hbw_da_4_base_trips = models.FloatField(null=False, blank=False)
	nhbw_da_base_trips = models.FloatField(null=False, blank=False)
	all_sr2_base_trips = models.FloatField(null=False, blank=False)
	all_sr3_base_trips = models.FloatField(null=False, blank=False)
	vanpool_base_trips = models.FloatField(null=False, blank=False)
	lt_truck_base_trips = models.FloatField(null=False, blank=False)
	md_truck_base_trips = models.FloatField(null=False, blank=False)
	hv_truck_base_trips = models.FloatField(null=False, blank=False)
	bike_base_trips = models.FloatField(null=False, blank=False)
	walk_base_trips = models.FloatField(null=False, blank=False)
	hbw_da_1_alt_trips = models.FloatField(null=False, blank=False)
	hbw_da_2_alt_trips = models.FloatField(null=False, blank=False)
	hbw_da_3_alt_trips = models.FloatField(null=False, blank=False)
	hbw_da_4_alt_trips = models.FloatField(null=False, blank=False)
	nhbw_da_alt_trips = models.FloatField(null=False, blank=False)
	all_sr2_alt_trips = models.FloatField(null=False, blank=False)
	all_sr3_alt_trips = models.FloatField(null=False, blank=False)
	vanpool_alt_trips = models.FloatField(null=False, blank=False)
	lt_truck_alt_trips = models.FloatField(null=False, blank=False)
	md_truck_alt_trips = models.FloatField(null=False, blank=False)
	hv_truck_alt_trips = models.FloatField(null=False, blank=False)
	bike_alt_trips = models.FloatField(null=False, blank=False)
	walk_alt_trip = models.FloatField(null=False, blank=False)



class UnreliabilityResult(models.Model):
	analysis = models.ForeignKey(Analysis)
	scenario = models.CharField(max_length=255, null=False, blank=False)
	tod = models.CharField(null=False, blank=False, max_length=3)
	unr_hbw_da_1_amt = models.FloatField(null=False, blank=False)
	unr_hbw_da_2_amt = models.FloatField(null=False, blank=False)
	unr_hbw_da_3_amt = models.FloatField(null=False, blank=False)
	unr_hbw_da_4_amt = models.FloatField(null=False, blank=False)
	unr_nhbw_da_amt = models.FloatField(null=False, blank=False)
	unr_all_sr2_amt = models.FloatField(null=False, blank=False)
	unr_all_sr3_amt = models.FloatField(null=False, blank=False)
	unr_vanpool_amt = models.FloatField(null=False, blank=False)
	unr_lt_truck_amt = models.FloatField(null=False, blank=False)
	unr_hv_truck_amt = models.FloatField(null=False, blank=False)
	unr_md_truck_amt = models.FloatField(null=False, blank=False)