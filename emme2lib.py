#!python
# encoding: utf-8
"""
emme2.py
version 0.1 2007-02-27

by Carl Batten
batten at portland dot econw dot com
http://www.econorthwest.com/

-------------------------------------------------------------------------------
Copyright (c) 2007 ECONorthwest.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
-------------------------------------------------------------------------------

This program was inspired by and borrows heavily from the emme2 package for R 
by Ben Stabler of PTV America, Inc. 
http://www.ptvamerica.com/

The emme2 package for R is available from the CRAN repository via http://www.r-project.org/
"""

import struct

def read_offsets(bank):
	"""
	reads the offsets to the individual "files" in an EMME/2 (version 9+) databank file
	    older versions of EMME/2 didn't store offsets as integers so this won't work
	the very start of the data bank contains offsets to all the files in the databank
	files are numbered from 1 to 99
	files 0, 10, 20, 30, etc. don't really exist and shouldn't be accessed from their offsets
	    for example, the first four bytes (would be offset to file 0) contains the emme/2 
	    version number, not an offset to a file
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
	Returns:
		a dictionary. Keys are file numbers as integers and values are offsets measured in 4-byte words.
		So multiply the offset by 4 to get the number of bytes to seek past.
	"""
	offsets = {}
	for i in range(0, 100):
		offsets[i] = {}
	infile = open(bank, 'rb')
	for i in ('offset', 'records', 'words_per_record', 'type'):
		chunk = infile.read(100 * 4)
		offset_values = struct.unpack('100i', chunk)
		for j in range(0, 100):
			offsets[j][i] = offset_values[j]
	infile.close()
	return offsets

def read_global_params(bank, offsets):
	"""
	reads the global parameters out of file 1 in an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
	Returns:
		a dictionary. Keys are global parameter names and values global parameter values.
		All global parameter values are returned as integers, even if they're really bit flags.
		Apply an appropriate bit mask to read a flag.
	"""
	global_params = {}
	global_names = ["ldi","ldo","lgi","lgo","ldai","ldao","lero","llio","lrep","lgraph",
	"iphys1","iphys2","iphys3","iphys4","iphys5","iphys6","iphys7","iphys8","iphys9","iphys10",
	"kmod","idev","ishort","lpsiz","ipge","idat","iusr","itpter","itppri","itpplo",
	"nexdg","nlerr","igcmd","modsid","iscen","imodl","lmodl","icgm","imfb",
	"ierop","klu","kcu","keu","iscpu","larrow","blank","blank","blank","blank",
	"idbrel","mscen","mcent","mnode","mlink","mturn","mline","mlseg","mmat","mfunc","moper"]
	for i in range(60, 80):
		global_names.append('blank')
	infile = open(bank, 'rb')
	#seek the start of file 1 in databank
	infile.seek(offsets[1]['offset'] * 4)
	chunk = infile.read(80 * 4)
	global_values = struct.unpack('80i', chunk)
	infile.close()
	for i in range(0, 80):
		if global_names[i] != 'blank':
			global_params[global_names[i]] = global_values[i]
	return global_params

def read_scenario_params(bank, offsets, global_params):
	"""
	reads the scenario parameters out of file 1 in an EMME/2 databank; also gets external scenario numbers
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
	Returns:
		a dictionary of dictionaries. Keys are external scenario numbers as strings and values are dictionaries.
		For each scenario name, the inner dictionary keys are scenario parameter names
			and the values are scenario parameter values.  Two additional keys, 'name' and
			'internal_number', provide the scenario name and internal scenario number.
		All scenario parameter values are returned as integers, even if they're really bit flags.
		Apply an appropriate bit mask to read a flag.
	"""
	scenario_params = {}
	infile = open(bank, 'rb')
	# get scenario names out of file 2
	infile.seek(offsets[2]['offset'] * 4)
	chunk = infile.read((global_params['mscen'] + 1) * 40 * 4)
	scenario_strings = struct.unpack('160s' * (global_params['mscen'] + 1), chunk)
	scenario_names = []
	# each four bytes of the name has two meaningful characters followed two meaningless
	#    characters. Leave out the meaningless characters, then trim any trailing whitespace
	for i in scenario_strings:
		scenario_name = ''
		for j in range(0, 121, 4):
			scenario_name += i[j:j+2]
		scenario_names.append(scenario_name.rstrip())
	# get external scenario numbers out of file 4
	infile.seek(offsets[4]['offset'] * 4)
	chunk = infile.read(global_params['mscen'] * 4)
	scenario_nums = struct.unpack('i' * global_params['mscen'], chunk)
	# get the scenario parameter values out of file 1
	infile.seek((offsets[1]['offset'] + 80) * 4)
	chunk = infile.read(global_params['mscen'] * 80 * 4)
	infile.close()
	scenario_values = struct.unpack('i' * (global_params['mscen'] * 80), chunk)
	scenario_pnames = ("ncent","nnode","nlink","nturn","nline","nlseg","nkturn","istats","itsimp","blank",
	"mpmat1","mgauto","mgtran","mgadd","mgadt","blank","blank","blank","blank","blank",
	"mtimau","mtimtr","mboatr","mwaitr","mauxtr","minvtr","blank","mnbotr","mw1tr","mcadt",
	"mautoc","mpmat4","mpmat2","mpmat3","mcadd","mindfa","mwpqau","mfpqau","mpmat5","mpmat6",
	"litau","lgapau","lepsau","iterau","istopc","ixlmax","iaddop","iaddlu1","iaddlu2","itsau",
	"littr","modtra","itimtr","iwtf","iwtw","iatw","ittw","lefhdw","modimp","itstr",
	"blank","npauto","nvauto","nvassc","nvdadc","nvadda","nvtrac","blank","blank","blank",
	"iadtop","iadtlu1","iadtlu2","iadtat1","iadtat2","iadtat3","iadtat4","blank","blank","blank")
	for i in range(0, global_params['mscen']):
		if scenario_nums[i]:
			scenario_params[str(scenario_nums[i])] = {'name':scenario_names[i + 1], 'internal_number':i}
			for j in range(0, 80):
				if scenario_pnames[j] != 'blank':
					scenario_params[str(scenario_nums[i])][scenario_pnames[j]] = scenario_values[i * 80 + j]
	return scenario_params

def read_link_names(bank, offsets, global_params, scenario_params, scenario):
	"""
	reads the link IDs for a particular scenario out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		scenario_params is the dictionary returned by read_scenario_params()
		scenario is an external scenario number as a string.  Example: scenario
	Returns:
		a list of link IDs as tuples (i-node, j-node).
	"""
	# get internal scenario number for scenario
	if scenario_params.has_key(str(scenario)):
		internal_scenario = scenario_params[str(scenario)]['internal_number']
	else:
		# no scenario by that name; return empty list
		return []
	# get maximum links and nodes and number of links for this scenario
	mlink = global_params['mlink']
	mnode = global_params['mnode']
	nlink = scenario_params[str(scenario)]['nlink']
	infile = open(bank, 'rb')
	# get the external node numbers for the i and j nodes of the link
	# first, get the list of external node numbers for the scenario from file 6
	infile.seek(offsets[6]['offset'] * 4 + internal_scenario * mnode * 4)
	chunk = infile.read(mnode * 4)
	ext_node_nums = struct.unpack('i' * mnode, chunk)
	# next, get the j-node for each link from file 11 and look up its external number
	infile.seek(offsets[11]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	j_nodes = struct.unpack('i' * nlink, chunk)
	# next, get the list of outgoing links for nodes from file 9
	infile.seek(offsets[9]['offset'] * 4 + internal_scenario * mnode * 4)
	chunk = infile.read(mnode * 4)
	out_links = struct.unpack('i' * mnode, chunk)
	infile.close()
	# the number of times an i-node repeats in the list of inodes for links will be
	#    the difference between the first outgoing link for that node and the first outgoing
	#    link for the next node.  So build a list of i-nodes by repeating each one that
	#    many times.
	i_nodes = []
	for i in range(1, mnode):
		for j in range(0, out_links[i] - out_links[i - 1]):
			i_nodes.append(i - 1)
	# build link ids by looking up the external node numbers of the i- and j-nodes.
	# j-nodes are off by one because emme/2 starts counting with 1 and we start with 0.
	link_ids = []
	for i in range(0, nlink):
		link_ids.append((ext_node_nums[i_nodes[i]], ext_node_nums[j_nodes[i] - 1]))
	return (link_ids)
	

def read_link_data(bank, offsets, global_params, scenario_params, scenario, link_names):
	"""
	reads the link data for a particular scenario out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		scenario_params is the dictionary returned by read_scenario_params()
		scenario is an external scenario number as a string.  Example: scenario
		link_names is the list returned by read_link_names
	Returns:
		a dictionary of dictionaries. The the keys in the outer dictionary are link IDs
			as tuples (i-node, j-node).
		For each link, the inner dictionary keys are link parameter names
			and the values are link parameter values.  
		Link parameter values are returned as floats or integers, as appropriate.
	"""
	link_data = {}
	# get internal scenario number for scenario
	if scenario_params.has_key(str(scenario)):
		internal_scenario = scenario_params[str(scenario)]['internal_number']
	else:
		# no scenario by that name; return empty list
		return link_data
	# get maximum links and scenarios and number of links for this scenario
	mlink = global_params['mlink']
	mscen = global_params['mscen']
	nlink = scenario_params[str(scenario)]['nlink']
	for i in link_names:
		link_data[i] = {}
	infile = open(bank, 'rb')
	# get link lengths from file 12
	# the link length is multiplied by 100 to make an integer
	# so divide by 100
	infile.seek(offsets[12]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('i' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['len'] = values[i]/100.0
	# get link types froim file 14
	infile.seek(offsets[14]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('i' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['ltyp'] = values[i]
	# get volume-delay function and number of lanes from file15
	# the volume-delay function id is multiplied by 100 and added to 
	#     the number of lanes times 10 to make an integer.
	# undo that to separate them
	infile.seek(offsets[15]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('i' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['vdf'] = values[i] // 100
		link_data[link_names[i]]['lan'] = (values[i] % 100) / 10.0
	# get auto volumes from file 18
	infile.seek(offsets[18]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['volau'] = values[i]
	# get auto times from file 17
	infile.seek(offsets[17]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['timau'] = values[i]
	# get auxiliary transit volumes from file 19
	infile.seek(offsets[19]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['volax'] = values[i]
	# get additional volumes from file 20
	infile.seek(offsets[20]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['volad'] = values[i]
	# get ul1, ul2, and ul3 from file 16
	infile.seek(offsets[16]['offset'] * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['ul1'] = values[i]
	infile.seek(offsets[16]['offset'] * 4 + mscen * mlink * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['ul2'] = values[i]
	infile.seek(offsets[16]['offset'] * 4 + 2 * mscen * mlink * 4 + internal_scenario * mlink * 4)
	chunk = infile.read(nlink * 4)
	values = struct.unpack('f' * nlink, chunk)
	for i in range(0, nlink):
		link_data[link_names[i]]['ul3'] = values[i]
	infile.close()
	return link_data

def read_extra_link_data(bank, offsets, global_params, scenario_params, scenario, link_names, attribute):
	"""
	reads one extra link attribute for a particular scenario out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		scenario_params is the dictionary returned by read_scenario_params()
		scenario is an external scenario number as a string.  Example: scenario
		attribute is the external extra attribute name as a string.  Example: '@abc' 
	Returns:
		a dictionary. The the keys are link IDs as tuples (i-node, j-node).
		The values are the link extra attribute values as floats.
	"""
	# get internal scenario number for scenario
	if scenario_params.has_key(str(scenario)):
		internal_scenario = scenario_params[str(scenario)]['internal_number']
	else:
		# no scenario by that name; return empty dictionary
		return {}
	# get number of links for scenario
	nlink = scenario_params[str(scenario)]['nlink']
	infile = open(bank, 'rb')
	# get extra attribute definitions
	infile.seek(offsets[57]['offset'] * 4 + internal_scenario * 5 * 100 * 4)
	chunk = infile.read(5 * 100 * 4)
	def_all = struct.unpack('500i', chunk)
	defs = []
	for i in range(0, 100):
		defs.append(def_all[i*5:(i+1)*5])
	# get extra attribute names
	infile.seek(offsets[58]['offset'] * 4 + internal_scenario * 12 * 100 * 4)
	chunk = infile.read(12 * 100 * 4)
	def_all = struct.unpack('48s' * 100, chunk)
	names = []
	for i in range(0, 100):
		names.append(def_all[i][:6].rstrip())
	# get extra attribute data
	if attribute in names:
		extra = names.index(attribute)
	else:
		# no attribute by that name
		infile.close()
		return {}
	if defs[extra][0] != 2:
		#not an attribute of links
		infile.close()
		return {}
	infile.seek(offsets[59]['offset'] * 4 + internal_scenario * offsets[59]['words_per_record'] * 4 + (defs[extra][1] - 1) * 4)
	chunk = infile.read(nlink * 4)
	extra_link_data = struct.unpack('f' * nlink, chunk)
	infile.close()
	extra_data = {}
	for i in range(0, nlink):
		extra_data[link_names[i]] = extra_link_data[i]
	return extra_data

def read_segment_data(bank, offsets, global_params, scenario_params, scenario, link_names):
	"""
	reads the transit segment data for a particular scenario out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		scenario_params is the dictionary returned by read_scenario_params()
		scenario is an external scenario number as a string.  Example: scenario
		link_names is the list returned by read_link_names
	Returns:
		a dictionary of dictionaries. The the keys in the outer dictionary are link IDs
			as tuples (i-node, j-node).
		For each segment, the inner dictionary keys are segment parameter names
			and the values are segment parameter values.  
		Segment parameter values are returned as floats or integers, as appropriate.
	"""
	segment_data = []
	# get internal scenario number for scenario
	if scenario_params.has_key(str(scenario)):
		internal_scenario = scenario_params[str(scenario)]['internal_number']
	else:
		# no scenario by that name; return empty list
		return segment_data
	# get maximum links and nodes and number of links for this scenario
	mscen = global_params['mscen']
	mlseg = global_params['mlseg']
	nlseg = scenario_params[str(scenario)]['nlseg']
	nlink = scenario_params[str(scenario)]['nlink']
	mnode = global_params['mnode']
	mline = global_params['mline']
	nline = scenario_params[str(scenario)]['nline']
	infile = open(bank, 'rb')
	# get the list of external node numbers for the scenario from file 6
	infile.seek(offsets[6]['offset'] * 4 + internal_scenario * mnode * 4)
	chunk = infile.read(mnode * 4)
	ext_node_nums = struct.unpack('i' * mnode, chunk)
	# get segment i-node and link from file 33
	infile.seek(offsets[33]['offset'] * 4 + internal_scenario * mlseg * 4)
	chunk = infile.read(nlseg * 4)
	values = struct.unpack('I' * nlseg, chunk)
	# make a list of the i-nodes in the list of link names
	link_names_i = []
	for i in link_names:
		link_names_i.append(i[0])
	# make a list of the link names for each segment
	segment_links = []
	for i in range(0, nlseg):
		# the i-node is in the least-significant 16 bits of the value
		# look up its external node number
		i_node = ext_node_nums[values[i] % 65536 - 1]
		# the rest of the value contains the offset into the sorted list of links from the first
		#    with this i-node.  Find the first, then add the offset.
		link = link_names_i.index(i_node)
		link += values[i] // 65536
		# now that we know which link, append its link name to the list
		segment_links.append(link_names[link])
	# put a dictionary for each segment into segment_links and put the link name into it
	for i in segment_links:
		segment_data.append({'link':i})
	# get line information from file 31
	infile.seek(offsets[31]['offset'] * 4 + internal_scenario * 22 * mline * 4)
	line_names = []
	for i in range(0, nline):
		chunk = infile.read(12)
		line_names.append(chunk[0:2] + chunk[4:6] + chunk[8:10])
	infile.seek(offsets[31]['offset'] * 4 + internal_scenario * 22 * mline * 4 + 4 * mline * 4)
	chunk = infile.read(nline * 4)
	first_segs = struct.unpack('i' * nline, chunk)
	infile.seek(offsets[31]['offset'] * 4 + internal_scenario * 22 * mline * 4 + 5 * mline * 4)
	chunk = infile.read(nline * 4)
	num_segs = struct.unpack('i' * nline, chunk)
	infile.seek(offsets[31]['offset'] * 4 + internal_scenario * 22 * mline * 4 + 7 * mline * 4)
	chunk = infile.read(nline * 4)
	headway = struct.unpack('i' * nline, chunk)
	infile.seek(offsets[31]['offset'] * 4 + internal_scenario * 22 * mline * 4 + 8 * mline * 4)
	chunk = infile.read(nline * 4)
	veh_type = struct.unpack('i' * nline, chunk)
	for i in range(0, nline):
		for j in range(first_segs[i] - 1, first_segs[i] + num_segs[i]):
			segment_data[j]['line'] = line_names[i]
			segment_data[j]['headway'] = headway[i] / 100.0
			segment_data[j]['veh_type'] = veh_type[i]
	# get information about vehicle types from file 30
	mveh = offsets[30]['words_per_record'] / 14
	infile.seek(offsets[30]['offset'] * 4 + internal_scenario * 14 * mveh * 4 + mveh * 2 * 4)
	chunk = infile.read(mveh * 2 * 4)
	seated_cap = struct.unpack('i' * 30, chunk[:mveh * 4])
	total_cap = struct.unpack('i' * 30, chunk[mveh * 4:])
	for i in range(0, len(segment_data)):
		segment_data[i]['seated_cap'] = seated_cap[segment_data[i]['veh_type'] - 1]
		segment_data[i]['total_cap'] = total_cap[segment_data[i]['veh_type'] - 1]
	# get segment times from file 38
	infile.seek(offsets[38]['offset'] * 4 + internal_scenario * mlseg * 4)
	chunk = infile.read(nlseg * 4)
	values = struct.unpack('f' * nlseg, chunk)
	for i in range(0, nlseg):
		segment_data[i]['timtr'] = values[i]
	# get tranit volumes from file 36
	infile.seek(offsets[36]['offset'] * 4 + internal_scenario * mlseg * 4)
	chunk = infile.read(nlseg * 4)
	values = struct.unpack('f' * nlseg, chunk)
	for i in range(0, nlseg):
		segment_data[i]['voltr'] = values[i]
	infile.close()
	# make a new list without any of the weird segments that have no volume or time
	segment_clean = []
	for i in segment_data:
		if i['timtr'] and i['voltr']:
			segment_clean.append(i)
	return segment_clean


def read_matrix_names(bank, offsets, global_params):
	"""
	reads the matrix names out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
	Returns:
		a list of five lists. 
			The first list is the names of scalar matrices in internal number order
			The second list is the names of origin matrices in internal mumber order
			The third list is the names of destination matrices in internal number order
			The fourth list is the names of full matrices in internal number order
			The fifth list is the flags for full matrices as integers in the same order
		All matrix names are returned as strings with trailing whitespace removed.
	"""
	# mmat is the maximum number of matrices of each type
	mmat = global_params['mmat']
	# get matrix names from file 4
	infile = open(bank, 'rb')
	infile.seek(offsets[60]['offset'] * 4)
	chunk = infile.read(mmat * 100 * 4)
	infile.close()
	# skip past the flags and timestamps
	skip = mmat * 4 * 2 * 4
	scalar = []
	origin = []
	destination = []
	full = []
	fflags = []
	# each four bytes of the name has two meaningful characters followed two meaningless
	#    characters. Leave out the meaningless characters, then trim any trailing whitespace
	for i in range(0, mmat):
		sname = chunk[skip + i * 12:skip + (i + 1) * 12]
		sname = sname[:2]+sname[4:6]+sname[8:10]
		scalar.append(sname.rstrip())
		oname = chunk[skip + (mmat + i) * 12:skip + (mmat + i + 1) * 12]
		oname = oname[:2]+oname[4:6]+oname[8:10]
		origin.append(oname.rstrip())
		dname = chunk[skip + (2 * mmat + i) * 12:skip + (2 * mmat + i + 1) * 12]
		dname = dname[:2]+dname[4:6]+dname[8:10]
		destination.append(dname.rstrip())
		fname = chunk[skip + (3 * mmat + i) * 12:skip + (3 * mmat + i + 1) * 12]
		fname = fname[:2]+fname[4:6]+fname[8:10]
		full.append(fname.rstrip())
		fflag = chunk[mmat * 4 * 3 + i * 4:mmat * 4 * 3 + (i + 1) * 4]
		fflags.append(struct.unpack('i', fflag)[0])
	return (tuple(scalar), tuple(origin), tuple(destination), tuple(full), tuple(fflags))

def read_scalar_matrices(bank, offsets, global_params, matrix_names):
	"""
	reads the scalar matrices out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		matrix_names is the list returned by read_matrix_names()
	Returns:
		a dictionary. The keys are scalar matrix names and the values are the scalars as floats.
	"""
	msmat = offsets[61]['words_per_record']
	infile = open(bank, 'rb')
	# read scalar matrices out of file 61
	infile.seek(offsets[61]['offset'] * 4)
	chunk = infile.read(msmat * 4)
	infile.close()
	s_all = struct.unpack('f' * msmat, chunk)
	scalars = {}
	for i in range(0, msmat):
		if matrix_names[0][i] > ' ':
			scalars[matrix_names[0][i]] = s_all[i]
	return scalars

def read_origin_matrices(bank, offsets, global_params, matrix_names):
	"""
	reads the origin matrices out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		matrix_names is the list returned by read_matrix_names()
	Returns:
	a list of dictionaries. The list is in the order of internal zones.  The keys 
		in the dictionaries are destination matrix names and the values are 
		destination matrix values as floats.
	"""
	# momat is the maximum number of origin matrices
	momat = offsets[62]['records']
	# mcent is the maximum number of zone centroids
	mcent = global_params['mcent']
	# read origin matrices from file 62
	infile = open(bank, 'rb')
	infile.seek(offsets[62]['offset'] * 4)
	chunk = infile.read(mcent * momat * 4)
	infile.close()
	o_all = struct.unpack('f' * (mcent * momat), chunk)
	origins = []
	for i in range(0, mcent):
		origins.append({})
	for i in range(0, momat):
		for j in range(0, mcent):
			origins[j][matrix_names[1][i]] = o_all[i * mcent + j]
	return origins

def read_destination_matrices(bank, offsets, global_params, matrix_names):
	"""
	reads the destination matrices out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		matrix_names is the list returned by read_matrix_names()
	Returns:
		a list of dictionaries. The list is in the order of internal zones.  The keys 
			in the dictionaries are destination matrix names and the values are 
			destination matrix values as floats.
	"""
	# mdmat is the maximum number of destination matrices
	mdmat = offsets[63]['records']
	# mcent is the maximum number of zone centroids
	mcent = global_params['mcent']
	infile = open(bank, 'rb')
	infile.seek(offsets[63]['offset'] * 4)
	chunk = infile.read(mcent * mdmat * 4)
	infile.close()
	d_all = struct.unpack('f' * (mcent * mdmat), chunk)
	destinations = []
	for i in range(0, mcent):
		destinations.append({})
	for i in range(0, mdmat):
		for j in range(0, mcent):
			destinations[j][matrix_names[2][i]] = d_all[i * mcent + j]
	return destinations

def read_full_matrix(bank, offsets, global_params, matrix_names, matrix, start_zone = 1, zones = 0):
	"""
	reads one full matrix out of an EMME/2 databank
	Parameters:
		bank is the path to an EMME/2 databank file.  Example: 'Bank1/EMME2BAN'
		offsets is the dictionary returned by read_offsets()
		global_params is the dictionary returned by read_global_params()
		matrix_names is the list returned by read_matrix_names()
		matrix is the name of the full matrix as a string
		start_zone is the first zone's worth of data to read; if missing starts at 1
		zones is the number of zones' worth of data to read; if missing reads all zones
	Returns:
		a list of lists. Each list is a row or partial row from the full matrix.  Lists are in internal order.
			If a matrix is stored columnwise, it is transposed before being returned.
	"""
	# mfmat is the maximum number of full matrices
	mfmat = offsets[64]['records']
	# mcent is the maximum number of zone centroids
	mcent = global_params['mcent']
	# get internal matrix number for matrix
	try: 
		internal_matrix = list(matrix_names[3]).index(matrix)
	except:
		# no matrix by that name
		return []
	# find out if this matrix is stored columnwise
	if matrix_names[4][internal_matrix] in (3, 7):
		columnwise = True
	else:
		columnwise = False
	if columnwise:
		start_row = 0
	else:
		start_row = start_zone - 1
	if (zones == 0) or columnwise:
		rows_to_read = mcent
	else:
		rows_to_read = min(zones, mcent  - start_row)
	full_matrix = []
	# get the full matrix from file 64
	infile = open(bank, 'rb')
	# seek past other full matrices with lower internal numbers and rows before start_row
	infile.seek(offsets[64]['offset'] * 4 + internal_matrix * mcent * mcent * 4 + start_row * mcent * 4)
	for i in range(0, rows_to_read):
		chunk = infile.read(mcent * 4)
		row = struct.unpack('f' * mcent, chunk)
		full_matrix.append(list(row))
	infile.close()
	if columnwise:
		# transpose in place
		for i in range(0, mcent - 1):
			for j in range(i + 1, mcent):
				temp = full_matrix[i][j]
				full_matrix[i][j] = full_matrix[j][i]
				full_matrix[j][i] = temp
		full_matrix = full_matrix[start_zone - 1:start_zone + rows_to_read]
	return full_matrix

def main():
	print "This is a library of functions for retrieving data from emme/2 data banks."

if __name__ == '__main__':
    main()
