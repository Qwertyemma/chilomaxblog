from django.contrib import admin
from .models import PasswordReset, Profile, Post, Category1, Category2, Comment

class ProfileAdmin(admin.ModelAdmin):
    # Fields to display in the list view of the admin
    list_display = ('user', 'bio', 'location', 'profileimg')
    
    # Enable searching by username and bio
    search_fields = ('user__username', 'bio')

# Register the models with the admin site
admin.site.register(PasswordReset)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)
admin.site.register(Category1)
admin.site.register(Category2)
admin.site.register(Comment)