import mongoengine as me
import datetime

from .classes import Class, Enrollment

Assignment_level = [
    ("Easy"),
    ("Intermediate"),
    ("Advance"),
]
Random_or_not = [("Random Choice"), ("Not Random Choice")]


class Assignment(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))
    course = me.ReferenceField("Course", dbref=True, required=True)
    level = me.StringField(choice=Assignment_level)
    random_or_not = me.StringField(choices=Random_or_not)
    random_count = me.IntField()

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

    def get_class_scores(self, class_, users=None):
        """Compute score/completion for many users with a single query.

        The naive per-user, per-challenge approach (`get_best_solution`/
        `is_done` in a loop) issues one unindexed Mongo query per
        (user, challenge) pair, so a class page costs O(users * challenges)
        round-trips and times out as either grows. This fetches every
        relevant Solution once, then reduces to best-per-(user, challenge)
        in memory.
        """
        from sadhu import models

        if users is None:
            users = [e.user for e in class_.get_enrollments()]

        challenge_score_map = {c.id: c.score for c in self.challenges}
        total_challenge_score = sum(challenge_score_map.values())

        best_scores = {}
        if self.challenges and users:
            # as_pymongo() avoids dereferencing owner/challenge into full
            # documents (which would reintroduce one query per row).
            raw_solutions = (
                models.Solution.objects(
                    enrolled_class=class_,
                    challenge__in=self.challenges,
                    owner__in=users,
                )
                .only("owner", "challenge", "score")
                .as_pymongo()
            )

            for sol in raw_solutions:
                key = (sol["owner"].id, sol["challenge"].id)
                score = sol.get("score") or 0
                if key not in best_scores or score > best_scores[key]:
                    best_scores[key] = score

        results = {}
        for user in users:
            user_score = 0
            complete = 0
            challenge_scores = {}
            for challenge_id, c_score in challenge_score_map.items():
                best = best_scores.get((user.id, challenge_id), 0)
                challenge_scores[challenge_id] = best
                user_score += best
                if c_score != 0 and best == c_score:
                    complete += 1

            score = 0
            if total_challenge_score != 0:
                score = user_score / total_challenge_score * self.score

            results[user.id] = dict(
                score=score, complete=complete, challenge_scores=challenge_scores
            )

        return results

    def get_score(self, class_, user):
        return self.get_class_scores(class_, [user])[user.id]["score"]

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
        return self.get_class_scores(class_, [user])[user.id]["complete"]


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
