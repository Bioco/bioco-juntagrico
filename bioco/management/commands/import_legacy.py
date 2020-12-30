from django.contrib.auth.models import User, Group, Permission
from django.core.management.base import BaseCommand, CommandError
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member, SubscriptionMembership
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionSize, SubscriptionType, SubscriptionProduct
from juntagrico.entity.share import Share
from juntagrico.entity.jobs import ActivityArea, RecuringJob, JobType, Assignment, JobExtraType, JobExtra

import datetime
from django.utils.timezone import make_aware
import json

ACTIVATION_DATE = '2020-01-01'
DEACTIVATION_DATE = '2020-01-02'

class Command(BaseCommand):
    help = 'Imports old bioco data'

    def add_arguments(self, parser):
        parser.add_argument('db_file_name', type=str, help='A database dump optained with dumpdata to be imported')

    def handle(self, *args, **options):
        db_file_name = options['db_file_name']
        print(f"=== Importing from {db_file_name} ===")
        with open(db_file_name, 'r') as infile:
            data = json.load(infile)

            self.create_abo_structure()
            self.create_job_extras()

            self.run_import(data, 'auth.group',                 'Group',        self.import_group)
            self.run_import(data, 'auth.user',                  'User',         self.import_user)
            self.run_import(data, 'my_ortoloco.loco',           'Member',       self.import_member)  # must be after users

            self.run_import(data, 'my_ortoloco.depot',          'Depot',        self.import_depot)   # must be after members
            self.run_import(data, 'my_ortoloco.abo',            'Abo',          self.import_abo)     # must be after member and depot
            self.run_import(data, 'my_ortoloco.anteilschein',   'Anteilschein', self.import_anteilschein)     # must be after member
            self.run_import(data, 'my_ortoloco.taetigkeitsbereich',   'Kernbereich', self.import_taetigkeitsbereich)     # must be after member
            self.run_import(data, 'my_ortoloco.jobtyp', 'Jobtyp', self.import_jobtyp)  # must be after members, aetigkeitsbereich
            self.run_import(data, 'my_ortoloco.job', 'Jobs', self.import_job)  # must be after members, jobtyp
            self.run_import(data, 'my_ortoloco.boehnli', 'Rüebli', self.import_assignment)  # must be after members, job

            self.run_import(data, 'my_ortoloco.loco',           'Member',       self.import_member_second_pass)  # must be after abo
            self.run_import(data, 'my_ortoloco.abo',            'Abo',          self.import_abo_second_pass)     # must be after loco_second_pass

            self.sql_sequence_reset()

        print("=== Import done ===")

    def create_job_extras(self):
        extra = JobExtraType()
        extra.name = "Auto"
        extra.display_empty = "<img src='/static/img/auto_red.png' title='Auto benötigt' width='32' />"
        extra.display_full = "<img src='/static/img/auto_green.png' title='Auto vorhanden' width='32' />"
        extra.save()

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

        # group.permissions are not imported but loaded from file
        # To list the internal code name for permissions use:
        # for p in Permission.objects.all(): print(p.codename + "\t\t" + p.name)
        group = Group(pk=data['pk'])
        group.name = fields['name']
        group.save()

        with open('initial_permissions.json') as json_file:
            perm_data = json.load(json_file)

        for key in perm_data:
            if group.name  == key:
                print(f"Importing {len(perm_data[key])} permissions for group '{key}'")
                for perm_code in perm_data[key]:
                    group.permissions.add(Permission.objects.get(codename=perm_code))

        if group.name not in perm_data.keys():
            print(f"No permissions found for group '{group.name }'")

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
        user.last_login = self.get_datetime(fields['last_login'])
        user.password = fields['password']
        user.save()

        user.groups.set(fields['groups'])

    def import_abo(self, data):
        fields = data['fields']

        abo = Subscription(pk=data['pk'])
        abo.depot = Depot.objects.get(pk=fields['depot'])
        abo.future_depot = None
        abo.primary_member = None # filled in later in second pass
        abo.nickname = 'Abo ' + fields['number']
        abo.start_date = ACTIVATION_DATE
        if fields['active']:
            abo.end_date = None
        else:
            abo.end_date = DEACTIVATION_DATE
        abo.notes = ""
        abo.save()

        if fields['active']:
            abo.activate(datetime.date.fromisoformat(ACTIVATION_DATE))
        else:
            abo.activate(datetime.date.fromisoformat(ACTIVATION_DATE))
            abo.deactivate(datetime.date.fromisoformat(DEACTIVATION_DATE))

    def import_anteilschein(self, data):
        fields = data['fields']

        if not fields['loco']:
            print(f"Share pk='{data['pk']}' without member - skipped.")
            return

        share = Share(pk=data['pk'])
        share.member = Member.objects.get(pk=fields['loco'])
        if fields['paid']:
            share.paid_date = datetime.date.fromisoformat(ACTIVATION_DATE)
            share.issue_date = datetime.date.fromisoformat(ACTIVATION_DATE)
            share.booking_date = datetime.date.fromisoformat(ACTIVATION_DATE)
        else:
            share.paid_date = None
            share.issue_date = None
            share.booking_date = None

        share.cancelled_date = None
        share.termination_date = None
        share.payback_date = None
        if fields['number']:
            share.number = fields['number']
            if int(fields['number']) != data['pk']:
                print(f"Share number {fields['number']} != pk {data['pk']}")
        else:
            # create a unique one, different from original numbers
            share.number = 1000000 + data['pk']
        share.sent_back = False
        share.notes = f'Imported from ID={data["pk"]}, number={fields["number"]}'
        share.save()

    def import_taetigkeitsbereich(self, data):
        fields = data['fields']
        ADMIN_MEMBER_ID = 1

        aa = ActivityArea(pk=data['pk'])

        aa.name = fields['name']
        aa.description = fields['description']
        aa.core = fields['core']
        if fields['coordinator'] == ADMIN_MEMBER_ID:
            coord = 107 # Admin user not created anymore - replace
        else:
            coord = fields['coordinator']
        aa.coordinator = Member.objects.get(pk=coord)
        aa.hidden = fields['hidden']
        aa.email = None
        aa.show_coordinator_phonenumber = True
        aa.save()

        for member in fields['locos']:
            if member == ADMIN_MEMBER_ID: continue
            aa.members.add(Member.objects.get(pk=member))

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

        sub = Subscription.objects.get(pk=data['pk'])
        subpart = SubscriptionPart(pk=data['pk'])
        subpart.subscription = sub
        subpart.deactivation_date = sub.deactivation_date
        subpart.cancellation_date = sub.cancellation_date
        subpart.activation_date = sub.activation_date
        subpart.creation_date = sub.creation_date
        subpart.type = SubscriptionType.objects.get(pk=subpart_type)
        subpart.save()

        if False:
            if fields['active']:
                subpart.activate(datetime.date.fromisoformat(ACTIVATION_DATE))
            else:
                subpart.activate(datetime.date.fromisoformat(ACTIVATION_DATE))
                subpart.deactivate(datetime.date.fromisoformat(DEACTIVATION_DATE))

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

    def import_jobtyp(self, data):
        desc_verteilfahrt = """
Du fährst zu den Depots. 
Du informierst dich über die Route zu den Depots http://bioco.ch/intranet-dokumente und den
aktuellen Verteilplan ("Verteilübersicht" im Intranet)

Bitte fülle das Fahrspesen-Rückforderungsformular aus und sende es an finanzen@bioco.ch.

Dieser Einsatz kann (muss aber nicht) mit dem vorhergehenden Verpacken gebucht werden.
Dafür bitte bei beiden Einsätzen eintragen. 

Der Zeitpunkt kann flexibel gewählt werden, so dass die Depots bis 16h beliefert sind, Start ab 11h.
"""

        desc_verpacken = """
Wir ernten unser Gemüse und erledigen sonstige Arbeiten.
Gute Schuhe und wetterfeste Kleidung anziehen.

Dieser Einsatz kann (muss aber nicht) mit dem nachfolgenden Verteilen gebucht werden.
Dafür bitte bei beiden Einsätzen eintragen. Es werden dann natürlich auch beide angerechnet.

Die Anzahl Körbe entnehmt ihr dem aktuellen Verteilplan ("Verteilübersicht" im Intranet).

Dauer ca. 2 - 3h."""

        desc = {5: desc_verteilfahrt, 6: desc_verteilfahrt, 163: desc_verpacken}
        if data['pk'] not in [5, 6, 163]: return

        fields = data['fields']

        JobType.objects.create(
            pk = data['pk'],
            name = fields['name'],
            displayed_name = fields['displayed_name'],
            description = desc[data['pk']],  # No HTML supported so far thus not using original field 'description'
            default_duration = fields['duration'],
            location = fields['location'],
            activityarea = ActivityArea.objects.get(pk=fields['bereich'])
        )

        if fields['car_needed']:
            JobExtra.objects.create(
                recuring_type = JobType.objects.get(pk=data['pk']),
                extra_type = JobExtraType.objects.get(pk=1)
            )

    def import_job(self, data):
        fields = data['fields']

        dt = self.get_datetime(fields["time"])
        if dt < make_aware(datetime.datetime.fromisoformat('2021-01-01T00:00:00')):
            return

        RecuringJob.objects.create(
            pk=data['pk'],
            type = JobType.objects.get(pk=fields['typ']),
            slots=fields["slots"],
            time = dt,
            multiplier = fields["multiplier"]
        )

    def import_assignment(self, data):
        fields = data['fields']

        try:
            job = RecuringJob.objects.get(pk=fields['job'])
        except:
            # Could not find matching job - probably in the past
            return

        Assignment.objects.create(
            pk=data['pk'],
            job=job,
            member=Member.objects.get(pk=fields['loco']),
            amount=1
        )

        if fields['with_car']:
            ass = Assignment.objects.get(pk=data['pk'])
            car = JobExtra.objects.get(recuring_type=job.type)
            #car = JobExtraType.objects.get(pk=1)
            ass.job_extras.add(car)

    def import_member_second_pass(self, data):
        if data['pk'] == 1: return  # intranet admin
        fields = data['fields']

        if not fields['abo']:
            return

        sub = Subscription.objects.get(pk=fields['abo'])
        SubscriptionMembership.objects.create(
            member=Member.objects.get(pk=data['pk']),
            subscription=sub,
            join_date=datetime.date.fromisoformat(ACTIVATION_DATE),
            leave_date=sub.deactivation_date
        )

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
