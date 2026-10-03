"""Figuras que muestran error, referencia e interpretación predictiva."""
import matplotlib.pyplot as plt
import seaborn as sns
from lumina_framework.visualization.business import save_figure


class ModelDiagnosticsVisualizer:
    def generate(self,predictions,metrics,importance,output_dir,selected_model='Ridge'):
        paths=[]
        fig,axes = plt.subplots(1,3,figsize=(12,4.7))
        for ax,metric,label in zip(axes,('mae','rmse','wape'),('MAE en unidades','RMSE en unidades','WAPE proporción')):
            sns.barplot(data=metrics,x='modelo',y=metric,ax=ax,color='#46849e')
            ax.set(title=label,xlabel='Modelo',ylabel=label)
            ax.tick_params(axis='x',rotation=25)
        fig.suptitle('Desempeño en el periodo de prueba',y=1.04)
        paths.append(save_figure(fig,output_dir,'comparacion_modelos.png'))
        fig,ax = plt.subplots(figsize=(9,4.6))
        cols = ['ventas_proximas_4_semanas','Ingenuo',selected_model]
        weekly = predictions.groupby('semana')[list(dict.fromkeys(cols))].sum()
        labels = {'ventas_proximas_4_semanas':'Ventas observadas','Ingenuo':'Referencia ingenua',selected_model:'Modelo elegido'}
        for column in weekly:
            ax.plot(weekly.index,weekly[column],label=labels[column],marker='o')
        ax.legend()
        ax.set(title='Ventas observadas y pronósticos de cuatro semanas',xlabel='Semana de corte',ylabel='Unidades futuras acumuladas')
        paths.append(save_figure(fig,output_dir,'real_vs_predicho.png'))
        fig,axes = plt.subplots(1,2,figsize=(11,4.6))
        f=predictions.copy()
        f['_error']=(f.ventas_proximas_4_semanas-f[selected_model]).abs()
        for ax,c,label in zip(axes,('sucursal_id','categoria'),('Sucursal','Categoría')):
            grouped=f.groupby(c,as_index=False)._error.mean()
            sns.barplot(data=grouped,x=c,y='_error',ax=ax,color='#46849e')
            ax.set(xlabel=label,ylabel='MAE en unidades')
            ax.tick_params(axis='x',rotation=25)
        fig.suptitle('Dónde se concentran los errores del modelo elegido',y=1.03)
        paths.append(save_figure(fig,output_dir,'errores_segmentados.png'))
        fig,ax = plt.subplots(figsize=(9,5))
        if not importance.empty:
            sns.barplot(data=importance.head(10),x='importancia',y='variable',color='#46849e',ax=ax)
        else:
            ax.text(.5,.5,'Referencia basada únicamente en ventas recientes',ha='center',transform=ax.transAxes)
        ax.set(title='Variables asociadas al desempeño predictivo',xlabel='Aumento de MAE al permutar la variable',ylabel='Variable')
        paths.append(save_figure(fig,output_dir,'importancia_variables.png'))
        return tuple(paths)
