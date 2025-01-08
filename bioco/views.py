import juntagrico
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
