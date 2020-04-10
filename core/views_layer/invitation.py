import json
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db import transaction

from rest_framework import generics
from authentication.models import User
from core.models import UserProfile, Invitation, Event
from core.serializers import InvitationSerializer
from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification
from rest_framework.permissions import IsAuthenticated


class InvitationViewSet(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.filter(is_active=True)

    @transaction.atomic()
    def post(self, request):
        """
        Function to add new invitations
        :param request: data containing information of an invite in format {
                                                "event": 11, (event_id)
                                                "discount_percentage": 10,
                                                "invitee_list": ["demo1@gmail.com","demo2@gmail.com"] (list_of_emails)
                                                }
        :return: Response with a list of all the generated invites
        """
        data = json.loads(request.body)
        event_id = data.get('event', None)
        discount_percentage = data.get('discount_percentage',0)
        invitee_list = data.get('invitee_list', [])

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
                        # TODO: get the contact no for the registered user.
                    except Exception as err:
                        return api_error_response(message="Some error occurred due to incorrect details", status=400)
                except User.DoesNotExist:
                    try:
                        self.queryset.filter(email=invitee, event=event_id).update(
                            event=event,
                            discount_percentage=discount_percentage,
                            email=invitee
                        )
                        response.append(inv_object)
                    except Exception as err:
                        return api_error_response(message="Some error occurred due to incorrect details", status=400)

            except Invitation.DoesNotExist:
                try:
                    user = User.objects.get(email=invitee)
                    inv_object = Invitation.objects.create(event=event,
                                                           discount_percentage=discount_percentage,
                                                           user=user,
                                                           email=user.email).save()
                    response.append(inv_object)
                except User.DoesNotExist:
                    inv_object = Invitation.objects.create(event=event,
                                                           discount_percentage=discount_percentage,
                                                           email=invitee).save()
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
            data.append(response_obj)
        message = f"We are inviting you to register for {event.name} with {discount_percentage}% discount"
        send_email_sms_and_notification(action_name="invitation_send",
                                        email_ids=invitee_list,
                                        message=message)
        data_object = {'invitee_list': data}
        return api_success_response(message="Successful invited", data=data_object)

    def delete(self, request):
        """
        Function to delete invitation list
        :param request: list of Id's in body with {'invitation_ids'=[list_of_ids]}
        :return:
        """
        data = json.loads(request.body)
        list_of_ids = data.get('invitation_ids')
        try:
            inv_obj = self.queryset.filter(id__in=list_of_ids).update(is_active=False)
            # TODO: To take contact no for sending messages.
            email_ids = inv_obj.values("email")
            send_email_sms_and_notification(action_name="invitation_delete", email_ids=email_ids)
            return api_success_response(message="Successfully deleted all Invitees", status=204)
        except Exception as err:
            return api_error_response(message='Could not delete due to some invalid reasons. Please Try Again',
                                      status=500)

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

        if event_id or user_id:
            queryset = Invitation.objects.filter(event=event_id, user=user_id)
        else:
            queryset = Invitation.objects.all()
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
            response_obj['event'] = {'event_id': invited.event.id, 'event_name': invited.event.name,
                                     'event_type': invited.event.type.type}
            response_obj['discount_percentage'] = invited.discount_percentage
            data.append(response_obj)
        data_object = {'invitee_list': data}
        return api_success_response(message="All Invitations", data=data_object)

