import os
import osmnx as ox
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString

os.chdir('diretório') ##incluir diretório aqui

name = "Niteroi, Rio de Janeiro, Brazil" ##nome do municipio/estado/país para download do OSM
graph = ox.graph_from_place(name, network_type = 'drive')
nodes = ox.graph_to_gdfs(graph, nodes=True,edges=False)
projecao = 32723 ##EPSG para reprojetar

graph_proj = ox.project_graph(graph, to_crs = projecao) ##reprojeção
graph_proj = ox.add_edge_speeds(graph_proj) ##incluir limites de velocidade
graph_proj = ox.add_edge_travel_times(graph_proj)
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)

pt = gpd.read_file('arq_pt.shp') ##insere shapefile com os endereços com algum campo dizendo a ordem deles - usar SRC WGS84
pt = gpd.GeoDataFrame(pt,geometry='geometry',crs=pt.crs)
pt.sort_values(by=['Id'],inplace=True) ##ordena os pontos em função do campo de ordem (aqui usei 'Id')
pt.index = range(0,len(pt))
 
rc = [] #lista que vai virar os trechos das rotas
  
for i in range(0,len(pt)):
	inicio = pt.loc[i,]['geometry'] ##extrai o novo ponto inicial
	inicio = Point(inicio.x,inicio.y)
	ini_xy = (inicio.y,inicio.x)
	ini_node = ox.get_nearest_node(graph, ini_xy, method = 'euclidean') ##extrai o nó do OSM mais próximo do ponto    
  
	fim =  pt.loc[i+1,]['geometry'] #extrai as informações do novo ponto final
	fim = Point(fim.x,fim.y)  
	fim_xy = (fim.y, fim.x)
	fim_node = ox.get_nearest_node(graph, fim_xy, method = 'euclidean')
 
	r = nx.shortest_path(G=graph, source=ini_node, target=fim_node, weight = 'length') ##caminho mais curto
  
	rc.append(r) ##adiciona novo trecho da rota
  
	if pt['Id'][i+1] == pt['Id'][len(pt)-1]: ##quebra o loop quando agitar o ponto final
		break
	else:
		pass

rota = [] #mescla de trechos (rota final)
for i in range(0,len(rc)):
    for j in range(0,len(rc[i])):
        rota.append(rc[i][j])
	
##aqui para gerar shp com a rota (linha)
route_nodes=nodes_proj.loc[rota]
route_line=LineString(list(route_nodes.geometry.values))
route_geom=gpd.GeoDataFrame([[route_line]],geometry='geometry',
         crs=edges_proj.crs,columns=['geometry'])
route_geom.loc[0, 'osmids'] = str(list(route_nodes['osmid'].values))
route_geom.to_file('rota.shp')
