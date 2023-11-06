# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 15:41:17 2019

@author: a0f00zq
"""
import plotly
from plotly.offline import init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import shapely.geometry
from shapely.geometry import Polygon
from shapely.geometry import Point
import numpy as np
import geog
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic 
import shapely.wkt
import pandas as pd
import plotly.io as pio
import plotly.express as px
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
from pyproj import Transformer
import json
from shapely.geometry import Point, mapping


class Plot(): 
    
    def __init__(self):
        """
        Token de acceso al mapa

        Returns
        -------
        None.

        """
        self.mapbox_access_token = 'pk.eyJ1IjoiYWRvbGZvZnVlbnRlc2oiLCJhIjoiY2pmZzNiYXA2MjRiOTJ6bWk3ejd3dm1vNiJ9.zPn_FLwNN0aysTC4VC9BiQ'
    
    
    def generate_geojson_polygon(self, Lista_df,censo_df):
        # Se crea un diccionario para crear un geojson
        geojd = {"type": "FeatureCollection"}
        geojd['features'] = []  

        # Se crea una una estructura con varios objetos geométricos. Cada objeto es particularmente un poligono
        for i in range(len(Lista_df)):
            Polygon = Lista_df[i]
            # Se guarda las coordenadas como una tupla longitud, latitud.
            lons = list(Polygon['Longitud'])
            lats=list(Polygon['Latitud'])
            coords = []
            for lon, lat in zip(lons, lats): 
                coords.append([lon, lat])   
            coords.append([lons[0], lats[0]])  #cierra el poligono 

            # Se incorpora las coordenadas, y el indexador a la estructura
            geojd['features'].append({ "type": "Feature",
                                       "geometry": {"type": "Polygon",
                                                    "coordinates": [coords] },
                                       'properties': {'Index': i},
                                        'id': i,
                                        })
        return geojd 
    
   
    def plot_polygon_mapbox(self, censo, geojd, center, id_color,opacity = 0.4, filename = False, scalecolor = False):
        if scalecolor== False:
            scalecolor = "Viridis"



        fig = px.choropleth_mapbox(censo, geojson=geojd, 
                                   locations = 'Index',
                                   featureidkey="properties.Index",
                                   color = id_color,
                                   color_continuous_scale = scalecolor,
                                   opacity = opacity,
                                   center = {"lat": center[1], "lon": center[0]},
                                   mapbox_style = "carto-positron", zoom = 6)
        fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0})
        if filename != False:
            plotly.offline.plot(fig, filename = filename)
        iplot(fig)
        
    def plot_density_mapbox(self,censo, center, count, opacity = 0.4, filename = False, scalecolor = False):
        if scalecolor== False:
            scalecolor = "Viridis"


        fig = px.density_mapbox(censo, lat = 'Latitud', lon = 'Longitud',z=count,
                                   radius = 30,
                                   color_continuous_scale = scalecolor,
                                   opacity = opacity,
                                   center = {"lat": center[1], "lon": center[0]},
                                   mapbox_style = "carto-positron", zoom = 6)
        fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0})
        if filename != False:
            plotly.offline.plot(fig, filename = filename)
        iplot(fig)
    
    
    
    def get_polygon(self, lons, lats, color='blue'):
        """
        Funcion que define la estructura de un poligono

        Parameters
        ----------
        lons : Dataframe
            Contiene las longitudes de los puntos del poligono
        lats : TYPE
            Contiene las latitudes de los puntos del poligono
        color : TYPE, optional
            The default is 'blue'.


        Returns
        -------
        layer : Diccionario
            Diccionario con claves de una capa.

        """
               
        if len(lons) != len(lats):
            raise ValueError('the legth of longitude list  must coincide with that of latitude')
        geojd = {"type": "FeatureCollection"}
        geojd['features'] = []
        coords = []
        for lon, lat in zip(lons, lats): 
            coords.append((lon, lat))   
        coords.append((lons[0], lats[0]))  #close the polygon  
        geojd['features'].append({ "type": "Feature",
                                   "geometry": {"type": "Polygon",
                                                "coordinates": [coords] }})
        layer=dict(sourcetype = 'geojson',
                 source =geojd,
                 below='',
                 type = 'fill',   
                 color = color,
                 opacity = 0.2                           
                 )
            
            
        return layer
    
   
    def get_lines(self, lons, lats, color='blue'):
        """
        Funcion que genera conexiones de varios puntos con lineas

        Parameters
        ----------
        lons : Dataframe
            Contiene las longitudes de los puntos a conectar
        lats : TYPE
            Contiene las latitudes de los puntos a conectar
            The default is 'blue'.


        Returns
        -------
        layer : Diccionario
            Diccionario con claves de una capa.

        """
        if len(lons) != len(lats):
            raise ValueError('the legth of longitude list  must coincide with that of latitude')
        geojd = {"type": "FeatureCollection"}
        geojd['features'] = []
        coords = []
        for lon, lat in zip(lons, lats): 
            coords.append((lon, lat))   
        coords.append((lons[0], lats[0]))  #close the polygon  
        geojd['features'].append({ "type": "Feature",
                                   "geometry": {"type": "LineString",
                                               "coordinates": coords }})
        layer=dict(sourcetype = 'geojson',
                source =geojd,
                 below='',
                 line = {'width':6},
                 type = 'line',   
                 color = color,
                  )
            
        return layer
  
    
    def Latlon(self, file_name = False, scalecolor = False, df = None, centro_map_lat = -999, centro_map_lon = -999, coordenadas_poligono = None):
        """
        Función que plotea puntos en un mapa geográfico según la longitud y latitud

        Parameters
        ----------
        df : DataFrame
            Contiene la información de latitud, longitud y etiqueta de los puntos que se quiere graficar.
            En caso de que se quiera utilizar una escala de color, el dataframe debe contener
            una columna que indique el color.
        centro_map_lat : float
            Latitud del centro del mapa. 
        centro_map_lon : float
            Longitud del centro del mapa.
        scale_color : Boolean, optional  
            Si se quiere graficar según una escala de color, se debe definir scale_color = True
            Caso contrario se debe definir como False. The default is False.
            El código está adaptado para graficar 5 clases con diferentes colores. En el dataframe, la asignación de
            color debe ser númerica (por ejemplo del 1 a 5), siendo el menor el primer color en la escala y
            mayor el último.
            La escala de color predefinida contiene los siguientes colores: burdeo, verde claro, verde oscuro, amarillo,
            naranjo y rojo. Por defecto color_scale es False, asi que el color predefinido es azul.
        coordenadas_poligono : DataFrame
            Dataframe que contiene las columnas Latitud y Longitud. Estas coordenadas corresponden al poligono que se que quiere 
            trazar. Por defecto coordenadas_poligono es None.
        file_name : str
            Nombre con el que se quiere guardar la figura en un archivo html. Por defecto el valor es False.
        Returns
        -------
        Retorna un gráfico de un mapa geográfico con puntos

        """
        init_notebook_mode(connected=True)   
        #pio.renderers.default = "svg"
        
        if df is None and coordenadas_poligono is not None:
            df = coordenadas_poligono
        elif df is None and coordenadas_poligono is None:
            print('Falta ingresar coordenadas')
   
        
        if scalecolor != False:
            data = go.Scattermapbox(
                        # Se define las columnas de latitud y longitud
                        lat = df['Latitud'],
                        lon = df['Longitud'],
                        # Determina el modo de dibujo de la información de los coordenadas.
                        #Si mode = "text", entonces el texto de los elementos aparecen en las coordenadas.
                        #De lo contrario, los textos aparecen al pasar el mouse.
                        mode ='markers',
                        # La información que aparecerá por punto, será en función a una columna con etiquetas.
                        text = df['Label'],
                        # Se define que la información que se desplagará será solo de la etiqueta
                        hoverinfo ='text',
                        # Configuración del texto
                        textfont = dict(size=16, color='black'),  
                        # Configuración de los puntos. Se define el tamaño y la escala de color.
                        marker = dict(
                            autocolorscale = False,
                            color = df['Color'],
                            showscale=True,
                            size = df['tamano'],                           
                            colorscale =  scalecolor
                        ),                        
                    )
            
            
        else:
            data = go.Scattermapbox(
                        lat = df['Latitud'],
                        lon = df['Longitud'],
                        mode ='markers',
                        text = df['Label'],
                        hoverinfo ='text',
                        textfont = dict(size=16, color='black'),                     
                        marker = dict(
                            size = df['tamano'],                           
                            color = 'blue'
                        ),                       
                    )
            
        # Si el usuario no ingresa las coordenadas del centro del mapa, se define como centro los promedios
        # de las latitudes y longitudes del dataframe.
        if centro_map_lat == -999 or centro_map_lon == -999:
            centro_map_lat = df['Latitud'].quantile(0.5)
            centro_map_lon = df['Longitud'].quantile(0.5)
           
                
            
                
        layout = go.Layout(
            # Determina si un ancho o alto de diseño que el usuario ha dejado sin definir se inicializa 
            # en cada retransmisión
            autosize = True,
            #width=950,  # Comentar para que el html sea del tamaño pantalla completo
            #height=530, # Comentar para que el html sea del tamaño pantalla completo
            hovermode ='closest',
            mapbox = dict(
                # Establece el token de acceso de mapbox que se utilizará para este mapa de mapbox. 
                accesstoken = self.mapbox_access_token,
                bearing = 0,
                center = dict(
                    # Establece la latitud del centro del mapa 
                    lat = centro_map_lat,
                    # Establece la longitud del centro del mapa 
                    lon = centro_map_lon
                ),
                #Establece el ángulo de inclinación del mapa
                pitch = 0,
                # Establece el nivel de zoom del mapa 
                zoom = 6),
            margin=go.layout.Margin(
                l=0,
                r=0,
                b=0,
                t=0)
       
        )
        
        # Si es que no se ingresan coordenadas geográficas de un poligono
        if coordenadas_poligono is None:
        
            # Se grafica el mapa geográfico con los puntos
            fig = dict(data=[data], layout=layout)
            iplot(fig)
            if file_name != False:
                plotly.offline.plot(fig, filename=file_name)
           
           
            
        
        else:
            fig = go.Figure(data = data, layout = layout)
            mylayers =[]
            mylayers.append(self.get_polygon(lons = list(coordenadas_poligono['Longitud']), lats=list(coordenadas_poligono['Latitud'])))
            fig.layout.update(mapbox_layers =mylayers);
            
            if file_name != False:
                plotly.offline.plot(fig,filename=file_name)
                
            iplot(fig)
   

    def Latlon_in_out(self, file_name = False, scalecolor = False, df = None, centro_map_lat = -999, centro_map_lon = -999,coordenadas_poligono = None):
        """
        Función que plotea puntos en un mapa geográfico según la longitud y latitud

        Parameters
        ----------
        df : DataFrame
            Contiene la información de latitud, longitud y etiqueta de los puntos que se quiere graficar.
            En caso de que se quiera utilizar una escala de color, el dataframe debe contener
            una columna que indique el color.
        centro_map_lat : float
            Latitud del centro del mapa. 
        centro_map_lon : float
            Longitud del centro del mapa.
        scale_color : Boolean, optional  
            Si se quiere graficar según una escala de color, se debe definir scale_color = True
            Caso contrario se debe definir como False. The default is False.
            El código está adaptado para graficar 5 clases con diferentes colores. En el dataframe, la asignación de
            color debe ser númerica (por ejemplo del 1 a 5), siendo el menor el primer color en la escala y
            mayor el último.
            La escala de color predefinida contiene los siguientes colores: burdeo, verde claro, verde oscuro, amarillo,
            naranjo y rojo. Por defecto color_scale es False, asi que el color predefinido es azul.
        coordenadas_poligono :Lista de DataFrame
            Lista de Dataframes, en la cual cada uno de ellos debe contener columnas Latitud y Longitud. Estas coordenadas corresponden al             poligono que se que quiere 
            trazar. Por defecto coordenadas_poligono es None.
        file_name : str
            Nombre con el que se quiere guardar la figura en un archivo html. Por defecto el valor es False.

        Returns
        -------
        Retorna un gráfico de un mapa geográfico con puntos

        """
        init_notebook_mode(connected=True) 
        
        if df is None and coordenadas_poligono is not None:
               print('Ocupar función Latlon')
               

        coords = pd.concat([df,coordenadas_poligono])
        
        if scalecolor != False:
            data = go.Scattermapbox(
                        # Se define las columnas de latitud y longitud
                        lat = coords['Latitud'],
                        lon = coords['Longitud'],
                        # Determina el modo de dibujo de la información de los coordenadas.
                        #Si mode = "text", entonces el texto de los elementos aparecen en las coordenadas.
                        #De lo contrario, los textos aparecen al pasar el mouse.
                        mode ='markers',
                        # Se define que el color de los puntos será en función de una columna con números.
                        # Aquel punto que sea menor, será asignado con el primer color de la escala
                        # Configuración de los puntos. Se define el tamaño y la escala de color.
                        marker = dict(
                            autocolorscale = False,
                            color = coords['Color'],
                            showscale=True,
                            size = 6,                           
                            colorscale =  scalecolor                        ),                        
                    )
        else:
           
            data = go.Scattermapbox(
                        lat = coords['Latitud'],
                        lon = coords['Longitud'],
                        mode ='markers',                 
                        marker = dict(
                            size = 6,                           
                            color = 'blue'
                        ),                       
                    )
            
        # Si el usuario no ingresa las coordenadas del centro del mapa, se define como centro los promedios
        # de las latitudes y longitudes del dataframe.
        if centro_map_lat == -999 or centro_map_lon == -999:
            centro_map_lat = df['Latitud'].quantile(0.5)
            centro_map_lon = df['Longitud'].quantile(0.5)
           
                
            
                
        layout = go.Layout(
            # Determina si un ancho o alto de diseño que el usuario ha dejado sin definir se inicializa 
            # en cada retransmisión
            autosize=True,
            width=950,  # Comentar para que el html sea del tamaño pantalla completo
            height=530, # Comentar para que el html sea del tamaño pantalla completo
            hovermode ='closest',
            mapbox = dict(
                # Establece el token de acceso de mapbox que se utilizará para este mapa de mapbox. 
                accesstoken = self.mapbox_access_token,
                bearing = 0,
                center = dict(
                    # Establece la latitud del centro del mapa 
                    lat = centro_map_lat,
                    # Establece la longitud del centro del mapa 
                    lon = centro_map_lon
                ),
                #Establece el ángulo de inclinación del mapa
                pitch = 0,
                # Establece el nivel de zoom del mapa 
                zoom = 11),
            margin=go.layout.Margin(
                l=0,
                r=0,
                b=0,
                t=0)
       
        )
        

        fig = go.Figure(data = data, layout = layout)
        mylayers =[]
        mylayers.append(self.get_lines(lons = list(df['Longitud']), lats=list(df['Latitud'])))
        fig.layout.update(mapbox_layers =mylayers);

        if file_name != False:
            plotly.offline.plot(fig,filename=file_name)
        iplot(fig)
                 

        
      
           
           
    def Latlon_n_poligonos(self, file_name = False, scalecolor = False, df = None, centro_map_lat = -999, centro_map_lon = -999,coordenadas_poligono = None):
        """
        Función que plotea puntos en un mapa geográfico según la longitud y latitud

        Parameters
        ----------
        df : DataFrame
            Contiene la información de latitud, longitud y etiqueta de los puntos que se quiere graficar.
            En caso de que se quiera utilizar una escala de color, el dataframe debe contener
            una columna que indique el color.
        centro_map_lat : float
            Latitud del centro del mapa. 
        centro_map_lon : float
            Longitud del centro del mapa.
        scale_color : Boolean, optional  
            Si se quiere graficar según una escala de color, se debe definir scale_color = True
            Caso contrario se debe definir como False. The default is False.
            El código está adaptado para graficar 5 clases con diferentes colores. En el dataframe, la asignación de
            color debe ser númerica (por ejemplo del 1 a 5), siendo el menor el primer color en la escala y
            mayor el último.
            La escala de color predefinida contiene los siguientes colores: burdeo, verde claro, verde oscuro, amarillo,
            naranjo y rojo. Por defecto color_scale es False, asi que el color predefinido es azul.
        coordenadas_poligono :Lista de DataFrame
            Lista de Dataframes, en la cual cada uno de ellos debe contener columnas Latitud y Longitud. Estas coordenadas corresponden al             poligono que se que quiere 
            trazar. Por defecto coordenadas_poligono es None.
        file_name : str
            Nombre con el que se quiere guardar la figura en un archivo html. Por defecto el valor es False.

        Returns
        -------
        Retorna un gráfico de un mapa geográfico con puntos

        """
        init_notebook_mode(connected=True) 
        
        if df is None and coordenadas_poligono is not None:
            df = coordenadas_poligono[0]
            df['Label'] = 1
        elif df is None and coordenadas_poligono is None:
            print('Falta ingresar coordenadas')
   
        
        if scalecolor != False:
            data = go.Scattermapbox(
                        # Se define las columnas de latitud y longitud
                        lat = df['Latitud'],
                        lon = df['Longitud'],
                        # Determina el modo de dibujo de la información de los coordenadas.
                        #Si mode = "text", entonces el texto de los elementos aparecen en las coordenadas.
                        #De lo contrario, los textos aparecen al pasar el mouse.
                        mode ='markers',
                        # Se define que el color de los puntos será en función de una columna con números.
                        # Aquel punto que sea menor, será asignado con el primer color de la escala
                        # Configuración de los puntos. Se define el tamaño y la escala de color.
                        marker = dict(
                            autocolorscale = False,
                            color = df['Color'],
                            showscale=True,
                            size = 3,                           
                            colorscale =  scalecolor                        ),                        
                    )
        else:
           
            data = go.Scattermapbox(
                        lat = df['Latitud'],
                        lon = df['Longitud'],
                        mode ='markers',                 
                        marker = dict(
                            size = 3,                           
                            color = 'blue'
                        ),                       
                    )
            
        # Si el usuario no ingresa las coordenadas del centro del mapa, se define como centro los promedios
        # de las latitudes y longitudes del dataframe.
        if centro_map_lat == -999 or centro_map_lon == -999:
            centro_map_lat = df['Latitud'].quantile(0.5)
            centro_map_lon = df['Longitud'].quantile(0.5)
           
                
            
                
        layout = go.Layout(
            # Determina si un ancho o alto de diseño que el usuario ha dejado sin definir se inicializa 
            # en cada retransmisión
            autosize=True,
            width=950,  # Comentar para que el html sea del tamaño pantalla completo
            height=530, # Comentar para que el html sea del tamaño pantalla completo
            hovermode ='closest',
            mapbox = dict(
                # Establece el token de acceso de mapbox que se utilizará para este mapa de mapbox. 
                accesstoken = self.mapbox_access_token,
                bearing = 0,
                center = dict(
                    # Establece la latitud del centro del mapa 
                    lat = centro_map_lat,
                    # Establece la longitud del centro del mapa 
                    lon = centro_map_lon
                ),
                #Establece el ángulo de inclinación del mapa
                pitch = 0,
                # Establece el nivel de zoom del mapa 
                zoom = 11),
            margin=go.layout.Margin(
                l=0,
                r=0,
                b=0,
                t=0)
       
        )
        
        # Si es que no se ingresan coordenadas geográficas de un poligono
        if coordenadas_poligono is None:
        
            # Se grafica el mapa geográfico con los puntos
            fig = dict(data=[data], layout=layout)
            iplot(fig)
            if file_name != False:
                plotly.offline.plot(fig, filename=file_name)
        else:
            fig = go.Figure(data = data, layout = layout)
            mylayers =[]
            
            for i in range(len(coordenadas_poligono)):
                    df_1 = coordenadas_poligono[i]
                    
                    mylayers.append(self.get_polygon(lons = list(df_1['Longitud']), lats=list(df_1['Latitud'])))
                    mylayers.append(self.get_lines(lons = list(df_1['Longitud']), lats=list(df_1['Latitud'])))
            fig.layout.update(mapbox_layers =mylayers);
            
            if file_name != False:
                plotly.offline.plot(fig,filename=file_name)
                
            iplot(fig)
  
           
            
   
        
    
class Poligono():        
        
    def Interior_Poligono(dataframe,polygon_circunferencia):
        """
        Función que retorna un dataframe de las coordenadas geográficas que están al interior del circulo.
    
        Parameters
        ----------
        dataframe : DataFrame
            Dataframe que contiene una columna de latitud y otra de longitud
        some_poly : Polygon
            Constructor Polygon de una circunferencia
    
        Returns
        -------
        df : Dataframe
            Dataframe que contiene oordenadas geográficas que están al interior del poligono.
    
        """
        # Seleccionamos las coordenadas geográficas
        try:
            some_poly = Polygon(polygon_circunferencia)
        except:
            some_poly = polygon_circunferencia
        B = dataframe[['Longitud','Latitud']].values
        # Se busca si las coordenadas geográficas del cliente se encuentran dentro del polígono.
        X = []
        for i in range(0,len(B)):
            point = Point(B[i])  
            app = some_poly.contains(point)
            X.append(app)
        dataframe['filtro'] = X
        # Seleccionamos aqullos que están al interior
        df = dataframe[dataframe['filtro'] == True]
    
        return df
    
    
    def Circunferencia_v4(lat_center, lon_center, radio):
        """
        Encuentra las coordenadas geográficas del perímetros de una circunferencia
    
        Parameters
        ----------
        lat_center : float
            Latitud del centro de la circunferencia.
        lon_center : float
            Longitud del centro de la circunferencia.
        radio : float
            Dimensión del radio de la circunferencia en km. The default is float.
    
        Returns
        -------
        polygon :array
            Tuplas de las coordenadas geográficas del perímetro de la circunferencia
        """
        point = Point(lon_center, lat_center)
        local_azimuthal_projection = f"+proj=aeqd +R=6371000 +units=m +lat_0={point.y} +lon_0={point.x}"

        wgs84_to_aeqd = partial(
            pyproj.transform,
            pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
            pyproj.Proj(local_azimuthal_projection),
        )

        aeqd_to_wgs84 = partial(
            pyproj.transform,
            pyproj.Proj(local_azimuthal_projection),
            pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
        )

        point_transformed = transform(wgs84_to_aeqd, point)

        buffer = point_transformed.buffer(radio*1000)

        buffer_wgs84 = transform(aeqd_to_wgs84, buffer)
        coords = json.dumps(mapping(buffer_wgs84))
        coords = json.loads(coords)['coordinates'][0]
        return coords
    
    def Circunferencia_v3(lat_center, lon_center, radio):
        """
        Encuentra las coordenadas geográficas del perímetros de una circunferencia
    
        Parameters
        ----------
        lat_center : float
            Latitud del centro de la circunferencia.
        lon_center : float
            Longitud del centro de la circunferencia.
        radio : float
            Dimensión del radio de la circunferencia en km. The default is float.
    
        Returns
        -------
        polygon :array
            Tuplas de las coordenadas geográficas del perímetro de la circunferencia
        """

        local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(
            lat_center, lon_center
        )
        wgs84_to_aeqd = Transformer.from_proj('+proj=longlat +datum=WGS84 +no_defs',
                                              local_azimuthal_projection)
        aeqd_to_wgs84 = Transformer.from_proj(local_azimuthal_projection,
                                              '+proj=longlat +datum=WGS84 +no_defs')
        # Get polygon with lat lon coordinates
        point_transformed = Point(wgs84_to_aeqd.transform(lon_center, lat_center))

        buffer = point_transformed.buffer(radio*1000)
        circle = transform(aeqd_to_wgs84.transform, buffer)
        coords =list(circle.exterior.coords)
        return coords

    def Circunferencia_v2(lat_center, lon_center, radio):
        """
        Encuentra las coordenadas geográficas del perímetros de una circunferencia
    
        Parameters
        ----------
        lat_center : float
            Latitud del centro de la circunferencia.
        lon_center : float
            Longitud del centro de la circunferencia.
        radio : float
            Dimensión del radio de la circunferencia en km. The default is float.
    
        Returns
        -------
        polygon :array
            Tuplas de las coordenadas geográficas del perímetro de la circunferencia
        """

        proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
        # Azimuthal equidistant projection
        aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
        project = partial(
            pyproj.transform,
            pyproj.Proj(aeqd_proj.format(lat=lat_center, lon=lon_center)),
            proj_wgs84)
        buf = Point(0, 0).buffer(radio * 1000)  # distance in metres
        polygon = transform(project, buf).exterior.coords[:]

        return polygon
    
    
    def Circunferencia_v1(lat_center,lon_center,n_points = int,radio = float):
        """
        Encuentra las coordenadas geográficas del perímetros de la circunferencia, y genera un objeto
        de la circunferencia rellena
    
        Parameters
        ----------
        lat_center : float
            Latitud del centro de la circunferencia.
        lon_center : float
            Longitud del centro de la circunferencia.
        n_points : int
            Cantidad de puntos que formen el perímetro de la circunferencia
        radio : float
            Dimensión del radio de la circunferencia. The default is float.
    
        Returns
        -------
        polygon :array
            Tuplas de las coordenadas geográficas del perímetro de la circunferencia
        some_poly : Polygon
        Estructura Polygon de una circunferencia
    
        """
        # Se define el centro de la circunferencia
        p = shapely.geometry.Point([lon_center,lat_center])
        # Radio en metros
        d = radio * 10 * 100
        # Ángulos de la circunferencia
        angles = np.linspace(0, 360, n_points)
        # Coordenadas geográficas de la circunferencia
        polygon = geog.propagate(p, angles, d)
        # Se define un objeto que representa un área rellena.
        some_poly = Polygon(polygon)
        return polygon, some_poly
    
    def Poligono_n_puntos(df):
        """
        Encuentra las coordenadas geográficas del perímetros de la circunferencia, y genera un objeto
        de la circunferencia rellena
    
        Parameters
        ----------
        lat_center : float
            Latitud del centro de la circunferencia.
        lon_center : float
            Longitud del centro de la circunferencia.
        n_points : int
            Cantidad de puntos que formen el perímetro de la circunferencia
        radio : float
            Dimensión del radio de la circunferencia. The default is float.
    
        Returns
        -------
        polygon :array
            Tuplas de las coordenadas geográficas del perímetro de la circunferencia
        some_poly : Polygon
        Estructura Polygon de una circunferencia
    
        """
        # Se define el centro de la circunferencia
        Latitud = df['Latitud']
        Longitud = df['Longitud']
        coordenadas_polygon = list(zip(*[df[c].values.tolist() for c in df]))
        # Se define un objeto que representa un área rellena.
        some_poly = Polygon(coordenadas_polygon)
        return some_poly
    
    
    
    
 
class Distancia():
    
    def __init__(self, unidad): 
        """
        Se declara la unidad como un atributo

        Parameters
        ----------
        unidad : str
            Unidad de medida de la distancia. Las opciones son km o m.

        Returns
        -------
        None.

        """
        self.unidad  = unidad
      
    def Calcular_distancia(self,coordenadas_1, coordenadas_2):
        """
        Calcula la distancias entre dos coordenadas geográficas
    
        Parameters
        ----------
        coordenadas_1 : Tupla
            Contiene una tupla de la forma( latitud,longitud)
        coordenadas_2 : TYPE
            Contiene una tupla de la forma( latitud,longitud)
        unidad : str
            Unidad de medida de la distancia. Las opciones son km o m.
    
        Returns
        -------
        distancia : float
            Distancia entre las coordenadas geográficas.
    
        """
        if self.unidad == 'km':
            distancia = geodesic(coordenadas_1, coordenadas_2).km
        elif self.unidad == 'm':
            distancia = geodesic(coordenadas_1, coordenadas_2).m
            
        return distancia
            
    
    def Distancia_ref(self, df, coordenadas_ref):
        """
        Calcula la distancia que hay entre una lista de coordenadas geograficas de un dataframe
        con una referencia
    
        Parameters
        ----------
        df : DataFrame
            Dataframe que al menos contiene una columna de latitud y una de longitud.
        coordenadas_ref : Tupla
            Tupla de la forma (Latitud, Longitud)
        unidad : str
            Unidad de medida de la distancia. Las opciones son km o m.
    
        Returns
        -------
        df : TYPE
            Devuelve el dataframe inicial con una nueva columna que contiene la distancia entre 
            las coordenadas geográficas con al referencia.
            
        """
        # Crea una nueva columna de distancia
        df['Distancia '+ self.unidad] = None
        # Itera por todas las direcciones
        for i in range(len(df)):    
            # Se generan las tuplas de coordenas geográficas
            Latitud = df['Latitud'].iloc[i] 
            Longitud = df['Longitud'][i]
            Tupla = (Latitud, Longitud)
            
            try:
                # Se calcula la distancia a la refererencia.
                distancia = self.Calcular_distancia(Tupla, coordenadas_ref)
            except:
                distancia = 'No reconocido'
            
            # Se guarda el valor en el dataframe      
            df.loc[i,'Distancia '+self.unidad] = distancia
        return df
            
    
    
    
def Geodecodificacion(df, servidor):
    """
    Calcula las coordenadas geográficas de una dirección

    Parameters
    ----------
    df : DataFrame
        Dataframe que contiene al menos una columna de dirección.
    servidor : str
        Tipo de servidor para realizar la decodificación. Las opciones son: Arcjis y Nominatim.

    Returns
    -------
    df : DataFrame
        Devuelve el dataframe inicial con dos nuevas columnas: Latitud y Longitud

    """
    # Define el tipo de servidor con el que se decodificará
    if servidor == 'Nominatim':        
        geolocator = Nominatim(user_agent="catalina.muruua@gmail.com")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    elif servidor == 'Arcgis':
        geolocator = ArcGIS() 
    else:
        print('Servidor no incorporado')
    
    # Crea las columnas de Latitud y Longitud ene l datafarme ingresado
    df['Latitud'] = 'No reconocido'
    df['Longitud'] = 'No reconocido'
    # Itera por todas las direcciones
    for i in range(len(df)):       
        direccion = df['DIRECCION_NORMALIZADA'].iloc[i]
        try:
            # Calcula las coordenadas geográficas
            location = geolocator.geocode( direccion)
            # Guarda la latitud y la longitud en el dataframe
            df.loc[i,'Latitud'] = location.latitude
            df.loc[i,'Longitud'] = location.longitude               
        except:             
            pass
    return df

