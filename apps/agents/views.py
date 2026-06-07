from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Agent


@login_required
def agent_list(request):
    query  = request.GET.get('q', '')
    agents = Agent.objects.filter(is_deleted=False).order_by('-created_at')

    if query:
        agents = agents.filter(name__icontains=query) | \
                 agents.filter(phone__icontains=query) | \
                 agents.filter(cnic__icontains=query)

    return render(request, 'agents/agent_list.html', {
        'agents': agents,
        'query':  query,
    })


@login_required
def agent_add(request):
    if request.method == 'POST':
        Agent.objects.create(
            name       = request.POST.get('name'),
            name_urdu  = request.POST.get('name_urdu', ''),
            phone      = request.POST.get('phone'),
            cnic       = request.POST.get('cnic', ''),
            address    = request.POST.get('address', ''),
            city       = request.POST.get('city', ''),
            created_by = request.user,
        )
        messages.success(request, 'Agent added successfully.')
        return redirect('agents:agent_list')

    return render(request, 'agents/agent_form.html', {
        'title': 'Add Agent'
    })


@login_required
def agent_edit(request, pk):
    agent = get_object_or_404(Agent, pk=pk, is_deleted=False)

    if request.method == 'POST':
        agent.name      = request.POST.get('name')
        agent.name_urdu = request.POST.get('name_urdu', '')
        agent.phone     = request.POST.get('phone')
        agent.cnic      = request.POST.get('cnic', '')
        agent.address   = request.POST.get('address', '')
        agent.city      = request.POST.get('city', '')
        agent.save()
        messages.success(request, 'Agent updated.')
        return redirect('agents:agent_list')

    return render(request, 'agents/agent_form.html', {
        'agent': agent,
        'title': 'Edit Agent',
    })


@login_required
def agent_delete(request, pk):
    agent = get_object_or_404(Agent, pk=pk, is_deleted=False)
    agent.is_deleted = True
    agent.save()
    messages.success(request, 'Agent deleted.')
    return redirect('agents:agent_list')