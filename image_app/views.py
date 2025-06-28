from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import signup_form, login_form, ImageUploadForm
from .models import Profile, Image
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.template.loader import render_to_string  #
from django.core.mail import EmailMultiAlternatives
from django.core.files.base import ContentFile
import os, base64, uuid, json
from .colorizer.colorize_image import colorize_image
from django.shortcuts import render
from .models import UploadedImage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Profile
from .forms import login_form  # Assuming this is your custom form



def colorize_result(request, image_id):
    try:
        # Get the image with the colorized version
        image = Image.objects.get(id=image_id)
            
        # Check if the image has been colorized
        if not image.edited_image:
            messages.error(request, "This image hasn't been colorized yet.")
            return redirect('photo_editor', image_id=image.id)
            
        context = {
            'image': image,
            'page_title': 'Colorized Result'
        }
        
        return render(request, 'colorize_page.html', context)
        
    except Image.DoesNotExist:
        messages.error(request, "Image not found.")
        return redirect('photo_editor')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('photo_editor')
    
def colorizer_view(request):
    try:
        selected_image = UploadedImage.objects.filter(user=request.user).latest('upload_date')
    except UploadedImage.DoesNotExist:
        selected_image = None
        
    return render(request, 'colorizer.html', {
        'selected_image': selected_image
    })



def getting_started(request):
    return render(request, 'start_page.html')


def photo_editor(request, image_id=None):
    image = None
    edited_image = None
    
    if image_id:
        try:
            image = Image.objects.get(id=image_id)
            # Check if this image has already been edited
            if image.edited_image:
                edited_image = image
                image = None  # Set to None since we're displaying the edited version
        except Image.DoesNotExist:
            messages.error(request, 'Image not found.')
    
    context = {
        'image': image,
        'edited_image': edited_image,
        'image_id': image_id  # Pass the image_id explicitly
    }
    
    return render(request, 'photo_editor.html', context)

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

# Signup view (updated with User-Profile linkage)
def signup(request):
    if request.method == 'POST':
        form = signup_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            membership_type = form.cleaned_data.get('membership_type', 'standard')

            # Check for existing profile or user
            if User.objects.filter(username=username).exists() or Profile.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect('signup')

            if User.objects.filter(email=email).exists() or Profile.objects.filter(email=email).exists():
                messages.error(request, "Email already registered")
                return redirect('signup')

            try:
                # Create Django User first
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Now create a Profile and link it to the user
                profile = Profile.objects.create(
                    user=user,
                    username=username,
                    email=email,
                    membership_type=membership_type
                )
                profile.set_password(password)  # Properly hash the password
                profile.save()

                # Set authentication backend
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth_login(request, user)

                # Email sending
                try:
                    subject = 'Welcome to Prismify! ☄️✨'
                    text_content = f'Hi {username},\n\nThank you for signing up!'
                    html_content = render_to_string('emails/signup_welcome.html', {'username': username})
                    
                    email_msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [email]
                    )
                    email_msg.attach_alternative(html_content, "text/html")
                    email_msg.send()
                except Exception as e:
                    messages.warning(request, f"Signup successful but email failed: {str(e)}")

                return redirect('dashboard')

            except Exception as e:
                # If there's an error with the User or Profile creation, clean up
                if 'user' in locals():
                    user.delete()  # Delete the user if profile creation failed
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect('signup')

        else:
            # Form is invalid
            messages.error(request, "Please correct the errors below")
            return render(request, 'signup.html', {'form': form})
    
    # GET request
    form = signup_form()
    return render(request, 'signup.html', {'form': form})



# Login view (updated with hybrid auth)
def login(request):
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                profile = Profile.objects.get(username=username)
                if profile.check_password(password):
                    # Get or create Django User
                    user, created = User.objects.get_or_create(
                        username=profile.username,
                        defaults={'email': profile.email}
                    )
                    
                    # Set backend explicitly
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    
                    auth_login(request, user)
                    request.session['username'] = profile.username
                    return redirect('dashboard')
                else:
                    messages.error(request, "Incorrect password.")
            except Profile.DoesNotExist:
                messages.error(request, "Profile not found.")
    else:
        form = login_form()

    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    try:
        # First try to get the profile from the user relation
        try:
            profile = request.user.profile
        except:
            # If that fails, try to get from session
            username = request.session.get('username')
            if username:
                profile = Profile.objects.get(username=username)
            else:
                # Create a new profile for the user if none exists
                profile = Profile.objects.create(
                    user=request.user,
                    username=request.user.username,
                    email=request.user.email,
                    password=make_password('temp_password')  # Just a placeholder
                )
        
        # Get recent edits (both colorized and canvas-edited)
        # Using Q objects to query for images with either edited_image OR canvas_edited_image
        from django.db.models import Q
        recent_edits = Image.objects.filter(
            user=profile
        ).filter(
            Q(edited_image__isnull=False, edited_image__gt='') | 
            Q(canvas_edited_image__isnull=False, canvas_edited_image__gt='')
        ).order_by('-upload_date')[:3]
        
        context = {
            'user': request.user,
            'username': profile.username,
            'email': profile.email,
            'membership_type': profile.membership_type,
            'edited_images': profile.edited_images,
            'recent_edits': recent_edits,
        }
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('login')

def upload_image(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first.')
            return redirect('dashboard')

        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the user profile (either directly or from the session)
                try:
                    # Try to get profile from direct relationship
                    user_profile = request.user.profile
                except:
                    # If that fails, try to get by username from session
                    username = request.session.get('username')
                    if username:
                        user_profile = Profile.objects.get(username=username)
                    else:
                        # Create a profile for the user if none exists
                        user_profile = Profile.objects.create(
                            user=request.user,
                            username=request.user.username,
                            email=request.user.email,
                            password=make_password('temp_password')  # This is just a placeholder
                        )
                
                # Check membership limits
                if user_profile.edited_images >= 5 and user_profile.membership_type == 'standard':
                    messages.error(request, 'Please upgrade to premium to continue editing pictures.')
                    return redirect('dashboard')
                
                # Process the image
                user_profile.edited_images += 1
                user_profile.save()
                
                # Save the image with the profile relationship
                image = form.save(commit=False)
                image.user = user_profile  # Link to Profile, not User
                image.save()
                
                messages.success(request, 'Image uploaded successfully!')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f'Error processing image: {str(e)}')
                return redirect('dashboard')
        
        messages.error(request, 'Invalid file format. Please upload JPG, PNG, or WEBP files.')
        return redirect('dashboard')
    
    messages.error(request, 'Invalid request method.')
    return redirect('dashboard')

def upload_image2(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first.')
            return redirect('dashboard')

        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Get the user profile (either directly or from the session)
                try:
                    # Try to get profile from direct relationship
                    user_profile = request.user.profile
                except:
                    # If that fails, try to get by username from session
                    username = request.session.get('username')
                    if username:
                        user_profile = Profile.objects.get(username=username)
                    else:
                        # Create a profile for the user if none exists
                        user_profile = Profile.objects.create(
                            user=request.user,
                            username=request.user.username,
                            email=request.user.email,
                            password=make_password('temp_password')  # This is just a placeholder
                        )
                
                # Check membership limits
                if user_profile.edited_images >= 5 and user_profile.membership_type == 'standard':
                    messages.error(request, 'Please upgrade to premium to continue editing pictures.')
                    return redirect('dashboard')
                
                # Process the image
                user_profile.edited_images += 1
                user_profile.save()
                
                # Save the image with the profile relationship
                image = form.save(commit=False)
                image.user = user_profile  # Link to Profile, not User
                image.save()
                
                messages.success(request, 'Image uploaded successfully!')
                return redirect('photo_editor', image_id=image.id)

            except Exception as e:
                messages.error(request, f'Error processing image: {str(e)}')
                return redirect('photo_editor')
        
        messages.error(request, 'Invalid file format. Please upload JPG, PNG, or WEBP files.')
        return redirect('photo_editor')
    
    messages.error(request, 'Invalid request method.')
    return redirect('photo_editor')

def show_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    try:
        # Try multiple ways to get the profile
        try:
            profile = request.user.profile
        except:
            username = request.session.get('username')
            if username:
                profile = Profile.objects.get(username=username)
            else:
                messages.error(request, "User profile not found.")
                return redirect('dashboard')
                
        # Use Q objects to get images with either edited_image or canvas_edited_image
        from django.db.models import Q
        images = Image.objects.filter(
            user=profile
        ).filter(
            Q(edited_image__isnull=False, edited_image__gt='') | 
            Q(canvas_edited_image__isnull=False, canvas_edited_image__gt='')
        ).order_by('-upload_date')
        
        return render(request, 'show_history.html', {'images': images})
        
    except Profile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('dashboard')

def logout(request):
    request.session.flush()
    return HttpResponse("You have been logged out.")


def show_uploads(request):
    username = request.session.get('username')
    if not username:
        return HttpResponse("User not logged in.")

    try:
        user = Profile.objects.get(username=username)
        images = Image.objects.filter(user=user)
    except Profile.DoesNotExist:
        return HttpResponse("User not found.")

    return render(request, 'show_uploads.html', {'images': images})

def save_edit2(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')
        image_id = data.get('image_id')  # <-- You must send this from JS (or use session)

        if image_data and image_id:
            try:
                # Find the instance to update
                instance = Image.objects.get(id=image_id)

                # Decode base64 image data
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = f"edit_image2_{uuid.uuid4()}.{ext}"
                image_file = ContentFile(base64.b64decode(imgstr), name=file_name)

                # Save it just like edit_image1
                instance.canvas_edited_image.save(file_name, image_file)
                instance.save()

                return JsonResponse({'status': 'success', 'filename': file_name})
            except Image.DoesNotExist:
                return JsonResponse({'status': 'fail', 'error': 'Image instance not found'}, status=404)

    return JsonResponse({'status': 'fail', 'error': 'Invalid request'}, status=400)

def edit_image(request, image_id):
    try:
        image = Image.objects.get(id=image_id)
        
        username = request.session.get('username')
        if image.user.username != username:
            return HttpResponse("Unauthorized")

        input_path = os.path.join(settings.MEDIA_ROOT, str(image.original_image))
        edited_filename = f"images/edited/edited_{os.path.basename(input_path)}"
        output_path = os.path.join(settings.MEDIA_ROOT, edited_filename)

        colorize_image(input_path, output_path)

        # Save path in model 
        image.edited_image.name = edited_filename
        image.save()

        return redirect('colorize_result', image_id=image.id)

    except Image.DoesNotExist: 
        return HttpResponse("Image not found")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")


def edit_image_page_upload(request, image_id):
    username = request.session.get('username')
    image = get_object_or_404(Image, id=image_id)
    if image.user.username != username:
        return HttpResponse("Unauthorized")

    return render(request, 'edit_image_canvas.html', {'image': image})


def edit_image_page_history(request, image_id):
    username = request.session.get('username')
    image = get_object_or_404(Image, id=image_id)
    if image.user.username != username:
        return HttpResponse("Unauthorized")

    return render(request, 'edit_image_canvas_2.html', {'image': image})


import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64
import uuid
import json

# Assuming you have an Image model imported
# from .models import Image

@csrf_exempt
def save_edited_image(request, image_id):
    if request.method == 'POST':
        try:
            username = request.session.get('username')
            image_obj = get_object_or_404(Image, id=image_id)
            if image_obj.user.username != username:
                return JsonResponse({"message": "Unauthorized"}, status=403)

            data = json.loads(request.body)
            image_data = data['image']
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'edited_{uuid.uuid4()}.{ext}')

            image_obj.edited_image.save(data.name, data)
            image_obj.save()

            return JsonResponse({'message': 'Image saved successfully'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid request'}, status=400)

from django.shortcuts import render
from .models import Image



def update_membership(request):
    if 'username' not in request.session:
        return redirect('login')
        
    if request.method == 'POST':
        username = request.session['username']
        membership_type = request.POST.get('membership_type')
        
        if membership_type not in ['standard', 'premium']:
            messages.error(request, "Invalid membership type.")
            return redirect('dashboard')
            
        try:
            user = Profile.objects.get(username=username)
            user.membership_type = membership_type
            user.save()
            
            if membership_type == 'premium':
                messages.success(request, "Congratulations! You've upgraded to Premium membership.")
            else:
                messages.success(request, "Your membership has been updated to Standard.")
                
            return redirect('dashboard')
        except Profile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('login')
            
    return redirect('dashboard')