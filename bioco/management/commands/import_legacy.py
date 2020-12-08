from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionSize
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.entity.subtypes import SubscriptionProduct

import datetime
from django.utils.timezone import make_aware
import traceback
import json

class Command(BaseCommand):
    help = 'Imports old bioco data'
    #
    # models_to_keep = [
    #     'auth.group',                             done
    #     'auth.user',                              done
    #     'my_ortoloco.abo',                        done
    #     'my_ortoloco.loco',                       done
    #     'my_ortoloco.depot',                      done
    #     'my_ortoloco.anteilschein',               todo
    #     'my_ortoloco.taetigkeitsbereich',         todo
    # ]

    def add_arguments(self, parser):
        parser.add_argument('db_file_name', type=str, help='A database dump optained with dumpdata to be imported')

    def handle(self, *args, **options):
        db_file_name = options['db_file_name']
        print(f"Opening {db_file_name}")
        with open(db_file_name, 'r') as infile:
            data = json.load(infile)

            self.create_abo_structure()

            self.run_import(data, 'auth.group',         'Group',    self.import_group)
            self.run_import(data, 'auth.user',          'User',     self.import_user)
            self.run_import(data, 'my_ortoloco.loco',   'Member',   self.import_member)  # must be after users
            self.run_import(data, 'my_ortoloco.depot',  'Depot',    self.import_depot)   # must be after members
            self.run_import(data, 'my_ortoloco.abo',    'Abo',      self.import_abo)     # must be after member and depot

            self.run_import(data, 'my_ortoloco.loco',   'Member',   self.import_member_second_pass)  # must be after abo
            self.run_import(data, 'my_ortoloco.abo',    'Abo',      self.import_abo_second_pass)     # must be after loco_second_pass

            self.sql_sequence_reset()

    def create_abo_structure(self):
        product = SubscriptionProduct()
        product.name = "Gemüse"
        product.description = "Gemüse"
        product.save()

        self.create_abo(product=product, pk=1, shares=1, name="Kein", long_name="Kein Gemüsekorb", people="0", size=0.0,
                        work=0, prize=0)
        self.create_abo(product=product, pk=2, shares=1, name="Mini", long_name="Halber Gemüsekorb", people="1-2",
                        size=0.5, work=2 * 5, prize=700)
        self.create_abo(product=product, pk=3, shares=2, name="Normal", long_name="Gemüsekorb", people="2-3", size=1.0,
                        work=2 * 10, prize=1200)
        self.create_abo(product=product, pk=4, shares=4, name="Doppelt", long_name="Doppelter Gemüsekorb", people="4-6",
                        size=2.0, work=2 * 20, prize=2200)

    def create_abo(self, product, pk, shares, name, long_name, people, size, work, prize):
        ssize = SubscriptionSize(pk=pk)
        ssize.name = name
        ssize.long_name = long_name
        ssize.units = size
        ssize.depot_list = True
        ssize.visible = True
        ssize.description = "Für " + people + " Personen"
        ssize.product = product
        ssize.save()

        stype = SubscriptionType(pk=pk)
        stype.name = ""
        stype.long_name = ""
        stype.size = ssize
        stype.shares = shares
        stype.required_assignments = work
        stype.required_core_assignments = 0
        stype.price = prize
        stype.visible = (size > 0)
        stype.trial = False
        stype.trial_days = 0
        stype.description = ssize.long_name
        stype.save()

    def run_import(self, data, model, title, command):
        for line in data:
            if line['model'] == model:
                try:
                    command(line)
                except:
                    print(f"{title} import failed for")
                    print(line)
                    raise

    def import_group(self, data):
        fields = data['fields']

        group = Group(pk=data['pk'])

        # intentionally not imported: group.permissions = []
        group.name = fields['name']
        group.save()

    def get_datetime(self, string):
        return make_aware(datetime.datetime.fromisoformat(string))

    def import_user(self, data):
        fields = data['fields']

        user = User(pk=data['pk'])
        user.email = fields['email']
        user.username = fields['username']
        user.date_joined = self.get_datetime(fields['date_joined'])
        user.first_name = fields['first_name']
        user.last_name = fields['last_name']
        user.is_superuser = fields['is_superuser']
        user.is_staff = fields['is_staff']
        user.is_active = fields['is_active']
        user.last_login  = self.get_datetime(fields['last_login'])
        user.password  = fields['password']

        user.save()

        # intentionally not imported: user.user_permissions = []
        if fields['groups']:
            print("groups :")
            print(fields['groups'])

        user.groups.set(fields['groups'])

    def import_abo(selfself, data):
        fields = data['fields']

        abo = Subscription(pk=data['pk'])
        abo.depot = Depot.objects.get(pk=fields['depot'])
        abo.future_depot = None
        abo.primary_member = None # filled in later in second pass
        abo.nickname = 'Abo ' + fields['number']
        abo.start_date = '2020-01-01' # TODO adjust all dates
        if fields['active']:
            abo.end_date = None
        else:
            abo.end_date = '2020-12-31'
        abo.notes = ""
        abo.save()

        if fields['active']:
            abo.activate(datetime.datetime.fromisoformat('2020-01-01'))
        else:
            abo.activate(datetime.datetime.fromisoformat('2020-01-01'))
            abo.cancel(datetime.datetime.fromisoformat('2020-01-01'))

    def import_abo_second_pass(self, data):
        fields = data['fields']
        abo = Subscription.objects.get(pk=data['pk'])
        abo.primary_member = Member.objects.get(pk=fields['primary_loco'])
        abo.save()

        size_mapping = {
            0: 1,
            1: 2,
            2: 3,
            4: 4,
        }
        subpart_type = size_mapping[fields['groesse']]
        #print(fields)

        subpart = SubscriptionPart(pk=data['pk'])
        subpart.subscription = Subscription.objects.get(pk=data['pk'])
        subpart.type = SubscriptionType.objects.get(pk=subpart_type)
        subpart.save()

        if fields['active']:
            subpart.activate(datetime.datetime.fromisoformat('2020-01-01'))
        else:
            subpart.activate(datetime.datetime.fromisoformat('2020-01-01'))
            subpart.cancel(datetime.datetime.fromisoformat('2020-01-01'))

    def import_member(self, data):
        if data['pk'] == 1: return  # intranet admin
        fields = data['fields']

        member = Member(pk=data['pk'])
        member.first_name = fields['first_name']
        member.last_name = fields['last_name']
        member.email = fields['email']
        member.phone = fields['phone']
        member.mobile_phone = fields['mobile_phone']
        member.addr_street = fields['addr_street']
        member.addr_zipcode = fields['addr_zipcode']
        member.addr_location = fields['addr_location']
        member.birthday = "1900-01-01" # we dont have any recorded - fields['birthday']
        # not existing fields['sex']
        member.abo = None # filled in in second pass
        member.user = User.objects.get(pk=fields['user'])
        member.iban = '' # not existing so far
        member.confirmed = fields['confirmed']
        member.reachable_by_email = True
        # canceled not writable on Heroku TODO why?
        #member.canceled = False
        #member.cancelation_date = None
        #member.end_date = None
        #member.inactive = False
        member.notes = 'Geschlecht: ' + fields['sex']

        member.save()

    def import_member_second_pass(self, data):
        if data['pk'] == 1: return  # intranet admin
        fields = data['fields']

        if not fields['abo']:
            return

        member = Member.objects.get(pk=data['pk'])
        member.foobar = "bar"
        member.subscription = Subscription.objects.get(pk=fields['abo'])
        member.save()

    def import_depot(self, data):
        fields = data['fields']
        depot = Depot(pk=data['pk'])

        depot.name = fields['name']
        depot.code = fields['code']
        depot.addr_zipcode = fields['addr_zipcode']
        depot.addr_street = fields['addr_street']
        depot.addr_location = fields['addr_location']
        depot.contact = Member.objects.get(pk=fields['contact'])
        depot.weekday = fields['weekday']
        depot.description = ''
        depot.latitude = fields['latitude']
        depot.longitude = fields['longitude']

        depot.save()

    def sql_sequence_reset(self):
        from django.core.management.color import no_style
        from django.db import connection

        sequence_sql = connection.ops.sequence_reset_sql(no_style(), [User, Group, Depot, Member, Subscription, SubscriptionPart, SubscriptionSize, SubscriptionType, SubscriptionProduct])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

#
#
# On heroku:
#
# groups :
# [2]
# groups :
# [2]
# Abo import failed for
# {'model': 'my_ortoloco.abo', 'fields': {'active': True, 'paid': True, 'depot': 16, 'groesse': 2, 'extra_abos': [], 'primary_loco': 42, 'number': '3'}, 'pk': 3}
# Traceback (most recent call last):
#   File "manage.py", line 10, in <module>
#     execute_from_command_line(sys.argv)
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/core/management/__init__.py", line 401, in execute_from_command_line
#     utility.execute()
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/core/management/__init__.py", line 395, in execute
#     self.fetch_command(subcommand).run_from_argv(self.argv)
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/core/management/base.py", line 330, in run_from_argv
#     self.execute(*args, **cmd_options)
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/core/management/base.py", line 371, in execute
#     output = self.handle(*args, **options)
#   File "/app/bioco/management/commands/import_legacy.py", line 45, in handle
#     self.run_import(data, 'my_ortoloco.abo',    'Abo',      self.import_abo)     # must be after member and depot
#   File "/app/bioco/management/commands/import_legacy.py", line 96, in run_import
#     command(line)
#   File "/app/bioco/management/commands/import_legacy.py", line 155, in import_abo
#     abo.activate('2020-01-01')
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/__init__.py", line 45, in activate
#     self.save()
#   File "/app/.heroku/python/lib/python3.8/site-packages/polymorphic/models.py", line 91, in save
#     return super(PolymorphicModel, self).save(*args, **kwargs)
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/db/models/base.py", line 753, in save
#     self.save_base(using=using, force_insert=force_insert,
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/db/models/base.py", line 777, in save_base
#     pre_save.send(
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/dispatch/dispatcher.py", line 177, in send
#     return [
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/dispatch/dispatcher.py", line 178, in <listcomp>
#     (receiver, receiver(signal=self, sender=sender, **named))
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/lifecycle/sub.py", line 24, in sub_pre_save
#     handle_activated_deactivated(instance, sender, sub_activated, sub_deactivated)
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/util/lifecycle.py", line 5, in handle_activated_deactivated
#     activated.send(sender=sender, instance=instance)
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/dispatch/dispatcher.py", line 177, in send
#     return [
#   File "/app/.heroku/python/lib/python3.8/site-packages/django/dispatch/dispatcher.py", line 178, in <listcomp>
#     (receiver, receiver(signal=self, sender=sender, **named))
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/lifecycle/sub.py", line 32, in handle_sub_activated
#     for member in instance.recipients:
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/subs.py", line 195, in recipients
#     return [m.member for m in self.recipients_qs.all()]
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/subs.py", line 189, in recipients_qs
#     return self.memberships_for_state.filter(
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/subs.py", line 203, in memberships_for_state
#     if self.state == 'waiting' or self.state == 'inactive':
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/__init__.py", line 84, in state
#     return SimpleStateModel.__state_dict.get(self.__state_code, 'error')
#   File "/app/.heroku/python/lib/python3.8/site-packages/juntagrico/entity/__init__.py", line 77, in __state_code
#     active = (self.activation_date is not None and self.activation_date <= now) << 0
# TypeError: '<=' not supported between instances of 'str' and 'datetime.date'
