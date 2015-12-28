import datetime

from django.test import TestCase

from app.models import Node
from app.utils import daily_aggregator

# Create your tests here.

# woops - no tests yet


class DailyBreakdownTestCase(TestCase):

    def setUp(self):
        self.day_one = datetime.datetime(year=2015, month=11, day=25, hour=12, minute=10)
        self.day_two = datetime.datetime(year=2015, month=11, day=26)
        self.day_three = datetime.datetime(year=2015, month=11, day=27)
        self.day_four = datetime.datetime(year=2015, month=11, day=28)

    def create_node(self, timestamp, total=0):
        node = Node.objects.create(
            livetvusername="taddeimania",
            current_total=total,
        )
        node.timestamp = timestamp
        node.save()
        return node

    def test_daily_aggregator_returns_list_of_namedtuples_given_one_day_of_data(self):
        self.create_node(self.day_one, total=6)
        self.create_node(self.day_one, total=1)
        self.create_node(self.day_one, total=3)
        self.create_node(self.day_one, total=0)
        qs = Node.objects.filter(livetvusername="taddeimania")
        aggregate_total = daily_aggregator(qs)
        self.assertEqual(len(aggregate_total), 1)
        self.assertEqual(aggregate_total[0].mean, 2.5)
        self.assertEqual(aggregate_total[0].max, 6)
        self.assertEqual(aggregate_total[0].day, '2015-11-25')
        self.assertEqual(aggregate_total[0].minutes, 0.33)

    def test_daily_aggregator_returns_list_of_namedtuples_given_multi_day_data(self):
        self.create_node(self.day_one, total=6)
        self.create_node(self.day_one, total=1)
        self.create_node(self.day_one, total=3)
        self.create_node(self.day_one, total=0)
        self.create_node(self.day_two, total=9)
        self.create_node(self.day_two, total=10)
        self.create_node(self.day_two, total=20)
        self.create_node(self.day_two, total=0)
        self.create_node(self.day_two, total=0)
        qs = Node.objects.filter(livetvusername="taddeimania")
        aggregate_total = daily_aggregator(qs)
        self.assertEqual(len(aggregate_total), 2)
        self.assertEqual(aggregate_total[0].mean, 7.8)
        self.assertEqual(aggregate_total[0].max, 20)
        self.assertEqual(aggregate_total[0].day, '2015-11-26')
        self.assertEqual(aggregate_total[1].mean, 2.5)
        self.assertEqual(aggregate_total[1].max, 6)
        self.assertEqual(aggregate_total[1].day, '2015-11-25')
