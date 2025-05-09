from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import seaborn as sns

def plot_line_graph(df, x_column, y_column, title=None, xlabel=None, ylabel=None, 
                    figsize=(15, 6), colors=None, linestyles=None,
                    grid=True, save_path=None):
    
    sns.set_style('whitegrid')
    
    fig, ax = plt.subplots(figsize=figsize)

    # If only one y_column is passed as string, make it a list
    if isinstance(y_column, str):
        y_column = [y_column]
    
    # Set default colors and linestyles if not provided
    if colors is None:
        colors = sns.color_palette("tab10")  # Use seaborn default palette
    if linestyles is None:
        linestyles = ['-'] * len(y_column)

    # Plot each y column
    for i, col in enumerate(y_column):
        ax.plot(df[x_column], df[col], 
                color=colors[i % len(colors)], 
                linestyle=linestyles[i % len(linestyles)], 
                label=col)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    
    ax.set_xlabel(xlabel if xlabel else x_column, fontsize=12)
    ax.set_ylabel(ylabel if ylabel else "Value", fontsize=12)
    
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    if grid:
        ax.grid(True)

    ax.legend()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig, ax
