"""
Added core related api view here
"""
import json
import jwt
from datetime import date

import requests
from django.db.models import F, Q, Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header

from core.models import Event, Subscription, EventType
from core.serializers import EventTypeSerializer
from eon_backend.settings import EVENT_URL

from utils.common import api_success_response, api_error_response
from utils.helper import send_email_sms_and_notification
from eon_backend.settings import SECRET_KEY, LOGGER_SERVICE
from utils.permission import IsOrganizer
from utils.constants import EVENT_STATUS, MONTH, PAYMENT_URL

logger = LOGGER_SERVICE


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_event_types(request):
    """
    Get api method for event type
    """
    event_type = EventType.objects.filter(is_active=True)
    serializer = EventTypeSerializer(event_type, many=True)
    logger.log_info("Event type GET operation is successful")
    return api_success_response(data=serializer.data)


class SubscriberNotify(APIView):
    """
        Created api method related to subscriber
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.filter(is_active=True)

    def post(self, request):
        """
        Post api method for subscriber notify
        """
        data = request.data
        event_id = data.get("event_id", None)
        message = data.get("message", "")
        _type = data.get("type", "reminder").lower()
        if event_id:
            event_name = Event.objects.values_list("name", flat=True).get(id=event_id)
            if event_name:
                self.queryset = self.queryset.filter(event=event_id)
                response = self.queryset.select_related('user'). \
                    annotate(email=F('user__email'),
                             users_id=F('user__id')).values("email",
                                                            "users_id")
                email_ids = list({_["email"] for _ in response})
                user_ids = list({_["users_id"] for _ in response})
                if _type == "reminder":
                    action_name = "event_reminder"
                else:
                    action_name = "send_updates"
                send_email_sms_and_notification(action_name=action_name,
                                                email_ids=email_ids,
                                                message=message,
                                                event_name=event_name,
                                                user_ids=user_ids,
                                                event_id=event_id)
                logger.log_info(f"Subscribers notified successfully for event {event_id}.")
                return api_success_response(message="Subscribers notified successfully.")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def send_mail_to_a_friend(request):
    """
        Function to send mail to an email_id.
        :param request: email_id: email_id of a friend list_object or string
        :return:
    """

    data = json.loads(request.body)
    email = data.get("email_id")
    event_id = data.get("event_id")
    if not (event_id and email):
        logger.log_error("Event_id or email is missing in the request")
        return api_error_response(message="Please provide necessary details", status=400)
    if isinstance(email, str):
        email = [email]
    message = data.get("message")
    try:
        event_name = Event.objects.get(id=event_id).name
    except Event.DoesNotExist:
        logger.log_error("Invalid email id")
        return api_error_response(message="Invalid email id", status=400)
    send_email_sms_and_notification(action_name="user_share",
                                    message=message,
                                    url=EVENT_URL + str(event_id),
                                    event_name=event_name,
                                    email_ids=email)
    logger.log_info(f"Mail send successfully to the friend by user {email} for event {event_id}")
    return api_success_response(message="Mail send successfully", status=200)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsOrganizer])
def get_event_summary(request):
    """
    API to return summary of ongoing events organized by the user
    :param request: organizer id
    :return: data object returning the event details like sold tickets, revenue etc.
    """
    token = get_authorization_header(request).split()[1]
    payload = jwt.decode(token, SECRET_KEY)
    user_id = payload['user_id']
    search_text = request.GET.get("search", None)
    event_status_filter = request.GET.get('event_status', EVENT_STATUS['all'])
    today = date.today()
    queryset = Event.objects.filter(event_created_by=user_id).order_by('id')
    queryset.filter(date__lt=str(today)).update(is_active=False)
    total_revenue, revenue_cancelled_events, revenue_completed_events, revenue_ongoing_events = 0, 0, 0, 0

    if event_status_filter.lower() == EVENT_STATUS['completed']:
        queryset = queryset.filter(is_active=False, is_cancelled=False)

    elif event_status_filter.lower() == EVENT_STATUS['cancelled']:
        queryset = queryset.filter(is_active=False, is_cancelled=True)

    elif event_status_filter.lower() == EVENT_STATUS['default']:
        queryset = queryset.filter(date__gte=str(today), is_active=True)

    if search_text:
        queryset = queryset.filter(Q(location__icontains=search_text) | Q(name__icontains=search_text))

    cancelled_events, completed_events, ongoing_events, total_events = 0, 0, 0, queryset.count()
    data = {'event_list': []}
    event_name_list = []
    event_revenue_list = []
    event_remaining_tickets = []
    event_sold_tickets = []
    try:
        for event in queryset:
            if event.subscription_fee == 0:
                revenue = 0
            else:
                total_amount = Subscription.objects.filter(event=event.id,
                                                           is_active=True).aggregate(Sum("amount"))
                if total_amount["amount__sum"]:
                    revenue = total_amount["amount__sum"]
                else:
                    revenue = 0
                total_revenue += revenue
            event_status = EVENT_STATUS['default']
            if event.is_cancelled:
                event_status = EVENT_STATUS['cancelled']
                revenue_cancelled_events += revenue
                cancelled_events += 1
            if not event.is_active and not event.is_cancelled:
                event_status = EVENT_STATUS['completed']
                revenue_completed_events += revenue
                completed_events += 1
            if event_status == EVENT_STATUS['default']:
                revenue_ongoing_events += revenue
                ongoing_events += 1

            data['event_list'].append({'key': event.id,
                                       'name': event.name,
                                       'total_tickets': event.no_of_tickets,
                                       'sold_tickets': event.sold_tickets,
                                       'revenue': revenue,
                                       'location': event.location,
                                       'status': event_status})
            event_name_list.append(event.name)
            event_revenue_list.append(revenue)
            event_remaining_tickets.append(event.no_of_tickets-event.sold_tickets)
            event_sold_tickets.append(event.sold_tickets)
        data['total_revenue'] = total_revenue
        data['total_events'] = total_events
        data['ongoing_events'] = ongoing_events
        data['completed_events'] = completed_events
        data['cancelled_events'] = cancelled_events
        data['revenue_ongoing_events'] = revenue_ongoing_events
        data['revenue_completed_events'] = revenue_completed_events
        data['revenue_cancelled_events'] = revenue_cancelled_events
        data['ticket_graph_object'] = {
            'name_list': event_name_list,
            'revenue_list': event_revenue_list,
            'remaining_tickets': event_remaining_tickets,
            'sold_tickets': event_sold_tickets
        }
        monthly_data = get_month_wise_data(queryset)
        data['monthly_event_count'] = monthly_data['events']
        data['monthly_revenue'] = monthly_data['revenue']

    except Exception as err:
        logger.log_error(str(err))
        return api_error_response(message="Some internal error occur", status=500)
    logger.log_info(f"Analytics successfully sent for events of organizer with user_id {user_id}")
    return api_success_response(message="Summary of all events", data=data, status=200)


def get_month_wise_data(queryset):
    """
    This function will calculate month wise stats of events
    :param queryset: queryset object of events
    :return: Events count
    """
    queryset = queryset.filter(date__year=date.today().year)
    event_count = [
        {
            'name': EVENT_STATUS['default'],
            'data': []
        },
        {
            'name': EVENT_STATUS['completed'],
            'data': []
        },
        {
            'name': EVENT_STATUS['cancelled'],
            'data': []
        }
    ]

    monthly_revenue = []
    for month in range(1, 13):
        current_queryset = queryset.filter(date__month=month)
        ongoing_events = current_queryset.filter(is_active=True, is_cancelled=False).count()
        completed_events = current_queryset.filter(is_active=False, is_cancelled=False).count()
        cancelled_events = current_queryset.filter(is_active=False, is_cancelled=True).count()
        event_count[0]['data'].append(ongoing_events)
        event_count[1]['data'].append(completed_events)
        event_count[2]['data'].append(cancelled_events)

        event_ids = current_queryset.values_list('id', flat=True)
        monthly_revenue.append(get_month_wise_revenue(event_ids))

    return {'events': event_count, 'revenue': monthly_revenue}


def get_month_wise_revenue(event_ids):
    """
    This function will return total revenue for a specific event_ids given
    :param event_ids: list of event ids
    :return: sum of revenue generated from all events
    """
    total_amount = Subscription.objects.filter(event__in=event_ids,
                                               is_active=True).aggregate(Sum("amount"))
    if total_amount["amount__sum"]:
        revenue = total_amount["amount__sum"]
    else:
        revenue = 0

    return revenue
