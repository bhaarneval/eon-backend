"""
Api related to invitation are here
"""
import json

import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import get_authorization_header
from rest_framework import generics
from django.db import transaction
from django.db.models import F

from authentication.models import User
from core.models import UserProfile, Invitation, Event
from core.serializers import InvitationSerializer
from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification
from utils.permission import IsOrganizer
from eon_backend.settings import SECRET_KEY, EVENT_URL


class InvitationViewSet(generics.GenericAPIView):
    """
    Add Api from here
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOrganizer)
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
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        data = json.loads(request.body)
        event_id = data.get('event', None)
        discount_percentage = data.get('discount_percentage', 0)
        invitee_list = data.get('invitee_list', [])
        testing = data.get("testing", False)

        response = []
        contact_nos = []

        try:
            event = Event.objects.get(id=event_id, is_active=True)
        except Event.DoesNotExist:
            return api_error_response(message="No event exist with id={}".format(event_id))
        if event.event_created_by.id != user_id:
            return api_error_response(message="You are not allowed to perform this action",
                                      status=400)
        for invitee in invitee_list:
            try:
                inv_object = self.queryset.get(email=invitee, event=event_id)

                try:
                    user = User.objects.get(email=invitee, is_active=True)
                    try:
                        self.queryset.filter(email=invitee, event=event_id).update(
                            event=event,
                            discount_percentage=discount_percentage,
                            user=user, email=user.email
                        )
                        response.append(inv_object)
                        number = UserProfile.objects.get(user=user)
                        contact_nos.append("".join(["+91", number.contact_number]))
                    except Exception:
                        return api_error_response(message="Something went wrong", status=500)
                except User.DoesNotExist:
                    try:
                        self.queryset.filter(email=invitee, event=event_id).update(
                            event=event,
                            discount_percentage=discount_percentage,
                            email=invitee,
                        )
                        response.append(inv_object)
                    except Exception:
                        return api_error_response(
                            message="Some error occurred due to incorrect details",
                            status=400)

            except Invitation.DoesNotExist:
                try:
                    user = User.objects.get(email=invitee, is_active=True)
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
        if not testing:
            send_email_sms_and_notification(action_name="invitation_send",
                                            email_ids=invitee_list,
                                            event_name=event.name,
                                            discount_percentage=discount_percentage,
                                            url=EVENT_URL+str(event_id),
                                            numbers_list=contact_nos)
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
            event = Event.objects.get(id=event_id, is_active=True)
        except Event.DoesNotExist:
            return api_error_response(message="Invalid event id", status=400)

        try:
            user_ids = self.queryset.filter(id__in=list_of_ids).select_related(
                "user").annotate(users_id=F("user__id")).values_list("users_id")
            contact_no = UserProfile.objects.filter(id__in=user_ids).values_list("contact_number")
            contact_nos = ["".join(["+91", _[0]]) for _ in contact_no]
            email_ids = self.queryset.filter(id__in=list_of_ids).values_list("email")
            email_ids = [_[0] for _ in email_ids]

            self.queryset.filter(id__in=list_of_ids).update(is_active=False)
            if not testing:
                send_email_sms_and_notification(action_name="invitation_delete",
                                                email_ids=email_ids,
                                                event_name=event.name,
                                                numbers_list=contact_nos)
            return api_success_response(message="Invitation successfully deleted", status=200)
        except Exception:
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
