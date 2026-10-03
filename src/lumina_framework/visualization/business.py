"""Exploración reproducible de ventas, categorías y promociones."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def save_figure(fig, output_dir, filename):
    """Exporta y cierra una figura concreta para no retener memoria."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    fig.tight_layout()
    path = output_dir / filename
    fig.savefig(path,dpi=160,bbox_inches='tight')
    plt.close(fig)
    return path


class BusinessVisualizer:
    def generate(self,data,output_dir):
        paths = []
        sns.set_theme(style='whitegrid',context='notebook')
        fig,ax = plt.subplots(figsize=(9,4.6))
        weekly = data.groupby('semana',as_index=False).unidades_vendidas.sum()
        sns.lineplot(data=weekly,x='semana',y='unidades_vendidas',ax=ax,color='#25618a')
        ax.set(title='Evolución semanal de las ventas',xlabel='Semana',ylabel='Unidades vendidas')
        paths.append(save_figure(fig,output_dir,'ventas_semanales.png'))
        fig,ax = plt.subplots(figsize=(9,4.6))
        sns.boxplot(data=data,x='categoria',y='unidades_vendidas',ax=ax,color='#74a6bc')
        ax.set(title='Distribución de ventas por categoría',xlabel='Categoría',ylabel='Unidades por producto y semana')
        paths.append(save_figure(fig,output_dir,'distribucion_categoria.png'))
        fig,ax = plt.subplots(figsize=(9,4.6))
        matrix = data.pivot_table(index='sucursal_id',columns='categoria',values='unidades_vendidas',aggfunc='mean')
        sns.heatmap(matrix,annot=True,fmt='.1f',cmap='YlGnBu',ax=ax,cbar_kws={'label':'Unidades promedio'})
        ax.set(title='Ventas promedio por sucursal y categoría',xlabel='Categoría',ylabel='Sucursal')
        paths.append(save_figure(fig,output_dir,'mapa_sucursal_categoria.png'))
        fig,ax = plt.subplots(figsize=(9,4.6))
        sns.boxplot(data=data,x='promocion',y='unidades_vendidas',ax=ax,color='#74a6bc')
        ax.set(title='Ventas durante semanas con y sin promoción',xlabel='Promoción activa 0 no 1 sí',ylabel='Unidades vendidas')
        paths.append(save_figure(fig,output_dir,'promocion_ventas.png'))
        return tuple(paths)
