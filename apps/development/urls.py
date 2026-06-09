from django.urls import path
from . import views

app_name = 'development'

urlpatterns = [

    # ── Towns ──────────────────────────────────────────
    path('towns/',
         views.town_list,
         name='town_list'),
    path('towns/add/',
         views.town_add,
         name='town_add'),
    path('towns/<int:pk>/edit/',
         views.town_edit,
         name='town_edit'),
    path('towns/<int:pk>/delete/',
         views.town_delete,
         name='town_delete'),

    # ── Blocks ─────────────────────────────────────────
    path('blocks/',
         views.block_list,
         name='block_list'),
    path('blocks/add/',
         views.block_add,
         name='block_add'),
    path('blocks/<int:pk>/edit/',
         views.block_edit,
         name='block_edit'),
    path('blocks/<int:pk>/delete/',
         views.block_delete,
         name='block_delete'),

    # ── Plots ──────────────────────────────────────────
    path('plots/',
         views.plot_list,
         name='plot_list'),
    path('plots/add/',
         views.plot_add,
         name='plot_add'),
    path('plots/<int:pk>/edit/',
         views.plot_edit,
         name='plot_edit'),
    path('plots/<int:pk>/delete/',
         views.plot_delete,
         name='plot_delete'),

    # ── Town Maps ──────────────────────────────────────
    path('towns/<int:town_pk>/maps/',
         views.map_list,
         name='map_list'),
    path('towns/<int:town_pk>/maps/upload/',
         views.map_upload,
         name='map_upload'),
    path('maps/<int:pk>/edit/',
         views.map_edit,
         name='map_edit'),
    path('maps/<int:pk>/delete/',
         views.map_delete,
         name='map_delete'),
    path('maps/<int:pk>/toggle/',
         views.map_toggle,
         name='map_toggle'),

    # ── Map Editor ─────────────────────────────────────
    path('maps/<int:pk>/editor/',
         views.map_editor,
         name='map_editor'),
    path('maps/<int:map_pk>/coordinates/save/',
         views.map_save_coordinate,
         name='map_save_coordinate'),
    path('maps/coordinates/<int:coord_pk>/delete/',
         views.map_delete_coordinate,
         name='map_delete_coordinate'),
    path('maps/<int:map_pk>/coordinates/',
         views.map_get_coordinates,
         name='map_get_coordinates'),

    # ── Map Viewer ─────────────────────────────────────
    path('maps/<int:pk>/viewer/',
         views.map_viewer,
         name='map_viewer'),

    # ── PDF Map Viewer ──────────────────────────────────
    path('maps/<int:pk>/pdf-viewer/',
         views.map_pdf_viewer,
         name='map_pdf_viewer'),
     
     path('plots/bulk-add/',
     views.plot_bulk_add,
     name='plot_bulk_add'),
     # ── Plot Availability Check ─────────────────────────
    path('plots/check-availability/',
         views.check_plot_availability,
         name='check_plot_availability'),
         # ── Town Name Availability Check ────────────────────
    path('towns/check-name/',
         views.check_town_name,
         name='check_town_name'),

     # ── Block Name Availability Check ───────────────────
    path('blocks/check-name/',
         views.check_block_name,
         name='check_block_name'),

]