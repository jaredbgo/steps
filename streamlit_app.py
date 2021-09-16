import pandas as pd
import streamlit as st
import altair as alt
from scipy import stats

sideb = st.sidebar

sideb.title('Jared likes to walk!')
sideb.write('Explore his adventures below \n\n\n\n')

miles = pd.read_csv('milage.csv').fillna('None')
steps = pd.read_csv('steps.csv').fillna('None')

event_df = pd.read_csv('events.csv')
event_df['Date'] = pd.to_datetime(event_df.Date).astype(str)

steps = steps.merge(event_df, how='left', on='Date')
miles = miles.merge(event_df, how='left', on='Date')

print(miles)

metric = sideb.radio("Steps or miles?", ('Steps', 'Miles'))

start_date = sideb.date_input("Pick a start date")
end_date = sideb.date_input("Pick an end date")

if metric == 'Miles':

	plotter = miles[(miles.Date >= str(start_date)) & (miles.Date <= str(end_date))].copy()

	total = miles.copy()
else:
	plotter = steps[(steps.Date >= str(start_date)) & (steps.Date <= str(end_date))].copy()
	total = steps.copy()


if plotter.shape[0] == 0:
	st.error('Oh no! We found no data for the supplied date range')
else:
	st.title('Walking from {s} to {e}\n'.format(s=str(start_date), e=str(end_date)))
	#st.bar_chart(plotter.set_index('Date'), columns= ['Miles', 'Event'])
	#print(plotter.set_index('Date'))
	#st.bar_chart(data=miles)

	base = alt.Chart(plotter).mark_bar().encode(x='Date', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45, labelOverlap=True) #labelAlign='center')
	st.altair_chart(base, use_container_width=True)


	# Adding maxumimum

	max_value = plotter[metric].max()
	max_value = int(max_value) if metric == 'Steps' else (round(max_value, 1))
	max_idx = plotter[metric].idxmax()
	#print(max_idx)
	max_date =  plotter.Date.loc[max_idx]

	avg = total[metric].mean()
	delta = ((max_value - avg) / avg) * 100

	compare_word = 'above' if delta > 0 else 'below'

	max_percentile = stats.percentileofscore(total[metric], max_value)

	plotter[metric].idxmax()

	st.write('Maximum of Time Range')

	col1, col2, col3 = st.columns(3)

	col1.metric("Date", max_date)
	col2.metric(metric, "{v}".format(v=max_value), "{p}% {w} average".format(p=round(delta,1), w=compare_word))
	col3.metric("Percentile", "{}%".format(round(max_percentile, 1)))

	# Adding maximum event

	event_init = plotter[plotter.Event != 'None'].copy()

	if event_init.shape[0] == 0:

		st.write('No events in selected time range')

	else:
		st.write('Event summary')

		event = event_init.groupby('Event')[metric].sum().sort_values(ascending=False)

		if metric == 'Steps':
			event = event.astype(int)

		else:
			event = event.round(1).astype(str)


		event

# Adding overall maximum

st.title('Overall')

st.write('Maximum of All Time')

max_o_value = total[metric].max()
max_o_value = int(max_o_value) if metric == 'Steps' else (round(max_o_value, 1))
max_o_idx = total[metric].idxmax()
#print(max_idx)
max_o_date =  total.Date.loc[max_o_idx]

o_avg = total[metric].mean()

o_delta = ((max_o_value - o_avg) / o_avg) * 100

ocol1, ocol2 = st.columns(2)

ocol1.metric("Date", max_o_date)
ocol2.metric(metric, "{v}".format(v=max_o_value), "{p}% above average".format(p=round(o_delta,1)))


o_event = total[total.Event != 'None'].groupby('Event')[metric].sum().sort_values(ascending=False)


if metric == 'Steps':
	o_event = o_event.astype(int)

else:
	o_event = o_event.round(1).astype(str)

st.write('Event summary')

o_event



