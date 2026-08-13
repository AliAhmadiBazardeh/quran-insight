from django.db import models
from quran.tasks import send_feedback_notification_task

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('suggestion', 'پیشنهاد'),
        ('search_problem', 'مشکل جستجوی آیه'),
        ('bug', 'گزارش باگ'),
        ('question', 'سوال'),
        ('other', 'سایر'),
    ]

    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='suggestion',
        verbose_name='نوع بازخورد'
    )
    message = models.TextField(
        verbose_name='پیام'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        verbose_name = 'بازخورد'
        verbose_name_plural = 'بازخوردها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_type_display()}"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        send_feedback_notification_task.delay(
            feedback_type=self.get_feedback_type_display(),
            text=self.message,
        )