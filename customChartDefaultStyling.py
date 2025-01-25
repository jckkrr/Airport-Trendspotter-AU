def styling(fig):
    
    textcolor = 'rgba(24,24,24,1)'
    axesFont = 'Inter'
    axeslinecolor = 'rgba(24,24,24,1)'
    gridcolor = 'rgba(245,245,245,1)'
    
    fig.update_layout(width = 800, height = 350, plot_bgcolor='#ffffff', paper_bgcolor='#ffffff')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=80))
    fig.update_layout(font_family=axesFont, font_color=textcolor, font_size=8)
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor=axeslinecolor, mirror=False, tickfont=dict(family=axesFont, size=10), tickangle=270)
    fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor=gridcolor)

    fig.update_yaxes(showline=False, linewidth=1, linecolor=axeslinecolor, mirror=False, tickfont=dict(family=axesFont, size=10), ) 
    # ticklabelposition="inside top" removed because it was causing certain subplot builds to crash for some reason  
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=gridcolor)
        
    fig.update_layout(legend=dict(orientation='h', font = dict(size = 10, color = "#181818")))
    
    fig.update_layout(title_font_family='Manrope', title_font_size=16, title_font_color='#181818') 
    fig.update_layout(title={'y':0.925,'x':0,'xanchor': 'left','yanchor': 'top'})
    fig.update_layout(legend={'y':1.1,'x':1,'xanchor': 'right','yanchor': 'top'})
    
######################################################