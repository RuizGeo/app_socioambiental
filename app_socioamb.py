import streamlit as st
from processa_geodados import ler_geodataframe, selecionar_imovel_incra
from geoviz import inserir_geojson_folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import folium

import pandas as pd
import plotly.express as px

# Configurações iniciais
st.set_page_config(page_title="SocioAmbiental", layout="wide")

# Título centralizado usando HTML e CSS
st.markdown(
    """
    <h1 style='text-align: center; color: darkblue;'>Sistema de Análise SocioAmbiental 🌍</h1>
    """,
    unsafe_allow_html=True
)

# Criar e exibir o mapa
st.subheader("Mapa Interativo")

# Caminho para o GeoPackage
gpkg_file = "./geodados_municipios.gpkg"

# Leitura dos dados do INCRA
incra = ler_geodataframe(gpkg_file, 'incra')

# Selecionar o códigos dos imóveis do INCRA
cod_imoveis_incra = incra['codigo_imo'].unique()

# Carregar os dados
st.sidebar.title("Filtros")

# Criar o selectbox com os códigos dos imóveis do INCRA
cod_imoveis_incra_selecionado = st.sidebar.selectbox("Escolha o imóvel:", cod_imoveis_incra)

# Selecionar o imóvel do INCRA e retorna as coordenadas envolventes do imóvel
gdf_incra_selecionado, centro_lat, centro_lon, miny, maxy, minx, maxx = selecionar_imovel_incra(incra, cod_imoveis_incra_selecionado)

# Centraliza no centroide dos dados do INCRA
#centro_x = incra.geometry.centroid.x.mean()
#centro_y = incra.geometry.centroid.y.mean()

# Iniciando o mapa Folium com INCRA
mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=10)

# Gerar o mampa com dados do INCRA
mapa = inserir_geojson_folium(incra, 'codigo_imo'
                              ,'Código do Imóvel'
                              ,'Imóveis do INCRA'
                              ,'white'
                              ,mapa)
                          



# Camadas no Banco de Dados Geoespaciais
dict_camadas = {'Embargos IBAMA':'cotriguacu_embargos_ibama_mt'
                ,'Sítios Arqueológicos':'cotriguacu_sitios_mt'
                ,'Terra Indígena':'cotriguacu_indigenas_funai_mt'
                ,'Embargos ICMBio':'cotriguacu_embargos_icmbio_mt'
                ,'Assentamentos':'cotriguacu_assentamento_brasil_mt'
                ,'Áreas Quilombolas':'cotriguacu_áreas_de_quilombolas_mt'
                ,'Desmatamentos':'cotriguacu_dashboard_alerts_shapefile'}

# Dicionário com os nomes dos campos da camada a serem exibidos
dict_camadas_colunas_ids = {'Embargos IBAMA':'numero_tad'
                ,'Sítios Arqueológicos':'codigo_iphan'
                ,'Terra Indígena':'terrai_codigo'
                ,'Embargos ICMBio':'numero_emb'
                ,'Assentamentos':'cd_sipra'
                ,'Áreas Quilombolas':'nr_process'
                ,'Desmatamentos':'CODEALERTA'}


# Acessar camadas que tenham sobreposição com o imóvel selecionado
camadas_intersect = [ k for k, v in dict_camadas.items() if gdf_incra_selecionado[v].values[0] > 0]


# Inserir camadas no mapa 
for c in camadas_intersect:
    print(c)
    # Leitura do GeoDataFrame
    gdf = ler_geodataframe(gpkg_file, dict_camadas[c])

    # Adicionar geodados socioambientais no mapa
    mapa = inserir_geojson_folium(gdf[[dict_camadas_colunas_ids[c],'geometry']].to_json()
                            , dict_camadas_colunas_ids[c]
                            ,dict_camadas_colunas_ids[c]
                            ,c
                            ,'red'
                            ,mapa)



# Adiciona controle de camadas
folium.LayerControl().add_to(mapa)


# Ajustar o mapa para os limites do polígono
mapa.fit_bounds([[miny, minx], [maxy, maxx]])

# Exibir o mapa
st_folium(mapa, use_container_width=True, height=500)

# Sidebar
st.sidebar.title("📊 Conformidade")

# Função para exibir status com emoji
def mostrar_status(nome, status):
    emoji = "✅" if status == 0 else "❌"
    st.sidebar.write(f"{emoji} {nome}")

# Exibir status
mostrar_status("Embargos IBAMA", gdf_incra_selecionado['cotriguacu_embargos_ibama_mt'].values[0])
mostrar_status("Sítios Arqueológicos", gdf_incra_selecionado['cotriguacu_sitios_mt'].values[0])
mostrar_status("Terra Indígena", gdf_incra_selecionado['cotriguacu_indigenas_funai_mt'].values[0])
mostrar_status("Embargos ICMBio", gdf_incra_selecionado['cotriguacu_embargos_icmbio_mt'].values[0])
mostrar_status("Assentamentos", gdf_incra_selecionado['cotriguacu_assentamento_brasil_mt'].values[0])
mostrar_status("Áreas Quilombolas", gdf_incra_selecionado['cotriguacu_áreas_de_quilombolas_mt'].values[0])
mostrar_status("Desmatamentos", gdf_incra_selecionado['cotriguacu_dashboard_alerts_shapefile'].values[0])


# Rename columns
columns_renamed = []
for chave, valor in dict_camadas.items(): 
    # renomear as colunas a partir da chave e valor
    gdf_incra_selecionado.rename(columns={valor:chave}, inplace=True)
    # Inserir ba lista as colunas renomeadas
    columns_renamed.append(chave)



# Criando um DataFrame

# Transpondo o DataFrame para um formato adequado ao gráfico de barras
df_melted = gdf_incra_selecionado[columns_renamed].melt( var_name='Categoria', value_name='Área')

# Agrupar
df_melted = df_melted.groupby('Categoria').mean().reset_index()

# Criando o gráfico de barras
fig = px.bar(df_melted, x='Categoria', y='Área', color='Categoria', barmode='group',
             labels={'Categoria': 'Categoria', 'Área': 'Área (ha)'})

fig.update_traces(width=0.7)  # Aumenta a largura das barras (valor padrão é ~0.8)

fig.update_layout(
    bargap=1,  # Controla o espaço entre grupos de barras
   
)

# Exibindo o gráfico no Streamlit
st.subheader("Gráfico das áreas (ha)")
st.plotly_chart(fig)

# Criar e exibir o mapa
st.subheader("Área Total Sobreposta (ha)")

# Mostrar a tabela interativa
st.dataframe(pd.DataFrame(gdf_incra_selecionado[columns_renamed].iloc[0]).T)
#pd.DataFrame(gdf_incra_selecionado[columns_renamed].iloc[0]).T)
