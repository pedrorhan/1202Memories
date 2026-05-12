from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from .models import Entry, Emotion, Milestone
from .utils import process_and_convert_image_to_webp
from datetime import date, datetime

from django.contrib.auth.models import User

@login_required
def timeline(request):
    # GEÇİCİ: Admin oluşturma (Shell erişimi olmadığı için)
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
    
    emotion_id = request.GET.get('emotion')
    
    pinned_qs = Entry.objects.filter(is_icebreaker=True, is_acknowledged=False).select_related('author', 'category', 'emotion')
    entries_qs = Entry.objects.select_related('author', 'category', 'emotion')
    
    if emotion_id:
        pinned_qs = pinned_qs.filter(emotion_id=emotion_id)
        entries_qs = entries_qs.filter(emotion_id=emotion_id)
        
    entries_qs = entries_qs.exclude(id__in=pinned_qs.values_list('id', flat=True))
    
    paginator = Paginator(entries_qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    emotions = Emotion.objects.all()
    
    today = date.today()
    todays_milestone = Milestone.objects.filter(date__month=today.month, date__day=today.day).first()
    
    context = {
        'page_obj': page_obj,
        'pinned_entries': pinned_qs if page_obj.number == 1 else None,
        'emotions': emotions,
        'current_emotion': int(emotion_id) if emotion_id else None,
        'todays_milestone': todays_milestone if page_obj.number == 1 else None
    }
    
    if request.htmx:
        if int(page_number) > 1:
            return render(request, 'core/partials/entry_list.html', context)
        return render(request, 'core/partials/entry_list_combined.html', context)
        
    return render(request, 'core/timeline.html', context)

@login_required
def add_entry(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image_file = request.FILES.get('image')
        is_icebreaker = request.POST.get('is_icebreaker') == 'on'
        emotion_id = request.POST.get('emotion')
        
        if content or image_file:
            entry = Entry(author=request.user, content=content, is_icebreaker=is_icebreaker)
            if emotion_id:
                entry.emotion_id = emotion_id
            
            if image_file:
                webp_image = process_and_convert_image_to_webp(image_file)
                if webp_image:
                    entry.image = webp_image
                else:
                    # Return a 400 Bad Request error if image processing fails
                    return HttpResponse("Geçersiz resim formatı. Lütfen geçerli bir resim dosyası yükleyin.", status=400)
            
            entry.save()
    
    # Yeni eklendikten sonra her halükarda sadece ilk sayfayı render edelim (HTMX update)
    pinned_entries = Entry.objects.filter(is_icebreaker=True, is_acknowledged=False).select_related('author', 'category')
    entries_list = Entry.objects.exclude(id__in=pinned_entries.values_list('id', flat=True)).select_related('author', 'category')
    paginator = Paginator(entries_list, 10)
    page_obj = paginator.get_page(1)
    
    if request.htmx:
        # Since add_entry targets #timeline-entries, we should render both pinned and the list
        context = {'page_obj': page_obj, 'pinned_entries': pinned_entries}
        # To make it easy without writing a new template, we can just return the timeline template content without base, 
        # but HTMX is replacing #timeline-entries innerHTML. 
        # Actually, let's create a combined response or handle it in a template.
        # For now, let's return timeline.html (with layout? No, that's outer).
        # We need to return the pinned + list.
        return render(request, 'core/partials/entry_list_combined.html', context)
    return redirect('core:timeline')

@login_required
def toggle_acknowledge(request, entry_id):
    if request.method == 'POST':
        try:
            entry = Entry.objects.get(id=entry_id)
            # Sadece kendi postu olmayanları onaylayabilir
            if entry.author != request.user:
                entry.is_acknowledged = not entry.is_acknowledged
                entry.save()
            
            if request.htmx:
                return render(request, 'core/partials/entry_single.html', {'entry': entry})
        except Entry.DoesNotExist:
            pass
            
    return redirect('core:timeline')

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    
    # Güvenlik ve Mühürleme Kontrolü
    if entry.author != request.user:
        return HttpResponseForbidden("Bu işlem için yetkiniz yok.")
    if entry.is_acknowledged:
        return HttpResponseForbidden("Bu gönderi karşı tarafça okunduğu için mühürlenmiştir ve değiştirilemez.")
        
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            entry.content = content
            entry.save()
            if request.htmx:
                return render(request, 'core/partials/entry_single.html', {'entry': entry})
        return redirect('core:timeline')
        
    # GET isteği - Düzenleme formunu getir
    if request.htmx:
        return render(request, 'core/partials/entry_edit.html', {'entry': entry})
    return redirect('core:timeline')

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    
    # Güvenlik ve Mühürleme Kontrolü
    if entry.author != request.user:
        return HttpResponseForbidden("Bu işlem için yetkiniz yok.")
    if entry.is_acknowledged:
        return HttpResponseForbidden("Bu gönderi mühürlenmiştir, silinemez.")
        
    if request.method == 'POST' or request.method == 'DELETE':
        entry.delete()
        if request.htmx:
            return HttpResponse("") # Empty string removes the element if hx-swap is outerHTML
    return redirect('core:timeline')

@login_required
def get_entry(request, entry_id):
    """Returns the single entry HTML (used for canceling an edit)"""
    entry = get_object_or_404(Entry, id=entry_id)
    if request.htmx:
        return render(request, 'core/partials/entry_single.html', {'entry': entry})
    return redirect('core:timeline')

@login_required
def milestones_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        note = request.POST.get('note')
        date_str = request.POST.get('date')
        
        if title and date_str:
            Milestone.objects.create(
                title=title,
                note=note,
                date=datetime.strptime(date_str, "%Y-%m-%d").date()
            )
            
    milestones = Milestone.objects.all().order_by('date')
    today = date.today()
    
    for m in milestones:
        try:
            next_anniversary = date(today.year, m.date.month, m.date.day)
        except ValueError:
            next_anniversary = date(today.year, 3, 1)
            
        if next_anniversary < today:
            try:
                next_anniversary = date(today.year + 1, m.date.month, m.date.day)
            except ValueError:
                next_anniversary = date(today.year + 1, 3, 1)
                
        m.days_until_next = (next_anniversary - today).days

    if request.method == 'POST' and request.htmx:
        return render(request, 'core/partials/milestones_list_partial.html', {'milestones': milestones})

    return render(request, 'core/milestones.html', {'milestones': milestones})
