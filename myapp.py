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
from bokeh.models import Slider, Select, MultiChoice, CheckboxGroup, DatetimeTickFormatter
from bokeh.models import CustomJS, Dropdown, DateSlider, RangeSlider
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
    'x'       : df.loc[(df.Location == 'DKI Jakarta') & (df.month == 3) & (df.year == '2020')].Date,
    'y'       : df.loc[(df.Location == 'DKI Jakarta') & (df.month == 3) & (df.year == '2020')].Total_Deaths,
    # 'Date': df.loc[(df.Location == 'DKI Jakarta') & (df.month == 3) & (df.year == '2020')].index.format()
})


# In[23]:


def callback(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    selectedMonth = slider.value
    selectedLocation = loc_select.value
    selectedData = data_select.value
    selectedYear = yr_select.value
    # Label axes of plot
    # plot.xaxis.axis_label = loc
    plot.yaxis.axis_label = selectedData
    # new data
    new_data = {
        'x'       : df.loc[(df.Location == selectedLocation) & (df.month == selectedMonth) & (df.year == selectedYear)].Date,
        'y'       : df[selectedData].loc[(df.Location == selectedLocation) & (df.month == selectedMonth) & (df.year == selectedYear)],
        'Data'    : df.loc[(df.Location == 'DKI Jakarta') & (df.month == 3) & (df.year == '2020')].index.format()
    # 'x'       : df.loc[(df.Location == loc) & (df.Date == date)].Date,
    # 'y'       : df.loc[(df.Location == loc) & (df.Date == date)].selectedData,
    # 'location' : df.loc[date].Location,
    }
    source.data = new_data


# In[24]:




TOOLTIPS = 'box_zoom,save,hover,reset'




plot = figure(title='Visualisasi Covid-19 per Provinsi', x_axis_label='Date', x_axis_type="datetime", y_axis_label='Total_Deaths',
           plot_height=400, plot_width=700)

plot.line(x='x', y='y', source=source)
plot.legend.location = "top_left"



plot.add_tools(HoverTool(
    tooltips=[
        ( 'date','@x{%F}'),
        ( 'Value', '@y'),
    ],

    formatters={
        '@x'      : 'datetime', # use 'datetime' formatter for 'date' field
    },

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='vline'
))




#Slider

slider = Slider(start=3, end=12, step=1, value=3, title='Bulan')

slider.on_change('value',callback)

#Dropdown
loc_select = Select(
    options= list(df.Location.unique()),
    value='DKI Jakarta',
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


data_select = Select(
    options= ["Total_Cases","Total_Deaths","Total_Recovered","Total_Active_Cases"],
    value='Total_Deaths',
    title='Data Covid-19'
)
data_select.on_change('value', callback)



layout = row(widgetbox(yr_select,slider,loc_select,data_select), plot)
curdoc().add_root(layout)
curdoc().title = 'Visualisasi Covid-19 per Provinsi'

show(layout)
