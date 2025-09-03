"""
Interactive plotting canvas with click handling:
- Handles axis configuration clicks
- Manages subplot layout
- Renders matplotlib figures
"""
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from dialogs import AxisConfigDialog, LegendConfigDialog, GridConfigDialog, TitleConfigDialog, LineLabelDialog
from PyQt6.QtWidgets import QMessageBox, QMenu
from PyQt6.QtGui import QAction
import matplotlib.ticker as ticker
from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

plt.rcParams['mathtext.fontset'] = 'cm' 


class INTERACTIVE_PLOT(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, data=[]):
        """
        Initialize interactive plotting canvas with line drawing capabilities
        
        Args:
            parent: Parent Qt widget
            width: Figure width in inches
            height: Figure height in inches
            dpi: Figure resolution in dots per inch
        """


        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = {}
        self.subplots = []
        self.draw_lines = []
        self.gs = gridspec.GridSpec(1, 1, figure=self.fig)
        super().__init__(self.fig)
        self.setParent(parent)
        self.canvas = FigureCanvas(self.fig)
        self.data = None
        self.textes = dict()

        self.mpl_connect("button_press_event", self.on_click)
        self.mpl_connect("pick_event", self.on_pick)
        self.context_menu = None
        self.current_line = None
        self.current_legend = None
        self.current_title = None
        self.current_subplot_id = None
        self.drawing_mode = False  # Flag to track if line drawing is active
        self.temp_line = None      # Temporary line object during drawing
        self.start_point = None    # Starting coordinates for line drawing
        self.current_label = None  # Currently active label object

    def on_click(self, event):
        """
        Handle mouse click events on the plot:
        - Axis clicks (configures axis properties)
        - Legend clicks (configures legend properties)
        - Title clicks (configures title properties)
        - Right-click (shows context menu for grid/legend/title)
        
        Handle mouse click events during line drawing mode:
        - First click sets starting point
        - Second click completes line and opens label dialog

        Args:
            event: Matplotlib mouse event
        """

        if not event.inaxes:
            return
        
        # Determine on which subplot the click occured
        for ax in self.axes.values():
            if event.inaxes == ax:
                self.current_subplot_id = ax._subplot_id
                
                # Click on the Y-axis
                if event.ydata < ax.get_ylim()[0] + 0.05 * (ax.get_ylim()[1] - ax.get_ylim()[0]):
                    dialog = AxisConfigDialog('x', ax, self)
                    dialog.exec()
                    return
                
                # Click on the X-axis
                if event.xdata < ax.get_xlim()[0] + 0.05 * (ax.get_xlim()[1] - ax.get_xlim()[0]):
                    dialog = AxisConfigDialog('y', ax, self)
                    dialog.exec()
                    return

                # Right click for the context menu
                if event.button == 3:
                    self.show_context_menu(event, ax)
                    return
                
                if self.drawing_mode and event.button == 1:  # Left click
                    if not self.start_point:
                        # First click - store starting point
                        self.start_point = (event.xdata, event.ydata)
                    else:
                        # Second click - finish line and open label dialog
                        self.current_ax = ax
                        self.finish_line((event.xdata, event.ydata))
                        self.start_point = None

                # Click on the legend
                if ax.get_legend():
                    # Используем преобразование координат для точного определения
                    legend_bbox = ax.get_legend().get_frame().get_window_extent()
                    # Преобразуем координаты события в пиксели фигуры
                    if legend_bbox.contains(event.x, event.y):
                        self.current_legend = ax.get_legend()
                        dialog = LegendConfigDialog(ax, self)
                        if dialog.exec():
                            ax.legend(loc=dialog.get_position(), frameon=False, fontsize=dialog.get_font_size())
                            self.canvas.draw()
                        return
                
                # Click on the title
                if ax.get_title():
                    # Получаем рендерер для преобразования координат
                    renderer = self.figure.canvas.get_renderer()
                    
                    # Получаем bbox заголовка в координатах фигуры
                    bbox = ax.title.get_window_extent(renderer)
                    
                    # Преобразуем координаты события в пиксели фигуры
                    x_px, y_px = self.figure.canvas.get_width_height()
                    x_ratio = event.x / x_px
                    y_ratio = 1 - (event.y / y_px)  # Инвертируем Y-координату
                    
                    # Проверяем попадание в заголовок
                    if (bbox.x0 <= x_ratio <= bbox.x1 and 
                        bbox.y0 <= y_ratio <= bbox.y1):
                        self.current_title = ax.title
                        dialog = TitleConfigDialog(ax, self)
                        if dialog.exec():
                            ax.set_title(dialog.get_title(), fontsize=dialog.get_font_size())
                            self.canvas.draw()
                        return

            
    def on_pick(self, event):
        """
        Handle line selection events:
        - Triggers line editing when a plot line is clicked
        
        Args:
            event: Matplotlib pick event
        """


        # Line selection processing
        if isinstance(event.artist, mpl.lines.Line2D):
            self.current_line = event.artist
            # Get subplot_id from parent widget
            parent = self.parent()  # INTERACTIVE_PLOT -> QWidget -> QScrollArea -> SubplotEditor
            if parent:
                parent.edit_line_style(self.current_line)

    def show_context_menu(self, event, ax):
        """
        Display context menu for plot customization options:
        - Toggle grid visibility
        - Edit legend properties
        - Edit title properties
        
        Args:
            event: Mouse event that triggered the menu
            ax: Matplotlib axis object where click occurred
        """


        self.context_menu = QMenu(self)
        
        # Get current subolot
        current_subplot = next((s for s in self.subplots if s[0] == ax._subplot_id), None)
        
        if current_subplot:
            # The menu item for the grid
            grid_action = QAction("Grid: " + ("On" if current_subplot[6]["show grid"] else "Off"), self)
            grid_action.triggered.connect(lambda: self.toggle_grid(ax))
            self.context_menu.addAction(grid_action)
            
            # The menu item for the Legend
            legend_action = QAction("Edit the legend", self)
            legend_action.triggered.connect(lambda: self.edit_legend(ax))
            self.context_menu.addAction(legend_action)
            
            # The menu item for the title
            title_action = QAction("Edit the title", self)
            title_action.triggered.connect(lambda: self.edit_title(ax))
            self.context_menu.addAction(title_action)
            
            self.context_menu.exec(event.guiEvent.globalPosition().toPoint())

    def toggle_grid(self, ax):
        """
        Toggle grid visibility for the specified axis
        
        Args:
            ax: Matplotlib axis object to modify
        """


        current_subplot = next((s for s in self.subplots if s[0] == ax._subplot_id), None)
        if current_subplot:
            current_subplot[6]["show grid"] = not current_subplot[6]["show grid"]
            self.update_one_plot(current_subplot, self.window())
            self.canvas.draw()

    def edit_legend(self, ax):
        """
        Open legend configuration dialog for the specified axis
        
        Args:
            ax: Matplotlib axis object containing the legend
        """


        self.current_legend = ax.get_legend()
        dialog = LegendConfigDialog(ax, self)
        if dialog.exec():
            ax.legend(loc=dialog.get_position(), frameon=False, fontsize=dialog.get_font_size())
            self.canvas.draw()

    def edit_title(self, ax):
        """
        Open title configuration dialog for the specified axis
        
        Args:
            ax: Matplotlib axis object containing the title
        """


        self.current_title = ax.title
        dialog = TitleConfigDialog(ax, self)
        if dialog.exec():
            ax.set_title(dialog.get_title(), fontsize=dialog.get_font_size())
            self.canvas.draw()

    def plot_all_data(self, win, rows, cols):
        """Generate the plot based on current configuration"""

        if not self.subplots:
            QMessageBox.warning(self, "No Subplots", "Please add at least one subplot")
            return
        
        del self.gs
        self.fig.clear()
        del self.axes
        self.axes = {}
        self.textes = dict()
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
            self.axes[plot_id] = ax
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
        """
        Update and redraw a single subplot with current configuration
        
        Args:
            subplot: Subplot configuration data
            win: Parent window reference for data access
        """

        plot_id, s_row, s_col, s_row_span, s_col_span, data_series, sub_info, lines = subplot
        axes_info = sub_info["axes"]
        title_info = sub_info["title"]
        legend_info = sub_info["legend"]
        grid_info = sub_info["grid"]
        ax: Axes = self.axes[plot_id]
        ax.clear()
    
        # Plot all series
        for series in data_series:
            if series['x'] != "None" and series['y'] != "None":
                if series['xerr'] != "None" or series['yerr'] != "None":
                    data = win.get_error_data(x=series['x'], y=series['y'], xerr=series['xerr'], yerr=series['yerr'])
                    if data:
                        container = ax.errorbar(x=data[0], y=data[2],xerr=data[1], yerr=data[3],
                            linewidth=series['width'], 
                            color=series['color'],
                            label=series['label'], 
                            ls=series["ls"],
                            alpha=series["alpha"],
                            marker=series["marker"],
                            markersize=series["marker size"])
                        line = container.lines[0] if container.lines else None
                    
                else:
                    data = win.get_data(series['x'], series['y'])
                    if data:
                        line = ax.plot(data[0], data[1], 
                                linewidth=series['width'], 
                                color=series['color'],
                                label=series['label'], 
                                ls=series["ls"],
                                alpha=series["alpha"],
                                marker=series["marker"],
                                markersize=series["marker size"])
    
        ax.set_title(title_info["title"], fontsize=title_info["title fs"])
        if grid_info["show grid"]:
            #ax.grid(True, linestyle='--', alpha=0.7)
            ax.grid(color="#7a7c7d", linewidth=0.3)
            ax.grid(which='minor', color='#7a7c7d', linestyle=':', linewidth=0.2)
        else:
            # ax.text(0.5, 0.5, f"Subplot {plot_id}", 
            #         ha='center', va='center', fontsize=12,
            #         transform=ax.transAxes)
            ax.grid(visible=False)
            pass

        ax.minorticks_on()
        

        #local functions for rounding labels
        def zero_formatter_x(x, pos, acc=axes_info["x round accuracy"]):
            rounded_x = round(x, acc)
            if abs(rounded_x) < 1e-8:
                return "0" 
            else:
                return f"{x:.{acc}f}"
    
        def zero_formatter_y(y, pos, acc=axes_info["y round accuracy"]):
            rounded_y = round(y, acc)
            if abs(rounded_y) < 1e-8:
                return "0" 
            else:
                return f"{y:.{acc}f}"
            
        #set x axis
        ax.set_xlabel(axes_info["x-label"], loc="center", fontsize=axes_info["x label fs"])
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(zero_formatter_x))
        ax.xaxis.set_ticks_position("bottom")
        ax.tick_params(axis='x', length=4, width=2, labelsize=axes_info["x label fs"], direction ='in')
        if not axes_info["x scale"]:
            ax.tick_params(axis='x', which='minor', direction='in', length=2, width=1, color='black')
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["x small ticks"]))
        else:
            ax.set_xscale("log")
        ax.set_xlim(axes_info["x min"], axes_info["x max"])
        ax.spines["left"].set_position(("data", axes_info["x min"]))
        ax.set_xticks(np.linspace(axes_info["x min"], axes_info["x max"], axes_info["x ticks"]))

        #set y axis
        ax.set_ylabel(axes_info["y-label"], loc="center", fontsize=axes_info["y label fs"])
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(zero_formatter_y))        
        ax.yaxis.set_ticks_position("left")
        ax.tick_params(axis='y', length=4, width=2, labelsize=axes_info["y label fs"], direction ='in')
        if not axes_info["y scale"]:
            ax.tick_params(axis='y', which='minor', direction='in', length=2, width=1, color='black')
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(axes_info["y small ticks"]))
        else:
            ax.set_yscale("log")
        ax.set_ylim(axes_info["y min"], axes_info["y max"])
        ax.spines["bottom"].set_position(("data", axes_info["y min"]))
        ax.set_yticks(np.linspace(axes_info["y min"], axes_info["y max"], axes_info["y ticks"]))
        
        #set legend
        ax.legend(loc=legend_info["legend position"], frameon=False, prop={"size": legend_info["legend fs"]})

        #draw lines
        for line in lines:
            self.draw_line(line, ax)

        #set ax id
        ax._subplot_id = plot_id

        # Add picker functionality to lines
        for line in ax.get_lines():
            line.set_picker(5)  # 5 pixels tolerance
            line._series_id = series.get('id', 0)
            line._subplot_id = plot_id

    def draw_line(self, params, ax=None):
        """Draws a line on the graph"""

        if not ax:
            ax = self.figure.gca()
        # Calculate the coordinates depending on the type
        if params['type'] == 0:  # Two points
            x = [params['x1'], params['x2']]
            y = [params['y1'], params['y2']]
        elif params['type'] == 1:  # equation
            x_min, x_max = ax.get_xlim()
            x = [x_min, x_max]
            y = [params['k'] * x_min + params['b'], params['k'] * x_max + params['b']]
            params['x1'], params['x2'] = x_min, x_max
            params['y1'], params['y2'] = y[0], y[1] 
        else:  # point and angle
            rad = params['angle']
            k = np.tan(rad)
            b = params['py'] - params['px'] * k
            x_min, x_max = ax.get_xlim()
            x = [x_min, x_max]
            y = [k * x_min + b, k * x_max + b]
            params['x1'], params['x2'] = x_min, x_max
            params['y1'], params['y2'] = y[0], y[1] 

        
        # draw line
        line = ax.plot(x, y, 
                color=params['color'], 
                linewidth=params['width'], 
                linestyle=params['style'])
        
        # add labels to lines
        if 'label' in params and params['label']:
            self.add_line_label(ax, line, params)

        # self.canvas.draw()
        # self.draw()

    def add_line_label(self, ax, line, params):
        """Add label to line."""

        # Define label position
        position = params.get('label_position', 'Above the middle of the line')
        fontsize = params.get('label_font_size', 10)
        
        # choordinates of start, end and middle of the line
        x0, y0 = params['x1'], params['y1']
        x1, y1 = params['x2'], params['y2']
        x_mid = (x0 + x1) / 2
        y_mid = (y0 + y1) / 2
        
        # shift for label
        offset_y = 0
        offset_x = 0
        
        # define choordinates for label
        if position == "Above the beginning of the line":
            x, y = x0, y0
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Above the middle of the line":
            x, y = x_mid, y_mid
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Above the end of the line":
            x, y = x1, y1
            ha = 'center'
            va = 'bottom'
            y += offset_y
        elif position == "Under the beginning of the line":
            x, y = x0, y0
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "Under the middle of the line":
            x, y = x_mid, y_mid
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "Under the end of the line":
            x, y = x1, y1
            ha = 'center'
            va = 'top'
            y -= offset_y
        elif position == "To the left of the beginning":
            x, y = x0, y0
            ha = 'right'
            va = 'center'
            x -= offset_y
        elif position == "To the left of the middle":
            x, y = x_mid, y_mid
            ha = 'right'
            va = 'center'
            x -= offset_x
        elif position == "To the left of the end":
            x, y = x1, y1
            ha = 'right'
            va = 'center'
            x -= offset_x
        elif position == "To the right of the beginning":
            x, y = x0, y0
            ha = 'left'
            va = 'center'
            x += offset_x
        elif position == "To the right of the middle":
            x, y = x_mid, y_mid
            ha = 'left'
            va = 'center'
            x += offset_x
        else:  # "To the right of the end"
            x, y = x1, y1
            ha = 'left'
            va = 'center'
            x += offset_x
        # add label
        if ax._subplot_id in self.textes:
            if not params['id'] in self.textes[ax._subplot_id]:
                self.textes[ax._subplot_id][params['id']] = ax.text(x, y, params['label'], 
                        fontsize=fontsize, 
                        color=params['color'],
                        horizontalalignment=ha,
                        verticalalignment=va,
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
            else:
                self.textes[ax._subplot_id][params['id']].set(x=x, y=y, label=params['label'],
                                                             fontsize=fontsize, color=params['color'],
                                                             horizontalalignment=ha,
                                                             verticalalignment=va,
                                                             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
        else:
            self.textes[ax._subplot_id] = dict()
            self.textes[ax._subplot_id][params['id']] = ax.text(x, y, params['label'], 
                    fontsize=fontsize, 
                    color=params['color'],
                    horizontalalignment=ha,
                    verticalalignment=va,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))
        return ax
    

    def toggle_drawing_mode(self, enabled):
        """
        Toggle line drawing mode on/off
        
        Args:
            enabled: Boolean indicating whether drawing mode should be activated
        """


        self.drawing_mode = enabled
        self.start_point = None
        if self.temp_line:
            self.temp_line.remove()
            self.temp_line = None
        self.canvas.draw_idle()
    
    def on_motion(self, event):
        """
        Handle mouse movement during line drawing:
        - Shows temporary line preview from start point to current position
        
        Args:
            event: Matplotlib mouse motion event
        """
        
        if not event.inaxes or not self.drawing_mode or not self.start_point:
            return
            
        # Remove previous temporary line
        if self.temp_line:
            self.temp_line.remove()
            
        # Create new temporary line
        self.temp_line, = event.inaxes.plot(
            [self.start_point[0], event.xdata],
            [self.start_point[1], event.ydata],
            'r--', linewidth=1  # Red dashed preview line
        )
        self.canvas.draw_idle()

    def finish_line(self, end_point):
        """
        Finalize drawn line and open label configuration dialog
        
        Args:
            end_point: Tuple (x, y) of line end point coordinates
        """
        # Remove temporary line
        if self.temp_line:
            self.temp_line.remove()
            self.temp_line = None
            
        # Create permanent line
        ax = self.current_ax
        line = ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            'b-', linewidth=1.5, picker=5
        )[0]
        
        # Store line reference
        self.draw_lines.append(line)
        
        # Open label dialog
        self.open_label_dialog(line, mid_point=(
            (self.start_point[0] + end_point[0]) / 2,
            (self.start_point[1] + end_point[1]) / 2
        ))

    def open_label_dialog(self, line, mid_point):
        """
        Open dialog for configuring line label
        
        Args:
            line: Matplotlib line object to label
            mid_point: Tuple (x, y) of line midpoint coordinates
        """
        dialog = LineLabelDialog(self)
        if dialog.exec():
            text = dialog.get_text()
            position = dialog.get_position()
            font_size = dialog.get_font_size()
            
            # Calculate label position based on selection
            x, y = mid_point
            if "top" in position:
                y += 0.05  # Offset above line
            elif "bottom" in position:
                y -= 0.05  # Offset below line
            if "left" in position:
                x -= 0.05  # Offset left of line
            elif "right" in position:
                x += 0.05  # Offset right of line
                
            # Create text annotation
            self.current_label = ax.text(
                x, y, text, 
                fontsize=font_size,
                ha='center' if 'center' in position else 
                    'left' if 'right' in position else 'right',
                va='center' if 'middle' in position else 
                    'bottom' if 'top' in position else 'top',
                bbox=dict(facecolor='white', alpha=0.7, pad=2)
            )
            
            # Connect label to line
            line._label = self.current_label
            self.canvas.draw()
