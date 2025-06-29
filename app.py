# 3. Gráfico por Cantidad de Guías Emitidas por Producto (AHORA ESTE GRÁFICO SE OCULTA)
# Se mantiene el cálculo por si acaso se necesitara para otros fines, pero no se grafica para evitar duplicidad.
# if not guias_por_producto.empty:
#     fig_guias_producto = px.bar(guias_por_producto,
#                        x=PRODUCTO_COLUMN, y='CANTIDAD_GUIAS',
#                        title=f'Cantidad de Guías por Producto - {fecha_dt_seleccionada.strftime("%d-%m-%Y")}',
#                        labels={PRODUCTO_COLUMN: 'Producto', 'CANTIDAD_GUIAS': 'Nro. de Guías'},
#                        color_discrete_sequence=px.colors.qualitative.G10)
#     st.plotly_chart(fig_guias_producto, use_container_width=True)
# else:
#     st.warning("No hay datos de guías por producto para mostrar el gráfico.")