from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileUpdateSerializer, UserRegistrationSerializer
from .functions.generate_verification import generate_verification_token
from .functions.send_mail import send_verification_email

@api_view(['POST'])
def login(request):
    identifier = request.data.get('identifier', '').strip()
    password = request.data.get('password')
    
    if not identifier or not password:
        return Response({
            "message": "Username/email and password are required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from django.contrib.auth import get_backends
    backend = get_backends()[0]  
    user = backend.authenticate(request, username=identifier, password=password)
    
    if user is not None:
        if not user.is_verified:
            return Response({
                "message": "Please verify your email before logging in"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return Response({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "message": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()  
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'message': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        verification_token = generate_verification_token()
        
        user = UserProfile.objects.create_user(
            username=serializer.validated_data['username'],
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            verification_token=verification_token
        )
        
        verification_link = f"{settings.BASE_URL}/verify-email/?token={verification_token}"
        send_verification_email(user.name, user.email, verification_link)
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_email(request):
    token = request.query_params.get('token')
    
    if not token:
        return Response({
            'message': 'Verification token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = UserProfile.objects.filter(verification_token=token).first()
    
    if user:
        user.is_verified = True
        user.verification_token = None
        user.save()
        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Invalid verification token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password(request):
    identifier = request.data.get('identifier', '').strip()
    
    if not identifier:
        return Response({
            'message': 'Username or email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if '@' in identifier:
        user = UserProfile.objects.filter(email=identifier).first()
    else:
        user = UserProfile.objects.filter(username=identifier).first()
        
    if not user:
        return Response({
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    verification_token = generate_verification_token()
    user.verification_token = verification_token
    user.save()
    
    reset_link = f"{settings.BASE_URL}/reset-password/?token={verification_token}"
    send_verification_email(user.name, user.email, reset_link, email_type="password_reset")
    
    return Response({
        'message': 'Password reset link sent to your email'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request):
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    if not token or not new_password:
        return Response({
            'message': 'Token and new password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = UserProfile.objects.filter(verification_token=token).first()
    
    if user:
        user.set_password(new_password)
        user.verification_token = None
        user.save()
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        old_email = request.user.email
        new_email = serializer.validated_data.get('email')
        
        if new_email and new_email != old_email:
            if UserProfile.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                return Response({
                    'message': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            verification_token = generate_verification_token()
            request.user.verification_token = verification_token
            request.user.save()
            
            verification_link = f"{settings.BASE_URL}/verify-email-update/?token={verification_token}&email={new_email}"
            send_verification_email(request.user.name, new_email, verification_link, email_type="email_update")
            
            return Response({
                'message': 'Verification email sent to new email address'
            }, status=status.HTTP_200_OK)
        
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserProfileSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def verify_email_update(request):
    token = request.query_params.get('token')
    new_email = request.query_params.get('email')
    
    if not token or not new_email:
        return Response({
            'message': 'Token and email are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = UserProfile.objects.filter(verification_token=token).first()
    
    if user:
        user.email = new_email
        user.verification_token = None
        user.save()
        return Response({
            'message': 'Email updated successfully'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):
    request.user.delete()
    return Response({
        'message': 'Account deleted successfully'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def verify_token(request):
    token = request.data.get('access_token')

    if not token:
        return Response({
            "success": False,
            "message": "Token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        UntypedToken(token)
        return Response({
            "success": True,
            "message": "Token is valid"
        }, status=status.HTTP_200_OK)
    except (TokenError, InvalidToken):
        return Response({
            "success": False,
            "message": "Token is invalid or expired"
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response({
            "success": False,
            "message": "Refresh token is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
        
        return Response({
            "success": True,
            "access_token": new_access_token,
            "message": "Token refreshed successfully"
        }, status=status.HTTP_200_OK)
    
    except Exception:
        return Response({
            "success": False,
            "message": "Invalid refresh token"
        }, status=status.HTTP_400_BAD_REQUEST)