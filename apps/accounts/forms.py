from django import forms


def _get_signup_base():
    from allauth.account.forms import SignupForm
    return SignupForm


class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name',
                                  widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=30, label='Last Name',
                                 widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
