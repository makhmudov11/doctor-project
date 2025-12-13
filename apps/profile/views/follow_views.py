from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.profile.models import Profile, Follow, FollowChoices
from apps.profile.serializers.profile import UserProfileDetailSerializer
from apps.utils import CustomResponse


class UserProfileFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        if not profile_id:
            return CustomResponse.error_response(message='Profile id kelishi shart')

        profile = request.user.profile
        if not profile:
            return CustomResponse.error_response(message='Userga tegishli profil topilmadi')

        try:
            following_user = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return CustomResponse.error_response(
                message=f'{profile_id}-idlik userga tegishli profil mavjud emas'
            )

        if profile.id == following_user.id:
            return CustomResponse.error_response(message="O'zingizni follow qila olmaysiz")

        follow_obj, created = Follow.objects.get_or_create(
            profile=profile,
            following=following_user
        )

        if created:
            follow_obj.status = FollowChoices.follow
            follow_obj.save()

            Profile.objects.filter(id=profile.id).update(
                following_count=F('following_count') + 1
            )

        else:
            if follow_obj.status == FollowChoices.follow:
                return CustomResponse.error_response(message="Siz allaqachon follow qilgansiz")

            follow_obj.status = FollowChoices.follow
            follow_obj.save()

            Profile.objects.filter(id=profile.id).update(
                following_count=F('following_count') + 1
            )

            Profile.objects.filter(id=following_user.id).update(
                followers_count=F('followers_count') + 1
            )

        user_data = UserProfileDetailSerializer(profile).data
        following_data = UserProfileDetailSerializer(following_user).data

        return CustomResponse.success_response(data={
            "user": user_data,
            "following_user": following_data
        })


class UserUnFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        if not profile_id:
            return CustomResponse.error_response("Profile id kelishi shart")

        profile = request.user.profile

        try:
            unfollowing_user = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return CustomResponse.error_response(
                f"{profile_id}-idlik profil topilmadi"
            )

        if profile.id == unfollowing_user.id:
            return CustomResponse.error_response("O'zingizni unfollow qila olmaysiz")

        try:
            follow_obj = Follow.objects.get(
                profile=profile,
                following=unfollowing_user,
                status=FollowChoices.follow
            )
        except Follow.DoesNotExist:
            return CustomResponse.error_response("Siz bu userni follow qilmagansiz")

        follow_obj.status = FollowChoices.unfollow
        follow_obj.save()

        Profile.objects.filter(id=profile.id).update(
            following_count=F('following_count') - 1
        )

        Profile.objects.filter(id=unfollowing_user.id).update(
            followers_count=F('followers_count') - 1
        )

        return CustomResponse.success_response({
            "user": UserProfileDetailSerializer(profile).data,
            "unfollowing_user": UserProfileDetailSerializer(unfollowing_user).data
        })
