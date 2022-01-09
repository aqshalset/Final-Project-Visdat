#!/usr/bin/env python
# coding: utf-8

# # Visualisasi Interaktif COVID-19 di Indonesia

# In[1]:


import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
from bokeh.models import Grid, LinearAxis, Plot, VBar
# from bokeh.palettes import Spectral6
from bokeh.layouts import widgetbox, row, gridplot
from bokeh.models import Slider, Select, MultiChoice, CheckboxGroup
from bokeh.models import CustomJS, Dropdown, DateSlider
from bokeh.io import output_file
from datetime import date
from bokeh.models.callbacks import CustomJS


# ## Load Dataset

# In[2]:


cov_data = pd.read_csv('data/covid_19_indonesia_time_series_all.csv')
cov_data.head()


# In[3]:


cov_data['Location Level']


# In[4]:


cov_data.info()


# In[5]:


cov_data.shape


# ## Preprocessing Data

# In[6]:


# Pemilihan kolom yang digunakan
df = cov_data.iloc[:,:12]
df.head()


# In[7]:


df.shape


# In[8]:


# remove data with location level = Country
idx = df[df['Location Level'] == 'Country'].index
df.drop(idx, axis=0, inplace=True)


# In[9]:


# remove unused columns
col = ['Location ISO Code', 'New Cases', 'New Deaths', 'New Recovered', 'New Active Cases', 'Location Level']
df.drop(col, axis=1, inplace=True)
df.shape


# In[10]:


# rename columns
col = {
    'Total Cases': 'Total_Cases', 
    'Total Deaths': 'Total_Deaths', 
    'Total Recovered': 'Total_Recovered', 
    'Total Active Cases': 'Total_Active_Cases'}
df.rename(col, axis=1, inplace=True)


# In[11]:


df.head()


# In[12]:


from datetime import datetime


# In[13]:


# convert strinf to datetime for column Date
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')


# In[14]:


df.info()


# In[15]:


df


# In[16]:


df['month'] = pd.DatetimeIndex(df['Date']).month
df['year'] = pd.DatetimeIndex(df['Date']).year
# df.drop('Date', inplace=True, axis=1)
df


# ## Pembuatan Visualisasi Menggunakan Bokeh

# In[17]:


# Make a list of the unique values from index (provinsi)
prov_list = list(df.Location.unique())

# Make a color mapper: color_mapper
color_mapper = CategoricalColorMapper(factors=prov_list)


# In[18]:


df.columns


# In[19]:


df.loc[df.Location == 'DKI Jakarta'].Total_Deaths


# In[20]:


df['year'] = df['year'].apply(str)
df.year.dtype


# In[21]:


df.dtypes


# In[22]:


# Make the ColumndfSource: source
source = ColumnDataSource(data={
#     'x':df.loc[df.Location == 'Jawa Barat'].Date,
#     'y':df.loc[df.Location == 'Jawa Barat'].Total_Deaths,
    'x'       : df.loc[(df.Location == 'Riau') & (df.month == 12) & (df.year == '2020')].Date,
    'y'       : df.loc[(df.Location == 'Riau') & (df.month == 12) & (df.year == '2020')].Total_Deaths,    
})


# In[23]:


def callback(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    selectedMonth = slider.value
    selectedLocation = loc_select.value
    # selectedData = data_select.labels
    selectedYear = yr_select.value
    # Label axes of plot
    # plot.xaxis.axis_label = loc
    # plot.yaxis.axis_label = selectedData
    # new data
    new_data = {
        'x'       : df.loc[(df.Location == selectedLocation) & (df.month == selectedMonth) & (df.year == selectedYear)].Date,
        'y'       : df.loc[(df.Location == selectedLocation) & (df.month == selectedMonth) & (df.year == selectedYear)].Total_Deaths,
    # 'x'       : df.loc[(df.Location == loc) & (df.Date == date)].Date,
    # 'y'       : df.loc[(df.Location == loc) & (df.Date == date)].selectedData,
    # 'location' : df.loc[date].Location,
    }
    source.data = new_data


# In[24]:




TOOLTIPS = 'box_zoom,save,hover,reset'


plot = figure(title='Covid-19 Indonesia', x_axis_label='Date', x_axis_type="datetime", y_axis_label='Total_Deaths',
           plot_height=400, plot_width=700, tools=TOOLTIPS)
# plot.xaxis.ticker = FixedTicker(ticks=[10, 20, 37.4])
plot.line(x='x', y='y', source=source)


#Slider

slider = Slider(start=3, end=12, step=1, value=3, title='Bulan')

slider.on_change('value',callback)

#Dropdown
loc_select = Select(
    options= list(df.Location.unique()),
    value='Riau',
    title='Provinsi'
)
# Attach the update_plot callback to the 'value' property of x_select
loc_select.on_change('value', callback)

yr_select = Select(
    options= ['2020','2021'],
    value='2020',
    title='Tahun'
)
yr_select.on_change('value', callback)

#Checkbox
# LABELS =["Total_Cases","Total_Deaths","Total_Recovered","Total_Active_Cases"]
# data_select = CheckboxGroup(
#     labels = LABELS,
#     active = [1],

# )
# Attach the update_plot callback to the 'value' property of y_select
# data_select.on_change('labels', callback)

layout = row(widgetbox(yr_select,slider,loc_select,data_select), plot)
curdoc().add_root(layout)

show(layout)


# In[25]:


# bokeh serve --show myapp.py


# In[ ]:


# # Create the figure: plot
# plot = figure(title='1970', x_axis_label='Fertility (children per woman)', y_axis_label='Life Expectancy (years)',
#            plot_height=400, plot_width=700, tools=[HoverTool(tooltips='@country')])

# # Add a circle glyph to the figure p
# plot.circle(x='x', y='y', source=source, fill_alpha=0.8,
#            color=dict(field='region', transform=color_mapper), legend='region')

# # Set the legend and axis attributes
# plot.legend.location = 'bottom_left'

# # Define the callback function: update_plot
# def update_plot(attr, old, new):
#     # set the `yr` name to `slider.value` and `source.data = new_data`
#     yr = slider.value
#     x = x_select.value
#     y = y_select.value
#     # Label axes of plot
#     plot.xaxis.axis_label = x
#     plot.yaxis.axis_label = y
#     # new data
#     new_data = {
#     'x'       : data.loc[yr][x],
#     'y'       : data.loc[yr][y],
#     'country' : data.loc[yr].Country,
#     'pop'     : (data.loc[yr].population / 20000000) + 2,
#     'region'  : data.loc[yr].region,
#     }
#     source.data = new_data
    
#     # Add title to figure: plot.title.text
#     plot.title.text = 'Gapminder data for %d' % yr

# # Make a slider object: slider
# slider = Slider(start=1970, end=2010, step=1, value=1970, title='Year')
# slider.on_change('value',update_plot)

# # Make dropdown menu for x and y axis
# # Create a dropdown Select widget for the x data: x_select
# x_select = Select(
#     options=['fertility', 'life', 'child_mortality', 'gdp'],
#     value='fertility',
#     title='x-axis data'
# )
# # Attach the update_plot callback to the 'value' property of x_select
# x_select.on_change('value', update_plot)

# # Create a dropdown Select widget for the y data: y_select
# y_select = Select(
#     options=['fertility', 'life', 'child_mortality', 'gdp'],
#     value='life',
#     title='y-axis data'
# )
# # Attach the update_plot callback to the 'value' property of y_select
# y_select.on_change('value', update_plot)
    
# # Create layout and add to current document
# layout = row(widgetbox(slider, x_select, y_select), plot)
# curdoc().add_root(layout)

# show(layout)

