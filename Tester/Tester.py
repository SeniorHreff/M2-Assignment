import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import urllib.request

# We define the URL for the raw edgelist file from our created GitHub repository.
github_edgelist_url = 'https://raw.githubusercontent.com/CamillaSSvendsen/M2/main/congress.edgelist'

# To get access to the data in the edgelist file from the GitHub repository, we use the urllib.request library.
edgelist_file = urllib.request.urlopen(github_edgelist_url)

# We then use the NetworkX library to read the edgelist as a directed graph (DiGraph) and define it G.
G = nx.read_edgelist(edgelist_file, create_using=nx.DiGraph(), data=True)
# The default is undirected graph.
# data=True is necessary since the edgelist file contains additional information (data) associated with the edges. The additional information is weight.

# We also load the json file containing an inList, inWeight, outList, outWeight, and usernameList.
data = pd.read_json("https://raw.githubusercontent.com/CamillaSSvendsen/M2/main/congress_network_data.json")
# From this file we are interested in the list of usernames.

df = pd.DataFrame(columns=['Source', 'Target', 'Weight'])

dfs = []

for a, b, wei in G.edges(data=True):
    source, target, weight = a, b, wei.get('weight', None)
    data = {'Source': [source], 'Target': [target], 'Weight': [weight]}
    df = pd.DataFrame(data)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

i = 0
for node in G.nodes():
    if 'usernameList' in data and i < len(data['usernameList'][0]):
        G.add_node(node, name=data['usernameList'][0][i])
        i += 1

dfs = []

for id, name in G.nodes(data=True):
    name_value = name.get('name')
    data = {'id': [int(id)], 'name': [name_value]}
    df = pd.DataFrame(data)
    dfs.append(df)

# Concatenate the list of DataFrames into a single DataFrame
names_df = pd.concat(dfs, ignore_index=True)


# Set header title
st.title('Network Graph Visualization of Drug-Drug Interactions')

# Define list of selection options and sort alphabetically
drug_list = names_df['name']
drug_list.sort()

# Implement multiselect dropdown menu for option selection (returns a list)
selected_drugs = st.multiselect('Select drug(s) to visualize', drug_list)

# Set info message on initial site load
if len(selected_drugs) == 0:
    st.text('Choose at least 1 drug to get started')

# Create network graph when user selects >= 1 item
else:
    df_select = df.loc[df['Source'].isin(selected_drugs) | \
                                df['Target'].isin(selected_drugs)]
    df_select = df_select.reset_index(drop=True)

    # Create networkx graph object from pandas dataframe
    G = nx.from_pandas_edgelist(df_select, 'drug_1_name', 'drug_2_name', 'weight')

    # Initiate PyVis network object
    drug_net = Network(height='465px', bgcolor='#222222', font_color='white')

    # Take Networkx graph and translate it to a PyVis graph format
    drug_net.from_nx(G)

    # Generate network with specific layout settings
    drug_net.repulsion(node_distance=420, central_gravity=0.33,
                       spring_length=110, spring_strength=0.10,
                       damping=0.95)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = '/tmp'
        drug_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = '/html_files'
        drug_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=435)
