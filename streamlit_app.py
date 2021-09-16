import pandas as pd
import streamlit as st
import altair as alt

sideb = st.sidebar

sideb.title('Jared likes to walk!')
sideb.write('Explore his adventures below \n\n\n\n')

miles = pd.read_csv('milage.csv').fillna('None')
steps = pd.read_csv('steps.csv').fillna('None')

print(miles)

metric = sideb.radio("Steps or miles?", ('Steps', 'Miles'))

start_date = sideb.date_input("Pick a start date")
end_date = sideb.date_input("Pick an end date")

if metric == 'Miles':

	plotter = miles[(miles.Date >= str(start_date)) & (miles.Date <= str(end_date))].copy()
else:
	plotter = steps[(steps.Date >= str(start_date)) & (steps.Date <= str(end_date))].copy()


if plotter.shape[0] == 0:
	st.error('Oh no! We found no data for the supplied date range')
else:
	st.write('## {m} Walked from {s} to {e}'.format(m=metric, s=str(start_date), e=str(end_date)))
	#st.bar_chart(plotter.set_index('Date'), columns= ['Miles', 'Event'])
	#print(plotter.set_index('Date'))
	#st.bar_chart(data=miles)

	base = alt.Chart(plotter).mark_bar().encode(x='Date', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45, labelOverlap=True) #labelAlign='center')
	st.altair_chart(base, use_container_width=True)


	# Adding maxumimum

	max_value = plotter[metric].max()

	