from django.db.models import Case, When, Value, CharField, F, Sum, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render

from core.models import Event, Subscription


def event_summary(request):
    content = event_analysis_report(request)
    return render(request, 'core/event_analysis.html', content)


def filtered_event_summary(request):
    event_status = request.GET.get('event_status', None)
    event_name = request.GET.get('event_name', None)
    content = event_analysis_report(request, event_status=event_status, event_name=event_name)
    data = []
    for entry in content['events_not_subscribed']:
        temp_data = {
            "name": entry.name,
            "no_of_tickets": entry.no_of_tickets,
            "sold_tickets": entry.sold_tickets,
            "status": entry.status,
            "event_created_by": entry.event_created_by.email
        }
        data.append(temp_data)
    content['events_not_subscribed'] = data

    data = []
    for entry in content['event_which_has_subscribers']:
        temp_data = {
            "name": entry['name'],
            "total_tickets": entry['total_tickets'],
            "total_sold_tickets": entry['total_sold_tickets'],
            "status": entry['status'],
            "final_amount": entry['final_amount'],
            "event_created_by": entry['event_created_by']
        }
        data.append(temp_data)
    content['event_which_has_subscribers'] = data
    return JsonResponse(content)


def event_analysis_report(request, event_status=None, event_name=None):
    """ Filtering on basis of event status if given otherwise all entries """

    if event_status == "Completed":
        if event_name:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=False)
            events_queryset = events_queryset.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=False).select_related(
                'event',
                'payment')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=False)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=False).select_related('event',
                                                                                                                'payment')
    elif event_status == "Cancelled":
        if event_name:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=True)
            events_queryset = events_queryset.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=True).select_related(
                'event',
                'payment')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=True)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=True).select_related('event',
                                                                                                               'payment')
    elif event_status == "Ongoing":
        if event_name:
            events_queryset = Event.objects.filter(is_active=True, is_cancelled=False)
            events_queryset = events_queryset.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=True,
                                                                      event__is_cancelled=False).select_related(
                'event',
                'payment')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=True, is_cancelled=False)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=True,
                                                                      event__is_cancelled=False).select_related('event',
                                                                                                                'payment')
    else:
        if event_name:
            events_queryset = Event.objects.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name)).select_related(
                'event', 'payment')
        else:
            events_queryset = Event.objects.all()
            event_which_has_subscribers = Subscription.objects.all().select_related('event', 'payment')

    event_completed_count = len(events_queryset.filter(is_active=False, is_cancelled=False))
    event_on_going_count = len(events_queryset.filter(is_active=True, is_cancelled=False))
    event_cancelled_count = len(events_queryset.filter(is_active=False, is_cancelled=True))

    event_which_has_subscribers_1 = event_which_has_subscribers.filter(payment__isnull=False,
                                                                       no_of_tickets__gt=0)
    event_which_has_subscribers_1 = event_which_has_subscribers_1.values('event').annotate(
        final_amount=Sum('payment__total_amount'), total_sold_tickets=F('event__sold_tickets'),
        total_tickets=F('event__no_of_tickets'), name=F('event__name'),
        event_created_by=F('event__event_created_by__email'),
        status=Case(
            When(
                event__is_active=False,
                event__is_cancelled=False,
                then=Value("Completed"),
            ),
            When(
                event__is_active=True,
                event__is_cancelled=False,
                then=Value("Ongoing"),
            ),
            When(
                event__is_active=False,
                event__is_cancelled=True,
                then=Value("Cancelled"),
            ),
            output_field=CharField(),
        ))
    event_which_has_subscribers_2 = event_which_has_subscribers.filter(payment__isnull=False,
                                                                       no_of_tickets__lt=0)
    event_which_has_subscribers_2 = event_which_has_subscribers_2.values('event').annotate(
        final_amount=Sum('payment__total_amount') * (-1), total_sold_tickets=F('event__sold_tickets'),
        total_tickets=F('event__no_of_tickets'), name=F('event__name'),
        event_created_by=F('event__event_created_by__email'),
        status=Case(
            When(
                event__is_active=False,
                event__is_cancelled=False,
                then=Value("Completed"),
            ),
            When(
                event__is_active=True,
                event__is_cancelled=False,
                then=Value("Ongoing"),
            ),
            When(
                event__is_active=False,
                event__is_cancelled=True,
                then=Value("Cancelled"),
            ),
            output_field=CharField(),
        ))

    event_which_has_subscribers_3 = event_which_has_subscribers.filter(payment__isnull=True)
    event_which_has_subscribers_3 = event_which_has_subscribers_3.values('event').annotate(
        final_amount=Coalesce('payment__total_amount', 0), total_sold_tickets=F('event__sold_tickets'),
        total_tickets=F('event__no_of_tickets'), name=F('event__name'),
        event_created_by=F('event__event_created_by__email'),
        status=Case(
            When(
                event__is_active=False,
                event__is_cancelled=False,
                then=Value("Completed"),
            ),
            When(
                event__is_active=True,
                event__is_cancelled=False,
                then=Value("Ongoing"),
            ),
            When(
                event__is_active=False,
                event__is_cancelled=True,
                then=Value("Cancelled"),
            ),
            output_field=CharField(),
        ))

    event_which_has_subscribers = event_which_has_subscribers_1.union(event_which_has_subscribers_2)
    event_which_has_subscribers = event_which_has_subscribers.union(event_which_has_subscribers_3)
    total_revenue = event_which_has_subscribers.aggregate(Sum('final_amount'))
    event_which_has_subscribers = event_which_has_subscribers_1.union(event_which_has_subscribers_3)

    if total_revenue['final_amount__sum'] is None:
        total_revenue = 0
    else:
        total_revenue = total_revenue['final_amount__sum']

    event_ids_present_in_subscription = event_which_has_subscribers.values_list('event', flat=True)

    events_not_subscribed = events_queryset.filter(~Q(id__in=list(event_ids_present_in_subscription))).annotate(
        status=Case(
            When(
                is_active=False,
                is_cancelled=False,
                then=Value("Completed"),
            ),
            When(
                is_active=True,
                is_cancelled=False,
                then=Value("Ongoing"),
            ),
            When(
                is_active=False,
                is_cancelled=True,
                then=Value("Cancelled"),
            ),
            output_field=CharField(),
        ))
    events_not_subscribed = events_not_subscribed.select_related('event_created_by')

    total_count = len(event_which_has_subscribers) + len(events_not_subscribed)

    content = dict(event_completed_count=event_completed_count,
                   event_on_going_count=event_on_going_count,
                   event_cancelled_count=event_cancelled_count,
                   total_revenue=total_revenue,
                   event_which_has_subscribers=event_which_has_subscribers,
                   events_not_subscribed=events_not_subscribed,
                   total_count=total_count,
                   data=dict(labels=['Completed', 'Ongoing', 'Cancelled'], datasets=[
                       dict(label='User Table',
                            data=[event_completed_count, event_on_going_count, event_cancelled_count],
                            backgroundColor=['rgba(255, 99, 132, 0.2)',
                                             'rgba(54, 162, 235, 0.2)',
                                             'rgba(255, 206, 86, 0.2)',
                                             'rgba(75, 192, 192, 0.2)'],
                            borderColor=['rgba(255, 99, 132, 1)',
                                         'rgba(54, 162, 235, 1)',
                                         'rgba(255, 206, 86, 1)',
                                         'rgba(75, 192, 192, 1)'],
                            borderWidth=1)]))
    return content
