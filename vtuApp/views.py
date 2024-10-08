from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth, messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone
from .models import PasswordReset, Profile , Post,Category1, Category2, Comment
from .forms import PostForm

# Home page view
def Index(request):
    return render(request, 'index.html')

# User registration view
def RegisterView(request):
    if request.method == "POST":
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        user_data_has_error = False

        # Check if passwords match
        if password != confirm_password:
            user_data_has_error = True
            messages.error(request, "Passwords do not match")
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists")

        # Check if email exists
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists")

        # Check password length
        if len(password) < 4:
            user_data_has_error = True
            messages.error(request, "Password must be at least 4 characters long")

        # If there are no errors, create the user
        if user_data_has_error:
            return render(request, 'register.html')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            new_user.save()
            messages.success(request, "Account created successfully.")
            
            # Log user in and redirect to settings page
            auth.login(request, new_user)

            # Create a Profile object for the new user
            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user=user_model)
            new_profile.save()
          
            return redirect('settings')

    return render(request, 'register.html')

# User login view
def LoginView(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
            
    return render(request, 'login.html')

@login_required(login_url='register')
def Settings(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        location = request.POST.get('location')

        if request.FILES.get('image'):
            user_profile.profileimg = request.FILES.get('image')

        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})


@login_required(login_url='login')
def AccountSettings(request):
    # Get the currently logged-in user
    user = request.user
    # Get or create the user's profile
    user_profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user fields
        user.username = request.POST.get('username', user.username)  # Default to current username if not provided
        user.email = request.POST.get('email', user.email)  # Default to current email if not provided
        user_profile.bio = request.POST.get('bio', user_profile.bio)  # Default to current bio if not provided
        user_profile.location = request.POST.get('location', user_profile.location)  # Default to current location if not provided
        user_profile.notification_preference = request.POST.get('notification_preference', user_profile.notification_preference)
        # Handle profile image if it was uploaded
        if 'profileimg' in request.FILES:
            user_profile.profileimg = request.FILES['profileimg']

        # Save user and profile changes
        try:
            user.save()  # Save the user changes
            user_profile.save()  # Save the user profile changes
            
            messages.success(request, "Account settings updated successfully.")
            return redirect('account-settings')  # Redirect to avoid form resubmission
        except Exception as e:
            messages.error(request, f"An error occurred while updating settings: {str(e)}")

    # Render the account settings page
    return render(request, 'account-settings.html', {'user': user, 'user_profile': user_profile})
    

@login_required(login_url='login')
def DashboardView(request):
    get_all_posts = Post.objects.all().order_by('-date')
    get_all_categories_in_category_1 = Category1.objects.all()[:2]
    get_all_categories_in_category_2 = Category2.objects.all()[:2]
    
    posts = Post.objects.filter(status=True)

    # Handle deletion of a post
    delete_post_id = request.GET.get('delete_post_id')
    delete_post_title = request.GET.get('delete_post_title')

    if request.method == 'POST' and delete_post_id:
        post = get_object_or_404(Post, id=delete_post_id, author=request.user)
        post.delete()
        messages.success(request, f"{delete_post_title} deleted successfully.")
        return redirect('dashboard')

    context = {
        'posts': get_all_posts,
        'delete_post_id': delete_post_id,
        'delete_post_title': delete_post_title,
        'cat1': get_all_categories_in_category_1,
        'cat2': get_all_categories_in_category_2,
    }
    
    return render(request, 'dashboard.html', context)
    
# User logout view
@login_required(login_url='login')
def LogoutView(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Forgot password view
def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Create a password reset record
            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password',  # Subject
                email_body,  # Body
                settings.EMAIL_HOST_USER,  # Sender
                [email]  # Recipient
            )
            email_message.fail_silently = False
            email_message.send()

            messages.success(request, "Password reset link sent to your email.")
            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request, 'forgot-password.html')

# Password reset sent view
def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password-reset-sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

# Password reset view
def ResetPassword(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')

            passwords_have_error = False

            # Validate passwords
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 4:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 4 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            # Check if reset link has expired
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')
                password_reset_id.delete()

            if not passwords_have_error:
                # Update user's password
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                # Delete password reset entry
                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # Redirect back to reset page with errors
                return redirect('reset-password', reset_id=reset_id)

    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset-password.html')

# Change password view
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('settings')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('settings')

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, "Password changed successfully. Please log in again.")
        auth.logout(request)
        return redirect('login')

    return render(request, 'settings.html')
    
    
def send_notification(user, message):
    user_profile = Profile.objects.get(user=user)
    if user_profile.notification_preference == 'email':
        send_mail(
            'Notification from Your Application',
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    elif user_profile.notification_preference == 'sms':
        # Implement SMS sending logic here
        pass
    elif user_profile.notification_preference == 'in_app':
        # Implement in-app notification logic here (e.g., saving in a Notification model)
        pass

# Article detail view for a given slug
@login_required(login_url='login') 
def ArticleDetail(request, slug):
    # Get the post based on the slug
    get_post = get_object_or_404(Post, slug=slug)
    # Get the currently logged-in user
    user = request.user
    # Retrieve or create the user's profile if authenticated
    if user.is_authenticated:
        user_profile, _ = Profile.objects.get_or_create(user=user)
    else:
        user_profile = None
    # Retrieve the post author's profile
    author_profile = get_object_or_404(Profile, user=get_post.author)
    # Retrieve all top-level comments (parent=None) related to the post
    comments = Comment.objects.filter(post=get_post)  # Only top-level comments
    number_of_comments = comments.count()

    # Create a list of comment profiles (author profiles for each comment)
    comment_profiles = [{
        'comment': comment,
        'profile': get_object_or_404(Profile, user=comment.author)
    } for comment in comments]

    # Handle form submission for adding a comment
    if request.method == 'POST':
        body = request.POST.get('body')
        if body and user.is_authenticated:
            new_comment = Comment(author=user, post=get_post, body=body)  # No parent for top-level comment
            new_comment.save()
            messages.success(request, 'Comment was added successfully!')
            return redirect('detail', slug=slug)
        else:
            messages.error(request, 'You need to be logged in to comment, and the comment body cannot be empty.')

    # Get categories for the sidebar
    get_all_categories_in_category_1 = Category1.objects.all()[:2]
    get_all_categories_in_category_2 = Category2.objects.all()[:2]
    get_all_posts = Post.objects.all()

    # Prepare context for rendering the article detail page
    context = {
        'posts': get_all_posts,
        'post': get_post,
        'category1': get_post.first_category,
        'category2': get_post.second_category,
        'cat1': get_all_categories_in_category_1,
        'cat2': get_all_categories_in_category_2,
        'comments': comments,  # Only top-level comments
        'number_of_comments': number_of_comments,
        'comment_profiles': comment_profiles,  # Pass comment profiles to the template
        'user_profile': user_profile,
        'author_profile': author_profile,  # Pass the post author's profile
    }

    return render(request, 'article.html', context)


@login_required(login_url='login')
def category_posts(request, category_slug):
    # Try to fetch the category from Category1 first
    category1 = Category1.objects.filter(slug=category_slug).first()
    
    if category1:
        # If found in Category1, set the category and fetch associated posts
        category = category1
        posts = Post.objects.filter(first_category=category)
    else:
        # Otherwise, try to fetch from Category2
        category2 = get_object_or_404(Category2, slug=category_slug)
        category = category2
        posts = Post.objects.filter(second_category=category)

    # Prepare context for rendering the template
    context = {
        'posts': posts,
        'category': category,
    }

    # Render the template with the context data
    return render(request, 'category_posts.html', context)
    
@login_required(login_url='login')
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        send_mail(
            f'Contact Form Submission from {name}',
            message,
            settings.DEFAULT_FROM_EMAIL,  # Your email
            ['emmanuelobiasogu32@gmail.com'], 
            fail_silently=False,
        )
        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')
    
@login_required(login_url='login')
def about(request):
  admin_user = User.objects.filter(is_superuser=True).first()
    
  if admin_user:
        # Get the admin's profile
    author_profile = Profile.objects.get(user=admin_user)
  else:
        author_profile = None

  return render(request, 'about.html', {'author_profile': author_profile})
    


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.instance.author = request.user  # Set the author of the post
            form.save()  # Save the post with the uploaded image
            messages.success(request, "Post created successfully.")
            return redirect('dashboard')
    else:
        form = PostForm()
    
    return render(request, 'create_post.html', {'form': form})

@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()  # Delete the post
        messages.success(request, "Post deleted successfully.")
        return redirect('dashboard')
    
    return redirect('dashboard')

@login_required(login_url='login')
def EditPostView(request, slug):
    # Retrieve the post based on the slug
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  # Bind the form to the post instance
        if form.is_valid():
            form.save()  # Save the updated post
            messages.success(request, "Post updated successfully.")
            return redirect('detail', slug=post.slug)  # Redirect to the article detail view
    else:
        form = PostForm(instance=post)  # Pre-fill the form with the current post data

    return render(request, 'edit_post.html', {'form': form, 'post': post})