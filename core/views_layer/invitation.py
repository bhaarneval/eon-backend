import json
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db import transaction

from rest_framework import mixins, generics
from authentication.models import User
from core.models import UserProfile, Invitation, Event
from core.serializers import InvitationSerializer
from utils.common import api_success_response, api_error_response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


class InvitationViewSet(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    serializer_class = InvitationSerializer
    queryset = Invitation.objects.all()


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

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return api_error_response(message="No event exist with id={}".format(event_id))
        for invitee in invitee_list:
            try:
                inv_object = Invitation.objects.get(email=invitee, event=event_id)

                try:
                    user = User.objects.get(email=invitee)
                    try:
                        Invitation.objects.filter(email=invitee,event=event_id).update(event=event,
                                                                        discount_percentage=discount_percentage,
                                                                        user=user, email=user.email)
                        response.append(inv_object)
                    except Exception as err:
                        return api_error_response(message="Some error occurred due to incorrect details", status=400)
                except User.DoesNotExist:
                    try:
                        Invitation.objects.filter(email=invitee,event=event_id).update(event=event,
                                                                        discount_percentage=discount_percentage,
                                                                        email=invitee)
                        response.append(inv_object)
                    except Exception as err:
                        return api_error_response(message="Some error occurred due to incorrect details", status=400)

            except Invitation.DoesNotExist:
                try:
                    user = User.objects.get(email=invitee)
                    Invitation.objects.create(event=event, discount_percentage=discount_percentage, user=user,
                                              email=user.email).save()
                    response.append(Invitation.objects.get(email=invitee))
                except User.DoesNotExist:
                    Invitation.objects.create(event=event, discount_percentage=discount_percentage, email=invitee).save()
                    response.append(Invitation.objects.get(email=invitee,event=event_id))

        data = []
        for invited in response:
            response_obj = {'email': invited.email}
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
        return api_success_response(message="Successful invited", data=data_object)

    def delete(self,request):
        """
        Function to delete invitation list
        :param request: list of Id's in body with {'invitation_ids'=[list_of_ids]}
        :return:
        """
        data = json.loads(request.body)
        list_of_ids = data.get('invitation_ids')
        try:
            Invitation.objects.filter(id__in=list_of_ids).delete()
            return api_success_response(message="Successfully deleted all Invitees", status=204)
        except Exception as err:
            return api_error_response(message='Could not delete due to some invalid reasons. Please Try Again',
                                      status=500)

    def get(self,request):
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
            response_obj = {'email': invited.email}
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

