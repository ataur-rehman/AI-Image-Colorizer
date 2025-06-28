
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

class Profile(models.Model):
    # Create one-to-one relationship with User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    username = models.CharField(max_length=25)
    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=255)
    
    membership_type = models.CharField(max_length=15, default='standard')
    edited_images = models.IntegerField(default=0)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.username

class ImageJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original = models.ImageField(upload_to='uploads/original/')
    processed = models.ImageField(upload_to='uploads/processed/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ), default='pending')
    
class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


class Image(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='images')  # Maintain original
    original_image = models.ImageField(upload_to='images/original')
    edited_image = models.ImageField(upload_to='images/edited')
    canvas_edited_image = models.ImageField(upload_to='images/edited/canvas', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

class ProfileAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            profile = Profile.objects.get(username=username)
            if profile.check_password(password):
                return profile.user
            return None
        except Profile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None