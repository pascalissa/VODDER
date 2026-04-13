import os
import re
from pathlib import Path
from mutagen.mp4 import MP4
from .models import Course, Section, Module, Video

def sync_vod_directory(base_path):
    base_dir = Path(base_path)
    if not base_dir.exists() or not base_dir.is_dir():
        return False, "Directory does not exist."

    course_name = base_dir.name
    course, _ = Course.objects.get_or_create(
        folder_path=str(base_dir.absolute()), 
        defaults={'name': course_name}
    )
    course.save() # Updates last_accessed

    section_pattern = re.compile(r'^(\d+)\s*[-_]\s*(.+)$')
    module_pattern = re.compile(r'^(\d+\.\d+)\s*[-_]\s*(.+)$')
    video_pattern = re.compile(r'^(\d+\.\d+\.\d+)\s*[-_]\s*(.+)\.mp4$', re.IGNORECASE)

    for item_path in base_dir.iterdir():
        if item_path.is_dir() and not item_path.name.startswith('.'):
            # Section Level
            s_match = section_pattern.match(item_path.name)
            if s_match:
                s_num, s_title = s_match.groups()
                section, _ = Section.objects.update_or_create(
                    course=course,
                    number=s_num,
                    defaults={'title': s_title, 'order': int(s_num)}
                )

                for mod_path in item_path.iterdir():
                    if mod_path.is_dir() and not mod_path.name.startswith('.'):
                        # Module Level
                        m_match = module_pattern.match(mod_path.name)
                        if m_match:
                            m_num, m_title = m_match.groups()
                            m_order = 0
                            try:
                                m_order = int(m_num.split('.')[-1])
                            except ValueError:
                                pass

                            module, _ = Module.objects.update_or_create(
                                section=section,
                                number=m_num,
                                defaults={'title': m_title, 'order': m_order}
                            )

                            for vid_path in mod_path.iterdir():
                                if vid_path.is_file() and vid_path.name.lower().endswith('.mp4'):
                                    # Video Level
                                    v_match = video_pattern.match(vid_path.name)
                                    if v_match:
                                        v_num, v_title = v_match.groups()
                                        v_order = 0
                                        try:
                                            v_order = int(v_num.split('.')[-1])
                                        except ValueError:
                                            pass

                                        # Get Duration utilizing Mutagen
                                        duration = 0
                                        try:
                                            video_data = MP4(vid_path)
                                            duration = int(video_data.info.length)
                                        except Exception as e:
                                            pass

                                        # Check for matching HTML file in sibling folder
                                        html_path_str = None
                                        try:
                                            # Replace '/VOD/' with '/HTML/' in the absolute path and change extension
                                            vid_abs_path = str(vid_path.absolute())
                                            if '/VOD/' in vid_abs_path:
                                                possible_html_path = vid_abs_path.replace('/VOD/', '/HTML/').rsplit('.', 1)[0] + '.html'
                                                if Path(possible_html_path).exists():
                                                    html_path_str = possible_html_path
                                        except Exception:
                                            pass

                                        Video.objects.update_or_create(
                                            module=module,
                                            number=v_num,
                                            defaults={
                                                'title': v_title,
                                                'file_path': str(vid_path.absolute()),
                                                'html_path': html_path_str,
                                                'duration': duration,
                                                'order': v_order
                                            }
                                        )
    return True, "Synced successfully!"
