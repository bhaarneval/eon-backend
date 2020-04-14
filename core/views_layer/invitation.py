"""
Api related to invitation are here
"""
import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from django.db.models import F

from rest_framework import generics
from authentication.models import User
from core.models import UserProfile, Invitation, Event
from core.serializers import InvitationSerializer
from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification
from utils.permission import IsOrganiser


class InvitationViewSet(generics.GenericAPIView):
    """
    Add Api from here
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOrganiser)
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.filter(is_active=True)

    @transaction.atomic()
    def post(self, request):
        """
        Function to add new invitations
        :param request: data containing information of an invite in format
            {
                "event": 11, (event_id)
                "discount_percentage": 10,
                "invitee_list": ["demo1@gmail.com","demo2@gmail.com"] (list_of_emails)
            }
        :param event_id: Event id (not required)
        :return: Response with a list of all the generated invites
        """
        data = json.loads(request.body)
        event_id = data.get('event', None)
        discount_percentage = data.get('discount_percentage', 0)
        invitee_list = data.get('invitee_list', [])
        testing = data.get("testing", False)

        response = []
        contact_nos = []

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return api_error_response(message="No event exist with id={}".format(event_id))
        for invitee in invitee_list:
            try:
                inv_object = self.queryset.get(email=invitee, event=event_id)

                try:
                    user = User.objects.get(email=invitee)
                    try:
                        self.queryset.filter(email=invitee, event=event_id).update(
                            event=event,
                            discount_percentage=discount_percentage,
                            user=user, email=user.email
                        )
                        response.append(inv_object)
                        number = UserProfile.objects.get(user=user)
                        contact_nos.append("".join(["+91", number.contact_number]))
                    except Exception as err:
                        return api_error_response(message="Something went wrong", status=500)
                except User.DoesNotExist:
                    try:
                        self.queryset.filter(email=invitee, event=event_id).update(
                            event=event,
                            discount_percentage=discount_percentage,
                            email=invitee,
                        )
                        response.append(inv_object)
                    except Exception as err:
                        return api_error_response(
                            message="Some error occurred due to incorrect details",
                            status=400)

            except Invitation.DoesNotExist:
                try:
                    user = User.objects.get(email=invitee)
                    inv_object = Invitation.objects.create(event=event,
                                                           discount_percentage=discount_percentage,
                                                           user=user,
                                                           email=user.email)
                    response.append(inv_object)
                    number = UserProfile.objects.get(user=user)
                    contact_nos.append("".join(["+91", number.contact_number]))
                except User.DoesNotExist:
                    inv_object = Invitation.objects.create(event=event,
                                                           discount_percentage=discount_percentage,
                                                           email=invitee)
                    response.append(inv_object)

        data = []
        for invited in response:
            response_obj = {'invitation_id': invited.id,
                            'email': invited.email,
                            'discount_percentage': discount_percentage}
            if invited.user is not None:
                try:
                    user_profile = UserProfile.objects.get(user=invited.user.id)
                    response_obj['user'] = {'user_id': invited.user.id, 'name': user_profile.name,
                                            'contact_number': user_profile.contact_number}
                except Exception:
                    pass
            response_obj['discount_percentage'] = invited.discount_percentage
            data.append(response_obj)
        data_object = {'invitee_list': data}
        return api_success_response(message="Successful invited", data=data_object)

    def delete(self, request):
        """
        Function to delete invitation list
        :param request: List of Id's in body with {'invitation_ids'=[list_of_ids]}
        :return:
        """
        data = request.data
        list_of_ids = data.get('invitation_ids')
        event_id = data.get('event_id')
        testing = data.get("testing", False)  # for not running mail service for testing
        if not event_id:
            return api_error_response(message="Event Id missing", status=400)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return api_error_response(message="Invalid event id", status=400)

        try:
            user_ids = self.queryset.filter(id__in=list_of_ids).select_related(
                "user").annotate(users_id=F("user__id")).values_list("users_id")
            contact_no = UserProfile.objects.filter(id__in=user_ids).values_list("contact_number")
            contact_no = ["".join(["+91", _[0]]) for _ in contact_no]
            email_ids = self.queryset.filter(id__in=list_of_ids).values_list("email")
            email_ids = [_[0] for _ in email_ids]

            self.queryset.filter(id__in=list_of_ids).update(is_active=False)
            message = f"You have been removed from invitation list of '{event.name}' event."
            if not testing:
                send_email_sms_and_notification(action_name="invitation_delete",
                                                message=message,
                                                email_ids=email_ids,
                                                numbers_list=contact_no)
            return api_success_response(message="Invitation successfully deleted", status=200)
        except Exception as err:
            return api_error_response(message='Something went wrong', status=500)

    def get(self, request):
        """
        Function to fetch invitation list
        :param request: may contain event_id or user_id to filter the invite list
        :return: Invitation list
        """
        event_id = request.GET.get('event_id')
        user_id = request.GET.get('user_id')

        if event_id:
            event_id = int(event_id)
        if user_id:
            user_id = int(user_id)

        if event_id and user_id:
            queryset = Invitation.objects.filter(event=event_id, user=user_id, is_active=True)
        elif event_id:
            queryset = Invitation.objects.filter(event=event_id, is_active=True)
        elif user_id:
            queryset = Invitation.objects.filter(user=user_id, is_active=True)
        else:
            queryset = Invitation.objects.filter(is_active=True)
        data = []
        for invited in queryset:
            response_obj = {'invitation_id': invited.id, 'email': invited.email}
            if invited.user is not None:
                try:
                    user_profile = UserProfile.objects.get(user=invited.user.id)
                    response_obj['user'] = {'user_id': invited.user.id, 'name': user_profile.name,
                                            'contact_number': user_profile.contact_number,
                                            'address': user_profile.address,
                                            'organization': user_profile.organization}
                except Exception:
                    pass
            response_obj['event'] = {'id': invited.event.id, 'name': invited.event.name,
                                     'type': invited.event.type.type}
            response_obj['discount_percentage'] = invited.discount_percentage
            data.append(response_obj)
        data_object = {'invitee_list': data}
        return api_success_response(message="Invitations details", data=data_object)
