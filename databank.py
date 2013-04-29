"""
Requires emme2.py and assumes it will be in the same directory or
on the $PYTHONPATH. Code is specific to PSRC model runs. Takes two
command-line arguments: the first is the path to the directory
containing the directories that contain the data banks this will be
the directory created by unzipping the archive provided by PSRC the
second is the name of the schema where the tables should be filled in
Reads only the matrices we care about. Many others exist in the data
banks.
"""

import sys, os
from emme2lib import *
from psycopg2 import connect

path_to_data = sys.argv[1]
schema = sys.argv[2]

connection = connect(database='psrc_lcp', host='localhost', user='postgres',password='BCAdatabase')
cursor = connection.cursor()

try:
	cursor.execute("drop schema %s cascade;" % schema)
except:
	pass
connection.commit()
cursor.execute("create schema %s;\n" % schema)
connection.commit()
cursor.execute("""
create table %s.links (like public.links, primary key (scenario, i_node, j_node));\n
create table %s.segments (like public.segments, primary key (scenario, i_node, j_node, line));\n
create table %s.bank1 (like public.bank1, primary key (o_zone, d_zone));\n
create table %s.bank2 (like public.bank2, primary key (o_zone, d_zone));\n
create table %s.bank3 (like public.bank3, primary key (o_zone, d_zone));\n
create table %s.bank4 (like public.bank4, primary key (o_zone, d_zone));\n
create table %s.parking (like public.parking, primary key (d_zone));\n
create table %s.parking_trips (like public.parking_trips, primary key (o_zone, d_zone));\n
create table %s.pr_trips (like public.pr_trips, primary key (o_zone, d_zone));\n
create table %s.hbw_trips (like public.hbw_trips, primary key (tod, o_zone, d_zone));\n""" % (schema, schema, schema, schema, schema, schema, schema, schema, schema, schema))
connection.commit()

def links_and_segments():
	def make_link_data(bank, scenario):
		print 'Making link data for scenario ' + str(scenario) + ' from data bank at ' + bank
		cursor.execute("DELETE FROM %s.links WHERE scenario = %s;" % (schema, str(scenario)))
		connection.commit()
		offsets = read_offsets(bank)
		global_params = read_global_params(bank, offsets)
		scenario_params = read_scenario_params(bank, offsets, global_params)
		link_names = read_link_names(bank, offsets, global_params, scenario_params, scenario)
		link_data = read_link_data(bank, offsets, global_params, scenario_params, scenario, link_names)
		toll1 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@toll1')
		toll2 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@toll2')
		toll3 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@toll3')
		trkc1 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@trkc1')
		trkc2 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@trkc2')
		trkc3 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@trkc3')
		ferry = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@ferry')
		bridg = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@bridg')
		voltr = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@voltr')
		sov = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@sov')
		hbw1 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hbw1')
		hbw2 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hbw2')
		hbw3 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hbw3')
		hbw4 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hbw4')
		hov2 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hov2')
		hov3 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@hov3')
		vpool = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@vpool')
		light = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@light')
		mediu = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@mediu')
		heavy = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@heavy')
		trkt2 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@trkt2')
		trkt3 = read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, '@trkt3')
		offsets = read_offsets(path_to_data + '/CostBenTool/emmebank')
		global_params = read_global_params(path_to_data + '/CostBenTool/emmebank', offsets)
		scenario_params = read_scenario_params(path_to_data + '/CostBenTool/emmebank', offsets, global_params)
		link_names = read_link_names(path_to_data + '/CostBenTool/emmebank', offsets, global_params, scenario_params, str(int(scenario) + 8900))
		link_data = read_link_data(path_to_data + '/CostBenTool/emmebank', offsets, global_params, scenario_params, str(int(scenario) + 8900), link_names)
		uncer = read_extra_link_data(path_to_data + '/CostBenTool/emmebank', offsets, global_params, scenario_params, str(int(scenario) + 8900), link_names, '@uncer')
		for i in link_data.keys():
			cursor.execute(
				"""insert into %s.links
				(scenario, i_node, j_node, length, link_type, volume_delay_function, lanes, aux_transit_volume, auto_time,
					additional_volume, ul1, ul2, ul3, toll_da, toll_2p, toll_3plus, toll_lt_truck, toll_med_truck, 
					toll_hvy_truck, ferry_link, bridge_link, transit_persons, sov_volume, hbw1_sov_volume, hbw2_sov_volume, 
					hbw3_sov_volume, hbw4_sov_volume, hov2_volume, hov3plus_volume, vanpool_volume, lt_truck_volume, 
					med_truck_volume, hvy_truck_volume, extra_time_medium_truck, extra_time_heavy_truck, uncertainty)
				values
				(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
				%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""" % (schema, scenario, i[0], i[1], link_data[i]['len'], link_data[i]['ltyp'], link_data[i]['vdf'], link_data[i]['lan'], 
					link_data[i]['volax'], link_data[i]['timau'], link_data[i]['volad'], link_data[i]['ul1'], 
					link_data[i]['ul2'], link_data[i]['ul3'], toll1.get(i, 0), toll2.get(i, 0), toll3.get(i, 0), 
					trkc1.get(i, 0), trkc2.get(i, 0), trkc3.get(i, 0), ferry.get(i, 0), bridg.get(i, 0), voltr.get(i, 0), 
					sov.get(i, 0), hbw1.get(i, 0), hbw2.get(i, 0), hbw3.get(i, 0), hbw4.get(i, 0), hov2.get(i, 0),
					hov3.get(i, 0), vpool.get(i, 0), light.get(i, 0), mediu.get(i, 0), heavy.get(i, 0), trkt2.get(i, 0), 
					trkt3.get(i, 0), uncer.get(i, 0)))
		connection.commit()
		print 'Link data made for scenario ' + str(scenario) + ' from data bank at ' + bank
		print

	def make_segment_data(bank, scenario):
		print 'Making segment data for scenario ' + str(scenario) + ' from data bank at ' + bank
		cursor.execute("DELETE FROM %s.segments WHERE scenario = %s;" % (schema, str(scenario)))
		connection.commit()
		offsets = read_offsets(bank)
		global_params = read_global_params(bank, offsets)
		scenario_params = read_scenario_params(bank, offsets, global_params)
		link_names = read_link_names(bank, offsets, global_params, scenario_params, scenario)
		segment_data = read_segment_data(bank, offsets, global_params, scenario_params, scenario, link_names)
		for i in segment_data:
			try:
				cursor.execute(
					"""insert into %s.segments
					(scenario, i_node, j_node, line, transit_time, transit_volume, headway, seated_capacity, total_capacity)
					values
					(%s, %s, %s, '%s', %f, %f, %f, %f, %f);""" % (schema, scenario, i['link'][0], i['link'][1], i['line'], i['timtr'], i['voltr'], i['headway'], i['seated_cap'], i['total_cap']))
			except:
				pass
			connection.commit()
		print 'Segment data made for scenario ' + str(scenario) + ' from data bank at ' + bank
		print


	# Make link and segment data for each relevant scenario
	for source in ((path_to_data + '/Bank1/emmebank', '1002'), (path_to_data + '/Bank2/emmebank', '1004'),
		(path_to_data + '/Bank3/emmebank', '1003'), (path_to_data + '/Bank3/emmebank', '1005'), 
		(path_to_data + '/Bank3/emmebank', '1006')):
		make_link_data(source[0], source[1])
		make_segment_data(source[0], source[1])
	return

def bank1_full():
	# Make zone-to-zone data for each full matrix in bank1
	cursor.execute("DELETE FROM %s.bank1;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank1/emmebank')
	global_params = read_global_params(path_to_data + '/Bank1/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank1/emmebank', offsets, global_params)
	variables = ('aa1cs1', 'aa1cs2', 'aa1cs3', 'aa1cs4', 'aauxau', 'aauxwa', 'abrdau', 'abrdwa', 'ahbw1v', 'ahbw2v', 
		'ahbw3v', 'ahbw4v', 'ahvtrk', 'aivtau', 'aivtwa', 'alttrk', 'ambike', 'amdtrk', 'amwalk', 'anbdau', 
		'anbdwa', 'atrnst', 'atrtau', 'atrtwa', 'atwkau', 'atwtau', 'atwtwa', 'au1cos', 'au1dis', 'au1tim', 
		'au2cos', 'au2tim', 'au3cos', 'au3tim', 'au4cos', 'au4tim', 'avehda', 'avehs2', 'avehs3', 'avpool', 
		'awt1au', 'awt1wa', 'biketm', 'hbwtaa', 'hbwtaw', 'hvygcs', 'hvytim', 'lgtgcs', 'lgttim', 'medgcs', 
		'medtim', 'pkfara', 'pkfarw', 'walktm', 'pnrtim', 'pnrdis')
	for start_zone in range(1, 1201, 10):
		matrix = {}
		for variable in variables:
			matrix[variable] = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, variable, start_zone, 10)
		for o_zone in range(start_zone, start_zone + 10):
			for d_zone in range(1, 1201):
				cursor.execute("""INSERT INTO %s.bank1 
					(o_zone, d_zone, aa1cs1, aa1cs2, aa1cs3, aa1cs4, aauxau, aauxwa, abrdau, abrdwa, ahbw1v, ahbw2v, 
					ahbw3v, ahbw4v, ahvtrk, aivtau, aivtwa, alttrk, ambike, amdtrk, amwalk, anbdau, 
					anbdwa, atrnst, atrtau, atrtwa, atwkau, atwtau, atwtwa, au1cos, au1dis, au1tim, 
					au2cos, au2tim, au3cos, au3tim, au4cos, au4tim, avehda, avehs2, avehs3, avpool, 
					awt1au, awt1wa, biketm, hbwtaa, hbwtaw, hvygcs, hvytim, lgtgcs, lgttim, medgcs, 
					medtim, pkfara, pkfarw, walktm, pnrtim, pnrdis) 
					VALUES 
					(%s, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f);""" % 
					(schema, o_zone, d_zone, matrix['aa1cs1'][o_zone-start_zone][d_zone-1], matrix['aa1cs2'][o_zone-start_zone][d_zone-1], matrix['aa1cs3'][o_zone-start_zone][d_zone-1], 
					matrix['aa1cs4'][o_zone-start_zone][d_zone-1], matrix['aauxau'][o_zone-start_zone][d_zone-1], matrix['aauxwa'][o_zone-start_zone][d_zone-1], 
					matrix['abrdau'][o_zone-start_zone][d_zone-1], matrix['abrdwa'][o_zone-start_zone][d_zone-1], matrix['ahbw1v'][o_zone-start_zone][d_zone-1], 
					matrix['ahbw2v'][o_zone-start_zone][d_zone-1], matrix['ahbw3v'][o_zone-start_zone][d_zone-1], matrix['ahbw4v'][o_zone-start_zone][d_zone-1], 
					matrix['ahvtrk'][o_zone-start_zone][d_zone-1], matrix['aivtau'][o_zone-start_zone][d_zone-1], matrix['aivtwa'][o_zone-start_zone][d_zone-1], 
					matrix['alttrk'][o_zone-start_zone][d_zone-1], matrix['ambike'][o_zone-start_zone][d_zone-1], matrix['amdtrk'][o_zone-start_zone][d_zone-1], 
					matrix['amwalk'][o_zone-start_zone][d_zone-1], matrix['anbdau'][o_zone-start_zone][d_zone-1], matrix['anbdwa'][o_zone-start_zone][d_zone-1], 
					matrix['atrnst'][o_zone-start_zone][d_zone-1], matrix['atrtau'][o_zone-start_zone][d_zone-1], matrix['atrtwa'][o_zone-start_zone][d_zone-1], 
					matrix['atwkau'][o_zone-start_zone][d_zone-1], matrix['atwtau'][o_zone-start_zone][d_zone-1], matrix['atwtwa'][o_zone-start_zone][d_zone-1], 
					matrix['au1cos'][o_zone-start_zone][d_zone-1], matrix['au1dis'][o_zone-start_zone][d_zone-1], matrix['au1tim'][o_zone-start_zone][d_zone-1], 
					matrix['au2cos'][o_zone-start_zone][d_zone-1], matrix['au2tim'][o_zone-start_zone][d_zone-1], matrix['au3cos'][o_zone-start_zone][d_zone-1], 
					matrix['au3tim'][o_zone-start_zone][d_zone-1], matrix['au4cos'][o_zone-start_zone][d_zone-1], matrix['au4tim'][o_zone-start_zone][d_zone-1], 
					matrix['avehda'][o_zone-start_zone][d_zone-1], matrix['avehs2'][o_zone-start_zone][d_zone-1], matrix['avehs3'][o_zone-start_zone][d_zone-1], 
					matrix['avpool'][o_zone-start_zone][d_zone-1], matrix['awt1au'][o_zone-start_zone][d_zone-1], matrix['awt1wa'][o_zone-start_zone][d_zone-1], 
					matrix['biketm'][o_zone-start_zone][d_zone-1], matrix['hbwtaa'][o_zone-start_zone][d_zone-1], matrix['hbwtaw'][o_zone-start_zone][d_zone-1], 
					matrix['hvygcs'][o_zone-start_zone][d_zone-1], matrix['hvytim'][o_zone-start_zone][d_zone-1], matrix['lgtgcs'][o_zone-start_zone][d_zone-1], 
					matrix['lgttim'][o_zone-start_zone][d_zone-1], matrix['medgcs'][o_zone-start_zone][d_zone-1], matrix['medtim'][o_zone-start_zone][d_zone-1], 
					matrix['pkfara'][o_zone-start_zone][d_zone-1], matrix['pkfarw'][o_zone-start_zone][d_zone-1], matrix['walktm'][o_zone-start_zone][d_zone-1],
					matrix['pnrtim'][o_zone-start_zone][d_zone-1], matrix['pnrdis'][o_zone-start_zone][d_zone-1]))
		connection.commit()
		print 'Added origin zones ', start_zone, ' to ', start_zone + 9,' to bank1.sql'
	return

def bank2_full():
	# Make zone-to-zone data for each full matrix in bank2
	cursor.execute("DELETE FROM %s.bank2;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank2/emmebank')
	global_params = read_global_params(path_to_data + '/Bank2/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank2/emmebank', offsets, global_params)
	variables = ('hnwcp1', 'hnwcp3', 'hnwcp4', 'hnwcp5', 'hnwcp6', 'ma1cs1', 'ma1cs2', 'ma1cs3', 'ma1cs4', 'md2btm', 
		'md3btm', 'mdsbtm', 'mh1bcs', 'mh2bcs', 'mh3bcs', 'mh4bcs', 'mhbw1v', 'mhbw2v', 'mhbw3v', 'mhbw4v', 
		'nwbktm', 'nwwktm', 'oauxwa', 'obrdwa', 'off1cs', 'off1ds', 'off1tm', 'off2cs', 'off2tm', 'off3cs', 
		'off3tm', 'ohvtrk', 'oivtwa', 'olttrk', 'omdtrk', 'onbdwa', 'opbike', 'opfara', 'opfarw', 'opwalk', 
		'otrnst', 'otrtwa', 'otwtwa', 'ovehda', 'ovehs2', 'ovehs3', 'owt1wa', 'lgtgcs', 'medgcs', 'hvygcs',
		'lgttim', 'medtim', 'hvytim')
	for start_zone in range(1, 1201, 10):
		matrix = {}
		for variable in variables:
			matrix[variable] = read_full_matrix(path_to_data + '/Bank2/emmebank', offsets, global_params, matrix_names, variable, start_zone, 10)
		for o_zone in range(start_zone, start_zone + 10):
			for d_zone in range(1, 1201):
				cursor.execute("""INSERT INTO %s.bank2 
					(o_zone, d_zone, hnwcp1, hnwcp3, hnwcp4, hnwcp5, hnwcp6, ma1cs1, ma1cs2, ma1cs3, ma1cs4, md2btm, 
						md3btm, mdsbtm, mh1bcs, mh2bcs, mh3bcs, mh4bcs, mhbw1v, mhbw2v, mhbw3v, mhbw4v, 
						nwbktm, nwwktm, oauxwa, obrdwa, off1cs, off1ds, off1tm, off2cs, off2tm, off3cs, 
						off3tm, ohvtrk, oivtwa, olttrk, omdtrk, onbdwa, opbike, opfara, opfarw, opwalk, 
						otrnst, otrtwa, otwtwa, ovehda, ovehs2, ovehs3, owt1wa, lgtgcs, medgcs, hvygcs,
						lgttim, medtim, hvytim) 
					VALUES 
					(%s, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f);""" % 
					(schema, o_zone, d_zone, matrix['hnwcp1'][o_zone-start_zone][d_zone-1], matrix['hnwcp3'][o_zone-start_zone][d_zone-1], matrix['hnwcp4'][o_zone-start_zone][d_zone-1], 
					matrix['hnwcp5'][o_zone-start_zone][d_zone-1], matrix['hnwcp6'][o_zone-start_zone][d_zone-1], matrix['ma1cs1'][o_zone-start_zone][d_zone-1], 
					matrix['ma1cs2'][o_zone-start_zone][d_zone-1], matrix['ma1cs3'][o_zone-start_zone][d_zone-1], matrix['ma1cs4'][o_zone-start_zone][d_zone-1], 
					matrix['md2btm'][o_zone-start_zone][d_zone-1], matrix['md3btm'][o_zone-start_zone][d_zone-1], matrix['mdsbtm'][o_zone-start_zone][d_zone-1], 
					matrix['mh1bcs'][o_zone-start_zone][d_zone-1], matrix['mh2bcs'][o_zone-start_zone][d_zone-1], matrix['mh3bcs'][o_zone-start_zone][d_zone-1], 
					matrix['mh4bcs'][o_zone-start_zone][d_zone-1], matrix['mhbw1v'][o_zone-start_zone][d_zone-1], matrix['mhbw2v'][o_zone-start_zone][d_zone-1], 
					matrix['mhbw3v'][o_zone-start_zone][d_zone-1], matrix['mhbw4v'][o_zone-start_zone][d_zone-1], matrix['nwbktm'][o_zone-start_zone][d_zone-1], 
					matrix['nwwktm'][o_zone-start_zone][d_zone-1], matrix['oauxwa'][o_zone-start_zone][d_zone-1], matrix['obrdwa'][o_zone-start_zone][d_zone-1], 
					matrix['off1cs'][o_zone-start_zone][d_zone-1], matrix['off1ds'][o_zone-start_zone][d_zone-1], matrix['off1tm'][o_zone-start_zone][d_zone-1], 
					matrix['off2cs'][o_zone-start_zone][d_zone-1], matrix['off2tm'][o_zone-start_zone][d_zone-1], matrix['off3cs'][o_zone-start_zone][d_zone-1], 
					matrix['off3tm'][o_zone-start_zone][d_zone-1], matrix['ohvtrk'][o_zone-start_zone][d_zone-1], matrix['oivtwa'][o_zone-start_zone][d_zone-1], 
					matrix['olttrk'][o_zone-start_zone][d_zone-1], matrix['omdtrk'][o_zone-start_zone][d_zone-1], matrix['onbdwa'][o_zone-start_zone][d_zone-1], 
					matrix['opbike'][o_zone-start_zone][d_zone-1], matrix['opfara'][o_zone-start_zone][d_zone-1], matrix['opfarw'][o_zone-start_zone][d_zone-1], 
					matrix['opwalk'][o_zone-start_zone][d_zone-1], matrix['otrnst'][o_zone-start_zone][d_zone-1], matrix['otrtwa'][o_zone-start_zone][d_zone-1], 
					matrix['otwtwa'][o_zone-start_zone][d_zone-1], matrix['ovehda'][o_zone-start_zone][d_zone-1], matrix['ovehs2'][o_zone-start_zone][d_zone-1], 
					matrix['ovehs3'][o_zone-start_zone][d_zone-1], matrix['owt1wa'][o_zone-start_zone][d_zone-1], matrix['lgtgcs'][o_zone-start_zone][d_zone-1],
					matrix['medgcs'][o_zone-start_zone][d_zone-1], matrix['hvygcs'][o_zone-start_zone][d_zone-1], matrix['lgttim'][o_zone-start_zone][d_zone-1],
					matrix['medtim'][o_zone-start_zone][d_zone-1],matrix['hvytim'][o_zone-start_zone][d_zone-1],))
		connection.commit()
		print 'Added origin zones ', start_zone, ' to ', start_zone + 9,' to bank2.sql'
	return

def bank3_full():
	# Make zone-to-zone data for each full matrix in bank3
	cursor.execute("DELETE FROM %s.bank3;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank3/emmebank')
	global_params = read_global_params(path_to_data + '/Bank3/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank3/emmebank', offsets, global_params)
	variables = ('au1dis', 'ea1cs1', 'ea1cs2', 'ea1cs3', 'ea1cs4', 'eau1cs', 'eau1ds', 'eau1tm', 'eau2cs', 'eau2tm', 
		'eau3cs', 'eau3tm', 'ebiket', 'ehbw1v', 'ehbw2v', 'ehbw3v', 'ehbw4v', 'ehvtrk', 'ehvycs', 'ehvytm', 
		'elgtcs', 'elgttm', 'elttrk', 'emdtrk', 'emedcs', 'emedtm', 'etrnst', 'evbike', 'evehda', 'evehs2', 
		'evehs3', 'evwalk', 'ewlktm', 'na1cs1', 'na1cs2', 'na1cs3', 'na1cs4', 'nau1cs', 'nau1ds', 'nau1tm', 
		'nau2cs', 'nau2tm', 'nau3cs', 'nau3tm', 'nbiket', 'nhbw1v', 'nhbw2v', 'nhbw3v', 'nhbw4v', 'nhvtrk', 
		'nhvycs', 'nhvytm', 'nibike', 'niwalk', 'nlgtcs', 'nlgttm', 'nlttrk', 'nmdtrk', 'nmedcs', 'nmedtm', 
		'ntrnst', 'nvehda', 'nvehs2', 'nvehs3', 'nwlktm', 'pa1cs1', 'pa1cs2', 'pa1cs3', 'pa1cs4', 'pau1cs', 
		'pau1ds', 'pau1tm', 'pau2cs', 'pau2tm', 'pau3cs', 'pau3tm', 'pau4cs', 'pau4tm', 'pbiket', 'phbw1v', 
		'phbw2v', 'phbw3v', 'phbw4v', 'phvtrk', 'phvycs', 'phvytm', 'plgtcs', 'plgttm', 'plttrk', 'pmbike', 
		'pmdtrk', 'pmedcs', 'pmedtm', 'pmwalk', 'ptrnst', 'pvehda', 'pvehs2', 'pvehs3', 'pvpool', 'pwlktm')
		#'dashar', 'cpshar', 'vpshar', 'bkshar', 'wkshar', 'bsshar'
	for start_zone in range(1, 1201, 10):
		matrix = {}
		for variable in variables:
			matrix[variable] = read_full_matrix(path_to_data + '/Bank3/emmebank', offsets, global_params, matrix_names, variable, start_zone, 10)
		for o_zone in range(start_zone, start_zone + 10):
			for d_zone in range(1, 1201):
				cursor.execute("""INSERT INTO %s.bank3 
					(o_zone, d_zone, au1dis, ea1cs1, ea1cs2, ea1cs3, ea1cs4, eau1cs, eau1ds, eau1tm, eau2cs, eau2tm, 
						eau3cs, eau3tm, ebiket, ehbw1v, ehbw2v, ehbw3v, ehbw4v, ehvtrk, ehvycs, ehvytm, 
						elgtcs, elgttm, elttrk, emdtrk, emedcs, emedtm, etrnst, evbike, evehda, evehs2, 
						evehs3, evwalk, ewlktm, na1cs1, na1cs2, na1cs3, na1cs4, nau1cs, nau1ds, nau1tm, 
						nau2cs, nau2tm, nau3cs, nau3tm, nbiket, nhbw1v, nhbw2v, nhbw3v, nhbw4v, nhvtrk, 
						nhvycs, nhvytm, nibike, niwalk, nlgtcs, nlgttm, nlttrk, nmdtrk, nmedcs, nmedtm, 
						ntrnst, nvehda, nvehs2, nvehs3, nwlktm, pa1cs1, pa1cs2, pa1cs3, pa1cs4, pau1cs, 
						pau1ds, pau1tm, pau2cs, pau2tm, pau3cs, pau3tm, pau4cs, pau4tm, pbiket, phbw1v, 
						phbw2v, phbw3v, phbw4v, phvtrk, phvycs, phvytm, plgtcs, plgttm, plttrk, pmbike, 
						pmdtrk, pmedcs, pmedtm, pmwalk, ptrnst, pvehda, pvehs2, pvehs3, pvpool, pwlktm) 
					VALUES 
					(%s, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f);""" % 
					(schema, o_zone, d_zone, matrix['au1dis'][o_zone-start_zone][d_zone-1], matrix['ea1cs1'][o_zone-start_zone][d_zone-1], matrix['ea1cs2'][o_zone-start_zone][d_zone-1], 
					matrix['ea1cs3'][o_zone-start_zone][d_zone-1], matrix['ea1cs4'][o_zone-start_zone][d_zone-1], matrix['eau1cs'][o_zone-start_zone][d_zone-1], 
					matrix['eau1ds'][o_zone-start_zone][d_zone-1], matrix['eau1tm'][o_zone-start_zone][d_zone-1], matrix['eau2cs'][o_zone-start_zone][d_zone-1], 
					matrix['eau2tm'][o_zone-start_zone][d_zone-1], matrix['eau3cs'][o_zone-start_zone][d_zone-1], matrix['eau3tm'][o_zone-start_zone][d_zone-1], 
					matrix['ebiket'][o_zone-start_zone][d_zone-1], matrix['ehbw1v'][o_zone-start_zone][d_zone-1], matrix['ehbw2v'][o_zone-start_zone][d_zone-1], 
					matrix['ehbw3v'][o_zone-start_zone][d_zone-1], matrix['ehbw4v'][o_zone-start_zone][d_zone-1], matrix['ehvtrk'][o_zone-start_zone][d_zone-1], 
					matrix['ehvycs'][o_zone-start_zone][d_zone-1], matrix['ehvytm'][o_zone-start_zone][d_zone-1], matrix['elgtcs'][o_zone-start_zone][d_zone-1], 
					matrix['elgttm'][o_zone-start_zone][d_zone-1], matrix['elttrk'][o_zone-start_zone][d_zone-1], matrix['emdtrk'][o_zone-start_zone][d_zone-1], 
					matrix['emedcs'][o_zone-start_zone][d_zone-1], matrix['emedtm'][o_zone-start_zone][d_zone-1], matrix['etrnst'][o_zone-start_zone][d_zone-1], 
					matrix['evbike'][o_zone-start_zone][d_zone-1], matrix['evehda'][o_zone-start_zone][d_zone-1], matrix['evehs2'][o_zone-start_zone][d_zone-1], 
					matrix['evehs3'][o_zone-start_zone][d_zone-1], matrix['evwalk'][o_zone-start_zone][d_zone-1], matrix['ewlktm'][o_zone-start_zone][d_zone-1], 
					matrix['na1cs1'][o_zone-start_zone][d_zone-1], matrix['na1cs2'][o_zone-start_zone][d_zone-1], matrix['na1cs3'][o_zone-start_zone][d_zone-1], 
					matrix['na1cs4'][o_zone-start_zone][d_zone-1], matrix['nau1cs'][o_zone-start_zone][d_zone-1], matrix['nau1ds'][o_zone-start_zone][d_zone-1], 
					matrix['nau1tm'][o_zone-start_zone][d_zone-1], matrix['nau2cs'][o_zone-start_zone][d_zone-1], matrix['nau2tm'][o_zone-start_zone][d_zone-1], 
					matrix['nau3cs'][o_zone-start_zone][d_zone-1], matrix['nau3tm'][o_zone-start_zone][d_zone-1], matrix['nbiket'][o_zone-start_zone][d_zone-1], 
					matrix['nhbw1v'][o_zone-start_zone][d_zone-1], matrix['nhbw2v'][o_zone-start_zone][d_zone-1], matrix['nhbw3v'][o_zone-start_zone][d_zone-1], 
					matrix['nhbw4v'][o_zone-start_zone][d_zone-1], matrix['nhvtrk'][o_zone-start_zone][d_zone-1], matrix['nhvycs'][o_zone-start_zone][d_zone-1], 
					matrix['nhvytm'][o_zone-start_zone][d_zone-1], matrix['nibike'][o_zone-start_zone][d_zone-1], matrix['niwalk'][o_zone-start_zone][d_zone-1], 
					matrix['nlgtcs'][o_zone-start_zone][d_zone-1], matrix['nlgttm'][o_zone-start_zone][d_zone-1], matrix['nlttrk'][o_zone-start_zone][d_zone-1], 
					matrix['nmdtrk'][o_zone-start_zone][d_zone-1], matrix['nmedcs'][o_zone-start_zone][d_zone-1], matrix['nmedtm'][o_zone-start_zone][d_zone-1], 
					matrix['ntrnst'][o_zone-start_zone][d_zone-1], matrix['nvehda'][o_zone-start_zone][d_zone-1], matrix['nvehs2'][o_zone-start_zone][d_zone-1], 
					matrix['nvehs3'][o_zone-start_zone][d_zone-1], matrix['nwlktm'][o_zone-start_zone][d_zone-1], matrix['pa1cs1'][o_zone-start_zone][d_zone-1], 
					matrix['pa1cs2'][o_zone-start_zone][d_zone-1], matrix['pa1cs3'][o_zone-start_zone][d_zone-1], matrix['pa1cs4'][o_zone-start_zone][d_zone-1], 
					matrix['pau1cs'][o_zone-start_zone][d_zone-1], matrix['pau1ds'][o_zone-start_zone][d_zone-1], matrix['pau1tm'][o_zone-start_zone][d_zone-1], 
					matrix['pau2cs'][o_zone-start_zone][d_zone-1], matrix['pau2tm'][o_zone-start_zone][d_zone-1], matrix['pau3cs'][o_zone-start_zone][d_zone-1], 
					matrix['pau3tm'][o_zone-start_zone][d_zone-1], matrix['pau4cs'][o_zone-start_zone][d_zone-1], matrix['pau4tm'][o_zone-start_zone][d_zone-1], 
					matrix['pbiket'][o_zone-start_zone][d_zone-1], matrix['phbw1v'][o_zone-start_zone][d_zone-1], matrix['phbw2v'][o_zone-start_zone][d_zone-1], 
					matrix['phbw3v'][o_zone-start_zone][d_zone-1], matrix['phbw4v'][o_zone-start_zone][d_zone-1], matrix['phvtrk'][o_zone-start_zone][d_zone-1], 
					matrix['phvycs'][o_zone-start_zone][d_zone-1], matrix['phvytm'][o_zone-start_zone][d_zone-1], matrix['plgtcs'][o_zone-start_zone][d_zone-1], 
					matrix['plgttm'][o_zone-start_zone][d_zone-1], matrix['plttrk'][o_zone-start_zone][d_zone-1], matrix['pmbike'][o_zone-start_zone][d_zone-1], 
					matrix['pmdtrk'][o_zone-start_zone][d_zone-1], matrix['pmedcs'][o_zone-start_zone][d_zone-1], matrix['pmedtm'][o_zone-start_zone][d_zone-1], 
					matrix['pmwalk'][o_zone-start_zone][d_zone-1], matrix['ptrnst'][o_zone-start_zone][d_zone-1], matrix['pvehda'][o_zone-start_zone][d_zone-1], 
					matrix['pvehs2'][o_zone-start_zone][d_zone-1], matrix['pvehs3'][o_zone-start_zone][d_zone-1], matrix['pvpool'][o_zone-start_zone][d_zone-1], 
					matrix['pwlktm'][o_zone-start_zone][d_zone-1]))
		connection.commit()
		print 'Added origin zones ', start_zone, ' to ', start_zone + 9,' to bank3.sql'
	return

def bank4_full():
	# Make zone-to-zone data for each full matrix in bank3
	cursor.execute("DELETE FROM %s.bank4;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/CostBenTool/emmebank')
	global_params = read_global_params(path_to_data + '/CostBenTool/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/CostBenTool/emmebank', offsets, global_params)
	variables = ('am1tim', 'am2tim', 'am3tim', 'am4tim', 'am1tm1', 'am1tm2', 'am1tm3', 'am1tm4', 'amltim', 'ammtim', 'amhtim', 
		'am1tol', 'am2tol', 'am3tol', 'am4tol', 'am1tl1', 'am1tl2', 'am1tl3', 'am1tl4', 'amltol', 'ammtol', 'amhtol', 
		'mm1tim', 'mm2tim', 'mm3tim', 'mm1tm1', 'mm1tm2', 'mm1tm3', 'mm1tm4', 'mmltim', 'mmmtim', 'mmhtim', 
		'mm1tol', 'mm2tol', 'mm3tol', 'mm1tl1', 'mm1tl2', 'mm1tl3', 'mm1tl4', 'mmltol', 'mmmtol', 'mmhtol', 
		'pm1tim', 'pm2tim', 'pm3tim', 'pm4tim', 'pm1tm1', 'pm1tm2', 'pm1tm3', 'pm1tm4', 'pmltim', 'pmmtim', 'pmhtim', 
		'pm1tol', 'pm2tol', 'pm3tol', 'pm4tol', 'pm1tl1', 'pm1tl2', 'pm1tl3', 'pm1tl4', 'pmltol', 'pmmtol', 'pmhtol', 
		'em1tim', 'em2tim', 'em3tim', 'em1tm1', 'em1tm2', 'em1tm3', 'em1tm4', 'emltim', 'emmtim', 'emhtim', 
		'em1tol', 'em2tol', 'em3tol', 'em1tl1', 'em1tl2', 'em1tl3', 'em1tl4', 'emltol', 'emmtol', 'emhtol', 
		'nm1tim', 'nm2tim', 'nm3tim', 'nm1tm1', 'nm1tm2', 'nm1tm3', 'nm1tm4', 'nmltim', 'nmmtim', 'nmhtim', 
		'nm1tol', 'nm2tol', 'nm3tol', 'nm1tl1', 'nm1tl2', 'nm1tl3', 'nm1tl4', 'nmltol', 'nmmtol', 'nmhtol',
		'am1unc', 'am2unc', 'am3unc', 'am4unc', 'am1uc1', 'am1uc2', 'am1uc3', 'am1uc4', 'amlunc', 'ammunc', 'amhunc', 
		'mm1unc', 'mm2unc', 'mm3unc', 'mm1uc1', 'mm1uc2', 'mm1uc3', 'mm1uc4', 'mmlunc', 'mmmunc', 'mmhunc', 
		'pm1unc', 'pm2unc', 'pm3unc', 'pm4unc', 'pm1uc1', 'pm1uc2', 'pm1uc3', 'pm1uc4', 'pmlunc', 'pmmunc', 'pmhunc', 
		'em1unc', 'em2unc', 'em3unc', 'em1uc1', 'em1uc2', 'em1uc3', 'em1uc4', 'emlunc', 'emmunc', 'emhunc', 
		'nm1unc', 'nm2unc', 'nm3unc', 'nm1uc1', 'nm1uc2', 'nm1uc3', 'nm1uc4', 'nmlunc', 'nmmunc', 'nmhunc')
	for start_zone in range(1, 1201, 10):
		matrix = {}
		for variable in variables:
			matrix[variable] = read_full_matrix(path_to_data + '/CostBenTool/emmebank', offsets, global_params, matrix_names, variable, start_zone, 10)
		for o_zone in range(start_zone, start_zone + 10):
			for d_zone in range(1, 1201):
				cursor.execute("""INSERT INTO %s.bank4 
					(o_zone, d_zone, am1tim, am2tim, am3tim, am4tim, am1tm1, am1tm2, am1tm3, am1tm4, amltim, ammtim, amhtim, 
					am1tol, am2tol, am3tol, am4tol, am1tl1, am1tl2, am1tl3, am1tl4, amltol, ammtol, amhtol, 
					mm1tim, mm2tim, mm3tim, mm1tm1, mm1tm2, mm1tm3, mm1tm4, mmltim, mmmtim, mmhtim, 
					mm1tol, mm2tol, mm3tol, mm1tl1, mm1tl2, mm1tl3, mm1tl4, mmltol, mmmtol, mmhtol, 
					pm1tim, pm2tim, pm3tim, pm4tim, pm1tm1, pm1tm2, pm1tm3, pm1tm4, pmltim, pmmtim, pmhtim, 
					pm1tol, pm2tol, pm3tol, pm4tol, pm1tl1, pm1tl2, pm1tl3, pm1tl4, pmltol, pmmtol, pmhtol, 
					em1tim, em2tim, em3tim, em1tm1, em1tm2, em1tm3, em1tm4, emltim, emmtim, emhtim, 
					em1tol, em2tol, em3tol, em1tl1, em1tl2, em1tl3, em1tl4, emltol, emmtol, emhtol, 
					nm1tim, nm2tim, nm3tim, nm1tm1, nm1tm2, nm1tm3, nm1tm4, nmltim, nmmtim, nmhtim, 
					nm1tol, nm2tol, nm3tol, nm1tl1, nm1tl2, nm1tl3, nm1tl4, nmltol, nmmtol, nmhtol,
					am1unc, am2unc, am3unc, am4unc, am1uc1, am1uc2, am1uc3, am1uc4, amlunc, ammunc, amhunc, 
					mm1unc, mm2unc, mm3unc, mm1uc1, mm1uc2, mm1uc3, mm1uc4, mmlunc, mmmunc, mmhunc, 
					pm1unc, pm2unc, pm3unc, pm4unc, pm1uc1, pm1uc2, pm1uc3, pm1uc4, pmlunc, pmmunc, pmhunc, 
					em1unc, em2unc, em3unc, em1uc1, em1uc2, em1uc3, em1uc4, emlunc, emmunc, emhunc, 
					nm1unc, nm2unc, nm3unc, nm1uc1, nm1uc2, nm1uc3, nm1uc4, nmlunc, nmmunc, nmhunc) 
					VALUES 
					(%s, %s, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, 
					%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f);""" % 
					(schema, o_zone, d_zone, matrix['am1tim'][o_zone-start_zone][d_zone-1], matrix['am2tim'][o_zone-start_zone][d_zone-1], matrix['am3tim'][o_zone-start_zone][d_zone-1], 
					matrix['am4tim'][o_zone-start_zone][d_zone-1], matrix['am1tm1'][o_zone-start_zone][d_zone-1], matrix['am1tm2'][o_zone-start_zone][d_zone-1], 
					matrix['am1tm3'][o_zone-start_zone][d_zone-1], matrix['am1tm4'][o_zone-start_zone][d_zone-1], matrix['amltim'][o_zone-start_zone][d_zone-1], 
					matrix['ammtim'][o_zone-start_zone][d_zone-1], matrix['amhtim'][o_zone-start_zone][d_zone-1], matrix['am1tol'][o_zone-start_zone][d_zone-1], 
					matrix['am2tol'][o_zone-start_zone][d_zone-1], matrix['am3tol'][o_zone-start_zone][d_zone-1], matrix['am4tol'][o_zone-start_zone][d_zone-1], 
					matrix['am1tl1'][o_zone-start_zone][d_zone-1], matrix['am1tl2'][o_zone-start_zone][d_zone-1], matrix['am1tl3'][o_zone-start_zone][d_zone-1], 
					matrix['am1tl4'][o_zone-start_zone][d_zone-1], matrix['amltol'][o_zone-start_zone][d_zone-1], matrix['ammtol'][o_zone-start_zone][d_zone-1], 
					matrix['amhtol'][o_zone-start_zone][d_zone-1], matrix['mm1tim'][o_zone-start_zone][d_zone-1], matrix['mm2tim'][o_zone-start_zone][d_zone-1], 
					matrix['mm3tim'][o_zone-start_zone][d_zone-1], matrix['mm1tm1'][o_zone-start_zone][d_zone-1], matrix['mm1tm2'][o_zone-start_zone][d_zone-1], 
					matrix['mm1tm3'][o_zone-start_zone][d_zone-1], matrix['mm1tm4'][o_zone-start_zone][d_zone-1], matrix['mmltim'][o_zone-start_zone][d_zone-1], 
					matrix['mmmtim'][o_zone-start_zone][d_zone-1], matrix['mmhtim'][o_zone-start_zone][d_zone-1], matrix['mm1tol'][o_zone-start_zone][d_zone-1], 
					matrix['mm2tol'][o_zone-start_zone][d_zone-1], matrix['mm3tol'][o_zone-start_zone][d_zone-1], matrix['mm1tl1'][o_zone-start_zone][d_zone-1], 
					matrix['mm1tl2'][o_zone-start_zone][d_zone-1], matrix['mm1tl3'][o_zone-start_zone][d_zone-1], matrix['mm1tl4'][o_zone-start_zone][d_zone-1], 
					matrix['mmltol'][o_zone-start_zone][d_zone-1], matrix['mmmtol'][o_zone-start_zone][d_zone-1], matrix['mmhtol'][o_zone-start_zone][d_zone-1], 
					matrix['pm1tim'][o_zone-start_zone][d_zone-1], matrix['pm2tim'][o_zone-start_zone][d_zone-1], matrix['pm3tim'][o_zone-start_zone][d_zone-1], 
					matrix['pm4tim'][o_zone-start_zone][d_zone-1], matrix['pm1tm1'][o_zone-start_zone][d_zone-1], matrix['pm1tm2'][o_zone-start_zone][d_zone-1], 
					matrix['pm1tm3'][o_zone-start_zone][d_zone-1], matrix['pm1tm4'][o_zone-start_zone][d_zone-1], matrix['pmltim'][o_zone-start_zone][d_zone-1], 
					matrix['pmmtim'][o_zone-start_zone][d_zone-1], matrix['pmhtim'][o_zone-start_zone][d_zone-1], matrix['pm1tol'][o_zone-start_zone][d_zone-1], 
					matrix['pm2tol'][o_zone-start_zone][d_zone-1], matrix['pm3tol'][o_zone-start_zone][d_zone-1], matrix['pm4tol'][o_zone-start_zone][d_zone-1], 
					matrix['pm1tl1'][o_zone-start_zone][d_zone-1], matrix['pm1tl2'][o_zone-start_zone][d_zone-1], matrix['pm1tl3'][o_zone-start_zone][d_zone-1], 
					matrix['pm1tl4'][o_zone-start_zone][d_zone-1], matrix['pmltol'][o_zone-start_zone][d_zone-1], matrix['pmmtol'][o_zone-start_zone][d_zone-1], 
					matrix['pmhtol'][o_zone-start_zone][d_zone-1], matrix['em1tim'][o_zone-start_zone][d_zone-1], matrix['em2tim'][o_zone-start_zone][d_zone-1], 
					matrix['em3tim'][o_zone-start_zone][d_zone-1], matrix['em1tm1'][o_zone-start_zone][d_zone-1], matrix['em1tm2'][o_zone-start_zone][d_zone-1], 
					matrix['em1tm3'][o_zone-start_zone][d_zone-1], matrix['em1tm4'][o_zone-start_zone][d_zone-1], matrix['emltim'][o_zone-start_zone][d_zone-1], 
					matrix['emmtim'][o_zone-start_zone][d_zone-1], matrix['emhtim'][o_zone-start_zone][d_zone-1], matrix['em1tol'][o_zone-start_zone][d_zone-1], 
					matrix['em2tol'][o_zone-start_zone][d_zone-1], matrix['em3tol'][o_zone-start_zone][d_zone-1], matrix['em1tl1'][o_zone-start_zone][d_zone-1], 
					matrix['em1tl2'][o_zone-start_zone][d_zone-1], matrix['em1tl3'][o_zone-start_zone][d_zone-1], matrix['em1tl4'][o_zone-start_zone][d_zone-1], 
					matrix['emltol'][o_zone-start_zone][d_zone-1], matrix['emmtol'][o_zone-start_zone][d_zone-1], matrix['emhtol'][o_zone-start_zone][d_zone-1], 
					matrix['nm1tim'][o_zone-start_zone][d_zone-1], matrix['nm2tim'][o_zone-start_zone][d_zone-1], matrix['nm3tim'][o_zone-start_zone][d_zone-1], 
					matrix['nm1tm1'][o_zone-start_zone][d_zone-1], matrix['nm1tm2'][o_zone-start_zone][d_zone-1], matrix['nm1tm3'][o_zone-start_zone][d_zone-1], 
					matrix['nm1tm4'][o_zone-start_zone][d_zone-1], matrix['nmltim'][o_zone-start_zone][d_zone-1], matrix['nmmtim'][o_zone-start_zone][d_zone-1], 
					matrix['nmhtim'][o_zone-start_zone][d_zone-1], matrix['nm1tol'][o_zone-start_zone][d_zone-1], matrix['nm2tol'][o_zone-start_zone][d_zone-1], 
					matrix['nm3tol'][o_zone-start_zone][d_zone-1], matrix['nm1tl1'][o_zone-start_zone][d_zone-1], matrix['nm1tl2'][o_zone-start_zone][d_zone-1], 
					matrix['nm1tl3'][o_zone-start_zone][d_zone-1], matrix['nm1tl4'][o_zone-start_zone][d_zone-1], matrix['nmltol'][o_zone-start_zone][d_zone-1], 
					matrix['nmmtol'][o_zone-start_zone][d_zone-1], matrix['nmhtol'][o_zone-start_zone][d_zone-1], matrix['am1unc'][o_zone-start_zone][d_zone-1], 
					matrix['am2unc'][o_zone-start_zone][d_zone-1], matrix['am3unc'][o_zone-start_zone][d_zone-1], matrix['am4unc'][o_zone-start_zone][d_zone-1], 
					matrix['am1uc1'][o_zone-start_zone][d_zone-1], matrix['am1uc2'][o_zone-start_zone][d_zone-1], matrix['am1uc3'][o_zone-start_zone][d_zone-1], 
					matrix['am1uc4'][o_zone-start_zone][d_zone-1], matrix['amlunc'][o_zone-start_zone][d_zone-1], matrix['ammunc'][o_zone-start_zone][d_zone-1], 
					matrix['amhunc'][o_zone-start_zone][d_zone-1], matrix['mm1unc'][o_zone-start_zone][d_zone-1], matrix['mm2unc'][o_zone-start_zone][d_zone-1], 
					matrix['mm3unc'][o_zone-start_zone][d_zone-1], matrix['mm1uc1'][o_zone-start_zone][d_zone-1], matrix['mm1uc2'][o_zone-start_zone][d_zone-1], 
					matrix['mm1uc3'][o_zone-start_zone][d_zone-1], matrix['mm1uc4'][o_zone-start_zone][d_zone-1], matrix['mmlunc'][o_zone-start_zone][d_zone-1], 
					matrix['mmmunc'][o_zone-start_zone][d_zone-1], matrix['mmhunc'][o_zone-start_zone][d_zone-1], matrix['pm1unc'][o_zone-start_zone][d_zone-1], 
					matrix['pm2unc'][o_zone-start_zone][d_zone-1], matrix['pm3unc'][o_zone-start_zone][d_zone-1], matrix['pm4unc'][o_zone-start_zone][d_zone-1], 
					matrix['pm1uc1'][o_zone-start_zone][d_zone-1], matrix['pm1uc2'][o_zone-start_zone][d_zone-1], matrix['pm1uc3'][o_zone-start_zone][d_zone-1], 
					matrix['pm1uc4'][o_zone-start_zone][d_zone-1], matrix['pmlunc'][o_zone-start_zone][d_zone-1], matrix['pmmunc'][o_zone-start_zone][d_zone-1], 
					matrix['pmhunc'][o_zone-start_zone][d_zone-1], matrix['em1unc'][o_zone-start_zone][d_zone-1], matrix['em2unc'][o_zone-start_zone][d_zone-1], 
					matrix['em3unc'][o_zone-start_zone][d_zone-1], matrix['em1uc1'][o_zone-start_zone][d_zone-1], matrix['em1uc2'][o_zone-start_zone][d_zone-1], 
					matrix['em1uc3'][o_zone-start_zone][d_zone-1], matrix['em1uc4'][o_zone-start_zone][d_zone-1], matrix['emlunc'][o_zone-start_zone][d_zone-1], 
					matrix['emmunc'][o_zone-start_zone][d_zone-1], matrix['emhunc'][o_zone-start_zone][d_zone-1], matrix['nm1unc'][o_zone-start_zone][d_zone-1], 
					matrix['nm2unc'][o_zone-start_zone][d_zone-1], matrix['nm3unc'][o_zone-start_zone][d_zone-1], matrix['nm1uc1'][o_zone-start_zone][d_zone-1], 
					matrix['nm1uc2'][o_zone-start_zone][d_zone-1], matrix['nm1uc3'][o_zone-start_zone][d_zone-1], matrix['nm1uc4'][o_zone-start_zone][d_zone-1], 
					matrix['nmlunc'][o_zone-start_zone][d_zone-1], matrix['nmmunc'][o_zone-start_zone][d_zone-1], matrix['nmhunc'][o_zone-start_zone][d_zone-1]))
		print 'Added origin zones ', start_zone, ' to ', start_zone + 9,' to bank4.sql'
		connection.commit()
	return

def parking():
	# make parking charge data from destination matrix data in bank 1
	cursor.execute("DELETE FROM %s.parking;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank1/emmebank')
	global_params = read_global_params(path_to_data + '/Bank1/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank1/emmebank', offsets, global_params)
	matrix = read_destination_matrices(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names)
	for d_zone in range(0, len(matrix)):
		cursor.execute("INSERT INTO %s.parking (d_zone, parkda, parksr, parkco, nwhrpk) VALUES (%s, %f, %f, %f, 0.0);\n" % 
			(schema, d_zone + 1, matrix[d_zone]['parkda'], matrix[d_zone]['parksr'], matrix[d_zone]['parkco']))
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank2/emmebank')
	global_params = read_global_params(path_to_data + '/Bank2/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank2/emmebank', offsets, global_params)
	matrix = read_destination_matrices(path_to_data + '/Bank2/emmebank', offsets, global_params, matrix_names)
	for d_zone in range(0, len(matrix)):
		cursor.execute("UPDATE %s.parking SET nwhrpk = %f WHERE d_zone = %s;\n" % 
			(schema, matrix[d_zone]['nwhrpk'], d_zone + 1))
	connection.commit()
	print "Added parking charges for destination zones to parking.sql"
	cursor.execute("DELETE FROM %s.parking_trips;" % schema)
	offsets = read_offsets(path_to_data + '/Bank1/emmebank')
	global_params = read_global_params(path_to_data + '/Bank1/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank1/emmebank', offsets, global_params)
	matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, 'hbwdap', 1, 956)
	parking_trips = []
	for o_zone in range(0, 956):
		parking_trips.append([])
		for d_zone in range(0, 956):
			parking_trips[o_zone].append([matrix[o_zone][d_zone]])
	matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, 'hbws2p', 1, 956)
	for o_zone in range(0, 956):
		for d_zone in range(0, 956):
			parking_trips[o_zone][d_zone].append(matrix[o_zone][d_zone] / 2.0)
	matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, 'hbws3p', 1, 956)
	for o_zone in range(0, 956):
		for d_zone in range(0, 956):
			parking_trips[o_zone][d_zone][1] += matrix[o_zone][d_zone] / 3.5
	matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, 'coldap', 1, 956)
	for o_zone in range(0, 956):
		for d_zone in range(0, 956):
			parking_trips[o_zone][d_zone].append(matrix[o_zone][d_zone])
	for o_zone in range(0, 956):
		for d_zone in range(0, 956):
			cursor.execute("INSERT INTO %s.parking_trips (o_zone, d_zone, da, sr, col) VALUES (%s, %s, %f, %f, %f);\n" %
				(schema, o_zone + 1, d_zone + 1, parking_trips[o_zone][d_zone][0], parking_trips[o_zone][d_zone][1], parking_trips[o_zone][d_zone][2]))
	connection.commit()
	print "Added parking trips to parking_trips.sql"
	
def park_and_ride():
	# make park and ride trip tables from 24-hour P-A matrix in bank 1
	cursor.execute("DELETE FROM %s.pr_trips;" % schema)
	connection.commit()
	offsets = read_offsets(path_to_data + '/Bank1/emmebank')
	global_params = read_global_params(path_to_data + '/Bank1/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank1/emmebank', offsets, global_params)
	matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, 'hbwtdp', 1, 1200)
	for o_zone in range(1, 1201):
		for d_zone in range(1, 1201):
			pr_trips = matrix[o_zone - 1][d_zone - 1] * 0.741 + matrix[d_zone - 1][o_zone - 1] * 0.259
			if pr_trips > 1000:
				pr_trips = 0
			cursor.execute("INSERT INTO %s.pr_trips (o_zone, d_zone, trips) VALUES (%s, %s, %f);\n" %
				(schema, o_zone, d_zone, pr_trips))
	print 'Added park and ride trip data to park_n_ride.sql'
	connection.commit()

def hbw_trips():
	# make trip counts by income for all HBW
	cursor.execute("DELETE FROM %s.hbw_trips;\n" % schema)
	offsets = read_offsets(path_to_data + '/Bank1/emmebank')
	global_params = read_global_params(path_to_data + '/Bank1/emmebank', offsets)
	matrix_names = read_matrix_names(path_to_data + '/Bank1/emmebank', offsets, global_params)
	factors = {'am' : {'da' : [0.331560, 0.009167], 's2' : [0.336199, 0.007641], 's3' : [0.270936, 0.000000], 
		'td' : [0.529801, 0.000000], 'tw' : [0.463256, 0.000930], 'bk' : [0.383459, 0.011278], 'wk' : [0.423404, 0.010638]}, 
		'md' : {'da' : [0.084793, 0.071779], 's2' : [0.090735, 0.037249], 's3' : [0.098522, 0.078818], 
		'td' : [0.052980, 0.019868], 'tw' : [0.047442, 0.016744], 'bk' : [0.071429, 0.026316], 'wk' : [0.097872, 0.053191]}, 
		'pm' : {'da' : [0.017843, 0.260763], 's2' : [0.026743, 0.271251], 's3' : [0.044335, 0.231527], 
		'td' : [0.013245, 0.178808], 'tw' : [0.012093, 0.313488], 'bk' : [0.026316, 0.263158], 'wk' : [0.036170, 0.242553]}, 
		'ev' : {'da' : [0.008676, 0.100180], 's2' : [0.007641, 0.079274], 's3' : [0.009852, 0.118227], 
		'td' : [0.000000, 0.059603], 'tw' : [0.000000, 0.100465], 'bk' : [0.007519, 0.154135], 'wk' : [0.002128, 0.080851]}, 
		'ni' : {'da' : [0.084957, 0.030283], 's2' : [0.089780, 0.053486], 's3' : [0.108374, 0.039409], 
		'td' : [0.145695, 0.000000], 'tw' : [0.036279, 0.009302], 'bk' : [0.033835, 0.022556], 'wk' : [0.029787, 0.023404]}}
	variables = ('hbwda1', 'hbwtd1', 'hbws21', 'hbws31', 'hbwtw1', 'hbwbk1', 'hbwwk1',
		'hbwda2', 'hbwtd2', 'hbws22', 'hbws32', 'hbwtw2', 'hbwbk2', 'hbwwk2',
		'hbwda3', 'hbwtd3', 'hbws23', 'hbws33', 'hbwtw3', 'hbwbk3', 'hbwwk3',
		'hbwda4', 'hbwtd4', 'hbws24', 'hbws34', 'hbwtw4', 'hbwbk4', 'hbwwk4')
	trips = []
	for variable in range(0, 25):
		print "Getting hbw_trips data for", variables[variable]
		trips.append([])
		for start_zone in range(1, 952, 10):
			matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, variables[variable], start_zone, min(10, 957 - start_zone))
			for o_zone in range(start_zone - 1, min(start_zone + 9, 956)):
				trips[variable].append([])
				for d_zone in range(0, 956):
					trips[variable][o_zone].append(matrix[o_zone - start_zone + 1][d_zone])
	matrix = None
	for tod in ('am', 'md', 'pm', 'ev', 'ni'):
		for o_zone in range(0, 956):
			for d_zone in range(0, 956):
				query = "INSERT INTO " + schema + ".hbw_trips (tod, o_zone, d_zone, "
				for variable in range(0, 25):
					query = query + "%s" % variables[variable]
					if variable < 24:
						query = query + ", "
				query = query + ") VALUES ('%s', %s, %s, " % (tod, o_zone + 1, d_zone + 1)
				for variable in range(0, 25):
					query = query + "%f" % (trips[variable][o_zone][d_zone] * factors[tod][variables[variable][3:5]][0] + trips[variable][d_zone][o_zone] * factors[tod][variables[variable][3:5]][1])
					if variable < 24:
						query = query + ", "
				cursor.execute(query + ");")
			connection.commit()
		print 'Added first 24 variables of park and ride trip data for ', tod, ' to hbw_trips.sql'

	trips = []
	for variable in range(0, len(variables) - 24):
		print "Getting hbw_trips data for", variables[variable + 24]
		trips.append([])
		for start_zone in range(1, 952, 10):
			matrix = read_full_matrix(path_to_data + '/Bank1/emmebank', offsets, global_params, matrix_names, variables[variable + 24], start_zone, min(10, 957 - start_zone))
			for o_zone in range(start_zone - 1, min(start_zone + 9, 956)):
				trips[variable].append([])
				for d_zone in range(0, 956):
					trips[variable][o_zone].append(matrix[o_zone - start_zone + 1][d_zone])
	matrix = None
	for tod in ('am', 'md', 'pm', 'ev', 'ni'):
		for o_zone in range(0, 956):
			for d_zone in range(0, 956):
				query = "UPDATE " + schema + ".hbw_trips SET "
				for variable in range(0, len(variables) - 24):
					query = query + "%s = %f" % (variables[variable + 24], trips[variable][o_zone][d_zone] * factors[tod][variables[variable + 24][3:5]][0] + trips[variable][d_zone][o_zone] * factors[tod][variables[variable + 24][3:5]][1])
					if variable < len(variables) - 25:
						query = query + ", "
				cursor.execute(query + " WHERE tod = '%s' and o_zone = %s and d_zone = %s;" % (tod, o_zone + 1, d_zone + 1))
			connection.commit()
		print 'Added remaining variables for park and ride trip data for ', tod, ' to hbw_trips.sql'

if __name__ == '__main__':
	links_and_segments()
	bank1_full()
	bank2_full()
	bank3_full()
	bank4_full()
	parking()
	park_and_ride()
	#hbw_trips()

