from django import newforms as forms
from django.newforms import ModelForm, ModelChoiceField
from django.newforms.util import ValidationError
from psrc.analysis.models import *
import re
from django.utils.translation import ugettext as _
from string import join

class FloatField(forms.Field):
	"""
	A custom field that gives floating-point number input
	"""
	def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, *args, **kwargs):
		self.max_value, self.min_value, self.max_digits, self.decimal_places = max_value, min_value, max_digits, decimal_places
		super(FloatField, self).__init__(*args, **kwargs)
		self.widget.attrs['size'] = '9'

	def clean(self, value):
		"""
		Validates that float() can be called on the input. Returns the result
		of float(). Returns None for empty values.
		"""
		super(FloatField, self).clean(value)
		if value in ('', None):
			return None

		value = str(value).replace(',', '.') # "," is used as fractional part separator in some languages (Russian, etc.)
		value = value.strip() # remove useless spaces
		value = re.sub('^-\s+', '-', value)
		value = re.sub('\s*\.\s*', '.', value)

		try:
			value = float(value)
		except (ValueError, TypeError):
			raise ValidationError(_('Enter a number.'))
		if self.max_value is not None and value > self.max_value:
			raise ValidationError(_('Ensure this value is less than or equal to %s.') % self.max_value)
		if self.min_value is not None and value < self.min_value:
			raise ValidationError(_('Ensure this value is greater than or equal to %s.') % self.min_value)
		if self.decimal_places is not None:
			if self.decimal_places > 0: regex = (r'\.\d{1,%d}$' % self.decimal_places)
			else: regex = r'\.0$'
			regex = re.compile(regex)
			if not regex.search(str(value)):
				raise ValidationError(_("Ensure this value's fractional part has at most %d digits") % self.decimal_places)
		if self.max_digits is not None and self.decimal_places is not None:
			regex = r'^[-]?\d{1,%d}\.' % (self.max_digits - self.decimal_places)
			regex = re.compile(regex)
			if not regex.search(str(value)):
				raise ValidationError(_("Ensure this value's sharp part has at most %d digits") % (self.max_digits - self.decimal_places))
		elif self.max_digits is not None:
			regex = r'^[-]?\d{1,%d}$' % self.max_digits
			regex = re.compile(regex)
			value_sams_trailing_zero = re.sub('\.(0$)?', '', str(value))
			if not regex.search(value_sams_trailing_zero):
				raise ValidationError(_('Ensure this value has at most %d digits (including sharp part)') % self.max_digits)
		return value

		
class AnalysisFormMain(forms.Form):
	scenario = forms.ChoiceField(
		label="Scenario",
		help_text='Choose an available scenario to analyze.	 Base and alternative model results must be in the database for a scenario to appear on this list.	Static analysis will produce results for one year of operation.	 Dynamic analysis will produce results for multiple years.',
		required = True,
		choices = scenario_choices()
	)
	

		
	region_id = ModelChoiceField(
		Region.objects.all(),
		label="Region",
		help_text='If you want a subregional analysis, choose the subregion here.  If it isn\'t in the list, define it first.  If you choose a subregion, you will also get results for the full region. Some benefits can be estimated only for the full region.',
		required = True,
	)
	
	title = forms.CharField(
		label="Title",
		help_text='This is the name of the analysis you are conducting. It will appear on all of your reports.',
		required = True,
		max_length = 20,
		min_length = 1
	)
	
	analyst_name = forms.CharField(
		label="Analyst Name",
		help_text='Enter your name.	 It will appear on all of your reports.',
		required = True,
		max_length = 20,
		min_length = 1
	)
	
	inflation_rate = FloatField(
		label="Inflation Rate",
		help_text=Default.objects.get(field='inflation_rate').description,
		required=True
	)
	
	fraction_of_base = FloatField(
		label="Fraction of Base",
		help_text=Default.objects.get(field='fraction_of_base').description,
		required=True
	)
	
	#Dynamic Analysis
	real_discount_rate = FloatField(
		label="Real Discount Rate",
		help_text=Default.objects.get(field='real_discount_rate').description,
		required=True
	)
	growth_rate = FloatField(
		label="Growth Rate",
		help_text=Default.objects.get(field='growth_rate').description,
		required=True
	)
	
	#out_year_choices = scenario_choices()
	##out_year_choices += (('','--------'),)
	#out_year = forms.ChoiceField(
	#	label="Out Year",
	#	required=False,
	#	initial='',
	#	choices = out_year_choices
	#)
	
	end_year = forms.IntegerField(
		label="End Year",
		help_text='For dynamic analysis only. Must be after the earlier model year, but may be before or after the later model year.',
		required=False
	)
	
	def __init__(self,*args,**kwargs):
		super(AnalysisFormMain,self).__init__(*args,**kwargs)
		self.fields['scenario'] = forms.ChoiceField(choices=scenario_choices())
		
	def clean_out_year(self):
		out_year = self.cleaned_data.get('out_year', '')
		scenario = self.cleaned_data.get('scenario', '')
		if out_year != '' and scenario != '':
			#make sure out year scenario is the same as scenario and year is greater
			s_spl = scenario.split('_')
			o_spl = out_year.split('_')
			if s_spl[0] != o_spl[0]:
				raise forms.ValidationError("The scenario type for the out year must match the base scenario type.")
			if int(o_spl[-1]) <= int(s_spl[-1]):
				raise forms.ValidationError("The year for the out year must be greater than the base scenario year.")
		return out_year
	
	def clean_end_year(self):
		out_year = self.cleaned_data.get('out_year', '')
		end_year = self.cleaned_data.get('end_year', None)
		scenario = self.cleaned_data.get('scenario', '')
		if out_year != '' and scenario != '':
			if end_year == None:
				raise forms.ValidationError("An end year is required for a dynamic analysis.")
			else:
				#make sure end year is greater than base year
				s_spl = scenario.split('_')
				if end_year <= int(s_spl[-1]):
					raise forms.ValidationError("The end year must be greater than the base scenario year.")
		return end_year

class RegionForm(ModelForm):
	class Meta:
		model = Region
		
#class TimeForm(forms.Form):
#	#values of time
#	hbw_drive_income_1 = FloatField(
#		label="HBW Drive Income 1",
#		required=True
#	)
#	hbw_drive_income_2 = FloatField(
#		label="HBW Drive Income 2",
#		required=True
#	)
#	hbw_drive_income_3 = FloatField(
#		label="HBW Drive Income 3",
#		required=True
#	)
#	hbw_drive_income_4 = FloatField(
#		label="HBW Drive Income 4",
#		required=True
#	)
#	
#	sr2_income_am = FloatField(
#		label="HOV2 AM",
#		required=True
#	)
#	sr2_income_md = FloatField(
#		label="HOV2 MD",
#		required=True
#	)
#	sr2_income_pm = FloatField(
#		label="HOV2 PM",
#		required=True
#	)
#	sr2_income_ev = FloatField(
#		label="HOV2 EV",
#		required=True
#	)
#	sr2_income_nt = FloatField(
#		label="HOV2 NT",
#		required=True
#	)
#	sr3_income_am = FloatField(
#		label="HOV3 AM",
#		required=True
#	)
#	sr3_income_md = FloatField(
#		label="HOV3 MD",
#		required=True
#	)
#	sr3_income_pm = FloatField(
#		label="HOV3 PM",
#		required=True
#	)
#	sr3_income_ev = FloatField(
#		label="HOV3 EV",
#		required=True
#	)
#	sr3_income_nt = FloatField(
#		label="HOV3 NT",
#		required=True
#	)
#	vanpool_income_am = FloatField(
#		label="Vanpool AM",
#		required=True
#	)
#	vanpool_income_md = FloatField(
#		label="Vanpool MD",
#		required=True
#	)
#	vanpool_income_pm = FloatField(
#		label="Vanpool PM",
#		required=True
#	)
#	vanpool_income_ev = FloatField(
#		label="Vanpool EV",
#		required=True
#	)
#	vanpool_income_nt = FloatField(
#		label="Vanpool NT",
#		required=True
#	)
#	other_driving = FloatField(
#		label="Other Driving",
#		required=True
#	)
#	hbw_transit_ivt_income_1 = FloatField(
#		label="HBW IVT 1",
#		required=True
#	)
#	hbw_transit_ivt_income_2 = FloatField(
#		label="HBW IVT 2",
#		required=True
#	)
#	hbw_transit_ivt_income_3 = FloatField(
#		label="HBW IVT 3",
#		required=True
#	)
#	hbw_transit_ivt_income_4 = FloatField(
#		label="HBW IVT 4",
#		required=True
#	)
#	hbw_transit_walk_income_1 = FloatField(
#		label="HBW Walk 1",
#		required=True
#	)
#	hbw_transit_walk_income_2 = FloatField(
#		label="HBW Walk 2",
#		required=True
#	)
#	hbw_transit_walk_income_3 = FloatField(
#		label="HBW Walk 3",
#		required=True
#	)
#	hbw_transit_walk_income_4 = FloatField(
#		label="HBW Walk 4",
#		required=True
#	)
#	hbw_transit_wait_income_1 = FloatField(
#		label="HBW Wait 1",
#		required=True
#	)
#	hbw_transit_wait_income_2 = FloatField(
#		label="HBW Wait 2",
#		required=True
#	)
#	hbw_transit_wait_income_3 = FloatField(
#		label="HBW Wait 3",
#		required=True
#	)
#	hbw_transit_wait_income_4 = FloatField(
#		label="HBW Wait 4",
#		required=True
#	)
#	other_transit_ivt = FloatField(
#		label="Other IVT",
#		required=True
#	)
#	other_transit_walk = FloatField(
#		label="Other Walk",
#		required=True
#	)
#	other_transit_wait = FloatField(
#		label="Other Wait",
#		required=True
#	)
#	light_trucks_time = FloatField(
#		label="Light Trucks",
#		required=True
#	)
#	medium_trucks_time = FloatField(
#		label="Medium Trucks",
#		required=True
#	)
#	heavy_trucks_time = FloatField(
#		label="Heavy Trucks",
#		required=True
#	)
#	bike_time = FloatField(
#		label="Bike",
#		required=True
#	)
#	walk_time = FloatField(
#		label="Walk",
#		required=True
#	)

class TimeForm(forms.Form):
	def __init__(self, obj=None, field_list=None):
		super(TimeForm, self).__init__(obj)
		for i in obj.keys():
			if join(i.split('_')[:-1], '_') in field_list:
				self.fields[i] = FloatField(
					label = i,
					initial = obj[i],
					required = True
				)
	
class DistanceForm(forms.Form):
	auto_cost = FloatField(
		label="Auto",
		required=True
	)
	light_trucks_cost = FloatField(
		label="Light Trucks",
		required=True
	)
	medium_trucks_cost = FloatField(
		label="Medium Trucks",
		required=True
	)
	heavy_trucks_cost = FloatField(
		label="Heavy Trucks",
		required=True
	)

class AccidentCostForm(forms.Form):
	property_damage_only = FloatField(label="Property Damage Only", required=True)
	injury = FloatField(label="Injury", required=True)
	fatality = FloatField(label="Fatality", required=True)

class AccidentsForm(forms.Form):
	def __init__(self, obj=None):
		super(AccidentsForm, self).__init__(obj) 
		for vc in vc_range_choices:
			for fc in functional_class_choices:
				initial_pdo = obj['property_damage_only_%s_%s' %(vc[0],fc[0])]
				initial_i = obj['injury_%s_%s' %(vc[0],fc[0])]
				initial_f = obj['fatality_%s_%s' %(vc[0],fc[0])]
					
				self.fields['property_damage_only_%s_%s' %(vc[0],fc[0])] = FloatField(
					label="property_damage_only_%s_%s" %(vc[0],fc[0]),
					initial= initial_pdo,
					required=True
				)
				
				self.fields['injury_%s_%s' %(vc[0],fc[0])] = FloatField(
					label="injury_%s_%s" %(vc[0],fc[0]),
					initial= initial_i,
					required=True
				)
				
				self.fields['fatality_%s_%s' %(vc[0],fc[0])] = FloatField(
					label="fatality_%s_%s" %(vc[0],fc[0]),
					initial=initial_f,
					required=True
				)
				
				#self.data['property_damage_only_%s_%s' %(vc[0],fc[0])] = initial_pdo
				#self.data['injury_%s_%s' %(vc[0],fc[0])] = initial_i
				#self.data['fatality_%s_%s' %(vc[0],fc[0])] = initial_f
				
				#self.fields['property_damage_only_%s_%s' %(vc[0],fc[0])].bf = forms.forms.BoundField(self, self.fields['property_damage_only_%s_%s' %(vc[0],fc[0])], 'property_damage_only_%s_%s' %(vc[0],fc[0]))
				#self.fields['property_damage_only_%s_%s' %(vc[0],fc[0])].bf._data = initial_pdo
				#
				#self.fields['injury_%s_%s' %(vc[0],fc[0])].bf = forms.forms.BoundField(self, self.fields['injury_%s_%s' %(vc[0],fc[0])], 'injury_%s_%s' %(vc[0],fc[0]))
				#self.fields['injury_%s_%s' %(vc[0],fc[0])].bf._data = initial_i
				#
				#self.fields['fatality_%s_%s' %(vc[0],fc[0])].bf = forms.forms.BoundField(self, self.fields['fatality_%s_%s' %(vc[0],fc[0])], 'fatality_%s_%s' %(vc[0],fc[0]))
				#self.fields['fatality_%s_%s' %(vc[0],fc[0])].bf._data = initial_f
	
class EmissionsCostForm(forms.Form):
	def __init__(self, obj=None):
		super(EmissionsCostForm, self).__init__(obj)
		for p in Pollutant.objects.all():
			self.fields['pollutant_%s' %(p.id)] = FloatField(
				label = 'pollutant_%s' %(p.id),
				initial = obj['pollutant_%s' %(p.id)],
				required = True
			)
			
class EmissionsForm(forms.Form):
	def __init__(self, obj=None):
		super(EmissionsForm, self).__init__(obj)
		for p in Pollutant.objects.all():
			for sc in speed_class_choices:
				initial_car = obj['car_%s_%s' %(p.id,sc[0])]
				initial_lt =  obj['light_truck_%s_%s' %(p.id,sc[0])]
				initial_mt =  obj['medium_truck_%s_%s' %(p.id,sc[0])]
				initial_ht =  obj['heavy_truck_%s_%s' %(p.id,sc[0])]
			
				self.fields['car_%s_%s' %(p.id,sc[0])] = FloatField(
					label="car_%s_%s" %(p.id,sc[0]),
					initial = initial_car,
					required=True
				)
				self.fields['light_truck_%s_%s' %(p.id,sc[0])] = FloatField(
					label="light_truck_%s_%s" %(p.id,sc[0]),
					initial = initial_lt,
					required=True
				)
				self.fields['medium_truck_%s_%s' %(p.id,sc[0])] = FloatField(
					label="medium_truck_%s_%s" %(p.id,sc[0]),
					required=True
				)
				self.fields['heavy_truck_%s_%s' %(p.id,sc[0])] = FloatField(
					label="heavy_truck_%s_%s" %(p.id,sc[0]),
					required=True
				)

class UnreliabilityForm(forms.Form):
	#unreliability
	i_ratio = FloatField(
		label="i Ratio",
		required=True
	)
	personal_discount_rate = FloatField(
		label="Personal Discount Rate",
		required=True
	)
	prob_not_meet_guar = FloatField(
		label="Probability Not Meet Guarantee",
		required=True
	)
	alpha = FloatField(
		label="alpha",
		required=True
	)
	beta_1 = FloatField(
		label="beta 1",
		required=True
	)
	beta_2 = FloatField(
		label="beta 2",
		required=True
	)