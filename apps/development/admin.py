from django.contrib import admin
from .models import Town, Block, Plot


# ======================================================
# TOWN
# ======================================================

@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display    = ('name', 'name_urdu', 'location', 'created_at')
    search_fields   = ('name', 'name_urdu', 'location')
    list_filter     = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


# ======================================================
# BLOCK
# ======================================================

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display    = ('name', 'town', 'total_plots', 'available_plots', 'created_at')
    search_fields   = ('name', 'town__name')
    list_filter     = ('town', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


# ======================================================
# PLOT
# ======================================================

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display    = ('plot_no', 'block', 'size', 'size_unit',
                       'plot_type', 'price', 'status', 'created_at')
    search_fields   = ('plot_no', 'block__name', 'block__town__name')
    list_filter     = ('status', 'plot_type', 'size_unit', 'block__town')
    readonly_fields = ('created_at', 'updated_at')