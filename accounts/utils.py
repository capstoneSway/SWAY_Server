from django.conf import settings

def get_profile_image_url(user):
    """
    유저 객체의 profile_image_changed가 존재하면 CloudFront 기반 URL 반환.
    없으면 기존 profile_image (URLField) 반환.
    """
    if user.profile_image_changed:
        return f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{user.profile_image_changed.name}"
    elif user.profile_image:
        return user.profile_image
    return None