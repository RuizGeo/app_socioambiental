import folium
import geopandas as gpd
from streamlit_folium import folium_static

def inserir_geojson_folium (gdf, nome_coluna
                            ,alias_coluna
                            ,nome_camada
                            ,cor_preenchimento
                            ,mapa):
    """
    Cria um mapa Folium a partir de um GeoDataFrame.
    """


    # Adiciona a camada GeoJSON ao mapa
    # Adicionar a camada de Imóveis Rurais
    folium.GeoJson(
        data=gdf,  # GeoDataFrame convertido diretamente em GeoJson
        name = nome_camada,  # Nome da camada no LayerControl
        tooltip=folium.GeoJsonTooltip(  # Configurar tooltip
            fields=[nome_coluna],  # Coluna(s) para mostrar no tooltip
            aliases=[alias_coluna+':'],  # Nomes amigáveis no tooltip
            localize=True
        ),
        style_function=lambda x: {
            'fillColor': cor_preenchimento,  # Cor de preenchimento
            'color': 'black',       # Cor das bordas
            'weight': 1,            # Largura das bordas
            'fillOpacity': 0.6      # Opacidade do preenchimento
        }
    ).add_to(mapa)

   

    return mapa