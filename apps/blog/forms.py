from django import forms

from apps.blog.models import Post, Comment


class PostCreateForm(forms.ModelForm):
    user_agreement = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the terms and conditions'
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'cover']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 6}),
        }
        labels = {
            'title': 'Title',
            'content': 'Content',
            'cover': 'Cover'
        }
        error_messages = {
            'title': {
                'required': 'Title is required'
            }
        }
        help_text = {
            'title': 'Enter the title of the post',
            'content': 'Enter the content of the post'
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if not title:
            raise forms.ValidationError('Title is required')
        if title in ['test', 'блин', 'блен', 'блан']:
            raise forms.ValidationError('Не матерись!')
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if content in ['test', 'блин', 'блен', 'блан']:
            raise forms.ValidationError('Не матерись!')
        return content

    def clean_user_agreement(self):
        user_agreement = self.cleaned_data['user_agreement']
        if not user_agreement:
            raise forms.ValidationError(
                'You must agree to the terms and conditions')
        return user_agreement


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if content in ['test', 'блин', 'блен', 'блан']:
            raise forms.ValidationError('Не матерись!')
        return content


class FeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control'}))
