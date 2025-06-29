# --- GRÁFICO 3: TONELAJE POR DESTINO ---
tonelaje_por_destino = df_filtrado_fecha.groupby(DESTINO_COLUMN)[VOLUME_COLUMN].sum().sort_values(ascending=False).reset_index()
if not tonelaje_por_destino.empty:
    fig_destino = px.bar(tonelaje_por_destino,
                         x=DESTINO_COLUMN,
                         y=VOLUME_COLUMN,
                         title=f'Tonelaje por Destino',
                         labels={DESTINO_COLUMN: 'Destino', VOLUME_COLUMN: 'Tonelaje (toneladas)'},
                         color_discrete_sequence=px.colors.qualitative.Prism)
    st.plotly_chart(fig_destino, use_container_width=True)