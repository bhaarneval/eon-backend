"""
Events related functions are here
"""
from datetime import date

import jwt
from django.db.models import ExpressionWrapper, F, IntegerField, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header

from core.models import Event, UserProfile, Subscription, WishList, Invitation, UserFeedback, Feedback
from core.serializers import ListUpdateEventSerializer, EventSerializer
from utils.common import api_error_response, api_success_response
from utils.helper import send_email_sms_and_notification
from utils.s3 import AwsS3
from utils.permission import IsOrganizerOrReadOnlySubscriber
from eon_backend.settings import SECRET_KEY
from utils.constants import EVENT_STATUS, SUBSCRIPTION_TYPE


class EventViewSet(ModelViewSet):
    """
      Event api are created here
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOrganizerOrReadOnlySubscriber)
    queryset = Event.objects.filter(
        is_active=True).select_related('type').annotate(event_type=F('type__type'))
    serializer_class = ListUpdateEventSerializer
    s3 = AwsS3()

    def list(self, request, *args, **kwargs):
        """
        Function to give list of Events based on different filter parameters
        :param request: contain the query type and it's value
        :return: Response contains complete list of events after the query
        """
        search_text = request.GET.get("search", None)
        event_type = request.GET.get("event_type", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        event_created_by = request.GET.get("event_created_by", False)
        is_wishlisted = request.GET.get('is_wishlisted', False)
        event_status = request.GET.get('event_status', EVENT_STATUS['default'])
        subscription_type = request.GET.get('subscription_type', SUBSCRIPTION_TYPE['default'])

        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        try:
            user_logged_in = user_id
            user_role = UserProfile.objects.get(user_id=user_logged_in).role.role
        except Exception:
            return api_error_response(
                message="Not able to fetch the role of the logged in user", status=500)

        today = date.today()
        self.queryset.filter(date__lt=str(today)).update(is_active=False)

        if event_status.lower() == EVENT_STATUS['completed']:
            self.queryset = Event.objects.filter(is_active=False, is_cancelled=False)

        if event_status.lower() == EVENT_STATUS['cancelled']:
            self.queryset = Event.objects.filter(is_active=False, is_cancelled=True)

        if event_status.lower() == EVENT_STATUS['default']:
            self.queryset = self.queryset.filter(date__gte=str(today))

        if is_wishlisted == 'True':
            try:
                event_ids = WishList.objects.filter(
                    user=user_id, is_active=True).values_list('event__id', flat=True)
                self.queryset = self.queryset.filter(id__in=event_ids)
            except Exception:
                return api_error_response(
                    message="Some internal error coming in fetching the wishlist", status=400)

        if subscription_type.lower() == SUBSCRIPTION_TYPE['free']:
            self.queryset = self.queryset.filter(subscription_fee=0)

        if subscription_type.lower() == SUBSCRIPTION_TYPE['paid']:
            self.queryset = self.queryset.filter(subscription_fee__gt=0)

        if search_text:
            self.queryset = self.queryset.filter(
                Q(location__icontains=search_text) | Q(name__icontains=search_text))
        if event_created_by == 'True':
            self.queryset = self.queryset.filter(event_created_by=user_id)
        if event_type:
            self.queryset = self.queryset.filter(type=event_type)
        if start_date and end_date:
            self.queryset = self.queryset.filter(date__range=[start_date, end_date])
        if len(self.queryset) > 1:
            self.queryset = self.queryset.annotate(diff=ExpressionWrapper(
                F('sold_tickets') * 100000 / F('no_of_tickets'), output_field=IntegerField()))
            self.queryset = self.queryset.order_by('-diff')

        is_subscriber = (user_role == 'subscriber')

        data = []

        for curr_event in self.queryset:
            response_obj = {"id": curr_event.id, "name": curr_event.name, "date": curr_event.date,
                            "time": curr_event.time, "location": curr_event.location, "event_type": curr_event.type.id,
                            "description": curr_event.description, "no_of_tickets": curr_event.no_of_tickets,
                            "sold_tickets": curr_event.sold_tickets, "subscription_fee": curr_event.subscription_fee,
                            "images": "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/"
                                      + curr_event.images, "external_links": curr_event.external_links,
                            'is_free': curr_event.subscription_fee == 0,
                            'feedback_count': UserFeedback.objects.filter(event_id=curr_event.id).count(),
                            'event_status': event_status
                            }

            if is_subscriber:
                # check for subscription
                subscription_list = Subscription.objects.filter(
                    user_id=user_logged_in, event_id=curr_event.id, is_active=True)
                if subscription_list:
                    is_subscribed = True
                else:
                    is_subscribed = False
                response_obj['is_subscribed'] = is_subscribed

                try:
                    # check if the event is wish-listed
                    WishList.objects.get(user_id=user_logged_in,
                                         event_id=curr_event.id, is_active=True)
                    response_obj['is_wishlisted'] = True
                except WishList.DoesNotExist:
                    response_obj['is_wishlisted'] = False

                try:
                    UserFeedback.objects.get(user_id=user_logged_in, event_id=curr_event.id, is_active=True)
                    feedback_given = True
                except UserFeedback.DoesNotExist:
                    feedback_given = False
                response_obj['feedback_given'] = feedback_given

            data.append(response_obj)

        return api_success_response(message="List of events", data=data)

    def create(self, request, *args, **kwargs):
        """
        Create Api for Event
        """
        request.data['type'] = request.data.pop('event_type', None)
        self.serializer_class = EventSerializer
        response = super(EventViewSet, self).create(request, *args, **kwargs)
        response.data['event_type'] = response.data.pop('type')
        response.data['images'] = \
            "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/" + response.data[
                'images']
        response.data['self_organised'] = True
        response.data['event_status'] = EVENT_STATUS['default']
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve Api for Event
        """
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        user_logged_in = user_id

        try:
            user_role = UserProfile.objects.get(user_id=user_logged_in).role.role
        except Exception:
            return api_error_response(
                message="Not able to fetch the role of the logged in user", status=500)

        event_id = int(kwargs.get('pk'))
        try:
            curr_event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return api_error_response(message="Given event {} does not exist".format(event_id))

        event_status = EVENT_STATUS['default']
        if not curr_event.is_active and not curr_event.is_cancelled:
            event_status = EVENT_STATUS['completed']
        if not curr_event.is_active and curr_event.is_cancelled:
            event_status = EVENT_STATUS['cancelled']

        if user_role != 'subscriber':
            invitee_list = Invitation.objects.filter(event=curr_event.id,
                                                     event__event_created_by_id=user_logged_in,
                                                     is_active=True)

            self_organised = (curr_event.event_created_by.id == user_logged_in)
            invitee_data = []
            for invited in invitee_list:
                response_obj = {'invitation_id': invited.id, 'email': invited.email}
                if invited.user is not None:
                    try:
                        user_profile = UserProfile.objects.get(user=invited.user.id)
                        response_obj['user'] = {'user_id': invited.user.id,
                                                'name': user_profile.name,
                                                'contact_number': user_profile.contact_number,
                                                'address': user_profile.address,
                                                'organization': user_profile.organization}
                    except UserProfile.DoesNotExist:
                        pass
                response_obj['discount_percentage'] = invited.discount_percentage
                invitee_data.append(response_obj)
            data = {"id": curr_event.id, "name": curr_event.name, "date": curr_event.date, "time": curr_event.time,
                    "location": curr_event.location, "event_type": curr_event.type.id,
                    "description": curr_event.description, "no_of_tickets": curr_event.no_of_tickets,
                    "sold_tickets": curr_event.sold_tickets, "subscription_fee": curr_event.subscription_fee,
                    "images": "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/" + curr_event.images,
                    "external_links": curr_event.external_links, "invitee_list": invitee_data,
                    "self_organised": self_organised, 'event_status': event_status,
                    'feedback_count': UserFeedback.objects.filter(event_id=curr_event.id).count()}

            return api_success_response(message="event details", data=data, status=200)
        else:
            data = {"id": curr_event.id, "name": curr_event.name,
                    "date": curr_event.date, "time": curr_event.time,
                    "location": curr_event.location, "event_type": curr_event.type.id,
                    "description": curr_event.description,
                    "subscription_fee": curr_event.subscription_fee,
                    "no_of_tickets": curr_event.no_of_tickets,
                    "images": "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/" + curr_event.images,
                    "external_links": curr_event.external_links, 'event_status': event_status
                    }
            try:
                WishList.objects.get(user_id=user_logged_in, event_id=curr_event.id, is_active=True)
                wishlisted = True
            except WishList.DoesNotExist:
                wishlisted = False
            is_subscribed = False
            try:
                UserFeedback.objects.get(user_id=user_logged_in, event_id=event_id, is_active=True)
                feedback_given = True
            except UserFeedback.DoesNotExist:
                feedback_given = False
            try:
                subscription_list = Subscription.objects.filter(
                    user_id=user_id, event_id=curr_event.id,
                    is_active=True)
                if subscription_list:
                    is_subscribed = True
                    no_of_tickets_bought = int(sum(list(
                        subscription_list.values_list('no_of_tickets', flat=True))))
                    if curr_event.subscription_fee <= 0:
                        # Free event
                        total_amount_paid = 0
                        total_discount_given = 0
                        discount_percentage = 0
                    else:
                        # paid event
                        refund_queryset = Subscription.objects.filter(user=user_id, event=event_id,
                                                                      payment__isnull=False, payment__status=3,
                                                                      is_active=True)
                        refund_amount = int(sum(list(
                            refund_queryset.values_list('payment__total_amount', flat=True))))
                        discount_updated = int(sum(
                            refund_queryset.values_list('payment__discount_amount', flat=True)))

                        total_amount_paid = int(sum(list(
                            Subscription.objects.filter(user=user_id, event=event_id,
                                                        payment__isnull=False, payment__status=0,
                                                        is_active=True).values_list
                            ('payment__total_amount', flat=True)))) - refund_amount
                        total_discount_given = int(sum(list(
                            Subscription.objects.filter(user=user_id, event=event_id,
                                                        payment__isnull=False, payment__status=0,
                                                        is_active=True).values_list
                            ('payment__discount_amount', flat=True)))) - discount_updated
                        try:
                            discount_percentage = \
                                Invitation.objects.get(user_id=user_id,
                                                       event_id=curr_event.id,
                                                       is_active=True).discount_percentage
                        except Invitation.DoesNotExist:
                            discount_percentage = 0
                    created_on = subscription_list.order_by('created_on')[0].created_on
                    data["subscription_details"] = {
                        "no_of_tickets_bought": no_of_tickets_bought,
                        "amount_paid": total_amount_paid,
                        "discount_given": total_discount_given,
                        "discount_percentage": discount_percentage,
                        "created_on": created_on
                    }
                else:
                    data["subscription_details"] = {}
                    try:
                        discount_allotted = \
                            Invitation.objects.get(user=user_id,
                                                   event=curr_event.id,
                                                   is_active=True).discount_percentage
                    except Invitation.DoesNotExist:
                        discount_allotted = 0
                    data['discount_percentage'] = discount_allotted
            except Subscription.DoesNotExist:
                try:
                    discount_allotted = Invitation.objects.get(user=user_id,
                                                               event=curr_event.id,
                                                               is_active=True).discount_percentage
                except Invitation.DoesNotExist:
                    discount_allotted = 0
                data['discount_percentage'] = discount_allotted
                data["subscription_details"] = dict()
            data['is_wishlisted'] = wishlisted
            data["is_subscribed"] = is_subscribed
            data['feedback_given'] = feedback_given
            return api_success_response(message="Event details", data=data, status=200)

    def destroy(self, request, *args, **kwargs):
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        event_id = int(kwargs.get('pk'))
        data = request.data
        message = data.get("message", "")
        try:
            event = self.queryset.get(id=event_id)
        except Event.DoesNotExist:
            return api_error_response(message="Given event id {} does not exist".format(event_id))

        if self.queryset.get(id=event_id).event_created_by.id != user_id:
            return api_error_response(
                message="You are not the organizer of this event {}".format(event_id), status=400)

        user_obj = Subscription.objects.filter(event=event_id).select_related('user').annotate(
            email=F('user__email'), users_id=F('user__id')).values("email", "users_id")
        email_ids = list({_["email"] for _ in user_obj})
        user_ids = list({_["users_id"] for _ in user_obj})
        self.queryset.filter(id=event_id).update(is_cancelled=True)
        self.queryset.filter(id=event_id).update(is_active=False)
        send_email_sms_and_notification(action_name="event_deleted",
                                        email_ids=email_ids,
                                        message=message,
                                        event_name=event.name,
                                        user_ids=user_ids,
                                        event_id=event_id)
        return api_success_response(message="Event successfully deleted", status=200)

    def update(self, request, *args, **kwargs):
        """
        Function to update a particular event
        :param request: body containing changes to be made
        :param kwargs: contains event id from the url given
        :return: changed response of an event
        """
        token = get_authorization_header(request).split()[1]
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload['user_id']
        event_id = int(kwargs.get('pk'))
        data = request.data
        user_logged_in = user_id
        try:
            user_role = UserProfile.objects.get(user_id=user_logged_in).role.role
        except Exception:
            return api_error_response(
                message="Not able to fetch the role of the logged in user", status=500)
        if user_role == 'subscriber':
            return api_error_response(
                message="A subscriber cannot change an event details", status=500)

        if self.queryset.get(id=event_id).event_created_by.id != user_logged_in:
            return api_error_response(
                message="You are not the organizer of this event {}".format(event_id), status=400)
        try:
            event_obj = Event.objects.get(id=event_id)
            prev_name = event_obj.name
            prev_location = event_obj.location
            prev_date = event_obj.date
            prev_time = event_obj.time
        except Event.DoesNotExist:
            return api_error_response(message=f"Event with id {event_id} does not exist",
                                      status=400)
        try:
            partial = kwargs.pop('partial', False)
            if 'event_type' in request.data:
                request.data['type'] = request.data.pop('event_type')
            serializer = EventSerializer(event_obj, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer.data['images'] = "https://s3.ap-south-1.amazonaws.com/backend-bucket-bits-pilani/" + \
                                        serializer.data['images'],
            serializer.data['event_type'] = serializer.data.pop('type')
        except Exception:
            return api_error_response(message="Some internal error coming while updating the event",
                                      status=500)
        event_name = event_obj.name
        field_list = []
        prev_list = []
        next_list = []
        if 'name' in data:
            field_list.append("name")
            prev_list.append(prev_name)
            next_list.append(data.get('name'))
        if 'location' in data:
            field_list.append("location")
            prev_list.append(prev_location)
            next_list.append(data.get('location'))
        if 'date' in data:
            field_list.append("date")
            prev_list.append(str(prev_date))
            next_list.append(data.get('date'))
        if 'time' in data:
            field_list.append("time")
            prev_list.append(str(prev_time))
            next_list.append(data.get('time'))

        field = ", ".join(field_list)
        prev_value = ", ".join(prev_list)
        next_value = ", ".join(next_list)

        user_obj = Subscription.objects.filter(event=event_id).select_related('user').annotate(
            email=F('user__email'), users_id=F('user__id')).values("email", "users_id")
        email_ids = list({_["email"] for _ in user_obj})
        user_ids = list({_["users_id"] for _ in user_obj})
        if field:
            send_email_sms_and_notification(action_name="event_updated",
                                            email_ids=email_ids,
                                            field=field,
                                            prev_value=prev_value,
                                            next_value=next_value,
                                            event_name=event_name,
                                            user_ids=user_ids,
                                            event_id=event_id)
        return api_success_response(data=serializer.data, status=200)