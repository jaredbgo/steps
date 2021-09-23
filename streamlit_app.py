import pandas as pd
import streamlit as st
import altair as alt
from scipy import stats
import plotly.express as px
import datetime
import numpy as np

#https://stackoverflow.com/questions/5180365/python-add-comma-into-number-string
def comma(num):
    '''Add comma to every 3rd digit. Takes int or float and
    returns string.'''
    num = pd.to_numeric(num)
    #print(type(num))
    if type(num) == int or type(num) == np.int64:
        return '{:,}'.format(num)
    elif type(num) == float or type(num) == np.float64:
        return '{:,.1f}'.format(num) # Rounds to 2 decimal places
    else:
    	print("Need int or float as input to function comma()!")

sideb = st.sidebar

sideb.title('Jared likes to walk!')
sideb.write('Explore his adventures below \n\n\n\n')

miles = pd.read_csv('milage.csv')
steps = pd.read_csv('steps.csv')
last_date = pd.read_csv('steps.csv').Date.max()
first_date = pd.read_csv('steps.csv').Date.min()

event_df = pd.read_csv('events.csv')
event_df['Date'] = pd.to_datetime(event_df.Date).astype(str)

steps = steps.merge(event_df, how='left', on='Date').fillna('None')
miles = miles.merge(event_df, how='left', on='Date').fillna('None')

metric = sideb.radio("Steps or miles?", ('Steps', 'Miles'))

start_date = sideb.date_input("Pick a start date", value = datetime.datetime(2021,7,1), min_value= pd.to_datetime(first_date),max_value=pd.to_datetime(last_date))
end_date = sideb.date_input("Pick an end date", value = pd.to_datetime(last_date), min_value= pd.to_datetime(first_date), max_value=pd.to_datetime(last_date))
title_clause = 'Selected Time Range'


uniq_events = event_df.sort_values(by='Date').Event.unique().tolist()
chosen_event = sideb.selectbox("Or pick an Event", ['None'] + uniq_events, index=0)

use_event = chosen_event != 'None'

if use_event:
	event_filt = event_df[event_df.Event == chosen_event].copy()
	start_date = event_filt.Date.min()
	end_date = event_filt.Date.max()
	title_clause = chosen_event


if metric == 'Miles':

	plotter = miles[(miles.Date >= str(start_date)) & (miles.Date <= str(end_date))].copy()

	total = miles.copy()
else:
	plotter = steps[(steps.Date >= str(start_date)) & (steps.Date <= str(end_date))].copy()
	total = steps.copy()


if plotter.shape[0] == 0:
	st.error('Oh no! We found no data')
else:
	#st.title('Daily {m} from {s} to {e}\n'.format(s=str(start_date), e=str(end_date), m=metric))
	st.title('Daily {m} for {c}\n'.format(m=metric,c=title_clause))

	val = plotter[metric].sum().astype(int) if metric == 'Steps' else plotter[metric].sum().round(1).astype(str)
	st.markdown('## _{v} in total_'.format(v=comma(val)))


	st.write('# ')
	#st.bar_chart(plotter.set_index('Date'), columns= ['Miles', 'Event'])
	#print(plotter.set_index('Date'))
	#st.bar_chart(data=miles)

	base = alt.Chart(plotter).mark_bar().encode(x='Date', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45, labelOverlap=True) #labelAlign='center')
	st.altair_chart(base, use_container_width=True)
	st.write('# ')


	# Adding maxumimum

	max_value = plotter[metric].max()
	max_value = int(max_value) if metric == 'Steps' else (round(max_value, 1))
	max_idx = plotter[metric].idxmax()
	#print(max_idx)
	max_date =  plotter.Date.loc[max_idx]
	max_event =  plotter.Event.loc[max_idx]

	avg = total[metric].mean()
	#delta = ((max_value - avg) / avg) * 100
	delta = max_value - avg

	compare_word = 'above' if delta > 0 else 'below'

	max_percentile = stats.percentileofscore(total[metric], max_value)

	plotter[metric].idxmax()

	if not use_event: 
		st.write('Daily Maximum for {c}'.format(c=title_clause))
	else:
		#st.write('Event Sum')
		# val = plotter[metric].sum().astype(int) if metric == 'Steps' else plotter[metric].sum().round(1).astype(str)

		# col,dcol = st.columns(2)
		# col.metric('Total ' + metric, "{v}".format(v=val))
		st.write('Daily Event Maximum')


	event_display = '*' + max_event  + '*' if max_event != 'None' else '*Not an event*'

	col1, col2, col3, col4 = st.columns([1, 2, 1.4, 1])

	col2.metric("Date", max_date)
	col1.markdown(event_display)
	col3.metric(metric, "{v}".format(v=comma(max_value)), "{p} {w} avg.".format(p=comma(round(delta,1)), w=compare_word))
	col4.metric("Percentile", "{}%".format(round(max_percentile, 1)))

	# Adding maximum event

	event_init = plotter[plotter.Event != 'None'].copy()

	if event_init.shape[0] == 0:

		st.write('No events in selected time range')

	else:
		#st.write('Event summary')

		# event = event_init.groupby('Event')[metric].sum().sort_values(ascending=False)

		# if metric == 'Steps':
		# 	event = event.astype(int)

		# else:
		# 	event = event.round(1).astype(str)


		# event
		event = event_init.groupby('Event', as_index=False)[metric].sum()#.sort_values(ascending=False)

		if metric == 'Steps':
			event[metric] = event[metric].astype(int)

		else:
			event[metric] = event[metric].round(1).astype(str)


		plotly_fig = px.pie(event, values=metric, names='Event', hole = .3, hover_name='Event', hover_data={'Event': False, metric: False})

		plotly_fig.update_traces(textinfo='value')
		plotly_fig.update_layout(
			title= dict(text="{} Walked By Event".format(metric), 
				font = dict(size=16)

				),
			title_x=0,
    		hoverlabel=dict(
        	font_family='arial'
    		)
		)


		if not use_event:
			st.write('# ')

			if len(event.Event.unique()) < 20:
				st.plotly_chart(plotly_fig, use_container_width=True)
			else:
				st.write("{} Walked By Event".format(metric))
				event_display = event.sort_values(by=metric, ascending=False).set_index('Event')
				event_display
				#st.plotly_chart(plotly_fig, use_container_width=True)
				#event


# Adding overall maximum

st.title('Overall')
st.write('# ')

st.write('Daily Maximum Overall')

max_o_value = total[metric].max()
max_o_value = int(max_o_value) if metric == 'Steps' else (round(max_o_value, 1))
max_o_idx = total[metric].idxmax()
#print(max_idx)
max_o_date =  total.Date.loc[max_o_idx]
max_o_event =  total.Event.loc[max_o_idx]

o_event_display = '*' + max_o_event  + '*' if max_o_event != 'None' else '*Not an event*'

o_avg = total[metric].mean()

#o_delta = ((max_o_value - o_avg) / o_avg) * 100
o_delta = max_o_value - o_avg

ocol1, ocol2, ocol3 = st.columns(3)

ocol1.markdown(o_event_display)
ocol2.metric("Date", max_o_date)
ocol3.metric(metric, "{v}".format(v=comma(max_o_value)), "{p} above avg.".format(p=comma(round(o_delta,1))))


# o_event = total[total.Event != 'None'].groupby('Event')[metric].sum().sort_values(ascending=False).head(3)


# if metric == 'Steps':
# 	o_event = o_event.astype(int)

# else:
# 	o_event = o_event.round(1).astype(str)

# st.write('Top 3 Events')

# o_event
days = total[total.Event != "None"].sort_values(by=metric, ascending=False).head(15).reset_index(drop=True).copy()
days['Rank'] = (days.index + 1).astype(str)


if metric == 'Steps':
	days[metric] = days[metric].astype(int)

else:
	days[metric] = days[metric].round(1)

#st.write('Top 3 Events')

#days
plotly_bar = px.bar(days[['Date', metric, 'Event', 'Rank']], x='Rank', y=metric,  category_orders={'Rank': days.Rank}, hover_data={'Date':True, 'Rank': False, metric: True}, color=metric, color_continuous_scale='geyser', hover_name='Event')

plotly_bar.update_layout(coloraxis_showscale=False, 
	title= dict(
		text="Daily {} Walked".format(metric),
		font = dict(size=16)),

	title_x=0,
	hoverlabel=dict(
        	font_family='arial'
    		),
	hovermode="x"
	)

st.plotly_chart(plotly_bar, use_container_width=True)
#tot_base = alt.Chart(days).mark_bar().encode(x='Rank', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45, labelOverlap=True)
#st.altair_chart(tot_base, use_container_width=True)
#base_tot = alt.Chart(days).mark_bar().encode(x='Date', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45, labelOverlap=True)
#st.altair_chart(base_tot, use_container_width=True)



