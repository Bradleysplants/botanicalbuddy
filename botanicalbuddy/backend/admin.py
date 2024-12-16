from django.contrib import admin
from .models import PlantData, QAEntry

@admin.register(PlantData)
class PlantDataAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'trefle_id', 'family', 'genus')
    search_fields = ('common_name', 'scientific_name', 'family', 'genus')
    list_filter = ('family', 'genus')
    readonly_fields = ('trefle_id', 'slug', 'vector_data')
    fieldsets = (
        ('Basic Information', {
            'fields': ('common_name', 'scientific_name', 'trefle_id', 'slug')
        }),
        ('Classification', {
            'fields': ('family_common_name', 'family', 'genus')
        }),
        ('Details', {
            'fields': ('description', 'care_instructions', 'soil_type', 'water_requirements', 'sunlight_requirements', 'maximum_height', 'flower_color','native_to','vector_data')
        }),
        ('Image', {
            'fields': ('image_url', 'year'),
        })
    )

@admin.register(QAEntry)
class QAEntryAdmin(admin.ModelAdmin):
    list_display = ('plant', 'question_text', 'created_at')
    search_fields = ('question_text', 'answer_text', 'plant__common_name', 'plant__scientific_name')
    list_filter = ('plant',)
    readonly_fields = ('question_vector', 'answer_vector', 'created_at')
    raw_id_fields = ('plant',)