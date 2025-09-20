# Documentation

## File: main_window.py

### ZAVLABMainWindow Class

- **`__init__(self) -> None`**  
  Initializes the main application window with all components and UI setup.

- **`_configure_window(self) -> None`**  
  Sets up basic window properties like title and size.

- **`_initialize_components(self) -> None`**  
  Initializes all application components including table, plotter, and menu.

- **`_initialize_plot_data(self) -> None`**  
  Initializes plot with column headers from the table.

- **`_setup_ui(self) -> None`**  
  Sets up the user interface layout and styling.

- **`_attach_elements(self) -> None`**  
  Adds widgets to main layout.

- **`_configure_main_splitter(self) -> None`**  
  Sets main splitter properties and stretch factors.

- **`_apply_styles(self) -> None`**  
  Gets and applies CSS styling based on current theme.

- **`_connect_signals(self) -> None`**  
  Connects internal signals between components.

- **`set_theme(self, theme_name: str) -> None`**  
  Changes application theme.

- **`setupTable(self) -> None`**  
  Initializes table with formula bar and decimal control.

- **`setupMenuBar(self) -> None`**  
  Updated to include JSON save/load options for formulas:

- **`tableDroppedHMenu(self, pos: QPoint) -> None`**  
  Context menu for horizontal headers (column management).

- **`tableDroppedVMenu(self, pos: QPoint) -> None`**  
  Context menu for vertical headers (row management).

- **`addMultipleColumnsLeft(self, position: int) -> None`**  
  Adds multiple columns to the left of the specified position.

- **`addMultipleColumnsRight(self, position: int) -> None`**  
  Adds multiple columns to the right of the specified position.

- **`addMultipleRowsAbove(self, position: int) -> None`**  
  Adds multiple rows above the specified position.

- **`addMultipleRowsBelow(self, position: int) -> None`**  
  Adds multiple rows below the specified position.

- **`deleteTableColumn(self, col: int) -> None`**  
  Deletes specified column with confirmation.

- **`deleteTableRow(self, row: int) -> None`**  
  Deletes specified row with confirmation.

- **`_new_file(self) -> None`**  
  Clears the table for a new experiment.

- **`_save_csv(self, file_name=None) -> None`**  
  Saves table data to CSV file.

- **`_load_csv(self) -> None`**  
  Loads data from CSV file into table.

- **`_save_json(self) -> None`**
  Saves table data to JSON file (including formulas and complete table state).

-**`_load_json(self) -> None`**
  Loads table data from JSON file (including formulas and complete table state).

- **`get_column_index(self, column_name: str) -> int`**  
  Finds column index by name.

- **`get_data(self, x: int|str, y: int|str, lenght: int|None = None) -> np.ndarray`**  
  Extracts data from table for plotting.

- **`get_error_data(self, x: int|str, xerr: int|str, y: int|str, yerr: int|str, lenght: int|None = None) -> np.ndarray`**  
  Extracts data with errors for error bar plotting.

- **`update_headers(self) -> None`**  
  Extracts headers and emits them as a list for plot updates.

- **`get_headers(self)`**  
  Returns all column headers.

- **`_save_plot_settings(self) -> None`**  
  Saves graph configuration to a JSON file.

- **`_load_plot_settings(self) -> None`**  
  Loads graph configuration from a JSON file.

- **`_save_plot_image(self) -> None`**  
  Saves the current graph as an image.

- **`_mainAppInfo(self) -> None`**  
  Shows application information dialog.

- **`_tableGuide(self) -> None`**  
  Shows table functionality guide.

- **`_plotGuide(self) -> None`**  
  Shows plotting system guide.

- **`_editorGuide(self) -> None`**  
  Shows plot customization options guide.

- **`_LinesGuide(self) -> None`**  
  Shows lines and annotations guide.

- **`_example(self) -> None`**  
  Shows recommended workflow example.

- **`get_min_max_from_column(self, x: int|str, lenght: None|int = None) -> list[float]`**  
  Gets minimum and maximum values from a column.

- **`get_min_max_value(self)`**  
  Gets min/max values for all columns.

- **`update_formula_bar(self) -> None`**  
  Updates the formula bar with the formula of the currently selected cell.

- **`apply_formula(self) -> None`**  
  Applies the formula from the formula bar to the selected cells.

- **`refresh_table(self) -> None`**  
  Refreshes the table view after data changes.

- **`change_decimal_places(self, value) -> None`**  
  Changes decimal places setting and refreshes display.

- **`show_decimal_dialog(self) -> None`**  
  Shows dialog to set decimal places.

- **`apply_formula_with_relative_refs(self) -> None`**  
  Applies formula with relative references to selected cells.

- **`restore_state(self) -> None`**  
  Tries to load last autosave state.

- **`closeEvent(self, event) -> None`**  
  Handles application close event with autosave.

- **`get_state(self)`**  
  Returns complete application state for saving.

- **`apply_state(self, state) -> None`**  
  Restores application state from saved data.

- **`convert_numpy_types(self, obj)`**  
  Converts numpy types to native Python types for JSON serialization.

---

## File: table.py

### ExcelLikeModel Class

- **`__init__(self, rows=20, cols=10)`**  
  Initializes the table model with data, formulas, and dependencies.

- **`rowCount(self, parent=None)`**  
  Returns number of rows in the model.

- **`columnCount(self, parent=None)`**  
  Returns number of columns in the model.

- **`headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole)`**  
  Returns header data for the given section and orientation.

- **`setHeaderData(self, section, orientation, value, role=Qt.ItemDataRole.EditRole)`**  
  Sets header data for the given section and orientation.

- **`flags(self, index)`**  
  Returns the item flags for the given index.

- **`data(self, index, role=Qt.ItemDataRole.DisplayRole)`**  
  Returns data for the given role and index.

- **`setData(self, index, value, role=Qt.ItemDataRole.EditRole)`**  
  Sets data at index to value for the given role.

- **`evaluate_cell(self, row, col)`**  
  Evaluates the formula in the specified cell.

- **`_safe_eval(self, expr)`**  
  Safely evaluates a mathematical expression.

- **`evaluate_all(self)`**  
  Recalculates all formulas in the table.

- **`is_number(self, s)`**  
  Checks if a string can be converted to a number.

- **`column_name_to_index(self, name)`**  
  Converts column name to index (supports both default and custom names).

- **`index_to_column_name(self, index)`**  
  Converts zero-based column index to Excel-style name (A, B, ...).

- **`clear_dependencies(self, row, col)`**  
  Removes this cell from all dependency lists.

- **`adjust_formula_references(self, formula, row_offset, col_offset)`**  
  Adjusts formula references based on row and column offsets.

- **`insertColumn(self, column, parent=QtCore.QModelIndex())`**  
  Inserts a new column at the specified position.

- **`removeColumn(self, column, parent=QtCore.QModelIndex())`**  
  Removes the column at the specified position.

- **`insertRow(self, row, parent=QtCore.QModelIndex())`**  
  Inserts a new row at the specified position.

- **`removeRow(self, row, parent=QtCore.QModelIndex())`**  
  Removes the row at the specified position.

- **`setColumnCount(self, cols)`**  
  Sets the number of columns in the model.

- **`setRowCount(self, rows)`**  
  Sets the number of rows in the model.

### FormulaLineEdit Class

- **`__init__(self, parent=None)`**  
  Initializes the formula line edit widget.

### ExcelTableView Class

- **`__init__(self, parent=None)`**  
  Initializes the Excel-like table view.

- **`editColumnHeader(self, section)`**  
  Edits the column header at the given section.

- **`mousePressEvent(self, event)`**  
  Handles mouse press events for selection.

---

## File: core.py

### AutoSaveManager Class

- **`__init__(self, parent=None, save_interval=TIMER_INTERVAL)`**  
  Initializes the auto-save manager with timer and directories.

- **`auto_save(self)`**  
  Creates backup files with current data and app settings.

- **`save_to_file(self, sub_state: dict, state: dict, filename_subs="./files/autosave_backup_subplots.json", filename="./files/autosave_backup_table.json")`**  
  Saves current state to files.

- **`load_backup(self, filename_subs="./files/sub_setting_final.json", filename="./files/settings_final.json", last_copy_subs="./files/autosave_backup_subplots.json", last_copy="./files/autosave_backup.json") -> tuple[dict, dict]`**  
  Loads backup files and returns application state.

---

## File: plot_manager.py

### SubplotCell Class

- **`__init__(self, row: int, col: int, parent=None) -> None`**  
  Initializes a grid cell.

- **`set_occupied(self, subplot_id: int, color: str) -> None`**  
  Marks this cell as occupied by a subplot.

### SubplotGrid Class

- **`__init__(self, parent=None) -> None`**  
  Initializes the grid display widget.

- **`__create_grid__(self, rows: int, cols: int) -> None`**  
  Creates grid that visualizes subplot positions.

- **`__clear_grid__(self) -> None`**  
  Clears the entire grid and removes all widgets.

- **`__add_subplot__(self, row: int, col: int, row_span: int, col_span: int, subplot_id: int) -> bool`**  
  Adds one subplot to the grid at specified position and size.

- **`__remove_subplot__(self, subplot_id: int) -> None`**  
  Removes the subplot from the grid.

- **`__update_subplot__(self, subplot_id: int, row: int, col: int, row_span: int, col_span: int) -> None`**  
  Updates a subplot's position and size.

### SubplotEditor Class

- **`__init__(self, parent=None) -> None`**  
  Initializes the subplot editor with default values and UI setup.

- **`__init_GridConfiguration(self, config_layout: QVBoxLayout) -> None`**  
  Initializes form for grid configuration.

- **`__init_CreationControl__(self, config_layout: QVBoxLayout) -> None`**  
  Initializes form for subplot position and size configuration.

- **`__init_EditingControl__(self, config_layout: QVBoxLayout) -> None`**  
  Initializes form with tabs for all subplot editing settings.

- **`__initUI__(self) -> None`**  
  Initializes the complete UI for the subplot editor window.

- **`__work_with_plot_signals__(self, sig)`**  
  Handles signals from the interactive plot canvas.

- **`update_column_data(self, headers: list[str]) -> None`**  
  Updates all combo boxes that contain headers from the table.

- **`__create_grid__(self) -> None`**  
  Creates a new grid based on row/column configuration.

- **`__handle_non_fitting_subplots__(self, non_fitting_subplots: list, current_subplots: list) -> None`**  
  Handles subplots that don't fit after grid resizing.

- **`__change_sub_pos__(self, base_info: list[int], subs: list, max_row: int, max_col: int) -> None`**  
  Calls SubplotPositionDialog to change subplot position.

- **`__add_subplot__(self) -> None`**  
  Adds a new subplot to the configuration.

- **`get_sub_id_select(self) -> None`**  
  Defines selected subplot id and loads subplot's properties.

- **`rectangles_overlap(self, rect1: tuple[int], rect2: tuple[int]) -> bool`**  
  Checks if two rectangles overlap.

- **`clear_subplots(self) -> None`**  
  Clears all subplots and resets the grid.

- **`update_subplot_list(self) -> None`**  
  Updates the subplot list widget with current subplot information.

- **`subplot_selected(self) -> None`**  
  Handles subplot selection from the list.

- **`select_subplot(self, plot_id) -> None`**  
  Selects a subplot and loads its properties into the editor.

- **`__add_subplot_lines(self, line_info) -> None`**  
  Adds lines to the lines tab for the selected subplot.

- **`__update_data_headers_spin__(self, data_series: dict) -> None`**  
  Updates all lists with data sets from subplot.

- **`clear_selection(self) -> None`**  
  Clears the current selection and disables editor controls.

- **`__update_subplot_position__(self) -> None`**  
  Updates the position and size of a subplot.

- **`__update_subplot_data__(self) -> None`**  
  Updates the data for a subplot.

- **`__update_sub_style__(self) -> None`**  
  Updates style properties for the subplot.

- **`__update_data_style__(self, index: str) -> None`**  
  Updates style properties for the subplot data.

- **`plot_graphs(self) -> None`**  
  Plots all subplots on the canvas.

- **`configure_data_series(self) -> None`**  
  Opens dialog to configure data series for subplots.

- **`add_data_series_subplot(self, series: list[dict], axes_info: dict, title_info: dict) -> None`**  
  Adds a new subplot with multiple data series to the configuration.

- **`__edit_data_series__(self)`**  
  Edits subplot data series by calling Data Series Dialog.

- **`find_first_nonzero_digit(self, number: int|float) -> int`**  
  Returns order of the first non zero digit.

- **`get_state(self) -> dict`**  
  Returns the current state to save.

- **`set_state(self, state: dict) -> None`**  
  Restores the state from the configuration.

- **`__add_line_to_subplot__(self, params=None) -> None`**  
  Adds a line to the selected subgraph.

- **`__work_with_lines_signals__(self, msg: str) -> None`**  
  Calls function regarding the signal.

- **`__work_with_sub_data_signals__(self, msg: str) -> None`**  
  Calls function regarding the signal.

- **`__update_lines_table__(self) -> None`**  
  Updates the table of existing lines.

- **`__delete_line__(self, line_index: int) -> None`**  
  Removes a line from a subgraph.

- **`__on_line_selected__(self, row: int) -> None`**  
  Fills in the signature fields when selecting a line.

- **`__add_label_to_line__(self, row: int) -> None`**  
  Adds or updates a signature for a selected line.

- **`__change_labels_params__(self, index: int) -> None`**  
  Changes label for selected line.

- **`__toggle_drawing_mode__(self, enabled: bool) -> None`**  
  Toggles line drawing mode on the plot canvas.

- **`__append_subplot__(self, plot_id: int, row: int, col: int, row_span: int, col_span: int, data_series: dict, sub_info: dict, line_info: list) -> None`**  
  Appends a new subplot to the internal data structure.

---

## File: subplotsEditors.py

### Overview
This file contains the UI components for styling and configuring subplots and data series in a matplotlib-based plotting application.

### Classes and Functions

#### DataStyleTab Class

- **`__init__(self, parent=None)`**  
  Initializes the data style tab.

- **`__init_style_tab_ui(self)`**  
  Initializes UI components for data styling.

- **`__data_styles_changed__(self)`**  
  Handles changes in data selection.

- **`choose_line_color(self)`**  
  Opens color dialog for line color selection.

- **`__update_data_style__(self)`**  
  Emits signal to update data style.

- **`__populate_controls__(self, data_series: dict)`**  
  Populates controls with data series information.

- **`__update_data_headers_spin__(self, data_series: dict, index: int)`**  
  Updates data headers in combo boxes.

- **`get_data_style_info(self)`**  
  Returns current data style settings.

- **`clear_selection(self)`**  
  Resets controls to default values.

- **`edit_line_style(self, line)`**  
  Enables interactive line editing.

#### SubplotStyleTab Class

- **`__init__(self, parent=None)`**  
  Initializes the subplot style tab.

- **`__init_subplot_style_tab_ui__(self)`**  
  Initializes UI components.

- **`__update_sub_style__(self)`**  
  Emits signal to update subplot style.

- **`__add_axes_group__(self)`**  
  Adds axes settings to the tree widget.

- **`__add_subplot_main_settings_group(self)`**  
  Adds main subplot settings.

- **`validate_x_limits(self)`**  
  Ensures X min < X max.

- **`validate_y_limits(self)`**  
  Ensures Y min < Y max.

- **`highlight_invalid(self, editor)`**  
  Highlights invalid input fields.

- **`reset_highlight(self, editor)`**  
  Removes highlight from fields.

- **`update_some_xAxis_states(self)`**  
  Updates X axis state when scale changes.

- **`update_some_yAxis_states(self)`**  
  Updates Y axis state when scale changes.

- **`__add_parameter__(self, parent, name, ptype, default, *args)`**  
  Adds parameter to tree widget.

- **`__set_new_axes_ranges__(self, axes_info: dict)`**  
  Sets new ranges for axis limits.

- **`get_sub_style_info(self)`**  
  Returns current subplot style settings.

- **`get_axes_info(self)`**  
  Returns current axes settings.

- **`get_title_info(self)`**  
  Returns current title settings.

- **`get_legend_info(self)`**  
  Returns current legend settings.

- **`get_grid_info(self)`**  
  Returns current grid settings.

- **`clear_selection(self)`**  
  Resets controls to default values.

- **`populate_control(self, sub_info: dict)`**  
  Populates controls with subplot properties.

#### LineStyleTab Class

- **`__init__(self, parent=None)`**  
  Initializes the line style tab.

- **`__init_line_style_tab_ui__(self)`**  
  Initializes UI components.

- **`update_line_params_ui(self)`**  
  Updates UI based on line creation method.

- **`choose_line_color(self)`**  
  Opens color dialog for line color.

- **`add_line_to_subplot(self)`**  
  Handles adding new line to subplot.

- **`update_lines_labels(self, line: dict)`**  
  Updates line labels.

- **`update_lines_table(self)`**  
  Updates table of existing lines.

- **`delete_line(self, line_index: int)`**  
  Removes line from subplot.

- **`__delete_line_label__(self, line_index: int)`**  
  Removes label options for deleted line.

- **`on_line_selected(self)`**  
  Handles line selection from table.

- **`add_label_to_line(self)`**  
  Adds/updates label for selected line.

- **`change_labels_params(self)`**  
  Handles label parameter changes.

- **`toggle_drawing_mode(self, enabled: bool)`**  
  Toggles interactive drawing mode.

#### PositioningChoosingDataTab Class

- **`__init__(self, parent=None)`**  
  Initializes the position/data tab.

- **`__init_pos_data_tab__(self)`**  
  Initializes UI components.

- **`__init_position_size_ui__(self)`**  
  Initializes position/size controls.

- **`__init_data_ui__(self)`**  
  Initializes data series controls.

- **`update_subplot_position(self)`**  
  Handles position/size updates.

- **`update_subplot_data(self)`**  
  Handles data series updates.

- **`edit_data_series(self)`**  
  Initiates data series editing.

- **`update_headers_column_data(self, headers: list[str])`**  
  Updates combo boxes with data headers.

- **`clear_selection(self)`**  
  Resets controls to default values.

- **`populate_control(self, row, col, row_span, col_span, data_series)`**  
  Populates controls with subplot properties.

---

## File: dialogs.py

### Overview
This file contains dialog windows for various configuration tasks in the plotting application.

### Classes and Functions

#### DataSeriesDialog Class

- **`__init__(self, headers: list[str], max_id=0, parent=None)`**  
  Initializes dialog.

- **`__init_dialog_window__(self)`**  
  Sets up dialog window properties.

- **`__init_dialog_ui__(self, headers: list[str], max_id=0)`**  
  Initializes UI components.

- **`__choose_color__(self)`**  
  Opens color selection dialog.

- **`__add_series__(self)`**  
  Adds new data series.

- **`__remove_series__(self)`**  
  Removes selected data series.

- **`get_series(self)`**  
  Returns all configured data series.

- **`get_axes_info(self)`**  
  Returns axes configuration info.

- **`get_title_info(self)`**  
  Returns title configuration info.

#### AxisConfigDialog Class

- **`__init__(self, axis_type, ax, subplot, parent=None)`**  
  Initializes dialog.

- **`__calculate_decimals__(self, value)`**  
  Calculates appropriate decimal places.

- **`find_first_nonzero_digit(self, number)`**  
  Finds order of first non-zero digit.

- **`__update_decimals__(self)`**  
  Updates decimals for min/max spinboxes.

- **`__init_dialog_ui__(self)`**  
  Initializes UI components.

- **`__accept_new_axes_info__(self)`**  
  Validates and applies new axis configuration.

- **`get_data(self)`**  
  Returns updated subplot configuration.

#### SubplotPositionDialog Class

- **`__init__(self, base_info, subs, max_row, max_col, parent=None)`**  
  Initializes dialog.

- **`__init_all_sub_config(self, subs, max_row, max_col, base_info)`**  
  Initializes configuration data.

- **`__init_dialog_window__(self)`**  
  Sets up dialog window.

- **`__init_dialog_ui__(self)`**  
  Initializes UI components.

- **`__validate_col__(self)`**  
  Validates column position and span.

- **`__validate_row__(self)`**  
  Validates row position and span.

- **`__rectangles_overlap__(self, rect1, rect2)`**  
  Checks if rectangles overlap.

- **`validate_ovelaps(self)`**  
  Checks for subplot overlaps.

- **`validate_input(self)`**  
  Validates all input data.

- **`get_data(self)`**  
  Returns new position/size data.

#### Additional Dialog Classes

- **`LegendConfigDialog`**  
  Dialog for legend configuration.

- **`TitleConfigDialog`**  
  Dialog for title configuration.

- **`GridConfigDialog`**  
  Dialog for grid configuration.

- **`LineLabelDialog`**  
  Dialog for line label configuration.

- **`DataStyleDialog`**  
  Dialog for data series style editing.

---

## File: interactive_plot.py

### Overview
This file contains the interactive plotting canvas with click handling capabilities.

### Classes and Functions

#### INTERACTIVE_PLOT Class

- **`__init__(self, parent=None, width=5, height=4, dpi=100, data=[])`**  
  Initializes canvas.

- **`on_click(self, event)`**  
  Handles mouse click events.

- **`find_closest_point(self, event, ax)`**  
  Finds data point closest to click.

- **`find_subplot(self, id)`**  
  Finds subplot by ID.

- **`find_series(self, subplot, series_id)`**  
  Finds data series by ID.

- **`edit_data_style(self, subplot_idx, series_idx)`**  
  Opens data style editor.

- **`on_pick(self, event)`**  
  Handles line selection events.

- **`show_context_menu(self, event, ax, subplot, sub_id)`**  
  Shows context menu.

- **`toggle_grid(self, ax, subplot, sub_id)`**  
  Toggles grid visibility.

- **`edit_legend(self, ax, subplot, sub_id)`**  
  Edits legend properties.

- **`edit_title(self, ax, subplot, sub_id)`**  
  Edits title properties.

- **`plot_all_data(self, win, rows, cols)`**  
  Generates plot based on configuration.

- **`update_one_plot(self, subplot, win)`**  
  Updates and redraws a single subplot.

- **`draw_line(self, params, ax=None)`**  
  Draws line on graph.

- **`add_line_label(self, ax, line, params)`**  
  Adds label to line.

- **`toggle_drawing_mode(self, enabled)`**  
  Toggles line drawing mode.

- **`on_motion(self, event)`**  
  Handles mouse movement during drawing.

- **`finish_line(self, end_point)`**  
  Finalizes drawn line.

- **`open_label_dialog(self, line, mid_point, ax)`**  
  Opens label configuration dialog.

- **`is_click_on_title(self, event, ax)`**  
  Checks if click was on title.

- **`handle_title_click(self, ax)`**  
  Handles title click events.

- **`on_mouse_move(self, event)`**  
  Handles mouse movement for point detection.

- **`get_point_near_cursor(self, event, line)`**  
  Finds point nearest to cursor.

- **`show_context_menu_point(self, event, line, x, y)`**  
  Shows context menu for point.

- **`hide_context_menu(self)`**  
  Hides context menu.

- **`on_mouse_release(self, event)`**  
  Handles mouse release events.

- **`show_data_context_menu(self, event, line, x, y, series_id)`**  
  Shows data context menu.