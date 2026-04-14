import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from .models import AppSetting, Course, Section, Module, Video
from .utils import sync_vod_directory

def dashboard(request):
    current_video_id = request.GET.get('v')
    
    vod_setting = AppSetting.objects.filter(key='VOD_DIR_PATH').first()
    active_path = vod_setting.value if vod_setting else None
    
    from pathlib import Path
    course_path = str(Path(active_path).absolute()) if active_path else ""
    
    sections = Section.objects.filter(course__folder_path=course_path).prefetch_related('modules__videos').all()
    base_video_qs = Video.objects.filter(module__section__course__folder_path=course_path)
    
    current_video = None
    if current_video_id:
        # User requested specific video, even if it's from another course technically, but let's constrain it:
        current_video = Video.objects.filter(id=current_video_id).first()
    
    if not current_video and sections.exists():
        course = sections.first().course
        if course.last_active_video:
            current_video = course.last_active_video
        else:
            first_section = sections.first()
            first_module = first_section.modules.first()
            if first_module:
                current_video = first_module.videos.first()

    total_videos = base_video_qs.count()
    completed_videos = base_video_qs.filter(is_completed=True).count()
    completion_percentage = int((completed_videos / total_videos * 100)) if total_videos > 0 else 0

    total_duration = base_video_qs.aggregate(Sum('duration'))['duration__sum'] or 0
    completed_duration = base_video_qs.filter(is_completed=True).aggregate(Sum('duration'))['duration__sum'] or 0
    in_progress_watched = base_video_qs.filter(is_completed=False).aggregate(Sum('progress'))['progress__sum'] or 0
    total_watched = completed_duration + in_progress_watched
    
    html_content = ""
    if current_video and current_video.html_path:
        if os.path.exists(current_video.html_path):
            try:
                with open(current_video.html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception:
                pass

    return render(request, 'webapp/dashboard.html', {
        'sections': sections,
        'current_video': current_video,
        'completion_percent': completion_percentage,
        'total_duration': total_duration,
        'total_watched': total_watched,
        'html_content': html_content,
    })

def quiz_view(request, section_id):
    section_obj = get_object_or_404(Section, id=section_id)
    
    vod_setting = AppSetting.objects.filter(key='VOD_DIR_PATH').first()
    active_path = vod_setting.value if vod_setting else None
    
    from pathlib import Path
    course_path = str(Path(active_path).absolute()) if active_path else ""
    
    sections = Section.objects.filter(course__folder_path=course_path).prefetch_related('modules__videos').all()
    base_video_qs = Video.objects.filter(module__section__course__folder_path=course_path)

    total_videos = base_video_qs.count()
    completed_videos = base_video_qs.filter(is_completed=True).count()
    completion_percentage = int((completed_videos / total_videos * 100)) if total_videos > 0 else 0

    total_duration = base_video_qs.aggregate(Sum('duration'))['duration__sum'] or 0
    completed_duration = base_video_qs.filter(is_completed=True).aggregate(Sum('duration'))['duration__sum'] or 0
    in_progress_watched = base_video_qs.filter(is_completed=False).aggregate(Sum('progress'))['progress__sum'] or 0
    total_watched = completed_duration + in_progress_watched
    
    quiz_data = []
    if section_obj.quiz_path and os.path.exists(section_obj.quiz_path):
        try:
            with open(section_obj.quiz_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                for key, val in raw_data.items():
                    quiz_data.append(val)
        except Exception:
            pass

    return render(request, 'webapp/dashboard.html', {
        'sections': sections,
        'current_video': None,
        'completion_percent': completion_percentage,
        'total_duration': total_duration,
        'total_watched': total_watched,
        'html_content': '',
        'current_quiz': {
            'section': section_obj,
            'questions': json.dumps(quiz_data)
        }
    })

def settings_view(request):
    vod_setting, _ = AppSetting.objects.get_or_create(key='VOD_DIR_PATH')
    message = None
    success = False

    if request.method == 'POST':
        path = request.POST.get('vod_path', '')
        vod_setting.value = path
        vod_setting.save()
        
        ok, msg = sync_vod_directory(path)
        message = msg
        success = ok

    recent_courses = Course.objects.order_by('-last_accessed')[:5]

    return render(request, 'webapp/settings.html', {
        'vod_setting': vod_setting,
        'message': message,
        'success': success,
        'recent_courses': recent_courses,
    })

def video_stream(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if not os.path.exists(video.file_path):
        raise Http404("Video file not found locally.")
    
    # FileResponse natively supports HTTP Content-Range streaming
    response = FileResponse(open(video.file_path, 'rb'), content_type='video/mp4')
    response['Accept-Ranges'] = 'bytes'
    return response

@csrf_exempt
def update_progress(request, video_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            progress = int(data.get('progress', 0))
            is_completed = data.get('is_completed', False)

            video = get_object_or_404(Video, id=video_id)
            if progress > video.progress:
                video.progress = progress
            if is_completed:
                video.is_completed = True
            video.save()
            
            course = video.module.section.course
            course.last_active_video = video
            course.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)
