from django import forms

from .models import MedicalReport


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['title', 'details', 'report_image', 'status']
        labels = {
            'title': 'Report title',
            'details': 'Report details',
            'report_image': 'Report Image',
            'status': 'Report status',
        }
        widgets = {
            'details': forms.Textarea(attrs={'rows': 5}),
        }
