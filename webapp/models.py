from django.db import models

class AppSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return self.key

class Course(models.Model):
    folder_path = models.CharField(max_length=2048, unique=True)
    name = models.CharField(max_length=200)
    last_accessed = models.DateTimeField(auto_now=True)
    last_active_video = models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_in_courses')

    def __str__(self):
        return self.name

    @property
    def short_path(self):
        from pathlib import Path
        p = Path(self.folder_path)
        return f"{p.parent.name}/{p.name}"

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    number = models.CharField(max_length=10, help_text="e.g., '1'")
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    quiz_path = models.CharField(max_length=2048, null=True, blank=True)

    class Meta:
        ordering = ['course', 'order', 'number']
        unique_together = ('course', 'number')

    def __str__(self):
        return f"{self.number} - {self.title}"

    @property
    def total_duration(self):
        return sum(m.total_duration for m in self.modules.all())

    @property
    def is_completed(self):
        modules = self.modules.all()
        return bool(modules) and all(m.is_completed for m in modules)

class Module(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='modules')
    number = models.CharField(max_length=20, help_text="e.g., '1.1'")
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'number']

    def __str__(self):
        return f"{self.number} - {self.title}"

    @property
    def total_duration(self):
        return sum(v.duration for v in self.videos.all())

    @property
    def is_completed(self):
        videos = self.videos.all()
        return bool(videos) and all(v.is_completed for v in videos)

class Video(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='videos')
    number = models.CharField(max_length=30, help_text="e.g., '1.1.1'")
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=2048)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")
    progress = models.IntegerField(default=0, help_text="Progress in seconds")
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    html_path = models.CharField(max_length=2048, null=True, blank=True)

    class Meta:
        ordering = ['order', 'number']

    def __str__(self):
        return f"{self.number} - {self.title}"
