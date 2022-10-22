import mongoengine as me
import datetime

from .classes import Class, Enrollment


class Assignment(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))
    course = me.ReferenceField("Course", dbref=True, required=True)

    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )

    challenges = me.ListField(
        me.ReferenceField("Challenge", db_ref=True, required=True)
    )

    owner = me.ReferenceField("User", db_ref=True, required=True)
    contributors = me.ListField(me.ReferenceField("User", dbref=True, required=True))

    meta = {"collection": "assignments"}

    def get_solutions(self, user, class_):
        from sadhu import models

        solutions = models.Solution.objects(
            owner=user, enrolled_class=class_, challenge__in=self.challenges
        )

        return solutions

    def get_score(self, class_, user):
        from sadhu import models

        user_score = 0
        challenge_score = 0
        for challenge in self.challenges:
            solution = challenge.get_best_solution(class_, user)
            challenge_score += challenge.score
            if solution:
                user_score += solution.score

        score = 0
        if challenge_score != 0:
            score = user_score / challenge_score * self.score

        return score

    def check_user_submission(self, class_, user):
        from sadhu import models

        challenge_checker = dict()
        solutions = models.Solution.objects(
            owner=user, enrolled_class=class_, challenge__in=self.challenges
        )

        for s in solutions:
            challenge_checker[s.challenge.id] = s.status

        return challenge_checker

    def count_done_challenges(self, class_, user):
        # very slow need update
        count = 0
        for challenge in self.challenges:
            if challenge.is_done(class_, user):
                count += 1

        return count


def get_assignment_schedule(user):
    now = datetime.datetime.now()

    available_classes = Class.objects(
        (me.Q(started_date__lte=now) & me.Q(ended_date__gte=now))
    ).order_by("ended_date")

    ass_schedule = []
    for class_ in available_classes:
        if not class_.is_enrolled(user.id):
            continue

        for ass_t in class_.assignment_schedule:
            if ass_t.started_date <= now and now < ass_t.ended_date:
                ass_schedule.append(dict(assignment_schedule=ass_t, class_=class_))

    def order_by_ended_date(e):
        return e["assignment_schedule"].ended_date

    ass_schedule.sort(key=order_by_ended_date)
    return ass_schedule


def get_past_assignment_schedule(user):
    now = datetime.datetime.now()

    available_classes = Class.objects(
        (me.Q(started_date__lte=now) & me.Q(ended_date__gte=now))
    ).order_by("ended_date")

    ass_schedule = []
    for class_ in available_classes:
        if not class_.is_enrolled(user.id):
            continue

        for ass_t in class_.assignment_schedule:
            if now > ass_t.ended_date:
                ass_schedule.append(dict(assignment_schedule=ass_t, class_=class_))

    def order_by_ended_date(e):
        return e["assignment_schedule"].ended_date

    ass_schedule.sort(key=order_by_ended_date)
    return ass_schedule
