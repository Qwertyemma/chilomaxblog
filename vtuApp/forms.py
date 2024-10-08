from django import forms
from .models import Post, Category1, Category2

class PostForm(forms.ModelForm):
    # Removed author_name since it should be derived from the logged-in user

    first_category = forms.ModelChoiceField(queryset=Category1.objects.all(), required=True, label="First Category")
    second_category = forms.ModelChoiceField(queryset=Category2.objects.all(), required=True, label="Second Category")

    class Meta:
        model = Post
        fields = ['title', 'body', 'first_category', 'second_category', 'image',]
        
    def __init__(self, *args, **kwargs):
        # You may want to accept the user as a parameter to set the author later
        self.user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        post = super(PostForm, self).save(commit=False)
        if self.user:  # Set the author if user is provided
            post.author = self.user
        if commit:
            post.save()
        return post