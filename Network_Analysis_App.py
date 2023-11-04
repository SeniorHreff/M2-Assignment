# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from streamlit_folium import st_folium
import networkx as nx
import json
import urllib.request # This package is used to get access to the edgelist file in the GitHub repository

# Import the libraries and link to the bokeh backend
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')
from bokeh.plotting import show

# Setting the default figure size a bit larger
defaults = dict(width=750, height=750, padding=0.1,
                xaxis=None, yaxis=None)
hv.opts.defaults(
    opts.EdgePaths(**defaults), opts.Graph(**defaults), opts.Nodes(**defaults))

st.set_option('deprecation.showPyplotGlobalUse', False)


# We define the URL for the raw edgelist file from our created GitHub repository.
github_edgelist_url = 'https://raw.githubusercontent.com/CamillaSSvendsen/M2/main/congress.edgelist'

# To get access to the data in the edgelist file from the GitHub repository, we use the urllib.request library.
edgelist_file = urllib.request.urlopen(github_edgelist_url)

# We then use the NetworkX library to read the edgelist as a directed graph (DiGraph) and define it G.
G = nx.read_edgelist(edgelist_file, create_using=nx.DiGraph(), data=True)

data = pd.read_json("https://raw.githubusercontent.com/CamillaSSvendsen/M2/main/congress_network_data.json")

# We create a new empty Pandas DataFrame that only consist of column names.
df = pd.DataFrame(columns=['Source', 'Target', 'Weight'])

# Create an empty list to hold DataFrames
dfs = []

for a, b, wei in G.edges(data=True):
    source, target, weight = a, b, wei.get('weight', None)
    data = {'Source': [source], 'Target': [target], 'Weight': [weight]}
    df = pd.DataFrame(data)
    dfs.append(df)

# Concatenate the list of DataFrames into a single DataFrame
result_df = pd.concat(dfs, ignore_index=True)

df = result_df

# We want to have a way to connect the usernames from the list in the json file to the nodes in the edgelist/dataframe.
# We apply an index to the usernameList in the json file "data", and combine the node number in the graph to a username from the json file "data".
i = 0
for node in G.nodes():
    if 'usernameList' in data and i < len(data['usernameList'][0]):
        G.add_node(node, name=data['usernameList'][0][i])
        i += 1

names_df = pd.DataFrame(columns=['id', 'name'])

# Create an empty list to hold DataFrames
dfs = []

for id, name in G.nodes(data=True):
    name_value = name.get('name')
    data = {'id': [int(id)], 'name': [name_value]}
    df = pd.DataFrame(data)
    dfs.append(df)

# Concatenate the list of DataFrames into a single DataFrame
result_df = pd.concat(dfs, ignore_index=True)

names_df = result_df

# We set up a networkx layout, to make sure, we get the same layout, evertime we load a visualization of a network.
G_layout = nx.layout.kamada_kawai_layout(G)

visualization_option = st.selectbox(
    "Select Visualization", 
    ["In-Degree Centrality",
     "Out-Degree Centrality",
     "Eigenvector Centrality",
     "Betweenness Centrality",
     "Community Detection"
    ]
)

if visualization_option == "In-Degree Centrality":
    in_degree_centrality = nx.in_degree_centrality(G)
    in_sorted_nodes = sorted(in_degree_centrality, key=in_degree_centrality.get, reverse=True)
    in_top_nodes = in_sorted_nodes[:75]
    in_top_nodes_subgraph = G.subgraph(in_top_nodes)
    cent_degree_in = dict(G.in_degree)
    for key in cent_degree_in:
     cent_degree_in[key] = cent_degree_in[key]/4
    nx.set_node_attributes(in_top_nodes_subgraph, cent_degree_in, 'in_cent_degree')
    g_plot = hv.Graph.from_networkx(in_top_nodes_subgraph, G_layout).opts(tools=['hover'],
                                                                        directed=True,
                                                                        edge_alpha=0.25,
                                                                        node_size='in_cent_degree',
                                                                        legend_position='right'
                                                                        )
    show(hv.render(g_plot))
