"""El engine pide cambiar un texto que aparece dos veces: edit_file se niega."""
from practica.editar import catalogo_temporal, edit_file

archivo = catalogo_temporal()
print(edit_file(archivo, 'i["cat"] == cat', 'i["cat"].lower() == cat.lower()'))
