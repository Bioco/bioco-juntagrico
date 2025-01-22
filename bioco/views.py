from django.utils import timezone
from datetime import timedelta
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.dao.jobdao import JobDao
from juntagrico.util.messages import home_messages
from django.contrib.auth.decorators import login_required
from juntagrico.dao.deliverydao import DeliveryDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.util.pdf import render_to_pdf_storage, render_to_pdf_http
from juntagrico.util.temporal import weekdays
from django.shortcuts import render
from juntagrico.dao.depotdao import DepotDao

# this is a copy from juntagrico/views.py but showing ALL deliveries, not filtered by date or subscription
@login_required
def deliveries(request):
    '''
    All deliveries to be sorted etc.
    '''
    deliveries = DeliveryDao.all_deliveries_order_by_delivery_date_desc()
    renderdict = {
        'deliveries': deliveries,
        'menu': {'deliveries': 'active'},
    }

    return render(request, 'deliveries.html', renderdict)



@login_required
def home(request):
    '''
    Overview on juntagrico

    TODO The original view goes only to +14 days, but then we often get an empty list because everything is booked out
    '''
    start = timezone.now()
    end = start + timedelta(365)
    NUM_NEXT_JOBS = 10
    next_jobs = set([j for j in JobDao.get_jobs_for_time_range(start, end) if j.free_slots > 0][:NUM_NEXT_JOBS])
    pinned_jobs = set([j for j in JobDao.get_pinned_jobs() if j.free_slots > 0])
    next_promotedjobs = set([j for j in JobDao.get_promoted_jobs() if j.free_slots > 0])
    messages = getattr(request, 'member_messages', []) or []
    messages.extend(home_messages(request))
    request.member_messages = messages
    renderdict = {
        'jobs': sorted(next_jobs.union(pinned_jobs).union(next_promotedjobs), key=lambda sort_job: sort_job.time),
        'areas': ActivityAreaDao.all_visible_areas_ordered(),
    }
    return render(request, 'home.html', renderdict)


# this is a copy from generate_depot_list.py to load the PDF on the fly instead of pregeneration
# TODO get generation working
def depot_overview_direct(request):
    depot_dict = {
        'subscriptions': SubscriptionDao.all_active_subscritions(),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_ordered(),
        'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                     DepotDao.distinct_weekdays_for_depot_list()},
        'messages': ListMessageDao.all_active()
    }

    return render_to_pdf_http('exports/depot_overview.html', depot_dict, 'depotlist.pdf')

    # if too slow use ugly HTML instead:
    # return  render(request, 'exports/depot_overview.html', depot_dict)
