from django.contrib import admin
from .models import PlantData, QAEntry, Conversation, Message

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
            'fields': ('image_url', 'year', 'image'), # Added 'image' here
        }),
        ('Pest and Disease Info', {
            'fields': ('common_diseases', 'common_pests'),
        })
    )

@admin.register(QAEntry)
class QAEntryAdmin(admin.ModelAdmin):
    list_display = ('plant', 'question_text', 'created_at')
    search_fields = ('question_text', 'answer_text', 'plant__common_name', 'plant__scientific_name')
    list_filter = ('plant',)
    readonly_fields = ('question_vector', 'answer_vector', 'created_at')
    raw_id_fields = ('plant',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'list_participants')
    readonly_fields = ('id', 'created_at')
    filter_horizontal = ('participants',)  # Use filter_horizontal for ManyToMany

    def list_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    list_participants.short_description = "Participants"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'sender', 'timestamp', 'is_read', 'short_content')
    list_filter = ('conversation', 'sender', 'timestamp', 'is_read')
    search_fields = ('content', 'sender__username')
    readonly_fields = ('timestamp',)

    def conversation_id(self, obj):
        return obj.conversation.id
    conversation_id.short_description = "Conversation ID"

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"