import geopandas as gpd


def ler_geodataframe(caminho_gpkg, tabela):
    """
    Lê os dados do GeoPackage e retorna um GeoDataFrame.
    """
    query = f"SELECT * FROM {tabela}"
    gdf = gpd.read_file(caminho_gpkg, sql=query)
    return gdf

def selecionar_imovel_incra (gdf_incra, codigo_imovel):
    
    """Selecionar o imóvel do INCRA com base no código.

    Args:
        gdf_incra (GeoDataFrame): GeoDataFrame com os dados do INCRA.
        codigo_imovel (String): Código do imóvel a ser selecionado.

    Returns:
        gdf_incra_selecionado, centro_lat, centro_lon, miny, maxy, minx, maxx
    """
    # Selecionar o CAR considerando selectbox
    gdf_incra_selecionado = gdf_incra[gdf_incra['codigo_imo']==codigo_imovel].copy()

    # Calcular o Bounding Box do polígono
    bounds = gdf_incra_selecionado.geometry.total_bounds
    # Coords do Bounding Box
    minx, miny, maxx, maxy = bounds

    # Definir o centro do mapa com base no polígono selecionado
    centro_lat = (miny + maxy) / 2
    centro_lon = (minx + maxx) / 2

    return gdf_incra_selecionado, centro_lat, centro_lon, miny, maxy, minx, maxx