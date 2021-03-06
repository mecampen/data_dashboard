import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.colors
from collections import OrderedDict
import requests


# default list of all countries of interest
country_default = OrderedDict([('Canada', 'CAN'), ('United States', 'USA'), 
    ('Brazil', 'BRA'), ('France', 'FRA'), ('India', 'IND'), ('Italy', 'ITA'), 
    ('Germany', 'DEU'), ('United Kingdom', 'GBR'), ('China', 'CHN'), ('Japan', 'JPN')])


def return_figures(countries=country_default):
    """Creates four plotly visualizations using the World Bank API

    # Example of the World Bank API endpoint:
    # arable land for the United States and Brazil from 1990 to 2015
    # http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.ARBL.HA?date=1990:2015&per_page=1000&format=json

    Args:
        country_default (dict): list of countries for filtering the data

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    # when the countries variable is empty, use the country_default dictionary
    if not bool(countries):
        countries = country_default

    # prepare filter data for World Bank API
    # the API uses ISO-3 country codes separated by ;
    country_filter = list(countries.values())
    country_filter = [x.lower() for x in country_filter]
    country_filter = ';'.join(country_filter)

    # World Bank indicators of interest for pulling data: 
    #    1) Adjusted net national income per capita (current US$)
    #    2) Life expectancy at birth, total (years)
    #    3) number of hospital beds per 1000 people
    indicators = ['NY.ADJ.NNTY.PC.CD', 'SP.DYN.LE00.IN', 'SH.MED.BEDS.ZS']

    data_frames = [] # stores the data frames with the indicator data of interest
    urls = [] # url endpoints for the World Bank API

    # pull data from World Bank API and clean the resulting json
    # results stored in data_frames variable
    for indicator in indicators:
        url = 'http://api.worldbank.org/v2/countries/' + country_filter +\
        '/indicators/' + indicator + '?date=1990:2019&per_page=1000&format=json'
        urls.append(url)

        try:
            r = requests.get(url)
            data = r.json()[1]
        except:
            print('could not load data ', indicator)

        #print(data)
        for i, value in enumerate(data):
            value['indicator'] = value['indicator']['value']
            value['country'] = value['country']['value']

        data_frames.append(data)

  
    # first chart plots Adjusted net national income per capita from 1990 to 2019
    # in top 10 economies 
    # as a line chart
    graph_one = []
    df_one = pd.DataFrame(data_frames[0])

    # filter and sort values for the visualization
    # filtering plots the countries in decreasing order by their values
    #df_one = df_one[(df_one['date'] == '2019') | (df_one['date'] == '1990')]
  
    #df_one.sort_values('value', ascending=False, inplace=True)

    # this  country list is re-used by all the charts to ensure legends have the same
    # order and color
  
    df_one["date"]
    print(df_one.dtypes)
    #df_one.sort_values('value', ascending=False, inplace=True)
    countrylist = df_one.country.unique().tolist()

    for country in countrylist:
        x_val = df_one[df_one['country'] == country].date.tolist()
        y_val =  df_one[df_one['country'] == country].value.tolist()

        graph_one.append(
            go.Scatter(
            x = x_val,
            y = y_val,
            mode = 'lines',
            name = country
            )
        )

    layout_one = dict(
        title = 'Change yearly net national income per capita <br> per Person 1990 to 2019 [current US$]',
        xaxis = dict(
            title = 'Year',
            autotick=False, 
            tick0=1990,
            dtick=5),
        yaxis = dict(title = 'yearly net income [US$]'),
    )

    # second chart plots ararble land for 2015 as a bar chart
    graph_two = []
    #df_one.sort_values('value', ascending=False, inplace=True)
    df_one = df_one[df_one['date'] == '2018'] 
  
    graph_two.append(
        go.Bar(
            x = df_one.country.tolist(),
            y = df_one.value.tolist(),
        )
    )

    layout_two = dict(
        title = 'net national income per capita in 2018',
        xaxis = dict(title = 'Country',),
        yaxis = dict(title = 'Hectares per person'),
    )

    # third chart plots percent of population that is rural from 1990 to 2015
    graph_three = []
    df_three = pd.DataFrame(data_frames[1])
    #df_three = df_three[(df_three['date'] == '2019') | (df_three['date'] == '1990')]

    #df_three.sort_values('value', ascending=False, inplace=True)
    for country in countrylist:
        x_val = df_three[df_three['country'] == country].date.tolist()
        y_val =  df_three[df_three['country'] == country].value.tolist()
        graph_three.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines',
                name = country
            )
        )

    layout_three = dict(
        title = 'change of Life expectancy from 1990 to 2019 <br> [years]',
        xaxis = dict(title = 'year',
        autotick=False, tick0=1990, dtick=25),
        yaxis = dict(title = 'Life expectancy'),
    )

    # fourth chart shows rural population vs arable land as percents
    graph_four = []
    df_four_a = pd.DataFrame(data_frames[1])
    df_four_a = df_four_a[['country', 'date', 'value']]
  
    df_four_b = pd.DataFrame(data_frames[2])
    df_four_b = df_four_b[['country', 'date', 'value']]

    df_four = df_four_a.merge(df_four_b, on=['country', 'date'])
    df_four.sort_values('date', ascending=True, inplace=True)

    plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS

    for i, country in enumerate(countrylist):

        current_color = []

        y_val = df_four[df_four['country'] == country].value_x.tolist()
        x_val = df_four[df_four['country'] == country].value_y.tolist()
        years = df_four[df_four['country'] == country].date.tolist()
        country_label = df_four[df_four['country'] == country].country.tolist()

        text = []
        for country, year in zip(country_label, years):
            text.append(str(country) + ' ' + str(year))

        graph_four.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines+markers',
                text = text,
                name = country,
                textposition = 'top center'
            )
        )

    layout_four = dict(
        title = ' Life expectancy versus <br> Hospital beds per 1000 people  <br> 1990-2019',
        yaxis = dict(title='Life expectancy [years]', range=[55, 90], dtick=10),
        xaxis = dict(title='Hospital beds per 1000 people', range=[0, 16], dtick=5),
    )


    # append all charts
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))

    return figures
