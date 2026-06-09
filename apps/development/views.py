from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Town, Block, Plot, TownMap, PlotCoordinate
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage



# ======================================================
# TOWNS
# ======================================================

@login_required
def town_list(request):
    towns = Town.objects.filter(is_deleted=False).order_by('-created_at')
    return render(request, 'development/town_list.html', {'towns': towns})


@login_required
@login_required
def town_add(request):
    from apps.land.models import LandContract
    contracts = LandContract.objects.filter(
        is_deleted=False,
        status='ACTIVE',
    ).select_related('landlord')

    if request.method == 'POST':
        contract_pk   = request.POST.get('land_contract')
        land_contract = None
        if contract_pk:
            land_contract = LandContract.objects.filter(
                pk=contract_pk,
                is_deleted=False,
                status='ACTIVE',
            ).first()
            if not land_contract:
                messages.error(request, 'Selected land contract is invalid.')
                return render(request, 'development/town_form.html', {
                    'contracts': contracts,
                    'title':     'Add Town',
                })

        town = Town.objects.create(
            name          = request.POST.get('name'),
            name_urdu     = request.POST.get('name_urdu', ''),
            land_contract = land_contract,
            location      = request.POST.get('location', ''),
            total_area    = request.POST.get('total_area') or None,
            description   = request.POST.get('description', ''),
            created_by    = request.user,
        )

        # ── Handle town image upload ──────────────────
        town_image = request.FILES.get('town_image')
        if town_image:
            from apps.development.models import TownMap
            TownMap.objects.create(
                town          = town,
                title         = f"{town.name} — Main Image",
                map_type      = 'IMAGE',
                map_file      = town_image,
                display_order = 0,
                is_active     = True,
                created_by    = request.user,
            )

        messages.success(request, 'Town added successfully.')
        return redirect('development:town_list')

    return render(request, 'development/town_form.html', {
        'contracts': contracts,
        'title':     'Add Town',
    })


@login_required
@login_required
def town_edit(request, pk):
    from apps.land.models import LandContract
    town      = get_object_or_404(Town, pk=pk, is_deleted=False)
    contracts = LandContract.objects.filter(
        is_deleted=False,
        status='ACTIVE',
    ).select_related('landlord')

    # Get existing main image
    existing_image = town.maps.filter(
        map_type='IMAGE',
        is_active=True
    ).first()

    if request.method == 'POST':
        contract_pk   = request.POST.get('land_contract')
        land_contract = None
        if contract_pk:
            land_contract = LandContract.objects.filter(
                pk=contract_pk,
                is_deleted=False,
                status='ACTIVE',
            ).first()
            if not land_contract:
                messages.error(request, 'Selected land contract is invalid.')
                return render(request, 'development/town_form.html', {
                    'town':           town,
                    'contracts':      contracts,
                    'existing_image': existing_image,
                    'title':          'Edit Town',
                })

        town.name          = request.POST.get('name')
        town.name_urdu     = request.POST.get('name_urdu', '')
        town.land_contract = land_contract
        town.location      = request.POST.get('location', '')
        town.total_area    = request.POST.get('total_area') or None
        town.description   = request.POST.get('description', '')
        town.save()

        # ── Handle town image upload ──────────────────
        town_image = request.FILES.get('town_image')
        if town_image:
            from apps.development.models import TownMap
            if existing_image:
                # Replace existing image
                existing_image.map_file = town_image
                existing_image.save()
            else:
                # Create new
                TownMap.objects.create(
                    town          = town,
                    title         = f"{town.name} — Main Image",
                    map_type      = 'IMAGE',
                    map_file      = town_image,
                    display_order = 0,
                    is_active     = True,
                    created_by    = request.user,
                )

        messages.success(request, 'Town updated.')
        return redirect('development:town_list')

    return render(request, 'development/town_form.html', {
        'town':           town,
        'contracts':      contracts,
        'existing_image': existing_image,
        'title':          'Edit Town',
    })


@login_required
def town_delete(request, pk):
    town            = get_object_or_404(Town, pk=pk)
    town.is_deleted = True
    town.save()
    messages.success(request, 'Town deleted.')
    return redirect('development:town_list')


# ======================================================
# BLOCKS
# ======================================================

@login_required
def block_list(request):
    town_id = request.GET.get('town')
    towns   = Town.objects.filter(is_deleted=False).order_by('name')
    blocks  = Block.objects.filter(is_deleted=False).order_by('town', 'name')

    if town_id:
        blocks = blocks.filter(town_id=town_id)

    return render(request, 'development/block_list.html', {
        'blocks':        blocks,
        'towns':         towns,
        'selected_town': town_id,
    })


@login_required
def block_add(request):
    towns = Town.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        town = get_object_or_404(Town, pk=request.POST.get('town'))
        Block.objects.create(
            town        = town,
            name        = request.POST.get('name'),
            name_urdu   = request.POST.get('name_urdu', ''),
            total_plots = request.POST.get('total_plots', 0),
            description = request.POST.get('description', ''),
            created_by  = request.user,
        )
        messages.success(request, 'Block added successfully.')
        return redirect('development:block_list')

    return render(request, 'development/block_form.html', {
        'towns': towns,
        'title': 'Add Block',
    })


@login_required
def block_edit(request, pk):
    block = get_object_or_404(Block, pk=pk, is_deleted=False)
    towns = Town.objects.filter(is_deleted=False).order_by('name')

    if request.method == 'POST':
        block.town        = get_object_or_404(Town, pk=request.POST.get('town'))
        block.name        = request.POST.get('name')
        block.name_urdu   = request.POST.get('name_urdu', '')
        block.total_plots = request.POST.get('total_plots', 0)
        block.description = request.POST.get('description', '')
        block.save()
        messages.success(request, 'Block updated.')
        return redirect('development:block_list')

    return render(request, 'development/block_form.html', {
        'block': block,
        'towns': towns,
        'title': 'Edit Block',
    })


@login_required
def block_delete(request, pk):
    block            = get_object_or_404(Block, pk=pk)
    block.is_deleted = True
    block.save()
    messages.success(request, 'Block deleted.')
    return redirect('development:block_list')


# ======================================================
# PLOTS
# ======================================================

@login_required
def plot_list(request):
    block_id = request.GET.get('block')
    town_id  = request.GET.get('town')
    status   = request.GET.get('status')

    towns      = Town.objects.filter(is_deleted=False).order_by('name')
    blocks     = Block.objects.filter(is_deleted=False).order_by('town', 'name')
    plots      = Plot.objects.filter(is_deleted=False).select_related('block__town')
    base_plots = Plot.objects.filter(is_deleted=False)

    if town_id:
        plots      = plots.filter(block__town_id=town_id)
        blocks     = blocks.filter(town_id=town_id)
        base_plots = base_plots.filter(block__town_id=town_id)
    if block_id:
        plots      = plots.filter(block_id=block_id)
        base_plots = base_plots.filter(block_id=block_id)
    if status:
        plots = plots.filter(status=status)

    status_counts = {}
    for val, label in Plot.STATUS_CHOICES:
        status_counts[val] = base_plots.filter(status=val).count()

    return render(request, 'development/plot_list.html', {
        'plots':           plots,
        'towns':           towns,
        'blocks':          blocks,
        'selected_town':   town_id,
        'selected_block':  block_id,
        'selected_status': status,
        'status_choices':  Plot.STATUS_CHOICES,
        'status_counts':   status_counts,
    })


@login_required
def plot_add(request):
    blocks = Block.objects.filter(
        is_deleted=False
    ).select_related('town').order_by('town__name', 'name')

    if request.method == 'POST':
        block = get_object_or_404(Block, pk=request.POST.get('block'))
        Plot.objects.create(
            block      = block,
            plot_no    = request.POST.get('plot_no'),
            size       = request.POST.get('size'),
            size_unit  = request.POST.get('size_unit', 'MARLA'),
            plot_type  = request.POST.get('plot_type', 'RESIDENTIAL'),
            price      = request.POST.get('price'),
            status     = request.POST.get('status', 'AVAILABLE'),
            notes      = request.POST.get('notes', ''),
            created_by = request.user,
        )
        messages.success(request, 'Plot added successfully.')
        return redirect('development:plot_list')

    return render(request, 'development/plot_form.html', {
        'blocks': blocks,
        'title':  'Add Plot',
    })


@login_required
def plot_edit(request, pk):
    plot   = get_object_or_404(Plot, pk=pk, is_deleted=False)
    blocks = Block.objects.filter(
        is_deleted=False
    ).select_related('town').order_by('town__name', 'name')

    if request.method == 'POST':
        plot.block     = get_object_or_404(Block, pk=request.POST.get('block'))
        plot.plot_no   = request.POST.get('plot_no')
        plot.size      = request.POST.get('size')
        plot.size_unit = request.POST.get('size_unit', 'MARLA')
        plot.plot_type = request.POST.get('plot_type', 'RESIDENTIAL')
        plot.price     = request.POST.get('price')
        plot.status    = request.POST.get('status', 'AVAILABLE')
        plot.notes     = request.POST.get('notes', '')
        plot.save()
        messages.success(request, 'Plot updated.')
        return redirect('development:plot_list')

    return render(request, 'development/plot_form.html', {
        'plot':   plot,
        'blocks': blocks,
        'title':  'Edit Plot',
    })


@login_required
def plot_delete(request, pk):
    plot = get_object_or_404(Plot, pk=pk, is_deleted=False)

    if plot.status in ('BOOKED', 'SOLD'):
        messages.error(request, 'Cannot delete a booked or sold plot.')
        return redirect('development:plot_list')

    plot.is_deleted = True
    plot.save()
    messages.success(request, 'Plot deleted.')
    return redirect('development:plot_list')


# ======================================================
# TOWN MAP VIEWS
# ======================================================

@login_required
def map_list(request, town_pk):
    town = get_object_or_404(Town, pk=town_pk)
    maps = TownMap.objects.filter(town=town).select_related('block')
    return render(request, 'development/map_list.html', {
        'town': town,
        'maps': maps,
    })


@login_required
def map_upload(request, town_pk):
    town   = get_object_or_404(Town, pk=town_pk)
    blocks = Block.objects.filter(town=town, is_deleted=False).order_by('name')

    if request.method == 'POST':
        title         = request.POST.get('title', '').strip()
        map_type      = request.POST.get('map_type', 'IMAGE')
        block_id      = request.POST.get('block', '')
        display_order = request.POST.get('display_order', 0)
        map_file      = request.FILES.get('map_file')

        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'development/map_upload.html', {
                'town': town, 'blocks': blocks
            })

        if not map_file:
            messages.error(request, 'Please select a file to upload.')
            return render(request, 'development/map_upload.html', {
                'town': town, 'blocks': blocks
            })

        fname = map_file.name.lower()
        if map_type == 'IMAGE' and not (
            fname.endswith('.jpg') or
            fname.endswith('.jpeg') or
            fname.endswith('.png')
        ):
            messages.error(request, 'Image maps must be JPG or PNG.')
            return render(request, 'development/map_upload.html', {
                'town': town, 'blocks': blocks
            })

        if map_type == 'PDF' and not fname.endswith('.pdf'):
            messages.error(request, 'PDF maps must be .pdf files.')
            return render(request, 'development/map_upload.html', {
                'town': town, 'blocks': blocks
            })

        block = Block.objects.filter(pk=block_id).first() if block_id else None

        TownMap.objects.create(
            town          = town,
            block         = block,
            title         = title,
            map_type      = map_type,
            map_file      = map_file,
            display_order = display_order or 0,
            is_active     = True,
            created_by    = request.user,
        )

        messages.success(request, f'Map "{title}" uploaded successfully.')
        return redirect('development:map_list', town_pk=town.pk)

    return render(request, 'development/map_upload.html', {
        'town':   town,
        'blocks': blocks,
    })


@login_required
def map_edit(request, pk):
    town_map = get_object_or_404(TownMap, pk=pk)
    town     = town_map.town
    blocks   = Block.objects.filter(town=town, is_deleted=False).order_by('name')

    if request.method == 'POST':
        town_map.title         = request.POST.get('title', town_map.title).strip()
        town_map.display_order = request.POST.get('display_order', 0)
        town_map.is_active     = request.POST.get('is_active') == 'on'
        block_id               = request.POST.get('block', '')
        town_map.block         = Block.objects.filter(pk=block_id).first() if block_id else None

        new_file = request.FILES.get('map_file')
        if new_file:
            town_map.map_file = new_file

        town_map.save()
        messages.success(request, 'Map updated successfully.')
        return redirect('development:map_list', town_pk=town.pk)

    return render(request, 'development/map_edit.html', {
        'town_map': town_map,
        'town':     town,
        'blocks':   blocks,
    })


@login_required
def map_delete(request, pk):
    town_map = get_object_or_404(TownMap, pk=pk)
    town_pk  = town_map.town.pk

    if request.method == 'POST':
        town_map.map_file.delete(save=False)
        town_map.delete()
        messages.success(request, 'Map deleted.')
        return redirect('development:map_list', town_pk=town_pk)

    return render(request, 'development/map_confirm_delete.html', {
        'town_map': town_map,
    })


@login_required
def map_toggle(request, pk):
    town_map           = get_object_or_404(TownMap, pk=pk)
    town_map.is_active = not town_map.is_active
    town_map.save()
    status = 'activated' if town_map.is_active else 'deactivated'
    messages.success(request, f'Map {status}.')
    return redirect('development:map_list', town_pk=town_map.town.pk)


# ======================================================
# MAP EDITOR (SUPERUSER ONLY)
# ======================================================

@login_required
def map_editor(request, pk):
    if request.user.role != 'SUPERUSER':
        messages.error(request, 'Access denied. Superuser only.')
        return redirect('development:map_list',
                        town_pk=TownMap.objects.get(pk=pk).town.pk)

    town_map = get_object_or_404(TownMap, pk=pk)
    town     = town_map.town

    if town_map.block:
        plots = Plot.objects.filter(
            block=town_map.block,
            is_deleted=False
        ).order_by('plot_no')
    else:
        plots = Plot.objects.filter(
            block__town=town,
            is_deleted=False
        ).select_related('block').order_by('block__name', 'plot_no')

    existing = PlotCoordinate.objects.filter(
        town_map=town_map
    ).select_related('plot')

    coords_data = []
    for c in existing:
        coords_data.append({
            'id':          c.pk,
            'plot_id':     c.plot.pk,
            'plot_no':     c.plot.plot_no,
            'plot_status': c.plot.status,
            'coordinates': c.coordinates,
        })

    marked_plot_ids = [c.plot.pk for c in existing]

    return render(request, 'development/map_editor.html', {
        'town_map':        town_map,
        'town':            town,
        'plots':           plots,
        'coords_json':     json.dumps(coords_data),
        'marked_plot_ids': marked_plot_ids,
    })


@login_required
@require_POST
def map_save_coordinate(request, map_pk):
    if request.user.role != 'SUPERUSER':
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        data        = json.loads(request.body)
        plot_id     = data.get('plot_id')
        coordinates = data.get('coordinates')

        if not plot_id or not coordinates:
            return JsonResponse(
                {'error': 'plot_id and coordinates required'}, status=400)

        town_map = get_object_or_404(TownMap, pk=map_pk)
        plot     = get_object_or_404(Plot, pk=plot_id)

        coord, created = PlotCoordinate.objects.update_or_create(
            town_map = town_map,
            plot     = plot,
            defaults = {
                'coordinates': coordinates,
                'created_by':  request.user,
            }
        )

        return JsonResponse({
            'success': True,
            'id':      coord.pk,
            'plot_no': plot.plot_no,
            'created': created,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def map_delete_coordinate(request, coord_pk):
    if request.user.role != 'SUPERUSER':
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        coord   = get_object_or_404(PlotCoordinate, pk=coord_pk)
        plot_no = coord.plot.plot_no
        coord.delete()
        return JsonResponse({'success': True, 'plot_no': plot_no})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def map_get_coordinates(request, map_pk):
    town_map = get_object_or_404(TownMap, pk=map_pk)
    existing = PlotCoordinate.objects.filter(
        town_map=town_map
    ).select_related('plot')

    coords_data = []
    for c in existing:
        coords_data.append({
            'id':          c.pk,
            'plot_id':     c.plot.pk,
            'plot_no':     c.plot.plot_no,
            'plot_status': c.plot.status,
            'size':        str(c.plot.size),
            'size_unit':   c.plot.size_unit,
            'plot_type':   c.plot.type,
            'price':       str(c.plot.price),
            'coordinates': c.coordinates,
        })

    return JsonResponse({'coordinates': coords_data})


# ======================================================
# MAP VIEWER
# ======================================================

@login_required
def map_viewer(request, pk):
    town_map = get_object_or_404(TownMap, pk=pk)
    return render(request, 'development/map_viewer.html', {
        'town_map': town_map,
    })


# ======================================================
# PDF MAP VIEWER
# ======================================================

@login_required
def map_pdf_viewer(request, pk):
    town_map = get_object_or_404(TownMap, pk=pk)
    if not town_map.is_pdf:
        messages.error(request, 'This map is not a PDF.')
        return redirect('development:map_viewer', pk=pk)
    return render(request, 'development/map_pdf_viewer.html', {
        'town_map': town_map,
    })

@login_required
def plot_bulk_add(request):
    blocks = Block.objects.filter(
        is_deleted=False
    ).select_related('town').order_by('town__name', 'name')

    if request.method == 'POST':
        import json
        plots_data = request.POST.get('plots_json', '[]')
        try:
            plots_list = json.loads(plots_data)
        except Exception:
            messages.error(request, 'Invalid data submitted.')
            return redirect('development:plot_bulk_add')

        created = 0
        errors = []
        for i, p in enumerate(plots_list):
            try:
                block = Block.objects.get(pk=p['block'])
                Plot.objects.create(
                    block      = block,
                    plot_no    = p['plot_no'],
                    size       = p['size'],
                    size_unit  = p.get('size_unit', 'MARLA'),
                    plot_type  = p.get('plot_type', 'RESIDENTIAL'),
                    price      = p['price'],
                    status     = p.get('status', 'AVAILABLE'),
                    notes      = p.get('notes', ''),
                    created_by = request.user,
                )
                created += 1
            except Exception as e:
                errors.append(f"Row {i+1} ({p.get('plot_no','?')}): {str(e)}")

        if errors:
            for err in errors:
                messages.error(request, err)
        if created:
            messages.success(request, f'{created} plot(s) saved successfully.')
        return redirect('development:plot_list')

    return render(request, 'development/plot_bulk_add.html', {
        'blocks': blocks,
        'title':  'Bulk Add Plots',
    })

@login_required
def check_plot_availability(request):
    plot_no  = request.GET.get('plot_no', '').strip()
    block_id = request.GET.get('block_id', '').strip()
    plot_pk  = request.GET.get('plot_pk', '').strip()  # for edit mode exclusion

    if not plot_no or not block_id:
        return JsonResponse({'available': True, 'plot': None})

    qs = Plot.objects.filter(
        plot_no__iexact=plot_no,
        block_id=block_id,
        is_deleted=False,
    )

    if plot_pk:
        qs = qs.exclude(pk=plot_pk)

    existing = qs.select_related('block__town').first()

    if existing:
        return JsonResponse({
            'available': False,
            'plot': {
                'plot_no':   existing.plot_no,
                'block':     existing.block.name,
                'town':      existing.block.town.name,
                'size':      str(existing.size),
                'size_unit': existing.size_unit,
                'plot_type': existing.get_plot_type_display(),
                'price':     str(existing.price),
                'status':    existing.status,
            }
        })

    return JsonResponse({'available': True, 'plot': None})

@login_required
def check_town_name(request):
    name     = request.GET.get('name', '').strip()
    town_pk  = request.GET.get('town_pk', '').strip()

    if not name:
        return JsonResponse({'available': True, 'town': None})

    qs = Town.objects.filter(name__iexact=name, is_deleted=False)

    if town_pk:
        qs = qs.exclude(pk=town_pk)

    existing = qs.first()

    if existing:
        return JsonResponse({
            'available': False,
            'town': {
                'name':     existing.name,
                'location': existing.location or '—',
                'blocks':   existing.blocks.filter(is_deleted=False).count(),
            }
        })

    return JsonResponse({'available': True, 'town': None})

@login_required
def check_block_name(request):
    name     = request.GET.get('name', '').strip()
    town_id  = request.GET.get('town_id', '').strip()
    block_pk = request.GET.get('block_pk', '').strip()

    if not name or not town_id:
        return JsonResponse({'available': True, 'block': None})

    qs = Block.objects.filter(
        name__iexact=name,
        town_id=town_id,
        is_deleted=False
    )

    if block_pk:
        qs = qs.exclude(pk=block_pk)

    existing = qs.select_related('town').first()

    if existing:
        return JsonResponse({
            'available': False,
            'block': {
                'name':        existing.name,
                'town':        existing.town.name,
                'total_plots': existing.total_plots,
                'available':   existing.available_plots,
                'sold':        existing.sold_plots,
            }
        })

    return JsonResponse({'available': True, 'block': None})