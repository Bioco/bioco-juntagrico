from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.util.pdf import render_to_pdf_storage, render_to_pdf_http
from juntagrico.util.temporal import weekdays
from django.shortcuts import render
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao

# this is a copy from generate_depot_list.py to load the PDF on the fly instead of pregeneration
# TODO get generation working
def depot_overview_direct(request):
    depot_dict = {
        'subscriptions': SubscriptionDao.all_active_subscritions(),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'extra_sub_categories': ExtraSubscriptionCategoryDao.categories_for_depot_list_ordered(),
        'depots': DepotDao.all_depots_order_by_code(),
        'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                     DepotDao.distinct_weekdays()},
        'messages': ListMessageDao.all_active()
    }

    return render_to_pdf_http('exports/depot_overview.html', depot_dict, 'depotlist.pdf')

    # if too slow use ugly HTML instead:
    # return  render(request, 'exports/depot_overview.html', depot_dict)
