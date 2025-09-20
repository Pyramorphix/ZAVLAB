class ThemeManager:
    """Centralized theme management for the application"""

    # Styles
    STYLESHEET_TEMPLATE = """
        QSplitter::handle:horizontal {{
            background-color: {handle_color};
            border: 1px solid {border_color};
            margin: 0px;
            height: 12px;
        }}
        
        QSplitter::handle:horizontal:hover {{
            background-color: {hover_color};
            border: 1px solid {hover_border_color};
        }}
    """
    
    # Theme colors
    THEMES = {
        'default': {
            'name': 'Default theme',
            'handle_color': '#cccccc',
            'border_color': '#bbbbbb',
            'hover_color': '#999999',
            'hover_border_color': '#777777'
        }
    }
    

    @classmethod
    def get_available_themes(cls) -> dict[str, str]:
        """Get list of available themes"""
        
        # return dict like {'default': 'Default theme', ...}
        return {theme_id: theme['name'] for theme_id, theme in cls.THEMES.items()}


    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        """Generate stylesheet by filling template with theme colors."""

        colors = cls.THEME_COLORS.get(theme_name, cls.THEMES['default'])
#                                     \________/  \___________________/
#                                     User input      Default value  

        return cls.STYLESHEET_TEMPLATE.format(**colors)