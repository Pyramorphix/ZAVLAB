"""
Interactive plotting canvas with click handling:
- Handles axis configuration clicks
- Manages subplot layout
- Renders matplotlib figures
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from dialogs import AxisConfigDialog
from PyQt6.QtWidgets import QMessageBox
import matplotlib.ticker as ticker


class INTERACTIVE_PLOT(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, data=[]):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = []
        self.subplots = []
        self.gs = gridspec.GridSpec(
            1, 1, 
            figure=self.fig,
            width_ratios=[1]*1,
            height_ratios=[1]*1,
            wspace=0.5,
            hspace=0.7
        )
        super().__init__(self.fig)
        self.setParent(parent)
        self.canvas = FigureCanvas(self.fig)
        self.data = None

        self.mpl_connect("button_press_event", self.on_click)
        # self.plot_data(data=None,labels=["x", "y"])

    def on_click(self, event):
        if not event.inaxes:
            return
        
        # Определяем, на каком графике произошел клик
        for i, ax in enumerate(self.axes):
            print(ax, type(ax))
            if event.inaxes == ax:
                # Определяем параметры для конкретного графика
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                tolerance = 0.05  # 5% от диапазона
                
                # Клик по оси X (нижняя часть)
                if event.ydata < y_min + tolerance * (y_max - y_min):
                    dialog = AxisConfigDialog('x', ax, self)
                    dialog.exec()
                    return
                
                # Клик по оси Y (левая часть)
                if event.xdata < x_min + tolerance * (x_max - x_min):
                    dialog = AxisConfigDialog('y', ax, self)
                    dialog.exec()
                    return
    
    def plot_all_data(self, win, rows, cols):
        """Generate the plot based on current configuration"""
        if not self.subplots:
            QMessageBox.warning(self, "No Subplots", "Please add at least one subplot")
            return
        
        # Create GridSpec
        self.gs = gridspec.GridSpec(
            rows, cols, 
            figure=self.fig,
            width_ratios=[1]*cols,
            height_ratios=[1]*rows,
            wspace=0.5,
            hspace=0.7
        )
        # Create a grid to track occupied cells
        occupied = [[False] * cols for _ in range(rows)]

        # Create axes for each subplot
        for subplot in self.subplots:
            plot_id, s_row, s_col, s_row_span, s_col_span, *_ = subplot
            ax = self.fig.add_subplot(self.gs[s_row:s_row+s_row_span, s_col:s_col+s_col_span])
            self.axes.append(ax)
            self.update_one_plot(subplot, win)
            
            # Mark occupied cells
            for r in range(s_row, s_row+s_row_span):
                for c in range(s_col, s_col+s_col_span):
                    if r < rows and c < cols:
                        occupied[r][c] = True
        # Add empty cells
        for r in range(rows):
            for c in range(cols):
                if not occupied[r][c]:
                    ax = self.fig.add_subplot(self.gs[r, c])
                    ax.text(0.5, 0.5, "Empty Cell", 
                            ha='center', va='center', fontsize=10,
                            transform=ax.transAxes, alpha=0.5)
                    ax.axis('off')
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.draw()
    
    def update_one_plot(self, subplot, win):
        plot_id, s_row, s_col, s_row_span, s_col_span, data_series, show_grid, subplot_info = subplot
        ax = self.axes[plot_id]
        ax.clear()
    
        # Plot all series
        for series in data_series:
            if series['x'] != "None" and series['y'] != "None":
                data = win.get_data(series['x'], series['y'])
                ax.plot(data[0], data[1], 
                        linewidth=series['width'], 
                        color=series['color'])
    
        ax.set_title(f"Subplot {plot_id}: {data_series[0]['y']}({data_series[0]['x']})", fontsize=10)
        ax.set_xlabel(data_series[0]["x"])
        ax.set_ylabel(data_series[0]["y"])
        if show_grid:
            #ax.grid(True, linestyle='--', alpha=0.7)
            ax.grid(color="#7a7c7d", linewidth=0.3)
            ax.grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)
        else:
            ax.text(0.5, 0.5, f"Subplot {plot_id}", 
                    ha='center', va='center', fontsize=12,
                    transform=ax.transAxes)
            ax.set_title(f"Subplot {plot_id}", fontsize=10)
        ax.minorticks_on()
        ax.tick_params(axis='x', length=4, width=2, labelsize=14, direction ='in')
        ax.tick_params(axis='y', length=4, width=2, labelsize=14, direction ='in')
        ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        return ax
