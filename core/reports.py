from django.db.models import Case, When, Value, CharField, F, Sum, Q, Count, IntegerField
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
                'event')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=False)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=False).select_related('event')

    elif event_status == "Cancelled":
        if event_name:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=True)
            events_queryset = events_queryset.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=True).select_related(
                'event')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=False, is_cancelled=True)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=False,
                                                                      event__is_cancelled=True).select_related('event')
    elif event_status == "Ongoing":
        if event_name:
            events_queryset = Event.objects.filter(is_active=True, is_cancelled=False)
            events_queryset = events_queryset.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=True,
                                                                      event__is_cancelled=False).select_related(
                'event')
            event_which_has_subscribers = event_which_has_subscribers.filter(
                Q(event__name__iexact=event_name) | Q(event__event_created_by__email__icontains=event_name))
        else:
            events_queryset = Event.objects.filter(is_active=True, is_cancelled=False)
            event_which_has_subscribers = Subscription.objects.filter(event__is_active=True,
                                                                      event__is_cancelled=False).select_related('event')
    else:
        if event_name:
            events_queryset = Event.objects.filter(
                Q(name__iexact=event_name) | Q(event_created_by__email__icontains=event_name))
            event_which_has_subscribers = Subscription.objects.filter(Q(event__name__iexact=event_name) | Q(
                event__event_created_by__email__icontains=event_name)).select_related(
                'event')
        else:
            events_queryset = Event.objects.all()
            event_which_has_subscribers = Subscription.objects.all().select_related('event')

    events_queryset = events_queryset.select_related('event_created_by')
    event_organisers = events_queryset.values('event_created_by').annotate(email=F('event_created_by__email'),
                                                                           completed=Count(Case(
                                                                               When(is_active=False, is_cancelled=False,
                                                                                    then=1),
                                                                               output_field=IntegerField())),
                                                                           on_going=Count(Case(
                                                                               When(is_active=True, is_cancelled=False,
                                                                                    then=1),
                                                                               output_field=IntegerField())),
                                                                           cancelled=Count(Case(
                                                                               When(is_active=False, is_cancelled=True,
                                                                                    then=1),
                                                                               output_field=IntegerField())))

    line_chart_organisers = []
    line_chart_completed = []
    line_chart_on_going = []
    line_chart_cancelled = []
    for event_organiser in event_organisers:
        line_chart_organisers.append(event_organiser['email'].split('@')[0])
        line_chart_completed.append(event_organiser['completed'])
        line_chart_on_going.append(event_organiser['on_going'])
        line_chart_cancelled.append(event_organiser['cancelled'])

    event_names_and_popularity = events_queryset.annotate(
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

    all_event_names = []
    all_event_sold_tickets = []
    all_event_no_of_tickets = []
    all_event_status = []

    for event_and_popularity in event_names_and_popularity:
        all_event_names.append(event_and_popularity.name)
        all_event_sold_tickets.append(event_and_popularity.sold_tickets)
        all_event_no_of_tickets.append(event_and_popularity.no_of_tickets)
        all_event_status.append(event_and_popularity.status)


    event_completed_count = len(events_queryset.filter(is_active=False, is_cancelled=False))
    event_on_going_count = len(events_queryset.filter(is_active=True, is_cancelled=False))
    event_cancelled_count = len(events_queryset.filter(is_active=False, is_cancelled=True))

    event_which_has_subscribers_1 = event_which_has_subscribers.filter(id_payment__isnull=False)
    event_which_has_subscribers_1 = event_which_has_subscribers_1.values('event').annotate(
        final_amount=Sum('amount'), total_sold_tickets=F('event__sold_tickets'),
        total_tickets=F('event__no_of_tickets'), name=F('event__name'), event_created_by=F('event__event_created_by__email'),
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

    event_which_has_subscribers_3 = event_which_has_subscribers.filter(id_payment__isnull=True)
    event_which_has_subscribers_3 = event_which_has_subscribers_3.values('event').annotate(
        final_amount=Coalesce('amount', 0), total_sold_tickets=F('event__sold_tickets'),
        total_tickets=F('event__no_of_tickets'), name=F('event__name'), event_created_by=F('event__event_created_by__email'),
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

    event_which_has_subscribers = event_which_has_subscribers_1.union(event_which_has_subscribers_3)
    total_revenue = event_which_has_subscribers.aggregate(Sum('final_amount'))

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

    total_count = len(event_which_has_subscribers) + len(events_not_subscribed)
    if all_event_names:
        res = max(all_event_names, key=len)
        max_length = len(res)
        max_length = max_length * 6.12
    else:
        max_length = 2

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
                            backgroundColor=['rgba(0,255,127, 0.75)',
                                             'rgba(255,140,0, 0.75)',
                                             'rgba(255,0,0, 0.75)'
                                             ],
                            borderWidth=1)]),
                   completed=line_chart_completed,
                   ongoing=line_chart_on_going,
                   cancelled=line_chart_cancelled,
                   event_organisers=line_chart_organisers,
                   max_length=max_length,
                   data2=dict(labels=all_event_names, datasets=[
                       dict(label="Total tickets",
                            data=all_event_no_of_tickets,
                            backgroundColor='rgba(255,140,0,0.2)',
                            borderColor='rgba(255,140,0,0.2)',
                            borderWidth=1,
                            xAxisID="bar-x-axis1"),
                       dict(label="Sold tickets",
                            data=all_event_sold_tickets,
                            backgroundColor='rgba(255,140,0,1)',
                            borderColor='rgba(255,140,0,1)',
                            borderWidth=1,
                            xAxisID="bar-x-axis2")
                   ]),
                   )
    return content
