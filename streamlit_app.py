import pandas as pd
import streamlit as st
import altair as alt

st.title('Jared likes to walk!')
st.write('## Explore his adventures below\n')
st.write('')

miles = pd.read_csv('milage.csv').fillna('None')
steps = pd.read_csv('steps.csv').fillna('None')

print(miles)

metric = st.radio("Steps or miles?", ('Steps', 'Miles'))

start_date = st.date_input("Pick a start date")
end_date = st.date_input("Pick an end date")


if metric == 'Miles':

	plotter = miles[(miles.Date >= str(start_date)) & (miles.Date <= str(end_date))].copy()
else:
	plotter = steps[(steps.Date >= str(start_date)) & (steps.Date <= str(end_date))].copy()


if plotter.shape[0] == 0:
	st.write('Oh no! We found no data for the supplied date range')
else:
	#st.bar_chart(plotter.set_index('Date'), columns= ['Miles', 'Event'])
	#print(plotter.set_index('Date'))
	#st.bar_chart(data=miles)

	base = alt.Chart(plotter).mark_bar().encode(x='Date', y=metric, tooltip=['Date', metric, 'Event']).interactive().configure_axisX(labelAngle=-45) #labelAlign='center')
	st.altair_chart(base, use_container_width=True)