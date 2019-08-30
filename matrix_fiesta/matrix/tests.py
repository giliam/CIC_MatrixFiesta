import datetime

from django.test import TestCase

from matrix import models


class ProfileUserTestCase(TestCase):
    def setUp(self):
        current_year = datetime.datetime.now().year

        p_y_2019 = models.PromotionYear.objects.create(name="2019/2020", value=current_year, current=True)
        p_y_2018 = models.PromotionYear.objects.create(name="2018/2019", value=current_year-1, current=True)
        p_y_2017 = models.PromotionYear.objects.create(name="2017/2018", value=current_year-2, current=True)
        p_y_2016 = models.PromotionYear.objects.create(name="2016/2017", value=current_year-3, current=True)

        data = [ 
            {
                "firstname": "Foo_noces",
                "lastname": "Bar_noces",
                "year_entrance": p_y_2019,
                "cesure": False,
                "user": None
            }, {
                "firstname": "Foo_ces",
                "lastname": "Bar_ces",
                "year_entrance": p_y_2019,
                "cesure": True,
                "user": None
            }, {
                "firstname": "2AFoo_noces",
                "lastname": "2ABar_noces",
                "year_entrance": p_y_2018,
                "cesure": False,
                "user": None
            }, {
                "firstname": "2AFoo_ces",
                "lastname": "2ABar_ces",
                "year_entrance": p_y_2018,
                "cesure": True,
                "user": None
            }, {
                "firstname": "3AFoo_noces",
                "lastname": "3ABar_noces",
                "year_entrance": p_y_2017,
                "cesure": False,
                "user": None
            }, {
                "firstname": "3AFoo_ces",
                "lastname": "3ABar_ces",
                "year_entrance": p_y_2017,
                "cesure": True,
                "user": None
            }, {
                "firstname": "4AFoo_noces",
                "lastname": "4ABar_noces",
                "year_entrance": p_y_2016,
                "cesure": False,
                "user": None
            }, {
                "firstname": "4AFoo_ces",
                "lastname": "4ABar_ces",
                "year_entrance": p_y_2016,
                "cesure": True,
                "user": None
            },
        ]

        for e in data:
            models.ProfileUser.objects.create(
                **e
            )

    def test_get_schoolyear(self):
        current_year = datetime.datetime.now().year

        p_y_2019 = models.PromotionYear.objects.get(value=current_year)
        p_y_2018 = models.PromotionYear.objects.get(value=current_year-1)
        noces = models.ProfileUser.objects.get(firstname="Foo_noces")
        ces = models.ProfileUser.objects.get(firstname="Foo_ces")
        noces_2A = models.ProfileUser.objects.get(firstname="2AFoo_noces")
        ces_2A = models.ProfileUser.objects.get(firstname="2AFoo_ces")
        noces_3A = models.ProfileUser.objects.get(firstname="3AFoo_noces")
        ces_3A = models.ProfileUser.objects.get(firstname="3AFoo_ces")
        noces_4A = models.ProfileUser.objects.get(firstname="4AFoo_noces")
        ces_4A = models.ProfileUser.objects.get(firstname="4AFoo_ces")

        self.assertEqual(noces.get_schoolyear(), 1)
        self.assertEqual(ces.get_schoolyear(), 1)
        self.assertEqual(noces_2A.get_schoolyear(), 2)
        self.assertEqual(ces_2A.get_schoolyear(), 2)
        self.assertEqual(noces_3A.get_schoolyear(), 3)
        self.assertEqual(ces_3A.get_schoolyear(), 2)
        self.assertEqual(noces_4A.get_schoolyear(), 4)
        self.assertEqual(ces_4A.get_schoolyear(), 3)

        self.assertEqual(noces_2A.get_schoolyear(current_year-1), 1)
        self.assertEqual(ces_2A.get_schoolyear(current_year-1), 1)
        self.assertEqual(noces_3A.get_schoolyear(current_year-1), 2)
        self.assertEqual(ces_3A.get_schoolyear(current_year-1), 2)
        self.assertEqual(noces_4A.get_schoolyear(current_year-1), 3)
        self.assertEqual(ces_4A.get_schoolyear(current_year-1), 2)


class SlugTestCase:
    def test_slug_creation(self):
        example = self.model(name="Blaéé coucou")
        example.save()
        self.assertEqual(example.slug, "blaee-coucou")

        example = self.model(name="_à&é\"uàzfjwsdvwxùv;ùaze")
        example.save()
        self.assertEqual(example.slug, "_aeuazfjwsdvwxuvuaze")


class LearningAchievementTestCase(TestCase, SlugTestCase):
    def setUp(self):
        self.model = models.LearningAchievement


class CourseTestCase(TestCase, SlugTestCase):
    def setUp(self):
        self.model = models.Course