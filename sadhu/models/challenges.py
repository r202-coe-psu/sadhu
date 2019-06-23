import mongoengine as me
import datetime


class TestResult(me.EmbeddedDocument):
    test_case = me.ReferenceField('TestCase', required=True, dbref=True)
    started_date = me.DateTimeField(default=datetime.datetime.now,
                                    required=True)
    ended_date = me.DateTimeField(default=datetime.datetime.now,
                                  required=True)

    expected_result = me.StringField()
    output = me.StringField()

    timeout = me.BooleanField(default=False, required=True)
    validated = me.BooleanField(default=False, required=True)
    public = me.BooleanField(default=False, required=True)


class Solution(me.Document):
    code = me.FileField(required=True)
    output = me.StringField()
    messages = me.StringField()
    score = me.FloatField(required=True, default=0)
    passed = me.BooleanField(required=True, default=False)

    status = me.StringField(required=True, default='waiting')
    enrolled_class = me.ReferenceField('Class',
                                       required=True,
                                       dbref=True)
    assignment = me.ReferenceField('Assignment',
                                   required=True,
                                   dbref=True)
    challenge = me.ReferenceField('Challenge',
                                  required=True,
                                  dbref=True)
    owner = me.ReferenceField('User',
                              required=True,
                              dbref=True)

    submitted_date = me.DateTimeField(required=True,
                                      default=datetime.datetime.now)

    executed_date = me.DateTimeField()
    executed_ended_date = me.DateTimeField()
    language = me.StringField(required=True)
    test_results = me.ListField(me.EmbeddedDocumentField('TestResult'))

    metadata = me.DictField()

    meta = {'collection': 'solutions'}

    def count_pass_testcases(self):
        count = 0
        for t in self.test_results:
            if t.validated:
                count += 1

        return count


class TestCase(me.Document):
    input_file = me.FileField()
    is_inputfile = me.BooleanField(required=True, default=False)
    input_string = me.StringField()

    output_file = me.FileField()
    is_outputfile = me.BooleanField(required=True, default=False)
    output_string = me.StringField()

    public = me.BooleanField(required=True, default=False)

    challenge = me.ReferenceField('Challenge', dbref=True, required=True)
    owner = me.ReferenceField('User', dbref=True, required=True)
    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    meta = {'collection': 'test_cases'}


class ChallengeStatus(me.Document):

    user = me.ReferenceField('User', dbref=True, required=True)
    challenge = me.ReferenceField('Challenge', dbref=True, required=True)
    assignment = me.ReferenceField('Assignment', dbref=True, required=True)
    enrolled_class = me.ReferenceField('Class', dbref=True, required=True)

    first_view = me.DateTimeField(required=True,
                                  default=datetime.datetime.now)

    meta = {'collection': 'challenge_status'}


class Challenge(me.Document):
    name = me.StringField(required=True)
    description = me.StringField(required=True)
    problem_statement = me.StringField(required=True)
    input_format = me.StringField()
    output_format = me.StringField()
    constraints = me.StringField(required=True)

    score = me.IntField(required=True, default=0)
    tags = me.ListField(me.StringField(required=True))

    test_cases = me.ListField(
            me.ReferenceField('TestCase',
                              dbref=True,
                              required=True))

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)

    owner = me.ReferenceField('User', dbref=True, required=True)
    contributors = me.ListField(
            me.ReferenceField('User',
                              dbref=True,
                              required=True))

    meta = {'collection': 'challenges'}

    def get_solutions(self, class_, user):
        return Solution.objects(challenge=self,
                                enrolled_class=class_,
                                owner=user)

    def get_best_solution(self, class_, user):
        solutions = self.get_solutions(class_, user)
        if not solutions:
            return None

        best_solution = None
        if solutions.count() > 0:
            best_solution = solutions[0]

        for solution in solutions:
            if solution.score > best_solution.score:
                best_solution = solution

        return best_solution

    def get_solution_score(self, class_, user):
        solution = self.get_best_solution(class_, user)
        if solution:
            return solution.score

        return 0

    def get_challenge_access(self, class_, user):
        return ChallengeStatus.objects(enrolled_class=class_,
                                       challenge=self,
                                       user=user).first()

    def is_done(self, class_, user):

        if self.get_solution_score(class_, user) == self.score:
            return True

        return False
